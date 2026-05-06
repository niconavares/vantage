"""
Claude AI integration — cerebro de VANTAGE.
Analiza resultados de escaneo, prioriza vulnerabilidades,
sugiere rutas de ataque y genera narrativas de informe.
"""
import anthropic
import logging
from django.conf import settings

logger = logging.getLogger(__name__)

_client = None


def get_client():
    global _client
    if _client is None:
        _client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)
    return _client


SYSTEM_PROMPT = """Eres un experto en ciberseguridad y pentesting de redes con 15 años de experiencia.
Trabajas como consultor para auditorías profesionales de empresas. Tu rol en VANTAGE es:

1. Analizar resultados de escaneos de red (nmap, nuclei, etc.)
2. Priorizar vulnerabilidades por riesgo REAL (no solo por CVSS teórico)
3. Identificar cadenas de ataque: cómo un atacante encadenaría los hallazgos
4. Generar remediaciones concretas y accionables
5. Redactar hallazgos en lenguaje profesional para informes de auditoría

Siempre responde en español. Sé directo, técnico y preciso.
No inventes vulnerabilidades. Si los datos son insuficientes, dilo claramente."""


def ask(prompt: str, system: str = None, max_tokens: int = 2000) -> str:
    """Simple one-shot query to Claude."""
    try:
        response = get_client().messages.create(
            model=settings.CLAUDE_MODEL,
            max_tokens=max_tokens,
            system=system or SYSTEM_PROMPT,
            messages=[{'role': 'user', 'content': prompt}]
        )
        return response.content[0].text
    except Exception as e:
        logger.error(f'Claude API error: {e}')
        return f'[Error Claude API: {e}]'


def analyze_host(host) -> str:
    """Generate AI summary for a single host."""
    from core.models import Port, Vulnerability

    ports = list(host.ports.filter(state='open').values(
        'number', 'protocol', 'service', 'product', 'version'
    ))
    vulns = list(host.vulnerabilities.values(
        'title', 'severity', 'cvss_score', 'cve_id', 'description'
    ))

    prompt = f"""Analiza este host de red y proporciona un resumen de seguridad conciso:

**Host:** {host.ip_address} ({host.hostname or 'sin hostname'})
**OS:** {host.os_name or 'desconocido'} ({host.os_family})
**Puertos abiertos:** {len(ports)}
{_format_ports(ports)}

**Vulnerabilidades encontradas:** {len(vulns)}
{_format_vulns(vulns)}

Proporciona:
1. Resumen ejecutivo del riesgo (2-3 líneas)
2. La vulnerabilidad más crítica y por qué
3. Vector de ataque más probable
4. Acción inmediata recomendada

Formato: texto plano, máximo 200 palabras."""

    return ask(prompt, max_tokens=400)


def analyze_engagement(engagement) -> dict:
    """Full AI analysis of an engagement — generates attack path + risk narrative."""
    from core.models import Host, Vulnerability, Credential

    hosts = Host.objects.filter(engagement=engagement, is_alive=True)
    vulns = Vulnerability.objects.filter(host__engagement=engagement)
    creds = Credential.objects.filter(host__engagement=engagement)

    by_sev = {
        'critical': vulns.filter(severity='critical').count(),
        'high':     vulns.filter(severity='high').count(),
        'medium':   vulns.filter(severity='medium').count(),
        'low':      vulns.filter(severity='low').count(),
    }

    top_vulns = list(vulns.filter(severity__in=['critical','high'])
                     .values('title', 'severity', 'host__ip_address', 'cve_id', 'description')[:15])

    cred_list = list(creds.values('service', 'username', 'password', 'host__ip_address')[:10])

    prompt = f"""Análisis completo de auditoría de red para el cliente: {engagement.client}

**Resumen del scope:**
- Hosts descubiertos: {hosts.count()}
- Sistemas Windows: {hosts.filter(os_family='windows').count()}
- Sistemas Linux: {hosts.filter(os_family='linux').count()}
- Dispositivos de red: {hosts.filter(os_family='network').count()}

**Vulnerabilidades:**
- Críticas: {by_sev['critical']}
- Altas: {by_sev['high']}
- Medias: {by_sev['medium']}
- Bajas: {by_sev['low']}

**Top vulnerabilidades críticas/altas:**
{_format_vulns(top_vulns)}

**Credenciales comprometidas:** {len(cred_list)}
{_format_creds(cred_list)}

Por favor proporciona:
1. **Resumen ejecutivo** (para el CEO, no técnico, 3-4 párrafos)
2. **Cadena de ataque principal** — paso a paso cómo un atacante podría comprometer la red
3. **Top 5 hallazgos críticos** con impacto de negocio
4. **Plan de remediación** priorizado (Quick wins vs largo plazo)
5. **Nivel de riesgo global** (Crítico/Alto/Medio/Bajo) con justificación"""

    analysis = ask(prompt, max_tokens=3000)

    # Also ask for attack path visualization data
    attack_path_prompt = f"""Basándote en estos hallazgos de {engagement.client},
genera un JSON con la cadena de ataque más probable. Formato:
{{
  "steps": [
    {{"step": 1, "action": "...", "host": "IP", "vuln": "...", "technique": "MITRE ATT&CK ID"}},
    ...
  ],
  "entry_point": "descripción del punto de entrada",
  "max_impact": "descripción del peor escenario"
}}

Vulnerabilidades disponibles: {_format_vulns(top_vulns[:5])}
Credenciales: {_format_creds(cred_list[:3])}

Responde SOLO con el JSON, sin texto adicional."""

    import json
    attack_path_raw = ask(attack_path_prompt, max_tokens=1000)
    try:
        # Extract JSON from response
        start = attack_path_raw.find('{')
        end   = attack_path_raw.rfind('}') + 1
        attack_path = json.loads(attack_path_raw[start:end])
    except Exception:
        attack_path = {'steps': [], 'entry_point': '', 'max_impact': ''}

    return {
        'analysis':    analysis,
        'attack_path': attack_path,
    }


