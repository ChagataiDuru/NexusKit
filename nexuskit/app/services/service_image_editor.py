import os
from PIL import Image, ImageFilter, ImageOps, ImageEnhance
import base64
import io
import glob
from . import cleanup_service, task_service

def handle_image_upload(file):
    task_id = task_service.create_task(tool_name='image-editor')
    task_dir = os.path.join(cleanup_service.TEMP_DIR, task_id)
    os.makedirs(task_dir, exist_ok=True)

    original_image_path = os.path.join(task_dir, file.filename)
    with open(original_image_path, "wb") as buffer:
        buffer.write(file.file.read())

    img = Image.open(original_image_path)
    # Save initial state as version 0
    version_path = os.path.join(task_dir, f"version_0.png")
    img.save(version_path)

    task_service.update_task(task_id, status='completed', result_path=version_path)
    cleanup_service.schedule_cleanup(task_id)

    return {
        "task_id": task_id,
        "filename": file.filename,
        "image_url": f"/api/v1/image/view/{task_id}/version_0.png"
    }

def apply_image_edit(task_id: str, action: str, params: dict):
    task = task_service.get_task_status(task_id)
    if not task:
        raise ValueError("Task not found")

    task_dir = os.path.dirname(task['result_path'])
    # Find the latest version
    versions = sorted(glob.glob(os.path.join(task_dir, "version_*.png")))
    latest_version_path = versions[-1]
    img = Image.open(latest_version_path)

    # Apply the edit
    img = _apply_action(img, action, params)

    # Save the new version
    new_version_num = len(versions)
    new_version_path = os.path.join(task_dir, f"version_{new_version_num}.png")
    img.save(new_version_path)

    task_service.update_task_result_path(task_id, new_version_path)

    return {
        "task_id": task_id,
        "image_url": f"/api/v1/image/view/{task_id}/{os.path.basename(new_version_path)}"
    }

def undo_last_edit(task_id: str):
    task = task_service.get_task_status(task_id)
    if not task:
        raise ValueError("Task not found")

    task_dir = os.path.dirname(task['result_path'])
    versions = sorted(glob.glob(os.path.join(task_dir, "version_*.png")))
    
    if len(versions) > 1:
        # Remove the latest version to undo
        os.remove(versions[-1])
        new_latest_version_path = versions[-2]
        task_service.update_task_result_path(task_id, new_latest_version_path)
        return {
            "task_id": task_id,
            "image_url": f"/api/v1/image/view/{task_id}/{os.path.basename(new_latest_version_path)}"
        }
    else:
        # Already at the original image
        return {
            "task_id": task_id,
            "image_url": f"/api/v1/image/view/{task_id}/{os.path.basename(versions[0])}"
        }

def redo_last_edit(task_id: str):
    # Redo is more complex and would require storing undone versions.
    # This is a placeholder for a more complete implementation.
    pass

def get_image_path(task_id: str, filename: str):
    task = task_service.get_task_status(task_id)
    if task:
        requested_path = os.path.join(os.path.dirname(task['result_path']), filename)
        if os.path.exists(requested_path):
            return requested_path
    return None

def _apply_action(img: Image.Image, action: str, params: dict) -> Image.Image:
    if action == "crop":
        img = img.crop((params['left'], params['top'], params['right'], params['bottom']))
    elif action == "resize":
        img = img.resize((params['width'], params['height']))
    elif action == "grayscale":
        img = ImageOps.grayscale(img)
    # ... (add all other image editing actions here in the same pattern)
    elif action == "reset":
        # This would now be handled by undoing all actions
        pass
    return img