from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status


class AnalyzeHostView(APIView):
    def post(self, request, host_id):
        from core.models import Host
        from ai.claude import analyze_host
        try:
            host = Host.objects.get(id=host_id)
            analysis = analyze_host(host)
            host.ai_summary = analysis
            host.save(update_fields=['ai_summary'])
            return Response({'analysis': analysis})
        except Host.DoesNotExist:
            return Response({'error': 'Host not found'}, status=404)


class AnalyzeVulnView(APIView):
    def post(self, request, vuln_id):
        from core.models import Vulnerability
        from ai.claude import analyze_vulnerability
        try:
            vuln = Vulnerability.objects.get(id=vuln_id)
            analysis = analyze_vulnerability(vuln)
            vuln.ai_analysis = analysis
            vuln.save(update_fields=['ai_analysis'])
            return Response({'analysis': analysis})
        except Vulnerability.DoesNotExist:
            return Response({'error': 'Vulnerability not found'}, status=404)


class AnalyzeEngagementView(APIView):
    def post(self, request, engagement_id):
        from ai.tasks import analyze_engagement_task
        task = analyze_engagement_task.delay(str(engagement_id))
        return Response({'task_id': task.id, 'status': 'queued'})


class AskClaudeView(APIView):
    """Free-form chat with Claude about the engagement context."""
    def post(self, request):
        from ai.claude import ask
        question = request.data.get('question', '')
        context  = request.data.get('context', '')
        if not question:
            return Response({'error': 'question required'}, status=400)

        prompt = f"{context}\n\nPregunta del analista: {question}" if context else question
        answer = ask(prompt)
        return Response({'answer': answer})
