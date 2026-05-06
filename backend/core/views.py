from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Count, Q
from .models import Engagement, Target, Host, Port, Vulnerability, Credential, ScanJob, ScanProfile
from .serializers import (
    EngagementSerializer, EngagementListSerializer, TargetSerializer,
    HostSerializer, HostListSerializer, PortSerializer,
    VulnerabilitySerializer, CredentialSerializer,
    ScanJobSerializer, ScanProfileSerializer,
)


class EngagementViewSet(viewsets.ModelViewSet):
    queryset = Engagement.objects.prefetch_related('targets')

    def get_serializer_class(self):
        if self.action == 'list':
            return EngagementListSerializer
        return EngagementSerializer

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    @action(detail=True, methods=['get'])
    def dashboard(self, request, pk=None):
        eng = self.get_object()
        hosts = Host.objects.filter(engagement=eng)
        vulns = Vulnerability.objects.filter(host__engagement=eng)

        # Risk distribution
        by_severity = {
            'critical': vulns.filter(severity='critical').count(),
            'high':     vulns.filter(severity='high').count(),
            'medium':   vulns.filter(severity='medium').count(),
            'low':      vulns.filter(severity='low').count(),
            'info':     vulns.filter(severity='info').count(),
        }

        # OS distribution
        os_dist = list(hosts.values('os_family').annotate(count=Count('id')))

        # Top vulnerable hosts
        top_hosts = list(
            hosts.annotate(
                crit=Count('vulnerabilities', filter=Q(vulnerabilities__severity='critical')),
                high=Count('vulnerabilities', filter=Q(vulnerabilities__severity='high')),
            ).order_by('-risk_score')[:10]
            .values('id', 'ip_address', 'hostname', 'risk_score', 'crit', 'high')
        )

        # Services summary
        top_services = list(
            Port.objects.filter(host__engagement=eng, state='open')
            .values('service').annotate(count=Count('id'))
            .order_by('-count')[:10]
        )

        # Scan jobs timeline
        jobs = list(
            eng.scan_jobs.values('scan_type', 'status', 'started_at', 'finished_at', 'hosts_found', 'vulns_found')
            .order_by('-created_at')[:10]
        )

        return Response({
            'engagement': EngagementListSerializer(eng).data,
            'totals': {
                'hosts':   hosts.count(),
                'ports':   Port.objects.filter(host__engagement=eng, state='open').count(),
                'vulns':   vulns.count(),
                'creds':   Credential.objects.filter(host__engagement=eng).count(),
            },
            'by_severity':   by_severity,
            'os_distribution': os_dist,
            'top_hosts':     top_hosts,
            'top_services':  top_services,
            'recent_jobs':   jobs,
        })

    @action(detail=True, methods=['get'])
    def network_map(self, request, pk=None):
        eng = self.get_object()
        hosts = Host.objects.filter(engagement=eng).prefetch_related('ports', 'vulnerabilities')

        nodes = []
        for h in hosts:
            max_sev = 'info'
            vulns = h.vulnerabilities.all()
            if vulns.filter(severity='critical').exists(): max_sev = 'critical'
            elif vulns.filter(severity='high').exists():   max_sev = 'high'
            elif vulns.filter(severity='medium').exists(): max_sev = 'medium'
            elif vulns.filter(severity='low').exists():    max_sev = 'low'

            nodes.append({
                'id':       str(h.id),
                'label':    h.hostname or h.ip_address,
                'ip':       h.ip_address,
                'os':       h.os_family,
                'severity': max_sev,
                'ports':    h.open_ports,
                'risk':     h.risk_score,
            })

        return Response({'nodes': nodes, 'edges': []})


class TargetViewSet(viewsets.ModelViewSet):
    queryset = Target.objects.all()
    serializer_class = TargetSerializer
    filterset_fields = ['engagement', 'in_scope']


class HostViewSet(viewsets.ModelViewSet):
    queryset = Host.objects.prefetch_related('ports', 'vulnerabilities', 'credentials')
    filterset_fields = ['engagement', 'os_family', 'is_alive']

    def get_serializer_class(self):
        if self.action == 'list':
            return HostListSerializer
        return HostSerializer

    @action(detail=True, methods=['get'])
    def timeline(self, request, pk=None):
        host = self.get_object()
        vulns = host.vulnerabilities.order_by('discovered_at').values(
            'title', 'severity', 'discovered_at', 'source'
        )
        return Response({'events': list(vulns)})


class PortViewSet(viewsets.ModelViewSet):
    queryset = Port.objects.select_related('host')
    serializer_class = PortSerializer
    filterset_fields = ['host', 'state', 'protocol', 'service']


class VulnerabilityViewSet(viewsets.ModelViewSet):
    queryset = Vulnerability.objects.select_related('host', 'port')
    serializer_class = VulnerabilitySerializer
    filterset_fields = ['host', 'severity', 'status', 'source']

    @action(detail=False, methods=['get'])
    def by_engagement(self, request):
        eng_id = request.query_params.get('engagement')
        if not eng_id:
            return Response({'error': 'engagement param required'}, status=400)
        vulns = self.queryset.filter(host__engagement_id=eng_id)
        serializer = self.get_serializer(vulns, many=True)
        return Response(serializer.data)


class CredentialViewSet(viewsets.ModelViewSet):
    queryset = Credential.objects.select_related('host', 'port')
    serializer_class = CredentialSerializer
    filterset_fields = ['host', 'service', 'valid']


class ScanJobViewSet(viewsets.ModelViewSet):
    queryset = ScanJob.objects.prefetch_related('logs')
    serializer_class = ScanJobSerializer
    filterset_fields = ['engagement', 'scan_type', 'status']

    def perform_create(self, serializer):
        job = serializer.save(created_by=self.request.user)
        # Launch task after creation
        from scanner.tasks.orchestrator import launch_scan
        launch_scan.delay(str(job.id))

    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        job = self.get_object()
        if job.celery_task_id:
            from vantage.celery import app
            app.control.revoke(job.celery_task_id, terminate=True)
        job.status = 3
        job.save()
        return Response({'status': 'cancelled'})


class ScanProfileViewSet(viewsets.ModelViewSet):
    queryset = ScanProfile.objects.all()
    serializer_class = ScanProfileSerializer


class DashboardView(viewsets.ViewSet):
    def list(self, request):
        from .models import Engagement, Host, Vulnerability
        return Response({
            'engagements': Engagement.objects.count(),
            'active_engagements': Engagement.objects.filter(status='active').count(),
            'total_hosts': Host.objects.count(),
            'total_vulns': Vulnerability.objects.count(),
            'critical_vulns': Vulnerability.objects.filter(severity='critical', status='open').count(),
            'recent_engagements': EngagementListSerializer(
                Engagement.objects.order_by('-created_at')[:5], many=True
            ).data,
        })
