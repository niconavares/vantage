from django.db import models
from django.contrib.auth.models import User
import uuid


# ── Engagement (proyecto de auditoría por cliente) ───────────────────────────

class Engagement(models.Model):
    STATUS = [
        ('planning',    'Planificación'),
        ('active',      'Activo'),
        ('paused',      'Pausado'),
        ('completed',   'Completado'),
        ('archived',    'Archivado'),
    ]
    id          = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name        = models.CharField(max_length=200)
    client      = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    status      = models.CharField(max_length=20, choices=STATUS, default='planning')
    start_date  = models.DateField(null=True, blank=True)
    end_date    = models.DateField(null=True, blank=True)
    created_by  = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at  = models.DateTimeField(auto_now_add=True)
    updated_at  = models.DateTimeField(auto_now=True)
    logo        = models.ImageField(upload_to='logos/', null=True, blank=True)
    notes       = models.TextField(blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.client} — {self.name}"

    @property
    def stats(self):
        hosts = self.hosts.count()
        vulns = Vulnerability.objects.filter(host__engagement=self)
        return {
            'hosts':    hosts,
            'critical': vulns.filter(severity='critical').count(),
            'high':     vulns.filter(severity='high').count(),
            'medium':   vulns.filter(severity='medium').count(),
            'low':      vulns.filter(severity='low').count(),
            'info':     vulns.filter(severity='info').count(),
        }


# ── Target (rango de IPs / CIDR) ─────────────────────────────────────────────

class Target(models.Model):
    engagement  = models.ForeignKey(Engagement, on_delete=models.CASCADE, related_name='targets')
    value       = models.CharField(max_length=100)          # 192.168.1.0/24, 10.0.0.1, host.company.com
    description = models.CharField(max_length=200, blank=True)
    in_scope    = models.BooleanField(default=True)
    created_at  = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.value


# ── Host (host descubierto) ───────────────────────────────────────────────────

class Host(models.Model):
    OS_FAMILY = [
        ('windows', 'Windows'), ('linux', 'Linux'), ('macos', 'macOS'),
        ('network', 'Network Device'), ('embedded', 'Embedded'), ('unknown', 'Unknown'),
    ]
    engagement  = models.ForeignKey(Engagement, on_delete=models.CASCADE, related_name='hosts')
    ip_address  = models.GenericIPAddressField()
    hostname    = models.CharField(max_length=255, blank=True)
    mac_address = models.CharField(max_length=17, blank=True)
    os_name     = models.CharField(max_length=200, blank=True)
    os_family   = models.CharField(max_length=20, choices=OS_FAMILY, default='unknown')
    os_accuracy = models.IntegerField(default=0)
    is_alive    = models.BooleanField(default=True)
    open_ports  = models.IntegerField(default=0)
    risk_score  = models.FloatField(default=0.0)
    first_seen  = models.DateTimeField(auto_now_add=True)
    last_seen   = models.DateTimeField(auto_now=True)
    notes       = models.TextField(blank=True)
    ai_summary  = models.TextField(blank=True)

    class Meta:
        unique_together = ('engagement', 'ip_address')
        ordering = ['-risk_score', 'ip_address']

    def __str__(self):
        return f"{self.ip_address} ({self.hostname or 'unknown'})"


# ── Port / Service ────────────────────────────────────────────────────────────

class Port(models.Model):
    STATE = [('open', 'Open'), ('filtered', 'Filtered'), ('closed', 'Closed')]
    PROTOCOL = [('tcp', 'TCP'), ('udp', 'UDP')]

    host        = models.ForeignKey(Host, on_delete=models.CASCADE, related_name='ports')
    number      = models.IntegerField()
    protocol    = models.CharField(max_length=3, choices=PROTOCOL, default='tcp')
    state       = models.CharField(max_length=10, choices=STATE, default='open')
    service     = models.CharField(max_length=100, blank=True)    # ssh, http, smb...
    product     = models.CharField(max_length=200, blank=True)    # OpenSSH, Apache...
    version     = models.CharField(max_length=200, blank=True)    # 8.9p1, 2.4.41...
    banner      = models.TextField(blank=True)
    extra_info  = models.TextField(blank=True)
    cpe         = models.CharField(max_length=300, blank=True)
    discovered_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('host', 'number', 'protocol')
        ordering = ['number']

    def __str__(self):
        return f"{self.host.ip_address}:{self.number}/{self.protocol} ({self.service})"


# ── Vulnerability ─────────────────────────────────────────────────────────────

