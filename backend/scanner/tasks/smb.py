import logging
from scanner.utils import run_cmd, log_to_job, ensure_results_dir

logger = logging.getLogger(__name__)


def smb_audit(job):
    """Audit SMB/Windows: shares, signing, EternalBlue, null sessions."""
    from core.models import Host, Port, Vulnerability

    smb_hosts = Host.objects.filter(
        engagement=job.engagement, is_alive=True,
        ports__number__in=[139, 445], ports__state='open'
    ).distinct()

    if not smb_hosts.exists():
        log_to_job(job, 'No hay hosts con SMB (139/445)', 'info')
        return

    log_to_job(job, f'🪟 SMB audit sobre {smb_hosts.count()} hosts')
    results_dir = ensure_results_dir(job.id)

    for host in smb_hosts:
        ip = host.ip_address
        log_to_job(job, f'  → {ip}')

        # nmap SMB scripts
        nmap_cmd = (
            f'nmap -p 139,445 --script smb-security-mode,smb-vuln-ms17-010,'
            f'smb-vuln-ms08-067,smb-enum-shares,smb-os-discovery,'
            f'smb2-security-mode,smb2-capabilities '
            f'{ip} 2>/dev/null'
        )
        stdout, _ = run_cmd(nmap_cmd, timeout=120)

        _parse_smb_issues(job, host, stdout, ip)

        # enum4linux for extra info
        enum_out = f'{results_dir}/enum4linux_{ip}.txt'
        run_cmd(f'enum4linux -a {ip} > {enum_out} 2>&1', timeout=120)


def _parse_smb_issues(job, host, nmap_out, ip):
    from core.models import Port, Vulnerability

    port = Port.objects.filter(host=host, number=445).first() or \
           Port.objects.filter(host=host, number=139).first()

    checks = [
        ('ms17-010 VULNERABLE',    'EternalBlue (MS17-010) — RCE sin autenticación', 'critical', 'CVE-2017-0144'),
        ('ms08-067 VULNERABLE',    'MS08-067 — RCE legacy', 'critical', 'CVE-2008-4250'),
        ('Message signing enabled but not required',
                                   'SMB Signing no requerido — vulnerable a relay attacks', 'high', ''),
        ('Message signing disabled', 'SMB Signing deshabilitado — relay attacks posibles', 'high', ''),
        ('guest',                  'Sesión NULL/Guest habilitada', 'medium', ''),
    ]

    for keyword, title, severity, cve in checks:
        if keyword.lower() in nmap_out.lower():
            Vulnerability.objects.get_or_create(
                host=host, title=title, port=port,
                defaults={
                    'severity':    severity,
                    'description': f'Detectado en {ip} via SMB audit',
                    'evidence':    nmap_out[:1000],
                    'source':      'nmap-smb',
                    'cve_id':      cve,
                    'solution':    _get_smb_solution(title),
                }
            )
            log_to_job(job, f'    [{severity.upper()}] {title}')


def _get_smb_solution(title):
    solutions = {
        'EternalBlue': 'Aplicar parche MS17-010 urgentemente. Deshabilitar SMBv1.',
        'MS08-067':    'Aplicar parche MS08-067. Sistema probablemente sin soporte.',
        'SMB Signing': 'Habilitar y requerir SMB Signing en Group Policy.',
        'NULL':        'Deshabilitar sesiones anónimas. Configurar RestrictAnonymous=2.',
    }
    for key, sol in solutions.items():
        if key.lower() in title.lower():
            return sol
    return ''
