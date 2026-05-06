from django.urls import re_path
from .consumers import ScanLogConsumer

websocket_urlpatterns = [
    re_path(r'ws/scan/(?P<job_id>[^/]+)/$', ScanLogConsumer.as_asgi()),
]
