from fastapi import APIRouter, File, UploadFile, Depends, Form
from fastapi.responses import FileResponse, StreamingResponse
from ..models.pdf_models import PDFUploadResponse, DeletePagesRequest, ReorderPagesRequest, AddSignatureRequest
from ..services import service_pdf, task_service
import os
from typing import List

router = APIRouter()

@router.post("/upload", response_model=PDFUploadResponse)
async def upload_pdf(file: UploadFile = File(...)):
    return service_pdf.handle_pdf_upload(file)

@router.get("/preview/{task_id}/{page_name}")
async def get_preview_image(task_id: str, page_name: str):
    task_dir = os.path.join(task_service.cleanup_service.TEMP_DIR, task_id)
    image_path = os.path.join(task_dir, page_name)
    if os.path.exists(image_path):
        return FileResponse(image_path)
    return {"error": "Image not found"}

@router.post("/{task_id}/add-blank-page", response_model=PDFUploadResponse)
async def add_blank_page(task_id: str):
    return service_pdf.add_blank_page(task_id)

@router.post("/{task_id}/delete-pages", response_model=PDFUploadResponse)
async def delete_pages(task_id: str, request: DeletePagesRequest):
    return service_pdf.delete_pages(task_id, request.pages)

@router.post("/{task_id}/reorder-pages", response_model=PDFUploadResponse)
async def reorder_pages(task_id: str, request: ReorderPagesRequest):
    return service_pdf.reorder_pages(task_id, request.page_order)

@router.post("/{task_id}/add-signature", response_model=PDFUploadResponse)
async def add_signature(task_id: str, request: AddSignatureRequest):
    return service_pdf.add_signature(task_id, request.page_index, request.x, request.y, request.width, request.signature_data_url)

@router.post("/merge")
async def merge_pdfs(files: List[UploadFile] = File(...)):
    merged_pdf = service_pdf.merge_pdfs(files)
    return StreamingResponse(merged_pdf, media_type="application/pdf", headers={"Content-Disposition": "attachment; filename=merged.pdf"})

@router.post("/compress")
async def compress_pdf(file: UploadFile = File(...), level: str = Form(...)):
    compressed_pdf = service_pdf.compress_pdf(file, level)
    return StreamingResponse(compressed_pdf, media_type="application/pdf", headers={"Content-Disposition": f"attachment; filename=compressed.pdf"})

@router.get("/{task_id}/download")
async def download_pdf(task_id: str):
    task = task_service.get_task_status(task_id)
    if task and task['status'] == 'completed':
        return FileResponse(task['result_path'], media_type='application/pdf', filename=os.path.basename(task['result_path']))
    return {"error": "File not found"}
