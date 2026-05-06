import subprocess
import logging
import os
from django.utils import timezone
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

logger = logging.getLogger(__name__)


def run_cmd(cmd, shell=True, timeout=3600):
    """Run a shell command and return (stdout, returncode)."""
    try:
        result = subprocess.run(
            cmd, shell=shell, capture_output=True, text=True, timeout=timeout
        )
        return result.stdout, result.returncode
    except subprocess.TimeoutExpired:
        return '', 1
    except Exception as e:
        logger.error(f"run_cmd error: {e}")
        return '', 1


def log_to_job(job, message, level='info'):
    """Save a log entry and push it over WebSocket."""
    from core.models import ScanLog
    ScanLog.objects.create(job=job, message=message, level=level)

    channel_layer = get_channel_layer()
    if channel_layer:
        try:
            async_to_sync(channel_layer.group_send)(
                f'scan_{job.id}',
                {'type': 'scan.log', 'level': level, 'message': message,
                 'timestamp': timezone.now().isoformat()}
            )
        except Exception:
            pass


def send_status(job):
    """Broadcast job status change over WebSocket."""
    channel_layer = get_channel_layer()
    if channel_layer:
        try:
            async_to_sync(channel_layer.group_send)(
                f'scan_{job.id}',
                {'type': 'scan.status', 'status': job.status}
            )
        except Exception:
            pass


def ensure_results_dir(job_id):
    from django.conf import settings
    path = os.path.join(settings.SCAN_RESULTS_DIR, str(job_id))
    os.makedirs(path, exist_ok=True)
    return path


def notify(title, message, color=0x00d4ff):
    """Send Discord + Telegram notification."""
    import requests
    from django.conf import settings

    if settings.DISCORD_WEBHOOK:
        try:
            requests.post(settings.DISCORD_WEBHOOK, json={
                'embeds': [{'title': title, 'description': message, 'color': color}]
            }, timeout=5)
        except Exception:
            pass

    if settings.TELEGRAM_BOT_TOKEN and settings.TELEGRAM_CHAT_ID:
        try:
            requests.post(
                f'https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/sendMessage',
                json={'chat_id': settings.TELEGRAM_CHAT_ID,
                      'text': f'*{title}*\n{message}', 'parse_mode': 'Markdown'},
                timeout=5
            )
        except Exception:
            pass
