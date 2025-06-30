from fastapi import APIRouter, File, UploadFile, BackgroundTasks
from fastapi.responses import FileResponse
from ..models.ffmpeg_models import FFmpegUploadResponse, FFmpegConvertRequest, TaskStatus
from ..services import service_ffmpeg
import os

router = APIRouter()

@router.post("/upload", response_model=FFmpegUploadResponse)
async def upload_media(file: UploadFile = File(...)):
    return service_ffmpeg.handle_ffmpeg_upload(file)

@router.post("/convert")
async def convert_media(request: FFmpegConvertRequest, background_tasks: BackgroundTasks):
    background_tasks.add_task(
        service_ffmpeg.run_ffmpeg_conversion,
        request.task_id,
        request.output_format,
        request.extract_audio,
        request.resolution,
        request.quality,
        request.bitrate
    )
    return {"message": "Conversion started", "task_id": request.task_id}

@router.get("/status/{task_id}", response_model=TaskStatus)
async def get_conversion_status(task_id: str):
    status = service_ffmpeg.get_ffmpeg_task_status(task_id)
    if status:
        return status
    return {"task_id": task_id, "status": "not_found"}

@router.get("/download/{task_id}/{filename}")
async def download_converted_file(task_id: str, filename: str):
    task = service_ffmpeg.TASKS.get(task_id)
    if task and task['status'] == 'completed':
        file_path = os.path.join(os.path.dirname(task['original_file_path']), filename)
        if os.path.exists(file_path):
            return FileResponse(file_path, media_type='application/octet-stream', filename=filename)
    return {"error": "File not found or conversion not complete"}
