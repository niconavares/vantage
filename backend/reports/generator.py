"""
Professional PDF report generator using WeasyPrint + Jinja2.
Generates client-ready audit reports with executive summary,
findings table, risk matrix, and remediation roadmap.
"""
import os
from datetime import date
from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML, CSS
from django.conf import settings
from django.template.loader import render_to_string


SEVERITY_COLORS = {
    'critical': '#ff3864',
    'high':     '#ff6b35',
    'medium':   '#ffd60a',
    'low':      '#4cc9f0',
    'info':     '#8ecae6',
}

SEVERITY_ORDER = {'critical': 0, 'high': 1, 'medium': 2, 'low': 3, 'info': 4}


def generate_pdf_report(engagement, output_path: str = None) -> str:
    """Generate a full PDF audit report for an engagement."""
    from core.models import Host, Vulnerability, Credential
    from ai.claude import generate_report_narrative

    hosts  = Host.objects.filter(engagement=engagement).prefetch_related('ports', 'vulnerabilities')
    vulns  = Vulnerability.objects.filter(host__engagement=engagement).order_by(
        'severity', 'host__ip_address'
    )
    creds  = Credential.objects.filter(host__engagement=engagement)

    # Stats
    by_sev = {
        'critical': vulns.filter(severity='critical').count(),
        'high':     vulns.filter(severity='high').count(),
        'medium':   vulns.filter(severity='medium').count(),
        'low':      vulns.filter(severity='low').count(),
        'info':     vulns.filter(severity='info').count(),
    }
    total_vulns = sum(by_sev.values())
    risk_level  = _overall_risk(by_sev)

    # Generate AI narratives
    executive_summary = generate_report_narrative(engagement, 'executive')
    methodology_text  = generate_report_narrative(engagement, 'methodology')
    conclusions_text  = generate_report_narrative(engagement, 'conclusions')

    # Build context
    context = {
        'engagement':        engagement,
        'report_date':       date.today().strftime('%d de %B de %Y'),
        'hosts':             hosts,
        'vulnerabilities':   vulns,
        'credentials':       creds,
        'by_severity':       by_sev,
        'total_vulns':       total_vulns,
        'risk_level':        risk_level,
        'risk_color':        SEVERITY_COLORS.get(risk_level.lower(), '#ff6b35'),
        'severity_colors':   SEVERITY_COLORS,
        'executive_summary': executive_summary,
        'methodology_text':  methodology_text,
        'conclusions_text':  conclusions_text,
        'open_ports_count':  sum(h.open_ports for h in hosts),
    }

    # Render HTML
    template_dir = os.path.join(os.path.dirname(__file__), 'templates')
    env = Environment(loader=FileSystemLoader(template_dir))
    template = env.get_template('report.html')
    html_content = template.render(**context)

    # Generate PDF
    if not output_path:
        reports_dir = os.path.join(settings.MEDIA_ROOT, 'reports')
        os.makedirs(reports_dir, exist_ok=True)
        safe_name = engagement.client.replace(' ', '_').lower()
        output_path = os.path.join(reports_dir, f'vantage_report_{safe_name}_{date.today()}.pdf')

    css_path = os.path.join(os.path.dirname(__file__), 'templates', 'report.css')
    HTML(string=html_content, base_url=template_dir).write_pdf(
        output_path,
        stylesheets=[CSS(filename=css_path)] if os.path.exists(css_path) else []
    )

    return output_path


def _overall_risk(by_sev) -> str:
    if by_sev.get('critical', 0) > 0:    return 'Critical'
    if by_sev.get('high', 0) > 0:        return 'High'
    if by_sev.get('medium', 0) > 0:      return 'Medium'
    if by_sev.get('low', 0) > 0:         return 'Low'
    return 'Info'
