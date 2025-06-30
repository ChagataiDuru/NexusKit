from pydantic import BaseModel

class YTdlRequest(BaseModel):
    url: str

class YTdlInfo(BaseModel):
    title: str
    thumbnail: str
    formats: list

class YTdlDownloadRequest(BaseModel):
    url: str
    format_id: str
    audio_only: bool
    audio_format: str | None = None

class Task(BaseModel):
    task_id: str
    status: str
    result: str | None = None
