"""
python manage.py setup_vantage
Creates superuser, default scan profiles, and first engagement.
"""
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User


class Command(BaseCommand):
    help = 'Initial VANTAGE setup'

    def handle(self, *args, **options):
        # Superuser
        if not User.objects.filter(username='n0v4r3k').exists():
            User.objects.create_superuser('n0v4r3k', '', 'vantage2026!')
            self.stdout.write(self.style.SUCCESS('✅ Usuario n0v4r3k creado (pass: vantage2026!)'))

        # Default scan profiles
        from core.models import ScanProfile
        profiles = [
            {
                'name': 'Quick Recon',
                'description': 'Host discovery + top 100 ports. Rápido (~5 min)',
                'scan_types': ['discovery', 'port'],
                'config': {'port': {'ports': 'top-100', 'timing': 'T4', 'os_detection': False}},
                'is_default': False,
            },
            {
                'name': 'Standard Audit',
                'description': 'Full port scan + services + SSL + vuln scan. (~30-60 min)',
                'scan_types': ['discovery', 'port', 'ssl', 'vuln'],
                'config': {
                    'port': {'ports': 'top-1000', 'timing': 'T4', 'os_detection': True},
                    'vuln': {'severity': ['critical', 'high', 'medium'], 'rate_limit': 50},
                },
                'is_default': True,
            },
            {
                'name': 'Full Pentest',
                'description': 'Todo: SMB, AD, credenciales, SNMP + IA. (~2-4h)',
                'scan_types': ['discovery', 'port', 'ssl', 'smb', 'snmp', 'ad', 'brute', 'vuln'],
                'config': {
                    'port': {'ports': 'top-1000', 'timing': 'T4', 'os_detection': True, 'udp': True},
                    'vuln': {'severity': ['critical', 'high', 'medium', 'low'], 'rate_limit': 100},
                    'brute': {'services': ['ssh', 'ftp', 'mysql', 'mssql', 'rdp', 'redis', 'snmp']},
                },
                'is_default': False,
            },
            {
                'name': 'Stealth Scan',
                'description': 'Timing T1, solo top-100, sin scripts agresivos',
                'scan_types': ['discovery', 'port'],
                'config': {'port': {'ports': 'top-100', 'timing': 'T1', 'os_detection': False, 'scripts': False}},
                'is_default': False,
            },
        ]

        for p in profiles:
            ScanProfile.objects.get_or_create(name=p['name'], defaults={k:v for k,v in p.items() if k != 'name'})
            self.stdout.write(f'  ✅ Profile: {p["name"]}')

        self.stdout.write(self.style.SUCCESS('\n🚀 VANTAGE listo. Accede en http://IP:9000'))
