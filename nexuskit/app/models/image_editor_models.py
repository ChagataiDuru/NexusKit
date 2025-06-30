from pydantic import BaseModel

class ImageUploadResponse(BaseModel):
    task_id: str
    filename: str
    image_url: str

class ImageEditRequest(BaseModel):
    task_id: str
    action: str
    params: dict

class ImageEditResponse(BaseModel):
    task_id: str
    image_url: str