def analyze_vulnerability(vuln) -> str:
    """Deep-dive analysis of a specific vulnerability."""
    prompt = f"""Analiza esta vulnerabilidad encontrada en una auditoría de red:

**Vulnerabilidad:** {vuln.title}
**Severidad:** {vuln.severity} (CVSS: {vuln.cvss_score or 'N/A'})
**CVE:** {vuln.cve_id or 'N/A'}
**Host afectado:** {vuln.host.ip_address} ({vuln.host.os_name or 'OS desconocido'})
**Puerto:** {f"{vuln.port.number}/{vuln.port.protocol}" if vuln.port else 'N/A'}
**Descripción:** {vuln.description[:500]}
**Evidencia:** {vuln.evidence[:300] if vuln.evidence else 'N/A'}

Proporciona:
1. Explicación técnica del riesgo (2-3 líneas)
2. Cómo un atacante la explotaría (paso a paso, sin código malicioso)
3. Impacto de negocio si se explota
4. Remediación específica y concreta
5. Referencias adicionales si las hay

Máximo 300 palabras."""

    return ask(prompt, max_tokens=600)


def generate_report_narrative(engagement, section: str) -> str:
    """Generate a specific section of the audit report."""
    sections = {
        'executive': """Escribe la sección "Resumen Ejecutivo" del informe de auditoría.
Tono: profesional, no técnico, orientado a riesgos de negocio.
Longitud: 400-500 palabras. Incluye: contexto, metodología resumida, hallazgos clave, recomendación general.""",

        'methodology': """Escribe la sección "Metodología" del informe de auditoría de red.
Describe las fases: reconocimiento, escaneo de puertos, detección de servicios, análisis de vulnerabilidades,
auditoría de autenticación, análisis de configuraciones.
Menciona las herramientas: nmap, nuclei, testssl, hydra, enum4linux.
Tono técnico pero comprensible. 300-400 palabras.""",

        'conclusions': """Escribe la sección "Conclusiones y Próximos Pasos" del informe.
Incluye: nivel de madurez de seguridad de la organización, patrón de vulnerabilidades observado,
hoja de ruta de remediación en 3 fases (0-30 días / 30-90 días / 90-180 días).
Cierra con recomendación de seguimiento. 300-400 palabras.""",
    }

    section_prompt = sections.get(section, '')
    if not section_prompt:
        return ''

    from core.models import Vulnerability
    vulns = Vulnerability.objects.filter(host__engagement=engagement)
    context = f"""
Cliente: {engagement.client}
Nombre auditoría: {engagement.name}
Período: {engagement.start_date} — {engagement.end_date}
Hosts auditados: {engagement.hosts.count()}
Vulnerabilidades críticas: {vulns.filter(severity='critical').count()}
Vulnerabilidades altas: {vulns.filter(severity='high').count()}
Vulnerabilidades medias: {vulns.filter(severity='medium').count()}
"""
    return ask(f"{context}\n\n{section_prompt}", max_tokens=800)


# ── Helpers ───────────────────────────────────────────────────────────────────

def _format_ports(ports):
    if not ports:
        return '  (ninguno)\n'
    lines = []
    for p in ports[:20]:
        ver = f" {p.get('product','')} {p.get('version','')}".strip()
        lines.append(f"  - {p['number']}/{p['protocol']} {p.get('service','?')}{' — '+ver if ver else ''}")
    return '\n'.join(lines)


def _format_vulns(vulns):
    if not vulns:
        return '  (ninguna)\n'
    lines = []
    for v in vulns[:15]:
        ip  = v.get('host__ip_address', v.get('host', {}).get('ip', '?'))
        cve = f" [{v.get('cve_id','')}]" if v.get('cve_id') else ''
        lines.append(f"  - [{v.get('severity','?').upper()}] {v.get('title','?')}{cve} @ {ip}")
    return '\n'.join(lines)


def _format_creds(creds):
    if not creds:
        return '  (ninguna)\n'
    lines = []
    for c in creds:
        ip = c.get('host__ip_address', '?')
        lines.append(f"  - {c.get('service','?')}://{c.get('username','?')}:{c.get('password','?')} @ {ip}")
    return '\n'.join(lines)
