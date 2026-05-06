import logging
from celery import shared_task, chain
from django.utils import timezone
from scanner.utils import log_to_job, notify, send_status

logger = logging.getLogger(__name__)


@shared_task(name='scanner.tasks.launch_scan', queue='scan_queue', bind=True)
def launch_scan(self, job_id):
    """Orchestrate a full scan job according to its scan_type and config."""
    from core.models import ScanJob

    try:
        job = ScanJob.objects.get(id=job_id)
    except ScanJob.DoesNotExist:
        return

    job.status = 1
    job.started_at = timezone.now()
    job.celery_task_id = self.request.id
    job.error_msg = ''
    job.save()

    log_to_job(job, f'🚀 Iniciando scan [{job.scan_type}] sobre {len(job.targets)} target(s)', 'info')
    notify(f'🔍 Scan iniciado — {job.engagement.name}',
           f'Tipo: {job.get_scan_type_display()}\nTargets: {", ".join(job.targets)}')

    task_map = {
        'discovery': _run_discovery,
        'port':      _run_port_scan,
        'service':   _run_service_scan,
        'vuln':      _run_vuln_scan,
        'ssl':       _run_ssl_audit,
        'smb':       _run_smb_audit,
        'ad':        _run_ad_audit,
        'brute':     _run_brute_force,
        'snmp':      _run_snmp_audit,
        'full':      _run_full_audit,
    }

    try:
        fn = task_map.get(job.scan_type)
        if fn:
            fn(job)
        job.status = 2
        job.finished_at = timezone.now()
        job.save()
        log_to_job(job, f'✅ Scan completado. Hosts: {job.hosts_found} | Puertos: {job.ports_found} | Vulns: {job.vulns_found}', 'success')
        send_status(job)
        notify(f'✅ Scan completado — {job.engagement.name}',
               f'Hosts: {job.hosts_found} | Vulns: {job.vulns_found}', color=0x00ff9d)

        # Trigger AI analysis after scan
        from ai.tasks import analyze_scan_results
        analyze_scan_results.delay(job_id)

    except Exception as e:
        job.status = 0
        job.error_msg = str(e)
        job.finished_at = timezone.now()
        job.save()
        log_to_job(job, f'❌ Error: {e}', 'error')
        send_status(job)
        logger.exception(f'Scan {job_id} failed')


def _run_discovery(job):
    from scanner.tasks.discovery import host_discovery
    host_discovery(job)


def _run_port_scan(job):
    from scanner.tasks.ports import port_scan
    port_scan(job)


def _run_service_scan(job):
    from scanner.tasks.services import service_detection
    service_detection(job)


def _run_vuln_scan(job):
    from scanner.tasks.vulns import vuln_scan
    vuln_scan(job)


def _run_ssl_audit(job):
    from scanner.tasks.ssl_audit import ssl_audit
    ssl_audit(job)


def _run_smb_audit(job):
    from scanner.tasks.smb import smb_audit
    smb_audit(job)


def _run_ad_audit(job):
    from scanner.tasks.active_directory import ad_audit
    ad_audit(job)


def _run_brute_force(job):
    from scanner.tasks.brute import brute_force
    brute_force(job)


def _run_snmp_audit(job):
    from scanner.tasks.snmp import snmp_audit
    snmp_audit(job)


def _run_full_audit(job):
    """Run all modules in sequence with aggressive settings."""
    log_to_job(job, '🔭 Full Audit — ejecutando todos los módulos (modo agresivo)', 'info')

    # Override config with full/deep settings
    job.config.setdefault('discovery', {})
    job.config['discovery']['timing'] = 'T4'

    job.config.setdefault('port', {})
    job.config['port']['ports']            = '1-65535'   # todos los puertos TCP
    job.config['port']['timing']           = 'T4'
    job.config['port']['os_detection']     = True
    job.config['port']['scripts']          = True
    job.config['port']['udp']              = True        # top-100 UDP también
    job.config['port']['version_intensity'] = 9          # máxima detección de versiones

    job.config.setdefault('vuln', {})
    job.config['vuln']['severity']    = ['critical', 'high', 'medium', 'low']
    job.config['vuln']['tags']        = ['network', 'service', 'cve', 'misconfigurations',
                                          'exposed-panels', 'default-logins', 'technologies',
                                          'ssl', 'http', 'ftp', 'ssh', 'smb', 'dns']
    job.config['vuln']['rate_limit']  = 100
    job.config['vuln']['threads']     = 25

    job.config.setdefault('brute', {})
    job.config['brute']['services']   = ['ssh', 'ftp', 'mysql', 'mssql', 'rdp', 'redis', 'snmp']
    job.config['brute']['max_tries']  = 30

    job.save(update_fields=['config'])

    _run_discovery(job)
    _run_port_scan(job)          # ~5-20 min en /24 con todos los puertos
    _run_service_scan(job)       # nmap -sV profundo
    _run_ssl_audit(job)          # certs, ciphers, heartbleed, POODLE
    _run_smb_audit(job)          # EternalBlue, null sessions, signing
    _run_snmp_audit(job)         # community strings
    _run_ad_audit(job)           # LDAP null bind, kerberos enum
    _run_brute_force(job)        # credenciales por defecto
    _run_vuln_scan(job)          # nuclei templates (el más largo)
