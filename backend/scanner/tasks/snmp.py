from scanner.utils import run_cmd, log_to_job, ensure_results_dir


def snmp_audit(job):
    from core.models import Host, Port, Vulnerability

    snmp_hosts = Host.objects.filter(
        engagement=job.engagement, is_alive=True,
        ports__number=161, ports__state='open'
    ).distinct()

    if not snmp_hosts.exists():
        log_to_job(job, 'No hay hosts con SNMP (161/UDP)', 'info')
        return

    log_to_job(job, f'📡 SNMP audit sobre {snmp_hosts.count()} hosts')
    results_dir = ensure_results_dir(job.id)
    COMMON_COMMUNITIES = ['public', 'private', 'community', 'snmp', 'manager', 'admin']

    for host in snmp_hosts:
        ip = host.ip_address
        log_to_job(job, f'  → {ip}')

        for community in COMMON_COMMUNITIES:
            stdout, rc = run_cmd(
                f'snmpwalk -v2c -c {community} {ip} sysDescr 2>/dev/null',
                timeout=10
            )
            if rc == 0 and stdout.strip():
                port = Port.objects.filter(host=host, number=161).first()
                Vulnerability.objects.get_or_create(
                    host=host, title=f'SNMP Community String débil: "{community}"',
                    defaults={
                        'severity':    'high' if community in ('public', 'private') else 'medium',
                        'description': f'Community string "{community}" aceptada en {ip}:161',
                        'evidence':    stdout[:500],
                        'source':      'snmpwalk',
                        'port':        port,
                        'solution':    'Cambiar community strings. Migrar a SNMPv3 con autenticación.',
                    }
                )
                log_to_job(job, f'    [HIGH] SNMP community "{community}" válida')
                break
