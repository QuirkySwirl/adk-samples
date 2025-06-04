document.addEventListener('DOMContentLoaded', () => {
    const googlePlacesApiKeyInput = document.getElementById('googlePlacesApiKey');
    const geminiApiKeyInput = document.getElementById('geminiApiKey'); // New input field
    const saveApiKeyButton = document.getElementById('saveApiKeyButton');
    const statusMessageDiv = document.getElementById('statusMessage');
    const goToChatLink = document.getElementById('goToChatLink');

    const backendUrl = 'http://127.0.0.1:5001';

    // Initially hide the chat link
    goToChatLink.style.display = 'none';

    // --- Helper to check if both keys are present ---
    const checkAllKeysPresent = () => {
        const storedPlacesKey = localStorage.getItem('googlePlacesApiKey');
        const storedGeminiKey = localStorage.getItem('geminiApiKey');
        return storedPlacesKey && storedGeminiKey;
    };

    // --- Load existing keys from localStorage ---
    const loadExistingKeys = () => {
        const storedPlacesKey = localStorage.getItem('googlePlacesApiKey');
        const storedGeminiKey = localStorage.getItem('geminiApiKey');

        if (storedPlacesKey) {
            googlePlacesApiKeyInput.value = storedPlacesKey;
        }
        if (storedGeminiKey) {
            geminiApiKeyInput.value = storedGeminiKey;
        }

        if (checkAllKeysPresent()) {
            statusMessageDiv.textContent = 'API Keys loaded from local storage.';
            statusMessageDiv.className = 'status-success';
            goToChatLink.style.display = 'inline-block';
            goToChatLink.href = 'index.html';
        } else if (storedPlacesKey || storedGeminiKey) {
            statusMessageDiv.textContent = 'Please ensure all API Keys are provided.';
            statusMessageDiv.className = 'status-info';
        } else {
            statusMessageDiv.textContent = 'Please enter your API Keys.';
            statusMessageDiv.className = 'status-info';
        }
    };

    loadExistingKeys();

    // --- Save button event listener ---
    saveApiKeyButton.addEventListener('click', async () => {
        const placesKey = googlePlacesApiKeyInput.value.trim();
        const geminiKey = geminiApiKeyInput.value.trim();

        if (!placesKey || !geminiKey) {
            statusMessageDiv.textContent = 'Both Google Places API Key and Gemini API Key are required.';
            statusMessageDiv.className = 'status-error';
            return;
        }

        // Data to send to the backend
        const apiKeyData = {
            user_id: "default_user",
            keys: [
                { name: "google_places", api_key: placesKey },
                { name: "gemini", api_key: geminiKey }
            ]
        };

        try {
            statusMessageDiv.textContent = 'Saving API Keys...';
            statusMessageDiv.className = 'status-info';

            const response = await fetch(`${backendUrl}/api/set_api_key`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(apiKeyData),
            });

            const result = await response.json();

            if (response.ok && result.status === 'success') {
                localStorage.setItem('googlePlacesApiKey', placesKey);
                localStorage.setItem('geminiApiKey', geminiKey);
                statusMessageDiv.textContent = 'API Keys saved successfully!';
                statusMessageDiv.className = 'status-success';
                goToChatLink.style.display = 'inline-block';
                goToChatLink.href = 'index.html';
            } else {
                const errorMessage = result.message || 'Failed to save API Keys on the server.';
                statusMessageDiv.textContent = `Error: ${errorMessage}`;
                statusMessageDiv.className = 'status-error';
                if (!checkAllKeysPresent()) { // Keep link hidden if not all keys were already valid
                     goToChatLink.style.display = 'none';
                }
            }
        } catch (error) {
            console.error('Error saving API keys:', error);
            statusMessageDiv.textContent = 'An error occurred while contacting the server. Please ensure the backend is running.';
            statusMessageDiv.className = 'status-error';
            if (!checkAllKeysPresent()) {
                 goToChatLink.style.display = 'none';
            }
        }
    });
});
