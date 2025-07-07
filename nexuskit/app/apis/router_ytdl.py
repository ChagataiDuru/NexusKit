from fastapi import APIRouter, BackgroundTasks, Depends
from fastapi.responses import FileResponse
from ..models.ytdl_models import YTdlRequest, YTdlInfo, YTdlDownloadRequest
from ..services import service_ytdl, task_service
from ..database import get_db
import os
import asyncio
import json
from sse_starlette.sse import EventSourceResponse

router = APIRouter()

@router.post("/fetch-info", response_model=YTdlInfo)
async def fetch_info(request: YTdlRequest):
    return service_ytdl.fetch_video_info(request.url)

@router.post("/download-request")
async def download_request(request: YTdlDownloadRequest, background_tasks: BackgroundTasks):
    task_id = service_ytdl.create_download_task(request.url, request.format_id, request.audio_only, request.audio_format)
    background_tasks.add_task(service_ytdl.run_download_task, task_id, request.url, request.format_id, request.audio_only, request.audio_format)
    return {"task_id": task_id}

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
async def download_file(task_id: str):
    task = task_service.get_task_status(task_id)
    if task and task['status'] == 'completed':
        return FileResponse(task['result_path'], media_type='application/octet-stream', filename=os.path.basename(task['result_path']))
    return {"error": "File not found or task not completed"}
