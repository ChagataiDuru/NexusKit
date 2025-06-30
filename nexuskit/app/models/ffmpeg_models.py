from pydantic import BaseModel

class FFmpegUploadResponse(BaseModel):
    task_id: str
    filename: str

class FFmpegConvertRequest(BaseModel):
    task_id: str
    output_format: str
    extract_audio: bool = False
    resolution: str | None = None
    quality: str | None = None
    bitrate: str | None = None

class TaskStatus(BaseModel):
    task_id: str
    status: str
    progress: float | None = None
    download_url: str | None = None
    error: str | None = None
