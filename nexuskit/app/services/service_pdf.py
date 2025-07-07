import os
import fitz  # PyMuPDF
from PyPDF2 import PdfReader, PdfWriter
import base64
import io
from PIL import Image
import subprocess
import tempfile
from . import cleanup_service, task_service

def handle_pdf_upload(file):
    task_id = task_service.create_task(tool_name='pdf-editor')
    task_dir = os.path.join(cleanup_service.TEMP_DIR, task_id)
    os.makedirs(task_dir, exist_ok=True)

    original_pdf_path = os.path.join(task_dir, file.filename)
    with open(original_pdf_path, "wb") as buffer:
        buffer.write(file.file.read())

    task_service.update_task_progress(task_id, 50) # Mark as processing

    # Generate previews
    preview_paths = []
    doc = fitz.open(original_pdf_path)
    for i, page in enumerate(doc):
        pix = page.get_pixmap()
        preview_path = os.path.join(task_dir, f"page_{i}.png")
        pix.save(preview_path)
        preview_paths.append(f"/api/v1/pdf/preview/{task_id}/page_{i}.png")

    task_service.complete_task(task_id, original_pdf_path)
    cleanup_service.schedule_cleanup(task_id)

    return {
        "task_id": task_id,
        "num_pages": len(doc),
        "pages": preview_paths
    }

def add_blank_page(task_id: str):
    task = task_service.get_task_status(task_id)
    pdf_path = task['result_path']

    reader = PdfReader(pdf_path)
    writer = PdfWriter()

    for page in reader.pages:
        writer.add_page(page)

    writer.add_blank_page()

    with open(pdf_path, "wb") as f:
        writer.write(f)

    return get_pdf_previews(task_id, pdf_path)

def delete_pages(task_id: str, pages_to_delete: list[int]):
    task = task_service.get_task_status(task_id)
    pdf_path = task['result_path']

    reader = PdfReader(pdf_path)
    writer = PdfWriter()

    for i in range(len(reader.pages)):
        if i not in pages_to_delete:
            writer.add_page(reader.pages[i])

    with open(pdf_path, "wb") as f:
        writer.write(f)

    return get_pdf_previews(task_id, pdf_path)

def reorder_pages(task_id: str, page_order: list[int]):
    task = task_service.get_task_status(task_id)
    pdf_path = task['result_path']

    reader = PdfReader(pdf_path)
    writer = PdfWriter()

    for page_index in page_order:
        writer.add_page(reader.pages[page_index])

    with open(pdf_path, "wb") as f:
        writer.write(f)

    return get_pdf_previews(task_id, pdf_path)

def add_signature(task_id: str, page_index: int, x: float, y: float, width: float, signature_data_url: str):
    task = task_service.get_task_status(task_id)
    pdf_path = task['result_path']

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

    rect = fitz.Rect(x, y, x + width, y + height)
    page.insert_image(rect, filename=signature_temp_path)

    doc.save(pdf_path, incremental=True, encryption=fitz.PDF_ENCRYPT_KEEP)
    doc.close()

    os.remove(signature_temp_path)

    return get_pdf_previews(task_id, pdf_path)

def merge_pdfs(files):
    writer = PdfWriter()
    for file in files:
        reader = PdfReader(file.file)
        for page in reader.pages:
            writer.add_page(page)
    
    output = io.BytesIO()
    writer.write(output)
    output.seek(0)
    return output

def compress_pdf(file, level):
    settings_map = {
        "Low": "/screen",
        "Medium": "/ebook",
        "High": "/printer"
    }
    gs_setting = settings_map.get(level, "/ebook")

    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_in:
        tmp_in.write(file.file.read())
        tmp_in_path = tmp_in.name

    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_out:
        tmp_out_path = tmp_out.name

    command = [
        "gs",
        "-sDEVICE=pdfwrite",
        "-dCompatibilityLevel=1.4",
        f"-dPDFSETTINGS={gs_setting}",
        "-dNOPAUSE",
        "-dQUIET",
        "-dBATCH",
        f"-sOutputFile={tmp_out_path}",
        tmp_in_path
    ]

    try:
        subprocess.run(command, check=True)
    except (subprocess.CalledProcessError, FileNotFoundError) as e:
        # Handle error, e.g., Ghostscript not found or compression failed
        raise RuntimeError(f"PDF compression failed: {e}")

    with open(tmp_out_path, "rb") as f:
        compressed_pdf = f.read()

    os.remove(tmp_in_path)
    os.remove(tmp_out_path)

    return io.BytesIO(compressed_pdf)

def get_pdf_previews(task_id: str, pdf_path: str):
    task_dir = os.path.dirname(pdf_path)
    preview_paths = []
    doc = fitz.open(pdf_path)
    for i, page in enumerate(doc):
        pix = page.get_pixmap()
        preview_path = os.path.join(task_dir, f"page_{i}.png")
        pix.save(preview_path)
        preview_paths.append(f"/api/v1/pdf/preview/{task_id}/page_{i}.png")

    return {
        "task_id": task_id,
        "num_pages": len(doc),
        "pages": preview_paths
    }

