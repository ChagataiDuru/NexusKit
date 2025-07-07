function formatter() {
    const formatterInput = document.getElementById('formatterInput');
    const formatTypeSelect = document.getElementById('formatType');
    const formatButton = document.getElementById('formatButton');
    const clearButton = document.getElementById('clearButton');
    const formatterOutput = document.getElementById('formatterOutput');

    if (!formatterInput || !formatTypeSelect || !formatButton || !clearButton || !formatterOutput) {
        return;
    }

    formatButton.addEventListener('click', async () => {
        const text = formatterInput.value;
        const formatType = formatTypeSelect.value;

        if (!text.trim()) {
            formatterOutput.textContent = 'Input text cannot be empty.';
            formatterOutput.className = 'text-danger';
            return;
        }

        try {
            const response = await fetch('/api/v1/formatter/format', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ text, format_type: formatType }),
            });

            const data = await response.json();

            if (response.ok) {
                formatterOutput.textContent = data.formatted_text;
                formatterOutput.className = `language-${formatType}`;
                if (typeof Prism !== 'undefined') {
                    Prism.highlightElement(formatterOutput);
                }
            } else {
                formatterOutput.textContent = `Error: ${data.detail}`;
                formatterOutput.className = 'text-danger';
            }
        } catch (error) {
            formatterOutput.textContent = `Error: ${error.message}`;
            formatterOutput.className = 'text-danger';
        }
    });

    clearButton.addEventListener('click', () => {
        formatterInput.value = '';
        formatterOutput.textContent = '';
        formatterOutput.className = '';
    });
}
