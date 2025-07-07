
const api = {
    async post(url, data) {
        try {
            const response = await fetch(url, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(data),
            });
            const responseData = await response.json();
            if (!response.ok) {
                if (responseData.error_id) {
                    showErrorModal(responseData);
                }
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return responseData;
        } catch (error) {
            console.error('API POST error:', error);
            throw error;
        }
    },

    async get(url) {
        try {
            const response = await fetch(url);
            const responseData = await response.json();
            if (!response.ok) {
                if (responseData.error_id) {
                    showErrorModal(responseData);
                }
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return responseData;
        } catch (error) {
            console.error('API GET error:', error);
            throw error;
        }
    },

    async upload(url, formData) {
        try {
            const response = await fetch(url, {
                method: 'POST',
                body: formData,
            });
            const responseData = await response.json();
            if (!response.ok) {
                if (responseData.error_id) {
                    showErrorModal(responseData);
                }
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return responseData;
        } catch (error) {
            console.error('API UPLOAD error:', error);
            throw error;
        }
    }
};
