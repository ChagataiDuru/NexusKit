
function showErrorModal(error) {
    const modalHTML = `
        <div class="modal fade" id="errorModal" tabindex="-1" aria-labelledby="errorModalLabel" aria-hidden="true">
            <div class="modal-dialog">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title" id="errorModalLabel">Oops! Something went wrong</h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                    </div>
                    <div class="modal-body">
                        <p>Please report this issue to the administrator.</p>
                        <pre><code>--- NexusKit Diagnostic Info ---
Error ID: ${error.error_id}
Timestamp (UTC): ${error.timestamp}
Tool: ${window.location.hash.slice(2) || 'dashboard'}
App Version: 1.1</code></pre>
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
                    </div>
                </div>
            </div>
        </div>
    `;

    // Remove existing modal if any
    const existingModal = document.getElementById('errorModal');
    if (existingModal) {
        existingModal.remove();
    }

    // Add new modal to the body
    document.body.insertAdjacentHTML('beforeend', modalHTML);

    // Show the modal
    const errorModal = new bootstrap.Modal(document.getElementById('errorModal'));
    errorModal.show();
}
