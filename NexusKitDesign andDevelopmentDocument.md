# NexusKit: Design and Development Document

**Version:** 1.0 (Initial MVP)
**Date:** June 30, 2025

## 1. Introduction

### 1.1. Project Name
NexusKit

### 1.2. Project Vision
NexusKit aims to be a locally hosted web application providing a suite of useful "Software as a Service (SaaS)" like tools for personal and small group (friends) usage. It prioritizes convenience, control over data, and a user-friendly interface for common digital tasks.

### 1.3. Goals for V1 (MVP)
* Develop a functional web application with the following core tools:
    * **yt-dlp Wrapper:** For downloading YouTube videos and shorts in various formats.
    * **PDF Editor:** For basic PDF manipulations like adding signatures, adding/deleting pages, and reordering pages.
    * **FFmpeg Wrapper:** For common media conversions (video and audio).
    * **Basic Image Editor:** For tasks like cropping, resizing, applying simple filters, and basic background removal.
* Ensure the system is hosted on a personal server using Nginx as a reverse proxy.
* Implement a "disposable session" model with no user accounts, where temporary files are cleaned up automatically.
* Design the system with extensibility in mind for adding more tools in the future.
* Provide a clean, modern, and responsive user interface accessible on desktop and mobile devices.

---

## 2. Target Audience and User Model

### 2.1. Target Audience
* The primary developer and a small group of friends (initially 2-5 users).
* Users are expected to have varying levels of technical proficiency but should find the tools intuitive to use through a web interface.

### 2.2. User Interaction Model
* **No User Accounts/Login:** The application will be accessed directly without any authentication.
* **Shared Interface:** All users access the same interface.
* **Disposable Sessions:** Each usage of a tool is considered a "one-time disposable" session.
    * Uploaded files and generated outputs are temporary.
    * Users are responsible for downloading their processed files.
    * The server will automatically clean up temporary files.
* **Concurrency:** The system should handle concurrent usage by a few users, with file isolation for each task.

---

## 3. System Architecture

### 3.1. High-Level Overview
NexusKit will be a web application with three main components:
1.  **Frontend:** A client-side interface built with Vanilla HTML, CSS, and JavaScript, styled with Bootstrap.
2.  **Backend:** A Python-based API built with FastAPI, responsible for business logic, interacting with command-line tools, and file management.
3.  **Web Server/Proxy:** Nginx will act as a reverse proxy in front of the FastAPI application (run by Uvicorn).

