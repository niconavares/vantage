from django.urls import path
from .views import AnalyzeHostView, AnalyzeVulnView, AnalyzeEngagementView, AskClaudeView

urlpatterns = [
    path('host/<int:host_id>/',           AnalyzeHostView.as_view()),
    path('vuln/<int:vuln_id>/',           AnalyzeVulnView.as_view()),
    path('engagement/<str:engagement_id>/', AnalyzeEngagementView.as_view()),
    path('ask/',                          AskClaudeView.as_view()),
]
