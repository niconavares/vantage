import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async


class ScanLogConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.job_id = self.scope['url_route']['kwargs']['job_id']
        self.group  = f'scan_{self.job_id}'
        await self.channel_layer.group_add(self.group, self.channel_name)
        await self.accept()

        # Send existing logs on connect so reconnects catch up automatically
        logs = await self._get_existing_logs()
        for log in logs:
            ts = log['created_at']
            await self.send(text_data=json.dumps({
                'type':      'log',
                'level':     log['level'],
                'message':   log['message'],
                'timestamp': ts.isoformat() if hasattr(ts, 'isoformat') else str(ts),
            }))

        # Send current job status so frontend syncs immediately
        status = await self._get_job_status()
        if status is not None:
            await self.send(text_data=json.dumps({
                'type':   'status',
                'status': status,
            }))

    async def disconnect(self, code):
        await self.channel_layer.group_discard(self.group, self.channel_name)

    async def scan_log(self, event):
        await self.send(text_data=json.dumps({
            'type':      'log',
            'level':     event['level'],
            'message':   event['message'],
            'timestamp': event['timestamp'],
        }))

    async def scan_status(self, event):
        """Receives job status updates broadcast from the scanner."""
        await self.send(text_data=json.dumps({
            'type':   'status',
            'status': event['status'],
        }))

    @database_sync_to_async
    def _get_existing_logs(self):
        from core.models import ScanLog
        return list(
            ScanLog.objects.filter(job_id=self.job_id)
            .order_by('created_at')
            .values('level', 'message', 'created_at')
        )

    @database_sync_to_async
    def _get_job_status(self):
        from core.models import ScanJob
        try:
            return ScanJob.objects.get(id=self.job_id).status
        except ScanJob.DoesNotExist:
            return None
