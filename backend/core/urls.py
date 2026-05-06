from rest_framework.routers import DefaultRouter
from django.urls import path, include
from .views import (
    EngagementViewSet, TargetViewSet, HostViewSet, PortViewSet,
    VulnerabilityViewSet, CredentialViewSet, ScanJobViewSet,
    ScanProfileViewSet, DashboardView,
)

router = DefaultRouter()
router.register('engagements',  EngagementViewSet)
router.register('targets',      TargetViewSet)
router.register('hosts',        HostViewSet)
router.register('ports',        PortViewSet)
router.register('vulns',        VulnerabilityViewSet)
router.register('credentials',  CredentialViewSet)
router.register('scan-jobs',    ScanJobViewSet)
router.register('scan-profiles', ScanProfileViewSet)
router.register('dashboard',    DashboardView, basename='dashboard')

urlpatterns = [path('', include(router.urls))]
