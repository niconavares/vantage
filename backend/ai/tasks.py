import logging
from celery import shared_task

logger = logging.getLogger(__name__)


@shared_task(name='ai.tasks.analyze_scan_results', queue='ai_queue')
def analyze_scan_results(job_id):
    """After a scan completes, run Claude analysis on all new hosts and vulns."""
    from core.models import ScanJob, Host, Vulnerability
    from ai.claude import analyze_host, analyze_vulnerability

    try:
        job = ScanJob.objects.get(id=job_id)
    except ScanJob.DoesNotExist:
        return

    logger.info(f'AI analysis started for job {job_id}')

    # Analyze each host
    hosts = Host.objects.filter(engagement=job.engagement, ai_summary='')
    for host in hosts:
        if host.vulnerabilities.exists() or host.ports.filter(state='open').exists():
            host.ai_summary = analyze_host(host)
            host.save(update_fields=['ai_summary'])
            logger.info(f'AI summary generated for {host.ip_address}')

    # Analyze critical/high vulns without AI analysis
    vulns = Vulnerability.objects.filter(
        host__engagement=job.engagement,
        severity__in=['critical', 'high'],
        ai_analysis=''
    )
    for vuln in vulns[:20]:  # cap at 20 to control API costs
        vuln.ai_analysis = analyze_vulnerability(vuln)
        vuln.save(update_fields=['ai_analysis'])

    logger.info(f'AI analysis completed for job {job_id}')


@shared_task(name='ai.tasks.analyze_engagement', queue='ai_queue')
def analyze_engagement_task(engagement_id):
    """Full engagement analysis — generates attack path and report narrative."""
    from core.models import Engagement
    from ai.claude import analyze_engagement

    try:
        eng = Engagement.objects.get(id=engagement_id)
    except Engagement.DoesNotExist:
        return

    result = analyze_engagement(eng)
    # Store in engagement notes
    eng.notes = result.get('analysis', '')
    eng.save(update_fields=['notes'])
    return result
