
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from .apis import router_ytdl, router_pdf, router_ffmpeg, router_image_editor
from .services import cleanup_service
import logging
import os

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

app = FastAPI(title="NexusKit")

@app.on_event("startup")
async def startup_event():
    cleanup_service.setup_temp_directory()

# Mount static files
app.mount("/static", StaticFiles(directory="nexuskit/app/static"), name="static")

# Include API routers
app.include_router(router_ytdl.router, prefix="/api/v1/ytdl", tags=["yt-dlp"])
app.include_router(router_pdf.router, prefix="/api/v1/pdf", tags=["pdf-editor"])
app.include_router(router_ffmpeg.router, prefix="/api/v1/ffmpeg", tags=["ffmpeg-converter"])
app.include_router(router_image_editor.router, prefix="/api/v1/image", tags=["image-editor"])

from fastapi.responses import RedirectResponse

@app.get("/")
async def read_root():
    return RedirectResponse(url="/static/index.html")
