document.addEventListener('DOMContentLoaded', () => {
    const imageUpload = document.getElementById('image-upload');
    const imageEditorArea = document.getElementById('image-editor-area');
    const mainImage = document.getElementById('main-image');
    const statusMessages = document.getElementById('status-messages');
    const downloadImageBtn = document.getElementById('download-image-btn');
    const resetBtn = document.getElementById('reset-btn');

    const cropToolBtn = document.getElementById('crop-tool-btn');
    const cropOverlay = document.getElementById('crop-overlay');
    const resizeToolBtn = document.getElementById('resize-tool-btn');
    const resizeModal = new bootstrap.Modal(document.getElementById('resizeModal'));
    const resizeWidthInput = document.getElementById('resize-width');
    const resizeHeightInput = document.getElementById('resize-height');
    const maintainAspectRatioCheckbox = document.getElementById('maintain-aspect-ratio');
    const applyResizeBtn = document.getElementById('apply-resize-btn');

    const filterModal = new bootstrap.Modal(document.getElementById('filterModal'));
    const filterSlider = document.getElementById('filter-slider');
    const filterLabel = document.getElementById('filter-label');
    const applyFilterBtn = document.getElementById('apply-filter-btn');

    let currentTaskId = null;
    let currentImageUrl = null;
    let isCropping = false;
    let cropStartX, cropStartY;
    let cropOverlayRect = { x: 0, y: 0, width: 0, height: 0 };

    const tools = {
        'grayscale': document.getElementById('grayscale-btn'),
        'sepia': document.getElementById('sepia-btn'),
        'invert': document.getElementById('invert-btn'),
        'brightness': document.getElementById('brightness-btn'),
        'contrast': document.getElementById('contrast-btn'),
        'blur': document.getElementById('blur-btn'),
        'rotate_90_left': document.getElementById('rotate-left-btn'),
        'rotate_90_right': document.getElementById('rotate-right-btn'),
        'rotate_180': document.getElementById('rotate-180-btn'),
        'flip_horizontal': document.getElementById('flip-horizontal-btn'),
        'flip_vertical': document.getElementById('flip-vertical-btn'),
        'remove_white_background': document.getElementById('remove-white-bg-btn'),
        'remove_black_background': document.getElementById('remove-black-bg-btn'),
    };

    imageUpload.addEventListener('change', async (event) => {
        const file = event.target.files[0];
        if (!file) {
            return;
        }

        statusMessages.innerHTML = '<div class="alert alert-info">Uploading image...</div>';
        imageEditorArea.style.display = 'none';

        const formData = new FormData();
        formData.append('file', file);

        try {
            const response = await fetch('/api/v1/image/upload', {
                method: 'POST',
                body: formData
            });

            if (!response.ok) {
                throw new Error('Failed to upload image.');
            }

            const data = await response.json();
            currentTaskId = data.task_id;
            currentImageUrl = data.image_url;
            mainImage.src = currentImageUrl;
            imageEditorArea.style.display = 'block';
            statusMessages.innerHTML = '';

        } catch (error) {
            statusMessages.innerHTML = `<div class="alert alert-danger">${error.message}</div>`;
        }
    });

    async function applyEdit(action, params = {}) {
        if (!currentTaskId) {
            statusMessages.innerHTML = '<div class="alert alert-danger">Please upload an image first.</div>';
            return;
        }

        statusMessages.innerHTML = `<div class="alert alert-info">Applying ${action}...</div>`;

        try {
            const response = await fetch('/api/v1/image/edit', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    task_id: currentTaskId,
                    action: action,
                    params: params
                })
            });

            if (!response.ok) {
                throw new Error(`Failed to apply ${action}.`);
            }

            const data = await response.json();
            currentImageUrl = data.image_url;
            mainImage.src = currentImageUrl + '?t=' + new Date().getTime(); // Bust cache
            statusMessages.innerHTML = '<div class="alert alert-success">Edit applied successfully.</div>';

        } catch (error) {
            statusMessages.innerHTML = `<div class="alert alert-danger">${error.message}</div>`;
        }
    }

    // Crop Tool
    cropToolBtn.addEventListener('click', () => {
        isCropping = true;
        cropOverlay.style.display = 'block';
        cropOverlay.style.left = '0px';
        cropOverlay.style.top = '0px';
        cropOverlay.style.width = mainImage.clientWidth + 'px';
        cropOverlay.style.height = mainImage.clientHeight + 'px';
        cropOverlayRect = { x: 0, y: 0, width: mainImage.clientWidth, height: mainImage.clientHeight };
        statusMessages.innerHTML = '<div class="alert alert-info">Drag to select crop area, then click Crop again to apply.</div>';
    });

    let isResizing = false;
    let isDragging = false;
    let activeResizer = null;

    cropOverlay.addEventListener('mousedown', (e) => {
        if (e.target.classList.contains('resizer')) {
            isResizing = true;
            activeResizer = e.target;
        } else {
            isDragging = true;
            cropStartX = e.clientX - cropOverlay.getBoundingClientRect().left;
            cropStartY = e.clientY - cropOverlay.getBoundingClientRect().top;
        }
    });

    document.addEventListener('mousemove', (e) => {
        if (!isCropping) return;

        if (isResizing) {
            const rect = mainImage.getBoundingClientRect();
            let newX = cropOverlay.offsetLeft;
            let newY = cropOverlay.offsetTop;
            let newWidth = cropOverlay.offsetWidth;
            let newHeight = cropOverlay.offsetHeight;

            if (activeResizer.classList.contains('nw')) {
                newX = e.clientX - rect.left;
                newY = e.clientY - rect.top;
                newWidth = cropOverlayRect.x + cropOverlayRect.width - newX;
                newHeight = cropOverlayRect.y + cropOverlayRect.height - newY;
            } else if (activeResizer.classList.contains('ne')) {
                newY = e.clientY - rect.top;
                newWidth = e.clientX - rect.left - cropOverlay.offsetLeft;
                newHeight = cropOverlayRect.y + cropOverlayRect.height - newY;
            } else if (activeResizer.classList.contains('sw')) {
                newX = e.clientX - rect.left;
                newWidth = cropOverlayRect.x + cropOverlayRect.width - newX;
                newHeight = e.clientY - rect.top - cropOverlay.offsetTop;
            } else if (activeResizer.classList.contains('se')) {
                newWidth = e.clientX - rect.left - cropOverlay.offsetLeft;
                newHeight = e.clientY - rect.top - cropOverlay.offsetTop;
            }

            cropOverlay.style.left = `${Math.max(0, newX)}px`;
            cropOverlay.style.top = `${Math.max(0, newY)}px`;
            cropOverlay.style.width = `${Math.max(0, newWidth)}px`;
            cropOverlay.style.height = `${Math.max(0, newHeight)}px`;

        } else if (isDragging) {
            const newX = e.clientX - mainImage.getBoundingClientRect().left - cropStartX;
            const newY = e.clientY - mainImage.getBoundingClientRect().top - cropStartY;

            cropOverlay.style.left = `${Math.max(0, Math.min(newX, mainImage.clientWidth - cropOverlay.offsetWidth))}px`;
            cropOverlay.style.top = `${Math.max(0, Math.min(newY, mainImage.clientHeight - cropOverlay.offsetHeight))}px`;
        }
    });

    document.addEventListener('mouseup', () => {
        if (isResizing || isDragging) {
            isResizing = false;
            isDragging = false;
            activeResizer = null;
            const rect = cropOverlay.getBoundingClientRect();
            const imgRect = mainImage.getBoundingClientRect();
            cropOverlayRect = {
                x: rect.left - imgRect.left,
                y: rect.top - imgRect.top,
                width: rect.width,
                height: rect.height
            };
        }
    });

    cropToolBtn.addEventListener('click', async () => {
        if (isCropping) {
            isCropping = false;
            cropOverlay.style.display = 'none';

            const imgWidth = mainImage.naturalWidth;
            const imgHeight = mainImage.naturalHeight;
            const displayWidth = mainImage.clientWidth;
            const displayHeight = mainImage.clientHeight;

            const scaleX = imgWidth / displayWidth;
            const scaleY = imgHeight / displayHeight;

            const cropParams = {
                left: Math.round(cropOverlayRect.x * scaleX),
                top: Math.round(cropOverlayRect.y * scaleY),
                right: Math.round((cropOverlayRect.x + cropOverlayRect.width) * scaleX),
                bottom: Math.round((cropOverlayRect.y + cropOverlayRect.height) * scaleY)
            };
            await applyEdit('crop', cropParams);
        }
    });

    // Resize Tool
    resizeToolBtn.addEventListener('click', () => {
        resizeWidthInput.value = mainImage.naturalWidth;
        resizeHeightInput.value = mainImage.naturalHeight;
        resizeModal.show();
    });

    maintainAspectRatioCheckbox.addEventListener('change', () => {
        if (maintainAspectRatioCheckbox.checked) {
            const aspectRatio = mainImage.naturalWidth / mainImage.naturalHeight;
            resizeHeightInput.value = Math.round(resizeWidthInput.value / aspectRatio);
        }
    });

    resizeWidthInput.addEventListener('input', () => {
        if (maintainAspectRatioCheckbox.checked) {
            const aspectRatio = mainImage.naturalWidth / mainImage.naturalHeight;
            resizeHeightInput.value = Math.round(resizeWidthInput.value / aspectRatio);
        }
    });

    resizeHeightInput.addEventListener('input', () => {
        if (maintainAspectRatioCheckbox.checked) {
            const aspectRatio = mainImage.naturalWidth / mainImage.naturalHeight;
            resizeWidthInput.value = Math.round(resizeHeightInput.value * aspectRatio);
        }
    });

    applyResizeBtn.addEventListener('click', async () => {
        const width = parseInt(resizeWidthInput.value);
        const height = parseInt(resizeHeightInput.value);
        if (isNaN(width) || isNaN(height) || width <= 0 || height <= 0) {
            statusMessages.innerHTML = '<div class="alert alert-danger">Please enter valid width and height.</div>';
            return;
        }
        await applyEdit('resize', { width, height });
        resizeModal.hide();
    });

    // Filters and other direct actions
    for (const action in tools) {
        if (tools[action]) {
            tools[action].addEventListener('click', async () => {
                if (action === 'brightness' || action === 'contrast' || action === 'blur') {
                    filterLabel.textContent = action.charAt(0).toUpperCase() + action.slice(1);
                    filterSlider.min = (action === 'blur') ? 0 : 0;
                    filterSlider.max = (action === 'blur') ? 10 : 200; // Max blur radius 10, max brightness/contrast 2.0 (200%)
                    filterSlider.value = (action === 'blur') ? 0 : 100; // Default 0 blur, 1.0 brightness/contrast
                    filterSlider.dataset.action = action;
                    filterModal.show();
                } else {
                    await applyEdit(action);
                }
            });
        }
    }

    applyFilterBtn.addEventListener('click', async () => {
        const action = filterSlider.dataset.action;
        let value = parseFloat(filterSlider.value);
        if (action === 'brightness' || action === 'contrast') {
            value /= 100; // Convert 0-200 to 0.0-2.0
        }
        await applyEdit(action, { factor: value, radius: value }); // Use appropriate param name
        filterModal.hide();
    });

    resetBtn.addEventListener('click', async () => {
        await applyEdit('reset');
    });

    downloadImageBtn.addEventListener('click', () => {
        if (currentImageUrl) {
            const link = document.createElement('a');
            link.href = currentImageUrl;
            link.download = 'edited_image.png'; // Or derive from original filename
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
        }
    });
});