function pdfEditor() {
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

    const mergePdfUpload = document.getElementById('merge-pdf-upload');
    const mergeFileList = document.getElementById('merge-file-list');
    const mergePdfsBtn = document.getElementById('merge-pdfs-btn');
    const mergeStatusMessages = document.getElementById('merge-status-messages');

    const compressPdfUpload = document.getElementById('compress-pdf-upload');
    const compressionLevel = document.getElementById('compression-level');
    const compressPdfBtn = document.getElementById('compress-pdf-btn');
    const compressStatusMessages = document.getElementById('compress-status-messages');

    let taskId = null;
    let draggedItem = null;
    let isDrawing = false;
    let lastX = 0;
    let lastY = 0;
    let currentSignatureDataUrl = null;
    let filesToMerge = [];
    let fileToCompress = null;

    // Signature drawing logic
    // ... (signature logic remains the same)

    pdfUpload.addEventListener('change', async (event) => {
        // ... (existing single PDF upload logic remains the same)
    });

    addBlankPageBtn.addEventListener('click', async () => {
        // ... (existing add blank page logic remains the same)
    });

    deletePagesBtn.addEventListener('click', async () => {
        // ... (existing delete pages logic remains the same)
    });

    reorderPagesBtn.addEventListener('click', async () => {
        // ... (existing reorder pages logic remains the same)
    });

    downloadBtn.addEventListener('click', () => {
        if (taskId) {
            window.location.href = `/api/v1/pdf/${taskId}/download`;
        }
    });

    async function applySignatureToPage(pageIndex, signatureDataUrl) {
        // ... (existing signature application logic remains the same)
    }

    // Merge PDFs logic
    // ... (merge logic remains the same)

    // Compress PDF logic
    compressPdfUpload.addEventListener('change', (event) => {
        fileToCompress = event.target.files[0];
    });

    compressPdfBtn.addEventListener('click', async () => {
        if (!fileToCompress) {
            compressStatusMessages.innerHTML = '<div class="alert alert-warning">Please select a PDF to compress.</div>';
            return;
        }

        compressStatusMessages.innerHTML = '<div class="alert alert-info">Compressing PDF...</div>';

        const formData = new FormData();
        formData.append('file', fileToCompress);
        formData.append('level', compressionLevel.value);

        try {
            const response = await fetch('/api/pdf/compress', {
                method: 'POST',
                body: formData
            });

            if (response.ok) {
                const blob = await response.blob();
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.style.display = 'none';
                a.href = url;
                a.download = 'compressed.pdf';
                document.body.appendChild(a);
                a.click();
                window.URL.revokeObjectURL(url);
                compressStatusMessages.innerHTML = '<div class="alert alert-success">PDF compressed successfully.</div>';
            } else {
                const error = await response.json();
                compressStatusMessages.innerHTML = `<div class="alert alert-danger">${error.detail}</div>`;
            }
        } catch (error) {
            compressStatusMessages.innerHTML = `<div class="alert alert-danger">An error occurred while compressing the PDF.</div>`;
        }
    });
}
