document.addEventListener('DOMContentLoaded', () => {
    const pdfUpload = document.getElementById('pdf-upload');
    const pdfViewer = document.getElementById('pdf-viewer');
    const thumbnailsDiv = document.getElementById('thumbnails');
    const pageView = document.getElementById('page-view');
    const addBlankPageBtn = document.getElementById('add-blank-page-btn');
    const deletePagesBtn = document.getElementById('delete-pages-btn');
    const reorderPagesBtn = document.getElementById('reorder-pages-btn');
    const addSignatureBtn = document.getElementById('add-signature-btn');
    const downloadBtn = document.getElementById('download-btn');
    const statusMessages = document.getElementById('status-messages');

    const signatureCanvas = document.getElementById('signature-canvas');
    const signatureCtx = signatureCanvas.getContext('2d');
    const clearSignatureBtn = document.getElementById('clear-signature-btn');
    const signatureUpload = document.getElementById('signature-upload');
    const uploadedSignaturePreview = document.getElementById('uploaded-signature-preview');
    const saveSignatureBtn = document.getElementById('save-signature-btn');

    let taskId = null;
    let draggedItem = null;
    let isDrawing = false;
    let lastX = 0;
    let lastY = 0;
    let currentSignatureDataUrl = null; // To store the signature data URL

    // Signature drawing logic
    signatureCtx.lineWidth = 2;
    signatureCtx.lineCap = 'round';
    signatureCtx.strokeStyle = 'black';

    signatureCanvas.addEventListener('mousedown', (e) => {
        isDrawing = true;
        [lastX, lastY] = [e.offsetX, e.offsetY];
    });

    signatureCanvas.addEventListener('mousemove', (e) => {
        if (!isDrawing) return;
        signatureCtx.beginPath();
        signatureCtx.moveTo(lastX, lastY);
        signatureCtx.lineTo(e.offsetX, e.offsetY);
        signatureCtx.stroke();
        [lastX, lastY] = [e.offsetX, e.offsetY];
    });

    signatureCanvas.addEventListener('mouseup', () => isDrawing = false);
    signatureCanvas.addEventListener('mouseout', () => isDrawing = false);

    clearSignatureBtn.addEventListener('click', () => {
        signatureCtx.clearRect(0, 0, signatureCanvas.width, signatureCanvas.height);
    });

    signatureUpload.addEventListener('change', (event) => {
        const file = event.target.files[0];
        if (file) {
            const reader = new FileReader();
            reader.onload = (e) => {
                uploadedSignaturePreview.src = e.target.result;
                uploadedSignaturePreview.style.display = 'block';
            };
            reader.readAsDataURL(file);
        }
    });

    saveSignatureBtn.addEventListener('click', () => {
        const activeTab = document.querySelector('#signatureTab .nav-link.active').id;

        if (activeTab === 'draw-tab') {
            currentSignatureDataUrl = signatureCanvas.toDataURL();
        } else if (activeTab === 'upload-tab') {
            currentSignatureDataUrl = uploadedSignaturePreview.src;
        }

        if (!currentSignatureDataUrl || currentSignatureDataUrl === uploadedSignaturePreview.src && !uploadedSignaturePreview.src) {
            statusMessages.innerHTML = '<div class="alert alert-danger">No signature to save.</div>';
            return;
        }

        const signatureModal = bootstrap.Modal.getInstance(document.getElementById('signatureModal'));
        signatureModal.hide();
        statusMessages.innerHTML = '<div class="alert alert-success">Signature saved. Click on a page thumbnail to add it.</div>';
    });

    pdfUpload.addEventListener('change', async (event) => {
        const file = event.target.files[0];
        if (!file) {
            return;
        }

        statusMessages.innerHTML = '<div class="alert alert-info">Uploading and processing PDF...</div>';

        const formData = new FormData();
        formData.append('file', file);

        try {
            const response = await fetch('/api/v1/pdf/upload', {
                method: 'POST',
                body: formData
            });

            if (!response.ok) {
                throw new Error('Failed to upload PDF.');
            }

            const data = await response.json();
            taskId = data.task_id;

            thumbnailsDiv.innerHTML = '';
            data.pages.forEach((pageUrl, index) => {
                const div = document.createElement('div');
                div.classList.add('list-group-item');
                div.setAttribute('draggable', true);
                div.dataset.pageIndex = index; // Store original index

                const checkbox = document.createElement('input');
                checkbox.type = 'checkbox';
                checkbox.classList.add('form-check-input', 'me-2');
                checkbox.dataset.pageIndex = index;
                div.appendChild(checkbox);

                const img = document.createElement('img');
                img.src = pageUrl;
                img.classList.add('img-fluid');
                img.addEventListener('click', () => {
                    pageView.src = pageUrl;
                    // If a signature is ready, apply it to this page
                    if (currentSignatureDataUrl) {
                        applySignatureToPage(index, currentSignatureDataUrl);
                        currentSignatureDataUrl = null; // Clear after applying
                    }
                });
                div.appendChild(img);

                // Drag and drop event listeners
                div.addEventListener('dragstart', (e) => {
                    draggedItem = div;
                    setTimeout(() => {
                        div.classList.add('dragging');
                    }, 0);
                });

                div.addEventListener('dragend', () => {
                    draggedItem.classList.remove('dragging');
                    draggedItem = null;
                });

                div.addEventListener('dragover', (e) => {
                    e.preventDefault();
                    const bounding = div.getBoundingClientRect();
                    const offset = bounding.y + (bounding.height / 2);
                    if (e.clientY - offset > 0) {
                        div.style.borderBottom = '2px solid blue';
                        div.style.borderTop = '';
                    } else {
                        div.style.borderTop = '2px solid blue';
                        div.style.borderBottom = '';
                    }
                });

                div.addEventListener('dragleave', () => {
                    div.style.borderBottom = '';
                    div.style.borderTop = '';
                });

                div.addEventListener('drop', (e) => {
                    e.preventDefault();
                    div.style.borderBottom = '';
                    div.style.borderTop = '';

                    if (draggedItem && draggedItem !== div) {
                        const allItems = Array.from(thumbnailsDiv.children);
                        const draggedIndex = allItems.indexOf(draggedItem);
                        const targetIndex = allItems.indexOf(div);

                        if (draggedIndex < targetIndex) {
                            thumbnailsDiv.insertBefore(draggedItem, div.nextSibling);
                        } else {
                            thumbnailsDiv.insertBefore(draggedItem, div);
                        }
                    }
                });

                thumbnailsDiv.appendChild(div);
            });

            if (data.pages.length > 0) {
                pageView.src = data.pages[0];
            }

            pdfViewer.style.display = 'block';
            statusMessages.innerHTML = '';

        } catch (error) { 
            statusMessages.innerHTML = `<div class="alert alert-danger">${error.message}</div>`;
        }
    });

    addBlankPageBtn.addEventListener('click', async () => {
        if (!taskId) return;

        statusMessages.innerHTML = '<div class="alert alert-info">Adding blank page...</div>';

        try {
            const response = await fetch(`/api/v1/pdf/${taskId}/add-blank-page`, {
                method: 'POST'
            });

            if (!response.ok) {
                throw new Error('Failed to add blank page.');
            }

            const data = await response.json();
            // Refresh the view
            pdfUpload.dispatchEvent(new Event('change'));

        } catch (error) {
            statusMessages.innerHTML = `<div class="alert alert-danger">${error.message}</div>`;
        }
    });

    deletePagesBtn.addEventListener('click', async () => {
        const selectedPages = Array.from(thumbnailsDiv.querySelectorAll('input[type=checkbox]:checked')).map(cb => parseInt(cb.dataset.pageIndex));

        if (selectedPages.length === 0) {
            statusMessages.innerHTML = '<div class="alert alert-warning">Please select pages to delete.</div>';
            return;
        }

        statusMessages.innerHTML = '<div class="alert alert-info">Deleting pages...</div>';

        try {
            const response = await fetch(`/api/v1/pdf/${taskId}/delete-pages`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ pages: selectedPages })
            });

            if (!response.ok) {
                throw new Error('Failed to delete pages.');
            }

            const data = await response.json();
            // Refresh the view
            pdfUpload.dispatchEvent(new Event('change'));

        } catch (error) {
            statusMessages.innerHTML = `<div class="alert alert-danger">${error.message}</div>`;
        }
    });

    reorderPagesBtn.addEventListener('click', async () => {
        if (!taskId) return;

        const newOrder = Array.from(thumbnailsDiv.children).map(item => parseInt(item.dataset.pageIndex));

        statusMessages.innerHTML = '<div class="alert alert-info">Reordering pages...</div>';

        try {
            const response = await fetch(`/api/v1/pdf/${taskId}/reorder-pages`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ page_order: newOrder })
            });

            if (!response.ok) {
                throw new Error('Failed to reorder pages.');
            }

            const data = await response.json();
            // Refresh the view
            pdfUpload.dispatchEvent(new Event('change'));

        } catch (error) {
            statusMessages.innerHTML = `<div class="alert alert-danger">${error.message}</div>`;
        }
    });

    downloadBtn.addEventListener('click', () => {
        if (taskId) {
            window.location.href = `/api/v1/pdf/${taskId}/download`;
        }
    });

    async function applySignatureToPage(pageIndex, signatureDataUrl) {
        if (!taskId) return;

        statusMessages.innerHTML = '<div class="alert alert-info">Adding signature...</div>';

        // For MVP, we'll use fixed coordinates and width. 
        // In a real app, this would come from user interaction (drag/resize).
        const x = 50; 
        const y = 50; 
        const width = 150; 

        try {
            const response = await fetch(`/api/v1/pdf/${taskId}/add-signature`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    page_index: pageIndex,
                    x: x,
                    y: y,
                    width: width,
                    signature_data_url: signatureDataUrl
                })
            });

            if (!response.ok) {
                throw new Error('Failed to add signature.');
            }

            const data = await response.json();
            // Refresh the view
            pdfUpload.dispatchEvent(new Event('change'));

        } catch (error) {
            statusMessages.innerHTML = `<div class="alert alert-danger">${error.message}</div>`;
        }
    }
});

