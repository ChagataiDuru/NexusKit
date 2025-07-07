from fastapi import APIRouter, File, UploadFile, Body
from fastapi.responses import FileResponse
from ..models.image_editor_models import ImageUploadResponse, ImageEditRequest, ImageEditResponse
from ..services import service_image_editor, task_service
import os

router = APIRouter()

@router.post("/upload", response_model=ImageUploadResponse)
async def upload_image(file: UploadFile = File(...)):
    return service_image_editor.handle_image_upload(file)

@router.post("/edit", response_model=ImageEditResponse)
async def edit_image(request: ImageEditRequest):
    return service_image_editor.apply_image_edit(request.task_id, request.action, request.params)

@router.post("/undo", response_model=ImageEditResponse)
async def undo_edit(task_id: str = Body(..., embed=True)):
    return service_image_editor.undo_last_edit(task_id)

@router.post("/redo", response_model=ImageEditResponse)
async def redo_edit(task_id: str = Body(..., embed=True)):
    return service_image_editor.redo_last_edit(task_id)

@router.get("/view/{task_id}/{filename}")
async def view_image(task_id: str, filename: str):
    image_path = service_image_editor.get_image_path(task_id, filename)
    if image_path:
        return FileResponse(image_path, media_type="image/png")
    return {"error": "Image not found"}
