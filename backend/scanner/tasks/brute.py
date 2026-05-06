from scanner.utils import run_cmd, log_to_job, ensure_results_dir


# Default credentials to try per service
DEFAULT_CREDS = {
    'ssh':   [('admin','admin'), ('root','root'), ('admin','password'), ('root','toor')],
    'ftp':   [('anonymous',''), ('admin','admin'), ('ftp','ftp')],
    'mysql': [('root',''), ('root','root'), ('admin','admin')],
    'mssql': [('sa',''), ('sa','sa'), ('admin','admin')],
    'rdp':   [('administrator',''), ('admin','admin')],
    'redis': [('',''), ('default','')],
    'http':  [],
}

SERVICE_PORT_MAP = {
    22: 'ssh', 21: 'ftp', 3306: 'mysql', 1433: 'mssql',
    3389: 'rdp', 6379: 'redis', 5432: 'postgres',
}


def brute_force(job):
    from core.models import Host, Port, Credential, Vulnerability

    config    = job.config.get('brute', {})
    services  = config.get('services', ['ssh', 'ftp', 'mysql', 'mssql', 'rdp', 'redis'])
    max_tries = config.get('max_tries', 10)

    results_dir = ensure_results_dir(job.id)
    log_to_job(job, f'🔑 Credential audit sobre: {", ".join(services)}')

    ports = Port.objects.filter(
        host__engagement=job.engagement, state='open',
        number__in=SERVICE_PORT_MAP.keys()
    ).select_related('host')

    for port in ports:
        svc = SERVICE_PORT_MAP.get(port.number)
        if svc not in services:
            continue

        creds = DEFAULT_CREDS.get(svc, [])[:max_tries]
        if not creds:
            continue

        log_to_job(job, f'  → {port.host.ip_address}:{port.number} ({svc})')

        for user, passwd in creds:
            valid = _try_credential(svc, port.host.ip_address, port.number, user, passwd)
            if valid:
                Credential.objects.get_or_create(
                    host=port.host, service=svc, username=user,
                    defaults={'password': passwd, 'port': port, 'valid': True}
                )
                Vulnerability.objects.get_or_create(
                    host=port.host, title=f'Credencial por defecto — {svc} ({user}:{passwd or "vacío"})',
                    defaults={
                        'severity':    'critical',
                        'description': f'Login exitoso con credenciales por defecto en {svc}',
                        'evidence':    f'{user}:{passwd} válido en {port.host.ip_address}:{port.number}',
                        'source':      'brute',
                        'port':        port,
                        'solution':    'Cambiar credenciales inmediatamente. Aplicar política de contraseñas.',
                    }
                )
                log_to_job(job, f'    [CRITICAL] 🔓 {user}:{passwd} — VÁLIDO', 'error')
                break


def _try_credential(service, host, port, user, password):
    """Try a single credential via hydra."""
    pass_arg  = password if password else ''
    pass_flag = f'-p "{pass_arg}"' if pass_arg else '-p ""'

    cmd = (
        f'hydra -l "{user}" {pass_flag} -t 1 -T 1 '
        f'{host} -s {port} {service} 2>/dev/null'
    )
    stdout, rc = run_cmd(cmd, timeout=15)
    return '[SUCCESS]' in stdout or '1 valid password' in stdout
