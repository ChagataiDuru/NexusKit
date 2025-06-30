from fastapi import APIRouter, BackgroundTasks
from fastapi.responses import FileResponse
from ..models.ytdl_models import YTdlRequest, YTdlInfo, YTdlDownloadRequest, Task
from ..services import service_ytdl
import os

router = APIRouter()

@router.post("/fetch-info", response_model=YTdlInfo)
async def fetch_info(request: YTdlRequest):
    return service_ytdl.fetch_video_info(request.url)

@router.post("/download-request")
async def download_request(request: YTdlDownloadRequest, background_tasks: BackgroundTasks):
    task_id = service_ytdl.create_download_task(request.url, request.format_id, request.audio_only, request.audio_format)
    background_tasks.add_task(service_ytdl.run_download_task, task_id)
    return {"task_id": task_id}

@router.get("/task-status/{task_id}", response_model=Task)
async def task_status(task_id: str):
    return service_ytdl.TASKS.get(task_id, {"task_id": task_id, "status": "not_found", "result": None})

@router.get("/download/{task_id}")
async def download_file(task_id: str):
    task = service_ytdl.TASKS.get(task_id)
    if task and task['status'] == 'completed':
        return FileResponse(task['result'], media_type='application/octet-stream', filename=os.path.basename(task['result']))
    return {"error": "File not found or task not completed"}
