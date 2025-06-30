import uuid
import os
import subprocess
import shutil
from . import cleanup_service

TASKS = {}

def handle_ffmpeg_upload(file):
    task_id = str(uuid.uuid4())
    task_dir = os.path.join(cleanup_service.TEMP_DIR, task_id)
    os.makedirs(task_dir, exist_ok=True)

    original_file_path = os.path.join(task_dir, file.filename)
    with open(original_file_path, "wb") as buffer:
        buffer.write(file.file.read())

    TASKS[task_id] = {
        "original_file_path": original_file_path,
        "status": "uploaded",
        "progress": 0,
        "download_url": None,
        "error": None
    }
    cleanup_service.schedule_cleanup(task_id)

    return {"task_id": task_id, "filename": file.filename}

def run_ffmpeg_conversion(task_id: str, output_format: str, extract_audio: bool, resolution: str | None, quality: str | None, bitrate: str | None):
    task = TASKS[task_id]
    original_file_path = task['original_file_path']
    task_dir = os.path.dirname(original_file_path)
    output_filename = f"{os.path.splitext(os.path.basename(original_file_path))[0]}.{output_format}"
    output_file_path = os.path.join(task_dir, output_filename)

    command = ["ffmpeg", "-i", original_file_path]

    if extract_audio:
        command.extend([ "-vn", "-acodec", output_format])
    else:
        if resolution:
            command.extend([ "-vf", f"scale={resolution}"])
        if quality:
            # This is a simplified mapping, real FFmpeg quality would be more complex
            if quality == "High":
                command.extend([ "-crf", "18"])
            elif quality == "Medium":
                command.extend([ "-crf", "23"])
            elif quality == "Low":
                command.extend([ "-crf", "28"])
        if bitrate:
            command.extend([ "-b:a", bitrate])

    command.append(output_file_path)

    try:
        TASKS[task_id]["status"] = "processing"
        process = subprocess.run(command, capture_output=True, text=True, check=True)
        TASKS[task_id]["status"] = "completed"
        TASKS[task_id]["download_url"] = f"/api/v1/ffmpeg/download/{task_id}/{output_filename}"
    except subprocess.CalledProcessError as e:
        TASKS[task_id]["status"] = "failed"
        TASKS[task_id]["error"] = f"FFmpeg Error: {e.stderr}"
    except Exception as e:
        TASKS[task_id]["status"] = "failed"
        TASKS[task_id]["error"] = str(e)

def get_ffmpeg_task_status(task_id: str):
    return TASKS.get(task_id)
