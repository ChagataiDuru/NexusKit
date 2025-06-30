import uuid
import os
import fitz  # PyMuPDF
from PyPDF2 import PdfReader, PdfWriter
import base64
import io
from PIL import Image
from . import cleanup_service

TASKS = {}

def handle_pdf_upload(file):
    task_id = str(uuid.uuid4())
    task_dir = os.path.join(cleanup_service.TEMP_DIR, task_id)
    os.makedirs(task_dir, exist_ok=True)

    original_pdf_path = os.path.join(task_dir, file.filename)
    with open(original_pdf_path, "wb") as buffer:
        buffer.write(file.file.read())

    # Generate previews
    preview_paths = []
    doc = fitz.open(original_pdf_path)
    for i, page in enumerate(doc):
        pix = page.get_pixmap()
        preview_path = os.path.join(task_dir, f"page_{i}.png")
        pix.save(preview_path)
        preview_paths.append(f"/api/v1/pdf/preview/{task_id}/page_{i}.png")

    TASKS[task_id] = {
        "original_pdf_path": original_pdf_path,
        "num_pages": len(doc),
        "pages": preview_paths
    }
    cleanup_service.schedule_cleanup(task_id)

    return {
        "task_id": task_id,
        "num_pages": len(doc),
        "pages": preview_paths
    }

def add_blank_page(task_id: str):
    task = TASKS[task_id]
    pdf_path = task['original_pdf_path']

    reader = PdfReader(pdf_path)
    writer = PdfWriter()

    for page in reader.pages:
        writer.add_page(page)

    writer.add_blank_page()

    new_pdf_path = f"{pdf_path}.new"
    with open(new_pdf_path, "wb") as f:
        writer.write(f)

    os.replace(new_pdf_path, pdf_path)

    # Regenerate previews
    preview_paths = []
    doc = fitz.open(pdf_path)
    for i, page in enumerate(doc):
        pix = page.get_pixmap()
        preview_path = os.path.join(os.path.dirname(pdf_path), f"page_{i}.png")
        pix.save(preview_path)
        preview_paths.append(f"/api/v1/pdf/preview/{task_id}/page_{i}.png")

    task['num_pages'] = len(doc)
    task['pages'] = preview_paths
    cleanup_service.schedule_cleanup(task_id)

    return {
        "task_id": task_id,
        "num_pages": len(doc),
        "pages": preview_paths
    }

def delete_pages(task_id: str, pages_to_delete: list[int]):
    task = TASKS[task_id]
    pdf_path = task['original_pdf_path']

    reader = PdfReader(pdf_path)
    writer = PdfWriter()

    for i in range(len(reader.pages)):
        if i not in pages_to_delete:
            writer.add_page(reader.pages[i])

    new_pdf_path = f"{pdf_path}.new"
    with open(new_pdf_path, "wb") as f:
        writer.write(f)

    os.replace(new_pdf_path, pdf_path)

    # Regenerate previews
    preview_paths = []
    doc = fitz.open(pdf_path)
    for i, page in enumerate(doc):
        pix = page.get_pixmap()
        preview_path = os.path.join(os.path.dirname(pdf_path), f"page_{i}.png")
        pix.save(preview_path)
        preview_paths.append(f"/api/v1/pdf/preview/{task_id}/page_{i}.png")

    task['num_pages'] = len(doc)
    task['pages'] = preview_paths
    cleanup_service.schedule_cleanup(task_id)

    return {
        "task_id": task_id,
        "num_pages": len(doc),
        "pages": preview_paths
    }

def reorder_pages(task_id: str, page_order: list[int]):
    task = TASKS[task_id]
    pdf_path = task['original_pdf_path']

    reader = PdfReader(pdf_path)
    writer = PdfWriter()

    for page_index in page_order:
        writer.add_page(reader.pages[page_index])

    new_pdf_path = f"{pdf_path}.new"
    with open(new_pdf_path, "wb") as f:
        writer.write(f)

    os.replace(new_pdf_path, pdf_path)

    # Regenerate previews
    preview_paths = []
    doc = fitz.open(pdf_path)
    for i, page in enumerate(doc):
        pix = page.get_pixmap()
        preview_path = os.path.join(os.path.dirname(pdf_path), f"page_{i}.png")
        pix.save(preview_path)
        preview_paths.append(f"/api/v1/pdf/preview/{task_id}/page_{i}.png")

    task['num_pages'] = len(doc)
    task['pages'] = preview_paths
    cleanup_service.schedule_cleanup(task_id)

    return {
        "task_id": task_id,
        "num_pages": len(doc),
        "pages": preview_paths
    }

def add_signature(task_id: str, page_index: int, x: float, y: float, width: float, signature_data_url: str):
    task = TASKS[task_id]
    pdf_path = task['original_pdf_path']

    # Decode base64 image
    header, encoded = signature_data_url.split(",", 1)
    data = base64.b64decode(encoded)
    img = Image.open(io.BytesIO(data))

    # Save signature temporarily as PNG
    signature_temp_path = os.path.join(os.path.dirname(pdf_path), "signature_temp.png")
    img.save(signature_temp_path)

    doc = fitz.open(pdf_path)
    page = doc[page_index]

    # Calculate height based on aspect ratio and desired width
    img_width, img_height = img.size
    height = (img_height / img_width) * width

    # Insert image (signature) onto the page
    # PyMuPDF uses points (1/72 inch) for coordinates
    # Assuming x, y, width are in pixels from frontend, need to convert to PDF points
    # A4 page is 595x842 points (approx)
    # This conversion might need fine-tuning based on actual PDF dimensions and frontend pixel density
    # For now, let's assume 1 pixel = 1 point for initial implementation, will need adjustment
    rect = fitz.Rect(x, y, x + width, y + height)
    page.insert_image(rect, filename=signature_temp_path)

    doc.save(pdf_path, incremental=True, encryption=fitz.PDF_ENCRYPT_KEEP)
    doc.close()

    os.remove(signature_temp_path)

    # Regenerate previews
    preview_paths = []
    doc = fitz.open(pdf_path)
    for i, page in enumerate(doc):
        pix = page.get_pixmap()
        preview_path = os.path.join(os.path.dirname(pdf_path), f"page_{i}.png")
        pix.save(preview_path)
        preview_paths.append(f"/api/v1/pdf/preview/{task_id}/page_{i}.png")

    task['num_pages'] = len(doc)
    task['pages'] = preview_paths
    cleanup_service.schedule_cleanup(task_id)

    return {
        "task_id": task_id,
        "num_pages": len(doc),
        "pages": preview_paths
    }
