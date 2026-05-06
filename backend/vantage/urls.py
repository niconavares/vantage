from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework.authtoken.views import obtain_auth_token

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/login/', obtain_auth_token),
    path('api/', include('core.urls')),
    path('api/scanner/', include('scanner.urls')),
    path('api/ai/', include('ai.urls')),
    path('api/reports/', include('reports.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
