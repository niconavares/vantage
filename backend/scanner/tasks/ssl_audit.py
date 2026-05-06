import json
import logging
from scanner.utils import run_cmd, log_to_job, ensure_results_dir

logger = logging.getLogger(__name__)


def ssl_audit(job):
    """Audit SSL/TLS on HTTPS ports using testssl.sh / nmap NSE."""
    from core.models import Host, Port, Vulnerability

    results_dir = ensure_results_dir(job.id)
    ssl_ports = Port.objects.filter(
        host__engagement=job.engagement, state='open'
    ).filter(
        number__in=[443, 8443, 8080, 465, 993, 995, 636, 3389]
    ) | Port.objects.filter(
        host__engagement=job.engagement, state='open', service__in=['https', 'ssl', 'tls']
    )

    if not ssl_ports.exists():
        log_to_job(job, 'No hay puertos SSL/TLS detectados', 'info')
        return

    log_to_job(job, f'🔐 SSL/TLS audit sobre {ssl_ports.count()} puertos')
    count = 0

    for port in ssl_ports.select_related('host')[:50]:
        target = f'{port.host.ip_address}:{port.number}'
        out_file = f'{results_dir}/ssl_{port.host.ip_address}_{port.number}.json'

        # Use nmap ssl scripts (faster, always available)
        nmap_cmd = (
            f'nmap -sV --script ssl-enum-ciphers,ssl-cert,ssl-heartbleed,'
            f'ssl-poodle,ssl-dh-params,ssl2-enum-algos '
            f'-p {port.number} {port.host.ip_address} '
            f'-oX {out_file.replace(".json",".xml")} 2>/dev/null'
        )
        log_to_job(job, f'  🔍 {target}')
        stdout, _ = run_cmd(nmap_cmd, timeout=120)

        # Parse nmap script output for known issues
        issues = _parse_ssl_issues(stdout, port.host, port)
        count += len(issues)

    log_to_job(job, f'✅ SSL audit: {count} issues encontrados', 'success')


def _parse_ssl_issues(nmap_stdout, host, port):
    from core.models import Vulnerability

    issues = []
    checks = {
        'ssl-heartbleed': ('Heartbleed (CVE-2014-0160)', 'critical', 'CVE-2014-0160'),
        'ssl-poodle':     ('POODLE — SSLv3 vulnerable', 'high', 'CVE-2014-3566'),
        'ssl2':           ('SSLv2 habilitado', 'high', ''),
        'VULNERABLE':     ('SSL/TLS vulnerability detected', 'high', ''),
        'NULL':           ('Cipher suite NULL — sin cifrado', 'critical', ''),
        'EXPORT':         ('Cipher suite EXPORT — cifrado débil (FREAK/LOGJAM)', 'high', ''),
        'RC4':            ('RC4 habilitado — cifrado obsoleto', 'medium', ''),
        'MD5':            ('Certificado firmado con MD5', 'medium', ''),
        'SHA-1':          ('Certificado firmado con SHA-1 (deprecated)', 'low', ''),
    }

    for keyword, (title, severity, cve) in checks.items():
        if keyword in nmap_stdout:
            vuln, created = Vulnerability.objects.get_or_create(
                host=host, title=title, port=port,
                defaults={
                    'severity':    severity,
                    'description': f'Detectado en {host.ip_address}:{port.number}',
                    'evidence':    nmap_stdout[:500],
                    'source':      'nmap-ssl',
                    'cve_id':      cve,
                }
            )
            if created:
                issues.append(vuln)

    return issues
