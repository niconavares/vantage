import os
from rest_framework.views import APIView
from rest_framework.response import Response
from django.http import FileResponse


class GenerateReportView(APIView):
    def post(self, request, engagement_id):
        from core.models import Engagement
        from reports.generator import generate_pdf_report
        try:
            eng = Engagement.objects.get(id=engagement_id)
            pdf_path = generate_pdf_report(eng)
            return Response({'path': pdf_path, 'filename': os.path.basename(pdf_path)})
        except Engagement.DoesNotExist:
            return Response({'error': 'Engagement not found'}, status=404)
        except Exception as e:
            return Response({'error': str(e)}, status=500)


class DownloadReportView(APIView):
    def get(self, request, engagement_id):
        from core.models import Engagement
        from reports.generator import generate_pdf_report
        try:
            eng = Engagement.objects.get(id=engagement_id)
            pdf_path = generate_pdf_report(eng)
            response = FileResponse(open(pdf_path, 'rb'), content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="{os.path.basename(pdf_path)}"'
            return response
        except Exception as e:
            return Response({'error': str(e)}, status=500)
