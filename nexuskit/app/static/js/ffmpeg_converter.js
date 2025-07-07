
function ffmpegConverter() {
    const mediaUpload = document.getElementById('media-upload');
    const conversionOptionsDiv = document.getElementById('conversion-options');
    const outputCategorySelect = document.getElementById('output-category');
    const outputFormatSelect = document.getElementById('output-format');
    const videoOptionsDiv = document.getElementById('video-options');
    const audioOptionsDiv = document.getElementById('audio-options');
    const extractAudioCheckbox = document.getElementById('extract-audio');
    const convertBtn = document.getElementById('convert-btn');
    const statusMessages = document.getElementById('status-messages');

    let currentTaskId = null;

    const videoFormats = [
        { value: 'mp4', text: 'MP4' },
        { value: 'mkv', text: 'MKV' },
        { value: 'webm', text: 'WebM' },
        { value: 'mov', text: 'MOV' },
        { value: 'gif', text: 'Animated GIF' },
    ];

    const audioFormats = [
        { value: 'mp3', text: 'MP3' },
        { value: 'm4a', text: 'M4A' },
        { value: 'wav', text: 'WAV' },
        { value: 'ogg', text: 'OGG' },
        { value: 'flac', text: 'FLAC' },
        { value: 'aac', text: 'AAC' },
    ];

    function populateOutputFormats() {
        outputFormatSelect.innerHTML = '';
        const selectedCategory = outputCategorySelect.value;
        let formatsToPopulate = [];

        if (selectedCategory === 'video') {
            formatsToPopulate = videoFormats;
            videoOptionsDiv.style.display = 'block';
            audioOptionsDiv.style.display = 'none';
        } else if (selectedCategory === 'audio') {
            formatsToPopulate = audioFormats;
            videoOptionsDiv.style.display = 'none';
            audioOptionsDiv.style.display = 'block';
        }

        formatsToPopulate.forEach(format => {
            const option = document.createElement('option');
            option.value = format.value;
            option.textContent = format.text;
            outputFormatSelect.appendChild(option);
        });
    }

    mediaUpload.addEventListener('change', async (event) => {
        const file = event.target.files[0];
        if (!file) {
            return;
        }

        statusMessages.innerHTML = '<div class="alert alert-info">Uploading file...</div>';
        conversionOptionsDiv.style.display = 'none';

        const formData = new FormData();
        formData.append('file', file);

        try {
            const data = await api.upload('/api/v1/ffmpeg/upload', formData);
            currentTaskId = data.task_id;
            statusMessages.innerHTML = '<div class="alert alert-success">File uploaded. Select conversion options.</div>';
            conversionOptionsDiv.style.display = 'block';
            populateOutputFormats();

        } catch (error) {
            statusMessages.innerHTML = `<div class="alert alert-danger">${error.message}</div>`;
        }
    });

    outputCategorySelect.addEventListener('change', populateOutputFormats);

    convertBtn.addEventListener('click', async () => {
        if (!currentTaskId) {
            statusMessages.innerHTML = '<div class="alert alert-danger">Please upload a file first.</div>';
            return;
        }

        const outputFormat = outputFormatSelect.value;
        const extractAudio = extractAudioCheckbox.checked;
        const resolution = document.getElementById('resolution').value;
        const quality = document.getElementById('quality').value;
        const bitrate = document.getElementById('bitrate').value;

        statusMessages.innerHTML = '<div class="alert alert-info">Starting conversion...</div>';

        try {
            await api.post('/api/v1/ffmpeg/convert', {
                task_id: currentTaskId,
                output_format: outputFormat,
                extract_audio: extractAudio,
                resolution: resolution,
                quality: quality,
                bitrate: bitrate
            });

            listenForTaskUpdates(currentTaskId);

        } catch (error) {
            statusMessages.innerHTML = `<div class="alert alert-danger">${error.message}</div>`;
        }
    });

    function listenForTaskUpdates(taskId) {
        const eventSource = new EventSource(`/api/v1/ffmpeg/tasks/${taskId}/stream`);

        eventSource.onmessage = (event) => {
            const data = JSON.parse(event.data);
            statusMessages.innerHTML = `<div class="alert alert-info">${data.status}: ${data.progress}%</div>`;

            if (data.status === 'completed') {
                eventSource.close();
                statusMessages.innerHTML = `<div class="alert alert-success">Conversion complete! <a href="/api/v1/ffmpeg/download/${taskId}" download>Click here to download</a></div>`;
            } else if (data.status === 'failed') {
                eventSource.close();
                statusMessages.innerHTML = `<div class="alert alert-danger">Conversion failed: ${data.error_message}</div>`;
            }
        };

        eventSource.onerror = (err) => {
            console.error("EventSource failed:", err);
            eventSource.close();
            statusMessages.innerHTML = `<div class="alert alert-danger">Error receiving updates.</div>`;
        };
    }
}
