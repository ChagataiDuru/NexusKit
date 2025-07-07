
import yt_dlp
import os
from . import cleanup_service, task_service

def fetch_video_info(url: str):
    """Fetches video information without downloading."""
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
    """Creates a download task in the database."""
    return task_service.create_task(tool_name='ytdl')

def run_download_task(task_id: str, url: str, format_id: str, audio_only: bool, audio_format: str | None):
    """Runs the download task, updating progress in the database."""
    output_dir = os.path.join(cleanup_service.TEMP_DIR, task_id)
    os.makedirs(output_dir, exist_ok=True)

    def progress_hook(d):
        if d['status'] == 'downloading':
            progress = int(d['_percent_str'].strip().replace('%', ''))
            task_service.update_task_progress(task_id, progress)
        elif d['status'] == 'finished':
            task_service.update_task_progress(task_id, 100)

    ydl_opts = {
        'outtmpl': f'{output_dir}/%(title)s.%(ext)s',
        'format': format_id,
        'progress_hooks': [progress_hook],
    }

    if audio_only:
        ydl_opts['postprocessors'] = [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': audio_format,
        }]

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
            result_file = os.listdir(output_dir)[0]
            result_path = os.path.join(output_dir, result_file)
            task_service.complete_task(task_id, result_path)
    except Exception as e:
        task_service.fail_task(task_id, str(e))
    finally:
        cleanup_service.schedule_cleanup(task_id)

