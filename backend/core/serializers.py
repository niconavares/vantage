from rest_framework import serializers
from .models import Engagement, Target, Host, Port, Vulnerability, Credential, ScanJob, ScanLog, ScanProfile


class TargetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Target
        fields = '__all__'


class EngagementSerializer(serializers.ModelSerializer):
    stats   = serializers.ReadOnlyField()
    targets = TargetSerializer(many=True, read_only=True)

    class Meta:
        model = Engagement
        fields = '__all__'
        read_only_fields = ('created_by', 'created_at', 'updated_at')


class EngagementListSerializer(serializers.ModelSerializer):
    stats = serializers.ReadOnlyField()

    class Meta:
        model = Engagement
        fields = ('id', 'name', 'client', 'status', 'start_date', 'end_date', 'stats', 'created_at')


class PortSerializer(serializers.ModelSerializer):
    class Meta:
        model = Port
        fields = '__all__'


class VulnerabilitySerializer(serializers.ModelSerializer):
    host_ip = serializers.CharField(source='host.ip_address', read_only=True)

    class Meta:
        model = Vulnerability
        fields = '__all__'


class CredentialSerializer(serializers.ModelSerializer):
    class Meta:
        model = Credential
        fields = '__all__'


class HostSerializer(serializers.ModelSerializer):
    ports           = PortSerializer(many=True, read_only=True)
    vulnerabilities = VulnerabilitySerializer(many=True, read_only=True)
    credentials     = CredentialSerializer(many=True, read_only=True)
    vuln_counts = serializers.SerializerMethodField()

    class Meta:
        model = Host
        fields = '__all__'

    def get_vuln_counts(self, obj):
        vulns = obj.vulnerabilities.all()
        return {
            'critical': vulns.filter(severity='critical').count(),
            'high':     vulns.filter(severity='high').count(),
            'medium':   vulns.filter(severity='medium').count(),
            'low':      vulns.filter(severity='low').count(),
            'info':     vulns.filter(severity='info').count(),
        }


class HostListSerializer(serializers.ModelSerializer):
    vuln_counts = serializers.SerializerMethodField()

    class Meta:
        model = Host
        fields = ('id', 'ip_address', 'hostname', 'os_name', 'os_family',
                  'is_alive', 'open_ports', 'risk_score', 'last_seen', 'vuln_counts', 'ai_summary')

    def get_vuln_counts(self, obj):
        vulns = obj.vulnerabilities.all()
        return {
            'critical': vulns.filter(severity='critical').count(),
            'high':     vulns.filter(severity='high').count(),
            'medium':   vulns.filter(severity='medium').count(),
            'low':      vulns.filter(severity='low').count(),
        }


class ScanLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = ScanLog
        fields = '__all__'


class ScanJobSerializer(serializers.ModelSerializer):
    logs = ScanLogSerializer(many=True, read_only=True)

    class Meta:
        model = ScanJob
        fields = '__all__'
        read_only_fields = ('celery_task_id', 'started_at', 'finished_at',
                            'hosts_found', 'ports_found', 'vulns_found', 'error_msg')

    def validate_targets(self, value):
        """Normalize targets to a list — accepts string, comma-separated string, or list."""
        if isinstance(value, str):
            # Split by comma and clean whitespace
            value = [t.strip() for t in value.split(',') if t.strip()]
        elif not isinstance(value, list):
            raise serializers.ValidationError("targets debe ser una lista o string separado por comas")
        return value


class ScanProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = ScanProfile
        fields = '__all__'
