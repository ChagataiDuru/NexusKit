import uuid
import os
from PIL import Image, ImageFilter, ImageOps, ImageEnhance
import base64
import io
from . import cleanup_service

TASKS = {}

def handle_image_upload(file):
    task_id = str(uuid.uuid4())
    task_dir = os.path.join(cleanup_service.TEMP_DIR, task_id)
    os.makedirs(task_dir, exist_ok=True)

    original_image_path = os.path.join(task_dir, file.filename)
    with open(original_image_path, "wb") as buffer:
        buffer.write(file.file.read())

    # Convert to PNG for consistent editing and preview
    img = Image.open(original_image_path)
    png_path = os.path.join(task_dir, f"original.png")
    img.save(png_path)

    TASKS[task_id] = {
        "original_image_path": png_path, # Store as PNG for consistency
        "current_image_path": png_path,
        "history": [png_path] # For reset to original
    }
    cleanup_service.schedule_cleanup(task_id)

    return {
        "task_id": task_id,
        "filename": file.filename,
        "image_url": f"/api/v1/image/view/{task_id}/original.png"
    }

def apply_image_edit(task_id: str, action: str, params: dict):
    task = TASKS[task_id]
    current_image_path = task['current_image_path']
    img = Image.open(current_image_path)

    if action == "crop":
        left = params['left']
        top = params['top']
        right = params['right']
        bottom = params['bottom']
        img = img.crop((left, top, right, bottom))
    elif action == "resize":
        width = params['width']
        height = params['height']
        img = img.resize((width, height))
    elif action == "grayscale":
        img = ImageOps.grayscale(img)
    elif action == "sepia":
        # Simple sepia filter
        sepia_filter = Image.new('RGB', img.size)
        for x in range(img.width):
            for y in range(img.height):
                r, g, b = img.getpixel((x, y))[:3]
                tr = int(0.393 * r + 0.769 * g + 0.189 * b)
                tg = int(0.349 * r + 0.686 * g + 0.168 * b)
                tb = int(0.272 * r + 0.534 * g + 0.131 * b)
                sepia_filter.putpixel((x, y), (min(tr, 255), min(tg, 255), min(tb, 255)))
        img = sepia_filter
    elif action == "invert":
        img = ImageOps.invert(img)
    elif action == "brightness":
        factor = params['factor'] # 0.0 to 2.0
        enhancer = ImageEnhance.Brightness(img)
        img = enhancer.enhance(factor)
    elif action == "contrast":
        factor = params['factor'] # 0.0 to 2.0
        enhancer = ImageEnhance.Contrast(img)
        img = enhancer.enhance(factor)
    elif action == "blur":
        radius = params['radius']
        img = img.filter(ImageFilter.GaussianBlur(radius))
    elif action == "rotate_90_left":
        img = img.transpose(Image.ROTATE_90)
    elif action == "rotate_90_right":
        img = img.transpose(Image.ROTATE_270)
    elif action == "rotate_180":
        img = img.transpose(Image.ROTATE_180)
    elif action == "flip_horizontal":
        img = ImageOps.mirror(img)
    elif action == "flip_vertical":
        img = ImageOps.flip(img)
    elif action == "remove_white_background":
        img = img.convert("RGBA")
        datas = img.getdata()
        newData = []
        for item in datas:
            # Change all white (also shades of white) pixels to transparent
            if item[0] > 200 and item[1] > 200 and item[2] > 200:
                newData.append((255, 255, 255, 0))
            else:
                newData.append(item)
        img.putdata(newData)
    elif action == "remove_black_background":
        img = img.convert("RGBA")
        datas = img.getdata()
        newData = []
        for item in datas:
            # Change all black (also shades of black) pixels to transparent
            if item[0] < 50 and item[1] < 50 and item[2] < 50:
                newData.append((0, 0, 0, 0))
            else:
                newData.append(item)
        img.putdata(newData)
    elif action == "reset":
        img = Image.open(task['original_image_path'])

    # Save the modified image
    modified_image_filename = f"modified_{uuid.uuid4()}.png"
    modified_image_path = os.path.join(os.path.dirname(current_image_path), modified_image_filename)
    img.save(modified_image_path)

    task['current_image_path'] = modified_image_path
    task['history'].append(modified_image_path)
    cleanup_service.schedule_cleanup(task_id)

    return {
        "task_id": task_id,
        "image_url": f"/api/v1/image/view/{task_id}/{modified_image_filename}"
    }

def get_image_path(task_id: str, filename: str):
    task = TASKS.get(task_id)
    if task:
        # Ensure the requested filename is part of the task's directory
        # This is a basic security check to prevent path traversal
        requested_path = os.path.join(os.path.dirname(task['original_image_path']), filename)
        if os.path.exists(requested_path) and os.path.commonprefix([requested_path, os.path.dirname(task['original_image_path'])]) == os.path.dirname(task['original_image_path']):
            return requested_path
    return None
