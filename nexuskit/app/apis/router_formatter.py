from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from enum import Enum
from ..services import service_formatter

router = APIRouter()

class FormatType(str, Enum):
    json = "json"
    yaml = "yaml"

class FormatRequest(BaseModel):
    text: str = Field(..., description="The text content to format (JSON or YAML).")
    format_type: FormatType = Field(..., description="The desired output format (json or yaml).")

@router.post("/format", summary="Format JSON or YAML text")
async def format_content(request: FormatRequest):
    try:
        formatted_text = service_formatter.format_text(request.text, request.format_type)
        return {"formatted_text": formatted_text}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
