from fastapi import APIRouter, File, UploadFile, BackgroundTasks, Depends
from fastapi.responses import FileResponse
from ..models.ffmpeg_models import FFmpegUploadResponse, FFmpegConvertRequest
from ..services import service_ffmpeg, task_service
from ..database import get_db
import os
import asyncio
import json
from sse_starlette.sse import EventSourceResponse

router = APIRouter()

@router.post("/upload", response_model=FFmpegUploadResponse)
async def upload_media(file: UploadFile = File(...)):
    return service_ffmpeg.handle_ffmpeg_upload(file)

@router.post("/convert")
async def convert_media(request: FFmpegConvertRequest, background_tasks: BackgroundTasks):
    task = task_service.get_task_status(request.task_id)
    if not task:
        return {"error": "Task not found"}
    
    background_tasks.add_task(
        service_ffmpeg.run_ffmpeg_conversion,
        request.task_id,
        task['result_path'], # The original file path is stored in result_path after upload
        request.output_format,
        request.extract_audio,
        request.resolution,
        request.quality,
        request.bitrate
    )
    return {"message": "Conversion started", "task_id": request.task_id}

@router.get("/tasks/{task_id}/stream")
async def stream_task_progress(task_id: str, db=Depends(get_db)):
    async def event_generator():
        last_progress = -1
        while True:
            task = task_service.get_task_status(task_id)
            if task:
                if task['progress'] != last_progress:
                    yield {"data": json.dumps(task)}
                    last_progress = task['progress']
                if task['status'] in ['completed', 'failed']:
                    break
            await asyncio.sleep(1)
    return EventSourceResponse(event_generator())

@router.get("/download/{task_id}")
async def download_converted_file(task_id: str):
    task = task_service.get_task_status(task_id)
    if task and task['status'] == 'completed':
        return FileResponse(task['result_path'], media_type='application/octet-stream', filename=os.path.basename(task['result_path']))
    return {"error": "File not found or conversion not complete"}
