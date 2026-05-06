import logging
import xml.etree.ElementTree as ET
from scanner.utils import run_cmd, log_to_job, ensure_results_dir

logger = logging.getLogger(__name__)


def host_discovery(job):
    """Discover live hosts using nmap ping scan + masscan for speed."""
    results_dir = ensure_results_dir(job.id)
    targets_str = ' '.join(job.targets)
    config = job.config.get('discovery', {})
    timing = config.get('timing', 'T4')
    use_masscan = config.get('use_masscan', False)

    log_to_job(job, f'🔭 Host discovery sobre: {targets_str}')

    # Fast masscan ping sweep (optional, needs root)
    if use_masscan:
        masscan_out = f'{results_dir}/masscan_hosts.txt'
        cmd = f'masscan {targets_str} --ping -p0 --rate=1000 -oG {masscan_out} 2>/dev/null'
        log_to_job(job, f'⚡ masscan: {cmd}')
        run_cmd(cmd)

    # nmap ICMP + TCP SYN/ACK discovery (more probes for routers/firewalls)
    nmap_out = f'{results_dir}/discovery.xml'
    cmd = (
        f'nmap -sn -PE -PS22,80,443,8080,8443 -PA80,443 -{timing} --max-retries 2 '
        f'-oX {nmap_out} {targets_str} 2>&1'
    )
    log_to_job(job, f'🗺️  nmap: {cmd}')
    stdout, rc = run_cmd(cmd)

    if rc != 0:
        log_to_job(job, f'nmap returned code {rc}', 'warning')

    # Parse nmap XML
    hosts_found = _parse_nmap_discovery(job, nmap_out)

    # Fallback: if target is a single IP (not CIDR) and nmap found nothing,
    # try a direct TCP connect to confirm liveness before giving up
    if hosts_found == 0 and len(job.targets) == 1 and '/' not in job.targets[0]:
        single_ip = job.targets[0]
        probe_out = f'{results_dir}/discovery_fallback.xml'
        probe_cmd = f'nmap -sT -p 80,443,22,53 --max-retries 1 -oX {probe_out} {single_ip} 2>&1'
        log_to_job(job, f'🔄 Fallback TCP probe: {probe_cmd}')
        run_cmd(probe_cmd)
        hosts_found = _parse_nmap_discovery(job, probe_out)
        if hosts_found == 0:
            # Last resort: check if nmap can reach it at all ignoring host discovery
            check_cmd = f'nmap -Pn -p 80 --max-retries 1 {single_ip} 2>&1'
            chk_out, chk_rc = run_cmd(check_cmd, timeout=15)
            if 'open' in chk_out or 'filtered' in chk_out:
                log_to_job(job, f'  ⚡ Host reachable (Pn probe) — forzando como activo')
                from core.models import Host
                host, _ = Host.objects.update_or_create(
                    engagement=job.engagement, ip_address=single_ip,
                    defaults={'is_alive': True}
                )
                hosts_found = 1
                log_to_job(job, f'  + Host: {single_ip} (descubierto via TCP probe)')

    job.hosts_found = hosts_found
    job.save(update_fields=['hosts_found'])
    log_to_job(job, f'✅ {hosts_found} hosts vivos encontrados', 'success')


def _parse_nmap_discovery(job, xml_path):
    from core.models import Host

    try:
        tree = ET.parse(xml_path)
        root = tree.getroot()
    except Exception as e:
        log_to_job(job, f'Error parsing nmap XML: {e}', 'error')
        return 0

    count = 0
    for host_el in root.findall('host'):
        status = host_el.find('status')
        if status is None or status.get('state') != 'up':
            continue

        # Get IP
        ip = None
        for addr in host_el.findall('address'):
            if addr.get('addrtype') == 'ipv4':
                ip = addr.get('addr')
            elif addr.get('addrtype') == 'mac':
                mac = addr.get('addr', '')

        if not ip:
            continue

        # Skip invalid/reserved IPs
        if ip in ('0.0.0.0', '255.255.255.255') or ip.startswith('0.'):
            log_to_job(job, f'  ⚠️  IP inválida ignorada: {ip}', 'warning')
            continue

        # Hostname
        hostname = ''
        hostnames_el = host_el.find('hostnames')
        if hostnames_el is not None:
            hn = hostnames_el.find('hostname')
            if hn is not None:
                hostname = hn.get('name', '')

        host, created = Host.objects.update_or_create(
            engagement=job.engagement,
            ip_address=ip,
            defaults={
                'hostname': hostname,
                'is_alive': True,
            }
        )
        if not created:
            # Update hostname if discovered
            if hostname and not host.hostname:
                host.hostname = hostname
                host.save(update_fields=['hostname'])
        count += 1
        log_to_job(job, f'  + Host: {ip} ({hostname or "sin hostname"})')

    return count
