from scanner.utils import run_cmd, log_to_job, ensure_results_dir


def ad_audit(job):
    """Active Directory enumeration: LDAP, Kerberos, BloodHound."""
    from core.models import Host, Port, Vulnerability

    ad_hosts = Host.objects.filter(
        engagement=job.engagement, is_alive=True,
        ports__number__in=[389, 636, 88, 445], ports__state='open'
    ).distinct()

    if not ad_hosts.exists():
        log_to_job(job, 'No se detectaron Domain Controllers (389/636/88)', 'info')
        return

    results_dir = ensure_results_dir(job.id)
    log_to_job(job, f'🏰 Active Directory audit sobre {ad_hosts.count()} posibles DCs')

    for host in ad_hosts:
        ip = host.ip_address
        log_to_job(job, f'  → DC: {ip}')

        # LDAP null bind
        stdout, rc = run_cmd(
            f'nmap -p 389 --script ldap-rootdse,ldap-search {ip} 2>/dev/null',
            timeout=60
        )

        if 'rootDomainNamingContext' in stdout or 'defaultNamingContext' in stdout:
            log_to_job(job, f'    LDAP responde — posible DC')

            # Check null bind
            null_stdout, null_rc = run_cmd(
                f'ldapsearch -x -h {ip} -p 389 -b "" -s base 2>/dev/null | head -20',
                timeout=30
            )
            if null_rc == 0 and 'namingContexts' in null_stdout:
                Vulnerability.objects.get_or_create(
                    host=host, title='LDAP Null Bind habilitado',
                    defaults={
                        'severity':    'medium',
                        'description': 'El servidor LDAP permite bind anónimo, exponiendo información del directorio.',
                        'evidence':    null_stdout[:500],
                        'source':      'ldapsearch',
                        'solution':    'Deshabilitar bind anónimo en Active Directory.',
                    }
                )

        # Kerberos user enumeration
        stdout, _ = run_cmd(
            f'nmap -p 88 --script krb5-enum-users '
            f'--script-args "krb5-enum-users.realm=WORKGROUP" {ip} 2>/dev/null',
            timeout=60
        )
        if 'Valid user' in stdout or 'Account disabled' in stdout:
            log_to_job(job, f'    [INFO] Kerberos user enumeration posible')

    log_to_job(job, '✅ AD audit completado', 'success')
