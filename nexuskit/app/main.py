
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from .apis import router_ytdl, router_pdf, router_ffmpeg, router_image_editor, router_formatter
from .services import cleanup_service
from . import database
import logging
import os
import uuid
import datetime
from pydantic import BaseModel

# Ensure logs directory exists
log_dir = "logs"
os.makedirs(log_dir, exist_ok=True)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(os.path.join(log_dir, "nexuskit.log"))
    ]
)

class ErrorResponse(BaseModel):
    error_id: str
    timestamp: str
    message: str

app = FastAPI(title="NexusKit")

@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    error_id = str(uuid.uuid4())
    timestamp = datetime.datetime.utcnow().isoformat() + "Z"
    logging.error(f"Error ID: {error_id} - {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content=ErrorResponse(error_id=error_id, timestamp=timestamp, message="An unexpected error occurred.").dict()
    )

@app.on_event("startup")
async def startup_event():
    cleanup_service.setup_temp_directory()
    database.init_db()

@app.on_event("shutdown")
async def shutdown_event():
    database.close_db_connection()

# Mount static files
app.mount("/static", StaticFiles(directory="nexuskit/app/static"), name="static")

# Include API routers
app.include_router(router_ytdl.router, prefix="/api/v1/ytdl", tags=["yt-dlp"])
app.include_router(router_pdf.router, prefix="/api/v1/pdf", tags=["pdf-editor"])
app.include_router(router_ffmpeg.router, prefix="/api/v1/ffmpeg", tags=["ffmpeg-converter"])
app.include_router(router_image_editor.router, prefix="/api/v1/image", tags=["image-editor"])
app.include_router(router_formatter.router, prefix="/api/v1/formatter", tags=["formatter"])

from fastapi.responses import RedirectResponse

@app.get("/")
async def read_root():
    return RedirectResponse(url="/static/index.html")