```mermaid
graph LR
    User[User's Browser] -- HTTPS --> Nginx
    Nginx -- Serves --> User(Static Files: HTML, CSS, JS)
    Nginx -- Reverse Proxy (HTTP) --> Uvicorn[Uvicorn ASGI Server]
    Uvicorn -- Runs --> FastAPI[FastAPI Application: Python]
    FastAPI -- Interacts with --> CLITools[yt-dlp, FFmpeg]
    FastAPI -- Interacts with --> PythonLibs[PDF Libs, Pillow]
    FastAPI -- Manages --> TempStorage[Temporary File Storage: /var/tmp/nexuskit_data/]
    User -- Interacts with --> Frontend[Frontend UI]
    Frontend -- API Calls --> FastAPI
````

### 3.2. Frontend

  * **Technology:** Vanilla HTML5, CSS3, JavaScript (ES6+).
  * **Styling:** Bootstrap 5 (or latest) for layout, responsiveness, and common components, augmented with custom CSS for a unique "clean and modern" look.
  * **Interaction:** Client-side JavaScript will handle user interactions, form submissions (via `fetch` API), API calls to the backend, and dynamic UI updates (e.g., displaying previews, progress, results).

### 3.3. Backend

  * **Technology:** Python 3.x with the FastAPI framework.
  * **ASGI Server:** Uvicorn (run directly from the command line for V1).
  * **Responsibilities:**
      * Exposing RESTful API endpoints for each tool.
      * Handling file uploads and downloads.
      * Executing command-line tools (`yt-dlp`, `ffmpeg`) securely using the `subprocess` module.
      * Performing PDF manipulations using Python libraries (e.g., `PyPDF2`, `fitz/PyMuPDF`, `reportlab`).
      * Performing image manipulations using Python libraries (e.g., `Pillow`).
      * Managing temporary files and their cleanup.
      * Handling long-running tasks using `BackgroundTasks`.
      * Providing progress updates for long tasks via polling endpoints.

### 3.4. Web Server / Reverse Proxy

  * **Technology:** Nginx.
  * **Responsibilities:**
      * Acting as a reverse proxy for the Uvicorn/FastAPI application.
      * SSL/TLS termination (using a self-signed certificate for internal use).
      * Serving static frontend files (HTML, CSS, JS, images) efficiently.
      * Routing API requests to the FastAPI application.
      * Implementing security headers.

-----

## 4\. Core Modules/Tools (V1 Detailed Breakdown)

Each tool will be accessible from a main dashboard/homepage and will reside on its own distinct URL path.

### 4.1. yt-dlp Wrapper

  * **URL Path:** `/ytdl`
  * **Description:** Allows users to download YouTube videos and shorts.
  * **Input:**
      * A text input field for the YouTube video or Shorts URL.
  * **Output Options & Quality:**
      * **Video Formats:** MP4 (primary), WebM (secondary option).
      * **Audio Formats:** MP3, M4A, OGG, WAV.
      * **Audio-only Toggle:** Checkbox/toggle to specify audio-only download.
      * **Audio Quality:** Always targets the best available audio quality (no user selection).
      * **Video Quality:** Dynamically fetches and lists all available video qualities (e.g., 1080p, 720p, 480p, Best Available) for the given URL, allowing user selection.
  * **Core Functionality:**
      * Download single videos and YouTube Shorts.
      * No playlist downloads for V1.
      * Fetch and display video title and thumbnail as a preview before download initiation.
      * Downloads are initiated by providing a download link for the generated file.
  * **User Interface Elements:**
      * URL input field.
      * Video format selector (dropdown: MP4, WebM).
      * Video quality selector (dropdown: dynamically populated).
      * Audio-only checkbox.
      * Audio format selector (dropdown: MP3, M4A, OGG, WAV) - visible if audio-only is checked or implied by selection.
      * "Fetch Info" button (or auto-fetch on URL paste/blur).
      * Preview area (for thumbnail and title).
      * "Download" button.
      * Message area for status, progress (via polling), errors, and download link.

### 4.2. PDF Editor

  * **URL Path:** `/pdf-editor`
  * **Description:** Basic PDF editing capabilities.
  * **Input:**
      * File upload for a single PDF file.
  * **Core Features (V1):**
    1.  **View PDF:** Display uploaded PDF pages, with a sidebar for page thumbnails.
    2.  **Add Signature:**
          * Create signature: Via a drawable pop-up modal (using HTML canvas).
          * Upload signature: Allow uploading a PNG image of a signature.
          * Placement: Drag and drop the created/uploaded signature onto any PDF page; allow resizing.
    3.  **Delete Pages:** Select one or more pages (via thumbnails) and remove them.
    4.  **Add Blank Pages:** Insert blank pages into the PDF.
    5.  **Reorder Pages:** Drag and drop page thumbnails in the sidebar to change their order.
  * **Output:**
      * Download the modified PDF file.
  * **User Interface Elements:**
      * File upload area.
      * Main PDF page viewing panel.
      * Sidebar with scrollable page thumbnails (for navigation, selection, reordering).
      * Toolbar with buttons for: "Add Signature," "Delete Page(s)," "Add Blank Page." (Reordering is via drag-drop on thumbnails).
      * Page navigation controls (if needed beyond thumbnail clicks).
      * Signature creation modal (drawable canvas, upload option).
      * "Download Modified PDF" button.
      * Message area for status and errors.

### 4.3. FFmpeg Wrapper

  * **URL Path:** `/ffmpeg-converter`
  * **Description:** Media conversion for common audio and video formats.
  * **Input:**
      * File upload for a media file.
      * Supported input video formats: MP4, MKV, AVI, MOV, WEBM.
      * Supported input audio formats: MP3, WAV, M4A, FLAC, OGG.
  * **Output Options / Conversion Targets:**
      * **Video Output Formats:** MP4, MKV, WEBM, MOV, animated GIF.
      * **Audio Output Formats:** MP3, M4A, WAV, OGG, FLAC, AAC.
      * **Conversion Parameters (Video):**
          * Selectable resolution (e.g., Original, 1080p, 720p, custom).
          * Quality level (e.g., High, Medium, Low presets translating to FFmpeg `-crf` or bitrate settings).
      * **Conversion Parameters (Audio):**
          * Selectable bitrate (e.g., 320kbps, 256kbps, 192kbps, 128kbps).
      * **Functionality:** Extract audio from video files.
  * **Core Functionality:**
      * Convert uploaded media to selected format and parameters.
      * Provide a download link for the converted file.
  * **User Interface Elements:**
      * File upload area.
      * Dropdown to select output category (e.g., Video, Audio).
      * Dropdown for target format (dynamically updated based on category).
      * Input fields/sliders/dropdowns for conversion parameters (resolution, quality, bitrate).
      * Checkbox for "Extract Audio" if a video file is uploaded.
      * "Start Conversion" button.
      * Message area for status, progress (via polling), errors, and download link.

### 4.4. Basic Image Editor

  * **URL Path:** `/image-editor`
  * **Description:** Basic image manipulation tools.
  * **Input:**
      * File upload for an image.
      * Supported input formats: JPEG, PNG, WEBP, GIF (first frame for editing operations).
  * **Core Features (V1):**
    1.  **View Image:** Display the uploaded image on a canvas.
    2.  **Cropping:** Draggable and resizable rectangle overlay; options for fixed aspect ratios (1:1, 4:3, 16:9, Freeform).
    3.  **Resizing:** By specific pixel dimensions (width/height) or by percentage; "maintain aspect ratio" option (default on).
    4.  **Filters:**
          * Grayscale
          * Sepia
          * Invert Colors
          * Brightness (slider)
          * Contrast (slider)
          * Basic Blur (slider for intensity)
    5.  **Rotation:** 90° Left, 90° Right, 180°.
    6.  **Flipping:** Horizontal, Vertical.
    7.  **Background Removal (Simple):**
          * Button: "Remove White Background" (targets near-pure white, makes transparent).
          * Button: "Remove Black Background" (targets near-pure black, makes transparent).
          * Output for this feature will be PNG.
    8.  **Output Format & Quality:**
          * Save as: JPEG (with quality slider 1-100), PNG, WEBP.
  * **Undo/Redo:**
      * A single "Reset to Original Image" button for V1.
  * **User Interface Elements:**
      * File upload area.
      * Main image viewing/editing canvas.
      * Toolbar/sidebar with controls/buttons for: Crop, Resize, Filters (dropdown or individual buttons/sliders), Rotate, Flip, Background Removal.
      * Dropdown for output format selection.
      * JPEG quality slider (visible if JPEG output is selected).
      * "Download Image" button.
      * "Reset to Original" button.
      * Message area for status and errors.

-----

## 5\. Backend Design

### 5.1. Technology Stack

  * **Language:** Python 3.9+
  * **Framework:** FastAPI
  * **ASGI Server:** Uvicorn
  * **Key Libraries (anticipated):**
      * `python-multipart` (for file uploads with FastAPI)
      * `yt-dlp` (Python package for YouTube downloading)
      * PDF manipulation: `PyPDF2` and/or `fitz` (PyMuPDF), `reportlab` (for creating blank pages or text on signature).
      * Image manipulation: `Pillow` (PIL Fork).
      * Standard library: `subprocess`, `os`, `shutil`, `uuid`, `logging`.

### 5.2. Proposed Directory Structure (Simplified)

```
nexuskit/
├── app/
│   ├── __init__.py
│   ├── main.py             # FastAPI app initialization, main router
│   ├── core/               # Core logic, settings, security utils
│   │   ├── config.py
│   │   └── security.py
│   ├── apis/               # API Routers for each tool
│   │   ├── __init__.py
│   │   ├── deps.py           # Common dependencies for routers
│   │   ├── router_ytdl.py
│   │   ├── router_pdf.py
│   │   ├── router_ffmpeg.py
│   │   └── router_image_editor.py
│   ├── services/           # Business logic for each tool
│   │   ├── __init__.py
│   │   ├── service_ytdl.py
│   │   ├── service_pdf.py
│   │   ├── service_ffmpeg.py
│   │   └── service_image_editor.py
│   ├── models/             # Pydantic models for request/response
│   │   ├── __init__.py
│   │   ├── common_models.py
│   │   ├── ytdl_models.py
│   │   └── # ... other tool-specific models
│   └── static/             # Frontend files (HTML, CSS, JS)
│       ├── index.html        # Main dashboard page
│       ├── css/
│       │   └── style.css     # Custom CSS (Bootstrap linked via CDN or local)
│       ├── js/
│       │   └── main.js       # Global JS, navigation
│       ├── ytdl/
│       │   ├── index.html
│       │   └── script.js
│       ├── pdf_editor/
│       │   ├── index.html
│       │   └── script.js
│       ├── # ... other tool-specific frontend files
│       └── assets/           # Images, fonts
│   ├── templates/          # Jinja2 templates (if server-rendering some HTML)
│       └── # ...
├── logs/                   # Log files (e.g., nexuskit.log) - ensure .gitignore
├── tmp_processing_dir_config/ # May not be needed if path is hardcoded or env var
├── requirements.txt
└── run.py                  # Simple script to start Uvicorn (optional)
```

### 5.3. API Design Principles

  * **RESTful:** Use HTTP methods appropriately (GET, POST, etc.).
  * **Clear URL Paths:** e.g., `/api/v1/ytdl/fetch-info`, `/api/v1/ytdl/download-request`, `/api/v1/pdf/upload`, `/api/v1/tasks/{task_id}/status`.
  * **JSON for Request/Response:** Use JSON for data exchange. Pydantic models in FastAPI will handle validation and serialization.
  * **Stateless:** APIs will be stateless, aligning with the disposable session model. Each request should contain all necessary information.
  * **Task IDs:** For long-running operations, an initial request might return a `task_id`. Subsequent polling requests will use this `task_id` to get status/results.

### 5.4. Task Management

  * **BackgroundTasks:** FastAPI's `BackgroundTasks` will be used for offloading long-running operations (downloads, conversions, complex processing) from the main request-response cycle.
      * Example: When a user requests a video download, the API endpoint will validate the request, schedule a background task to perform the download using `yt-dlp`, and immediately return a `task_id` to the client.
  * **Polling for Progress:**
      * The client will use the `task_id` to periodically poll a status endpoint (e.g., `/api/v1/tasks/{task_id}/status`).
      * This status endpoint will query the state of the background task. The state can be stored in a simple in-memory dictionary (keyed by `task_id`) or a more robust temporary store if needed (though for 2-5 users, in-memory might suffice initially, being mindful of persistence if Uvicorn workers restart).
      * The status response can include: `status` (e.g., "pending", "processing", "completed", "failed"), `progress_percent`, `message`, and `download_url` (if completed).
      * The background task itself will need to update its progress in this shared state.

### 5.5. File Management

  * **Temporary Storage Path:** `/var/tmp/nexuskit_data/` (ensure this directory exists and the application has write permissions).
  * **Unique Task Directories:**
      * Upon initiating any operation involving files, a UUID will be generated (e.g., `task_uuid`).
      * All temporary files for this task (uploads, intermediates, outputs) will be stored in `/var/tmp/nexuskit_data/{task_uuid}/`.
  * **File Uploads:** Handled by FastAPI using `UploadFile`. Max file sizes will be configurable (e.g., in `app/core/config.py`) and checked.
  * **File Downloads:** FastAPI's `FileResponse` or `StreamingResponse` for serving processed files.
  * **Cleanup Strategy (Hybrid Approach):**
    1.  **Grace Period Deletion (BackgroundTasks):**
          * After a task successfully completes and the result is made available (or if a task fails), a follow-up background task will be scheduled to delete the entire `/var/tmp/nexuskit_data/{task_uuid}/` directory.
          * This deletion will occur after a **1-hour** grace period (configurable) to allow users time to download.
    2.  **Periodic Scheduled Sweeper (Cron Job):**
          * A system `cron` job will run a Python script **once a day** (configurable).
          * This script will scan `/var/tmp/nexuskit_data/` and delete any subdirectory `{task_uuid}` older than **24 hours** (configurable). This acts as a fallback for orphaned files.
          * The script can check directory modification times or a timestamp file within each task directory.

### 5.6. Error Handling and Logging

  * **Custom Exception Handlers:** FastAPI allows defining custom exception handlers to return structured JSON error responses.
  * **Error Responses:** Will include a user-friendly `message` and potentially an `error_code` or `error_id`.
  * **Logging:**
      * Use Python's built-in `logging` module.
      * Log to both **console** (standard output) and a **log file** (e.g., `logs/nexuskit.log` or `/var/log/nexuskit.log`).
      * Log format: Timestamp, Log Level (INFO, WARNING, ERROR, DEBUG), Module Name, Message.
      * Include Python stack traces for unhandled exceptions.
      * Log relevant output/errors from CLI tools (`yt-dlp`, `ffmpeg`).
      * Generate a unique `error_id` for critical errors, which can be shown to the user for reporting.

-----

## 6\. Frontend Design

### 6.1. Technology Stack

  * **HTML:** Semantic HTML5.
  * **CSS:** Bootstrap 5 (via CDN or local files) for core layout and components, plus `style.css` for custom styling to achieve a clean, modern look.
  * **JavaScript:** Vanilla JavaScript (ES6+) for DOM manipulation, event handling, API calls (`fetch`), and managing UI state for each tool.

### 6.2. Proposed Directory Structure (Static Assets)

Located under `app/static/`:

  * `index.html`: Main dashboard/homepage.
  * `css/style.css`: Custom global styles.
  * `js/main.js`: Global JavaScript (e.g., for dashboard navigation logic).
  * `assets/`: For images, custom fonts, etc.
  * Each tool will have its own subdirectory (e.g., `app/static/ytdl/`, `app/static/pdf_editor/`) containing:
      * `index.html`: The main HTML page for the tool.
      * `script.js`: JavaScript specific to that tool's functionality.
      * `style.css` (optional): CSS specific to that tool.

### 6.3. Page Structure and Navigation

  * **Dashboard/Homepage (`/` or `index.html`):**
      * Displays a welcome message and cards/links to access each available tool.
      * No persistent global navigation bar across all pages. Users return to the dashboard to switch tools.
  * **Tool Pages (e.g., `/ytdl`, `/pdf-editor`):**
      * Each tool operates on its own distinct URL, serving its specific `index.html`.
      * A link/button to return to the main dashboard might be present.

### 6.4. UI Components and Styling

  * **Bootstrap:** Used for grid system, responsive layout, buttons, forms, modals, navs (if any), cards, progress bars (for polling display), toasts.
  * **Custom CSS:** To override Bootstrap defaults where necessary and apply a unique visual theme (clean, modern, intuitive).
  * **Common Elements:** Consistent header/footer style (if any on tool pages), consistent button styling, clear visual hierarchy.

### 6.5. Client-side Logic

  * **`fetch` API:** Used for all communication with the backend REST API.
  * **Event Handling:** Attach event listeners to forms, buttons, inputs.
  * **DOM Manipulation:** Update the page dynamically to show previews, results, error messages, progress.
  * **Polling Implementation:**
      * After initiating a long-running task and receiving a `task_id`, the tool's `script.js` will use `setInterval` or `setTimeout` recursively to call the backend status endpoint (e.g., `/api/v1/tasks/{task_id}/status`).
      * Update a progress bar or status message based on the response.
      * Once the task is "completed", display the download link or result.
      * If "failed", display the error message.
      * Stop polling when the task is completed or failed.
  * **Form Handling:** Prevent default form submission and handle data via JavaScript and `fetch`.

### 6.6. Responsiveness

  * The UI must be fully responsive and usable on desktops, tablets, and mobile phones.
  * Leverage Bootstrap's responsive grid and components.
  * Test on various screen sizes during development.

-----

## 7\. Deployment and Infrastructure

### 7.1. Server Setup

  * The application will be hosted on a single physical machine (user's own server).
  * Operating System: A Linux distribution is typical (e.g., Ubuntu, Debian, CentOS).

### 7.2. Nginx Configuration

  * Nginx will be installed and configured as a reverse proxy.
  * **Example Nginx Site Configuration (`/etc/nginx/sites-available/nexuskit`):**
    ```nginx
    server {
        listen 80;
        listen 443 ssl; # Listen for HTTPS
        server_name your_domain.com; # Or IP address

        # SSL Configuration (Self-Signed)
        ssl_certificate /etc/nginx/ssl/nexuskit.crt; # Path to your self-signed certificate
        ssl_certificate_key /etc/nginx/ssl/nexuskit.key; # Path to your private key

        # Security Headers (Recommended)
        add_header X-Content-Type-Options "nosniff" always;
        add_header X-Frame-Options "SAMEORIGIN" always;
        # add_header Content-Security-Policy "default-src 'self'; script-src 'self'; style-src 'self' [https://cdn.jsdelivr.net](https://cdn.jsdelivr.net); img-src 'self' data:; font-src 'self' [https://cdn.jsdelivr.net](https://cdn.jsdelivr.net);"; # Example CSP, adjust as needed

        location / {
            root /path/to/nexuskit/app/static; # Serve main dashboard and other root static files
            try_files $uri $uri/ /index.html; # For dashboard page
        }

        # Location for tool-specific static assets (HTML, JS, CSS)
        # Assumes each tool has its own HTML file like /ytdl/, /pdf-editor/
        location ~ ^/(ytdl|pdf-editor|ffmpeg-converter|image-editor)/ {
            alias /path/to/nexuskit/app/static/$1/; # $1 captures the tool name
            try_files $uri $uri/ /index.html; # Serves the index.html of the specific tool
        }
        
        # Location for other static assets like CSS, JS if not caught by tool-specific locations
        location ~ ^/(css|js|assets)/ {
            root /path/to/nexuskit/app/static;
            try_files $uri =404;
        }

        location /api {
            proxy_pass [http://127.0.0.1:8000](http://127.0.0.1:8000); # Assuming Uvicorn runs on port 8000
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }

        # Optional: Error pages
        # error_page 500 502 503 504 /50x.html;
        # location = /50x.html {
        #     root /usr/share/nginx/html; # Or your custom error page location
        # }
    }
    ```
      * The `/path/to/nexuskit/app/static/` should be updated to the actual deployment path.
      * The `server_name` should be adjusted.

### 7.3. FastAPI/Uvicorn Execution

  * The FastAPI application will be run using Uvicorn.
  * For V1, this can be done directly from the command line from the root `nexuskit` directory:
    ```bash
    uvicorn app.main:app --host 127.0.0.1 --port 8000
    ```
    (Nginx will proxy to this).
  * For more robust deployment later, consider using a process manager like `systemd` or `supervisor` to manage the Uvicorn process.

### 7.4. SSL Certificate

  * A **self-signed SSL certificate** will be used for HTTPS, as this is for internal/friends usage.
  * Tools like OpenSSL can be used to generate the certificate and key.
    ```bash
    # Example commands to generate a self-signed certificate
    # openssl req -x509 -nodes -days 365 -newkey rsa:2048 -keyout /etc/nginx/ssl/nexuskit.key -out /etc/nginx/ssl/nexuskit.crt
    ```
    (Ensure the SSL directory is created and Nginx has permission to read these files).

-----

## 8\. Security Considerations

### 8.1. Input Sanitization (CRITICAL)

  * All user-provided input, especially URLs (for yt-dlp) and any parameters that might be part of shell commands (for ffmpeg), **must be rigorously validated and sanitized** on the backend before being used.
  * Use Python's `shlex.quote()` for any part of a user-supplied string that will be passed as an argument in a shell command.
  * Avoid constructing shell commands by simple string concatenation with raw user input.
  * Validate file types and content where possible.

### 8.2. File Uploads

  * **Configurable Size Limits:** Implement checks in FastAPI for maximum allowed file sizes for uploads. These limits should be configurable per tool (e.g., smaller for PDFs, larger for videos).
  * **Temporary Storage:** Files are stored in isolated, UUID-named directories and cleaned up. This limits exposure.
  * **Permissions:** Ensure the temporary file storage directory (`/var/tmp/nexuskit_data/`) has appropriate permissions (writable by the application user, not world-writable).

### 8.3. Dependency Management

  * **`requirements.txt`:** Keep this file updated.
  * **GitHub CI/CD and Dependabot:** If the project is hosted on GitHub, use its CI/CD features for automated checks and Dependabot to get alerts and PRs for outdated/vulnerable dependencies.
  * Regularly update system packages like `ffmpeg` and `yt-dlp` (the CLI tools themselves if installed system-wide, or the Python package for `yt-dlp`).

### 8.4. Nginx Hardening

  * Use the security headers mentioned in the Nginx configuration section (X-Content-Type-Options, X-Frame-Options, CSP).
  * Keep Nginx updated.
  * Disable unused Nginx modules.

### 8.5. General Backend Security

  * Do not expose sensitive information in error messages to the client (use generic messages and log details on the server).
  * Be mindful of resource exhaustion (CPU/memory) from long-running tasks; `BackgroundTasks` helps but ensure processes are killed if they hang or exceed reasonable limits (more advanced for V1).

-----

## 9\. Extensibility

The architecture should facilitate adding new tools in the future:

  * **Backend (FastAPI):**
      * **Modular Routers:** Create a new `router_newtool.py` in `app/apis/` for the new tool's API endpoints.
      * **Service Layer:** Add a corresponding `service_newtool.py` in `app/services/` for its business logic.
      * **Pydantic Models:** Define request/response models in `app/models/`.
      * Register the new router in `app/main.py`.
  * **Frontend (Vanilla JS/HTML):**
      * Create a new directory under `app/static/` (e.g., `app/static/newtool/`) with its `index.html` and `script.js`.
      * Add a card/link to the new tool on the main dashboard page (`app/static/index.html` and its corresponding JS).
  * **Configuration:** New tool-specific configurations can be added to `app/core/config.py`.
  * This approach keeps each tool's code relatively isolated.

-----

## 10\. Error Reporting (to Admin)

When a backend error occurs that cannot be resolved by the user:

1.  **Unique Error ID:** The backend logging mechanism will generate a unique ID (e.g., UUID) for each significant logged error (especially for 500-level errors).
2.  **Frontend Display:** The frontend, upon receiving a server error (or a specific error response indicating a severe issue), will display a user-friendly message like: "An unexpected error occurred. Please contact the administrator with the following Error ID: [UNIQUE\_ERROR\_ID]."
3.  **Admin Debugging:** The user (admin) can then use this Error ID to quickly find the detailed log entry (including stack trace and context) in the server logs (`logs/nexuskit.log`).
4.  No automated reporting system is planned for V1; users will communicate this ID manually (e.g., via chat).

-----

## 11\. Future Considerations / Potential Enhancements (Beyond V1)

  * **User Accounts:** If more granular control or persistent data per user is ever needed.
  * **Advanced Task Queue:** Replace `BackgroundTasks` with Celery and a message broker (Redis/RabbitMQ) for more robust, scalable, and persistent task management (retries, scheduled tasks).
  * **Real-time Progress:** Implement Server-Sent Events (SSE) instead of polling for smoother real-time progress updates.
  * **WebSockets:** For more complex interactive tools requiring bidirectional communication.
  * **More Tools:**
      * JSON/YAML Formatter/Validator
      * Markdown Editor with Live Preview
      * Temporary Email Address Generator
      * File Sharing Module
      * More advanced PDF features (OCR, compression, merging multiple PDFs).
      * More advanced image editing (more filters, text overlay, AI features if feasible).
  * **Internationalization (i18n):** Support for multiple languages.
  * **Themes:** Light/Dark mode toggle.
  * **Process Management for Uvicorn:** Use `systemd` or `supervisor` for running Uvicorn in production.
  * **Automated SSL with Let's Encrypt:** If the server becomes internet-accessible with a proper domain.
  * **Rate Limiting:** If usage grows or any tool is prone to abuse.

<!-- end list -->