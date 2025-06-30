from pydantic import BaseModel

class PDFUploadResponse(BaseModel):
    task_id: str
    num_pages: int
    pages: list[str]

class DeletePagesRequest(BaseModel):
    pages: list[int]

class ReorderPagesRequest(BaseModel):
    page_order: list[int]

class AddSignatureRequest(BaseModel):
    page_index: int
    x: float
    y: float
    width: float
    signature_data_url: str
