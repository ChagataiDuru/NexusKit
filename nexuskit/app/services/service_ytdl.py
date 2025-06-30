import yt_dlp
import uuid
import os
from . import cleanup_service

TASKS = {}

def fetch_video_info(url: str):
    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'skip_download': True,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        formats = [{'format_id': f['format_id'], 'ext': f['ext'], 'resolution': f.get('resolution') or f.get('acodec')} for f in info['formats']]
        return {
            'title': info.get('title', 'No title'),
            'thumbnail': info.get('thumbnail', ''),
            'formats': formats
        }

def create_download_task(url: str, format_id: str, audio_only: bool, audio_format: str | None):
    task_id = str(uuid.uuid4())
    TASKS[task_id] = {
        "status": "pending", 
        "result": None,
        "url": url,
        "format_id": format_id,
        "audio_only": audio_only,
        "audio_format": audio_format
    }
    return task_id

def run_download_task(task_id: str):
    task = TASKS[task_id]
    try:
        output_dir = os.path.join(cleanup_service.TEMP_DIR, task_id)
        os.makedirs(output_dir, exist_ok=True)

        ydl_opts = {
            'outtmpl': f'{output_dir}/%(title)s.%(ext)s',
            'format': task['format_id'],
        }

        if task['audio_only']:
            ydl_opts['postprocessors'] = [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': task['audio_format'],
            }]

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([task['url']])
            # Get the downloaded file name
            result_file = os.listdir(output_dir)[0]
            TASKS[task_id]["status"] = "completed"
            TASKS[task_id]["result"] = f"/api/v1/ytdl/download/{task_id}/{result_file}"

    except Exception as e:
        TASKS[task_id]["status"] = "failed"
        TASKS[task_id]["result"] = str(e)
    finally:
        cleanup_service.schedule_cleanup(task_id)
