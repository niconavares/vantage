from scanner.utils import run_cmd, log_to_job


def service_detection(job):
    """Service detection — skipped when called after port_scan (which already runs -sV).
    Only does additional work if ports exist but service info is missing."""
    from core.models import Host, Port
    hosts_with_ports = Host.objects.filter(
        engagement=job.engagement, is_alive=True, open_ports__gt=0
    )
    # If any port already has service info, port_scan -sV already ran — skip
    if Port.objects.filter(host__engagement=job.engagement, service__gt='').exists():
        log_to_job(job, '🔎 Service detection — ya cubierto por port scan (-sV), saltando')
        return
    log_to_job(job, '🔎 Service detection — ejecutando nmap -sV')
    from scanner.tasks.ports import port_scan
    port_scan(job)
