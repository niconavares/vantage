from django.urls import path
from .views import GenerateReportView, DownloadReportView

urlpatterns = [
    path('<str:engagement_id>/generate/', GenerateReportView.as_view()),
    path('<str:engagement_id>/download/', DownloadReportView.as_view()),
]