class Vulnerability(models.Model):
    SEVERITY = [
        ('critical', 'Critical'),
        ('high',     'High'),
        ('medium',   'Medium'),
        ('low',      'Low'),
        ('info',     'Info'),
    ]
    STATUS = [
        ('open',        'Open'),
        ('confirmed',   'Confirmed'),
        ('false_positive', 'False Positive'),
        ('mitigated',   'Mitigated'),
        ('accepted',    'Risk Accepted'),
    ]

    host        = models.ForeignKey(Host, on_delete=models.CASCADE, related_name='vulnerabilities')
    port        = models.ForeignKey(Port, on_delete=models.SET_NULL, null=True, blank=True, related_name='vulnerabilities')
    title       = models.CharField(max_length=300)
    severity    = models.CharField(max_length=10, choices=SEVERITY)
    status      = models.CharField(max_length=20, choices=STATUS, default='open')
    cvss_score  = models.FloatField(null=True, blank=True)
    cve_id      = models.CharField(max_length=20, blank=True)
    description = models.TextField()
    evidence    = models.TextField(blank=True)
    solution    = models.TextField(blank=True)
    references  = models.JSONField(default=list, blank=True)
    tags        = models.JSONField(default=list, blank=True)
    source      = models.CharField(max_length=50, blank=True)   # nuclei, nmap, manual, ai...
    template_id = models.CharField(max_length=100, blank=True)
    ai_analysis = models.TextField(blank=True)
    discovered_at = models.DateTimeField(auto_now_add=True)
    updated_at  = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = [
            models.Case(
                models.When(severity='critical', then=0),
                models.When(severity='high', then=1),
                models.When(severity='medium', then=2),
                models.When(severity='low', then=3),
                models.When(severity='info', then=4),
                default=5,
            )
        ]

    def __str__(self):
        return f"[{self.severity.upper()}] {self.title} @ {self.host.ip_address}"


# ── Credential (credenciales encontradas) ─────────────────────────────────────

class Credential(models.Model):
    host        = models.ForeignKey(Host, on_delete=models.CASCADE, related_name='credentials')
    port        = models.ForeignKey(Port, on_delete=models.SET_NULL, null=True, blank=True)
    service     = models.CharField(max_length=50)
    username    = models.CharField(max_length=200)
    password    = models.CharField(max_length=500, blank=True)
    hash_value  = models.CharField(max_length=500, blank=True)
    hash_type   = models.CharField(max_length=50, blank=True)
    valid       = models.BooleanField(default=True)
    notes       = models.TextField(blank=True)
    found_at    = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.service}://{self.username}@{self.host.ip_address}"


# ── ScanJob (trabajo de escaneo) ──────────────────────────────────────────────

class ScanJob(models.Model):
    SCAN_TYPES = [
        ('discovery',    'Host Discovery'),
        ('port',         'Port Scan'),
        ('service',      'Service Detection'),
        ('vuln',         'Vulnerability Scan'),
        ('ssl',          'SSL/TLS Audit'),
        ('smb',          'SMB Audit'),
        ('ad',           'Active Directory'),
        ('brute',        'Credential Brute Force'),
        ('snmp',         'SNMP Audit'),
        ('full',         'Full Audit'),
    ]
    STATUS = [
        (-1, 'Queued'),
        (1,  'Running'),
        (2,  'Completed'),
        (0,  'Failed'),
        (3,  'Cancelled'),
    ]

    id          = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    engagement  = models.ForeignKey(Engagement, on_delete=models.CASCADE, related_name='scan_jobs')
    scan_type   = models.CharField(max_length=20, choices=SCAN_TYPES)
    targets     = models.JSONField(default=list)       # IPs/CIDRs to scan
    config      = models.JSONField(default=dict)       # tool options
    status      = models.IntegerField(choices=STATUS, default=-1)
    celery_task_id = models.CharField(max_length=100, blank=True)
    started_at  = models.DateTimeField(null=True, blank=True)
    finished_at = models.DateTimeField(null=True, blank=True)
    hosts_found = models.IntegerField(default=0)
    ports_found = models.IntegerField(default=0)
    vulns_found = models.IntegerField(default=0)
    error_msg   = models.TextField(blank=True)
    created_by  = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at  = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.scan_type} @ {self.engagement.name} [{self.get_status_display()}]"


class ScanLog(models.Model):
    LEVEL = [('info', 'Info'), ('warning', 'Warning'), ('error', 'Error'), ('success', 'Success')]
    job     = models.ForeignKey(ScanJob, on_delete=models.CASCADE, related_name='logs')
    level   = models.CharField(max_length=10, choices=LEVEL, default='info')
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']


# ── ScanProfile (plantillas de escaneo configurables) ─────────────────────────

class ScanProfile(models.Model):
    name        = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    scan_types  = models.JSONField(default=list)     # which modules to run
    config      = models.JSONField(default=dict)     # per-module config
    is_default  = models.BooleanField(default=False)
    created_at  = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
