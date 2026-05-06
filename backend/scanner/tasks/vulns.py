import json
import logging
from scanner.utils import run_cmd, log_to_job, ensure_results_dir

logger = logging.getLogger(__name__)

SEVERITY_MAP = {'critical': 'critical', 'high': 'high', 'medium': 'medium',
                'low': 'low', 'info': 'info', 'unknown': 'info'}


def vuln_scan(job):
    """Run nuclei (network + service templates) against discovered hosts."""
    from core.models import Host, Port

    results_dir = ensure_results_dir(job.id)
    config   = job.config.get('vuln', {})
    severity = config.get('severity', ['critical', 'high', 'medium'])
    tags     = config.get('tags', ['network', 'service', 'cve', 'misconfigurations',
                                    'exposed-panels', 'default-logins'])
    rate     = config.get('rate_limit', 50)
    threads  = config.get('threads', 10)

    hosts = Host.objects.filter(engagement=job.engagement, is_alive=True)
    if not hosts.exists():
        log_to_job(job, 'No hay hosts. Ejecuta discovery+port scan primero.', 'warning')
        return

    # Build targets file: ip:port for each open port
    targets_file = f'{results_dir}/vuln_targets.txt'
    with open(targets_file, 'w') as f:
        for host in hosts:
            for port in host.ports.filter(state='open'):
                scheme = 'https' if port.service in ('https', 'ssl') or port.number in (443, 8443) else 'http'
                if port.service in ('ssh', 'ftp', 'smtp', 'smb', 'rdp', 'mysql', 'mssql', 'redis', 'mongodb'):
                    f.write(f'{host.ip_address}:{port.number}\n')
                else:
                    f.write(f'{scheme}://{host.ip_address}:{port.number}\n')

    output_file = f'{results_dir}/nuclei_results.jsonl'
    severity_str = ','.join(severity)
    tags_str     = ','.join(tags)

    cmd = (
        f'nuclei -l {targets_file} '
        f'-severity {severity_str} '
        f'-tags {tags_str} '
        f'-rate-limit {rate} -c {threads} '
        f'-json-export {output_file} '
        f'-silent 2>/dev/null'
    )
    log_to_job(job, f'🧪 nuclei: {cmd}')
    run_cmd(cmd, timeout=7200)

    vulns_found = _parse_nuclei_results(job, output_file)
    _calculate_risk_scores(job)
    job.vulns_found = vulns_found
    job.save(update_fields=['vulns_found'])
    log_to_job(job, f'✅ {vulns_found} vulnerabilidades encontradas', 'success')


def _join_cves(cve_field):
    """Normalize CVE IDs from nuclei — can be str or list."""
    if not cve_field:
        return ''
    if isinstance(cve_field, list):
        return ','.join(str(c) for c in cve_field if c)
    return str(cve_field)


def _parse_nuclei_results(job, output_file):
    from core.models import Host, Port, Vulnerability

    count = 0
    try:
        with open(output_file) as f:
            raw = f.read().strip()
    except FileNotFoundError:
        log_to_job(job, 'nuclei output no encontrado', 'warning')
        return 0

    if not raw:
        return 0

    # nuclei v3 can write JSON array or JSONL; try both
    results = []
    if raw.startswith('['):
        try:
            parsed = json.loads(raw)
            # Flatten: could be [[result1, result2]] or [result1, result2]
            for item in parsed:
                if isinstance(item, dict):
                    results.append(item)
                elif isinstance(item, list):
                    results.extend(r for r in item if isinstance(r, dict))
        except json.JSONDecodeError:
            # Might be multiple JSON arrays on separate lines — try JSONL
            pass

    if not results:
        for line in raw.splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
                if isinstance(obj, dict):
                    results.append(obj)
                elif isinstance(obj, list):
                    results.extend(r for r in obj if isinstance(r, dict))
            except json.JSONDecodeError:
                continue

    for result in results:
        if not isinstance(result, dict):
            continue

        ip_str = result.get('host', '').split(':')[0].replace('https://', '').replace('http://', '')
        try:
            host = Host.objects.get(engagement=job.engagement, ip_address=ip_str)
        except Host.DoesNotExist:
            continue

        info = result.get('info', {})
        if not isinstance(info, dict):
            info = {}
        sev_raw  = info.get('severity', 'info').lower()
        severity = SEVERITY_MAP.get(sev_raw, 'info')

        port_obj = None
        matched_at = result.get('matched-at', '')
        if ':' in matched_at:
            try:
                pnum = int(matched_at.split(':')[-1].split('/')[0])
                port_obj = Port.objects.filter(host=host, number=pnum).first()
            except (ValueError, IndexError):
                pass

        refs = info.get('reference', [])
        if isinstance(refs, str):
            refs = [refs]

        classification = info.get('classification', {})
        if not isinstance(classification, dict):
            classification = {}

        evidence = result.get('extracted-results', result.get('matched-at', ''))
        if isinstance(evidence, list):
            evidence = ', '.join(str(e) for e in evidence)

        vuln, created = Vulnerability.objects.get_or_create(
            host=host,
            title=info.get('name', result.get('template-id', 'Unknown')),
            template_id=result.get('template-id', ''),
            defaults={
                'severity':    severity,
                'description': info.get('description', ''),
                'evidence':    str(evidence)[:2000],
                'references':  refs,
                'tags':        info.get('tags', []),
                'source':      'nuclei',
                'port':        port_obj,
                'cvss_score':  classification.get('cvss-score'),
                'cve_id':      _join_cves(classification.get('cve-id', [])),
            }
        )
        if created:
            count += 1
            log_to_job(job, f'  [{severity.upper()}] {vuln.title} @ {ip_str}')

    return count


def _calculate_risk_scores(job):
    """Calculate risk score per host based on vulnerabilities."""
    from core.models import Host, Vulnerability

    WEIGHTS = {'critical': 10.0, 'high': 7.0, 'medium': 4.0, 'low': 1.5, 'info': 0.1}

    for host in Host.objects.filter(engagement=job.engagement):
        score = 0.0
        for vuln in host.vulnerabilities.all():
            score += WEIGHTS.get(vuln.severity, 0)
            if vuln.cvss_score:
                score += vuln.cvss_score * 0.5
        host.risk_score = min(score, 100.0)
        host.save(update_fields=['risk_score'])
