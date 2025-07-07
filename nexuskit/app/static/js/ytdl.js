
function ytdl() {
    const fetchInfoBtn = document.getElementById('fetch-info-btn');
    const downloadBtn = document.getElementById('download-btn');
    const videoInfoDiv = document.getElementById('video-info');
    const videoTitle = document.getElementById('video-title');
    const videoThumbnail = document.getElementById('video-thumbnail');
    const videoQualitySelect = document.getElementById('video-quality');
    const audioOnlyCheckbox = document.getElementById('audio-only');
    const audioFormatContainer = document.getElementById('audio-format-container');
    const statusMessages = document.getElementById('status-messages');

    fetchInfoBtn.addEventListener('click', async () => {
        const url = document.getElementById('youtube-url').value;
        if (!url) {
            statusMessages.innerHTML = '<div class="alert alert-danger">Please enter a YouTube URL.</div>';
            return;
        }

        statusMessages.innerHTML = '<div class="alert alert-info">Fetching video info...</div>';

        try {
            const data = await api.post('/api/v1/ytdl/fetch-info', { url });

            videoTitle.textContent = data.title;
            videoThumbnail.src = data.thumbnail;
            videoInfoDiv.style.display = 'block';

            // Populate video quality dropdown
            videoQualitySelect.innerHTML = '';
            data.formats.forEach(format => {
                if (format.resolution) {
                    const option = document.createElement('option');
                    option.value = format.format_id;
                    option.textContent = format.resolution;
                    videoQualitySelect.appendChild(option);
                }
            });

            statusMessages.innerHTML = '';

        } catch (error) {
            statusMessages.innerHTML = `<div class="alert alert-danger">${error.message}</div>`;
        }
    });

    audioOnlyCheckbox.addEventListener('change', () => {
        audioFormatContainer.style.display = audioOnlyCheckbox.checked ? 'block' : 'none';
    });

    downloadBtn.addEventListener('click', async () => {
        const url = document.getElementById('youtube-url').value;
        const formatId = document.getElementById('video-quality').value;
        const audioOnly = document.getElementById('audio-only').checked;
        const audioFormat = document.getElementById('audio-format').value;

        statusMessages.innerHTML = '<div class="alert alert-info">Initiating download...</div>';

        try {
            const data = await api.post('/api/v1/ytdl/download-request', { 
                url, 
                format_id: formatId, 
                audio_only: audioOnly, 
                audio_format: audioFormat 
            });

            listenForTaskUpdates(data.task_id);

        } catch (error) {
            statusMessages.innerHTML = `<div class="alert alert-danger">${error.message}</div>`;
        }
    });

    function listenForTaskUpdates(taskId) {
        const eventSource = new EventSource(`/api/v1/ytdl/tasks/${taskId}/stream`);

        eventSource.onmessage = (event) => {
            const data = JSON.parse(event.data);
            statusMessages.innerHTML = `<div class="alert alert-info">${data.status}: ${data.progress}%</div>`;

            if (data.status === 'completed') {
                eventSource.close();
                statusMessages.innerHTML = `<div class="alert alert-success">Download complete! <a href="/api/v1/ytdl/download/${taskId}" download>Click here to download</a></div>`;
            } else if (data.status === 'failed') {
                eventSource.close();
                statusMessages.innerHTML = `<div class="alert alert-danger">Download failed: ${data.error_message}</div>`;
            }
        };

        eventSource.onerror = (err) => {
            console.error("EventSource failed:", err);
            eventSource.close();
            statusMessages.innerHTML = `<div class="alert alert-danger">Error receiving updates.</div>`;
        };
    }
}
