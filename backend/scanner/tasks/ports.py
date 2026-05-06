import xml.etree.ElementTree as ET
import logging
from scanner.utils import run_cmd, log_to_job, ensure_results_dir

logger = logging.getLogger(__name__)

OS_FAMILY_MAP = {
    'windows': 'windows', 'linux': 'linux', 'ubuntu': 'linux',
    'debian': 'linux', 'centos': 'linux', 'fedora': 'linux',
    'macos': 'macos', 'darwin': 'macos', 'ios': 'macos',
    'cisco': 'network', 'juniper': 'network', 'fortinet': 'network',
    'freebsd': 'linux', 'android': 'linux',
}


def port_scan(job):
    """Full TCP + UDP port scan with OS detection."""
    from core.models import Host

    results_dir = ensure_results_dir(job.id)
    config = job.config.get('port', {})
    timing       = config.get('timing', 'T4')
    ports        = config.get('ports', 'top-1000')   # top-1000, top-100, 1-65535
    udp          = config.get('udp', False)
    os_detection = config.get('os_detection', True)
    scripts      = config.get('scripts', True)

    hosts = Host.objects.filter(engagement=job.engagement, is_alive=True)
    if not hosts.exists():
        log_to_job(job, 'No hay hosts vivos. Ejecuta discovery primero.', 'warning')
        return

    targets_str = ' '.join(h.ip_address for h in hosts)
    log_to_job(job, f'🔌 Port scan sobre {hosts.count()} hosts')

    # Build nmap command
    nmap_out = f'{results_dir}/ports.xml'
    port_spec = f'--top-ports 1000' if ports == 'top-1000' else \
                f'--top-ports 100'  if ports == 'top-100'  else \
                f'-p {ports}'

    version_intensity = config.get('version_intensity', 5)
    flags = [f'-sS -{timing}', port_spec]
    if os_detection: flags.append('-O --osscan-guess')
    if scripts:      flags.append(f'-sV --version-intensity {version_intensity}')
    if udp:          flags.append('-sU --top-ports 100')
    flags.append(f'-oX {nmap_out}')
    flags.append('--max-retries 2 --open')

    cmd = f'nmap {" ".join(flags)} {targets_str}'
    log_to_job(job, f'🗺️  {cmd}')
    stdout, rc = run_cmd(cmd, timeout=7200)

    ports_found = _parse_nmap_ports(job, nmap_out)
    job.ports_found = ports_found
    job.save(update_fields=['ports_found'])
    log_to_job(job, f'✅ {ports_found} puertos abiertos encontrados', 'success')


def _parse_nmap_ports(job, xml_path):
    from core.models import Host, Port

    try:
        tree = ET.parse(xml_path)
        root = tree.getroot()
    except Exception as e:
        log_to_job(job, f'Error parsing nmap XML: {e}', 'error')
        return 0

    total_ports = 0

    for host_el in root.findall('host'):
        status = host_el.find('status')
        if status is None or status.get('state') != 'up':
            continue

        ip = None
        for addr in host_el.findall('address'):
            if addr.get('addrtype') == 'ipv4':
                ip = addr.get('addr')
        if not ip:
            continue

        try:
            host = Host.objects.get(engagement=job.engagement, ip_address=ip)
        except Host.DoesNotExist:
            continue

        # OS detection
        os_el = host_el.find('os')
        if os_el is not None:
            best_match = None
            best_acc   = 0
            for osmatch in os_el.findall('osmatch'):
                acc = int(osmatch.get('accuracy', 0))
                if acc > best_acc:
                    best_acc   = acc
                    best_match = osmatch.get('name', '')
            if best_match:
                family = 'unknown'
                bm_lower = best_match.lower()
                for key, val in OS_FAMILY_MAP.items():
                    if key in bm_lower:
                        family = val
                        break
                host.os_name     = best_match
                host.os_family   = family
                host.os_accuracy = best_acc

        # Ports
        ports_el = host_el.find('ports')
        open_count = 0
        if ports_el is not None:
            for port_el in ports_el.findall('port'):
                state_el = port_el.find('state')
                if state_el is None or state_el.get('state') != 'open':
                    continue

                portnum   = int(port_el.get('portid'))
                proto     = port_el.get('protocol', 'tcp')
                service   = ''
                product   = ''
                version   = ''
                extra     = ''
                cpe       = ''
                banner    = ''

                svc_el = port_el.find('service')
                if svc_el is not None:
                    service = svc_el.get('name', '')
                    product = svc_el.get('product', '')
                    version = svc_el.get('version', '')
                    extra   = svc_el.get('extrainfo', '')
                    cpe     = ' '.join(c.get('item', '') for c in svc_el.findall('cpe'))

                # Banner from scripts
                for script in port_el.findall('script'):
                    if script.get('id') in ('banner', 'ssh-hostkey'):
                        banner = script.get('output', '')[:500]

                Port.objects.update_or_create(
                    host=host, number=portnum, protocol=proto,
                    defaults={
                        'state':   'open',
                        'service': service,
                        'product': product,
                        'version': version,
                        'extra_info': extra,
                        'cpe':     cpe,
                        'banner':  banner,
                    }
                )
                open_count += 1
                total_ports += 1

        host.open_ports = open_count
        host.save()
        log_to_job(job, f'  {ip} — {open_count} puertos abiertos ({host.os_name or "OS desconocido"})')

    return total_ports
