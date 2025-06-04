document.addEventListener('DOMContentLoaded', () => {
    const chatMessagesDiv = document.getElementById('chatMessages');
    const chatForm = document.getElementById('chatForm');
    const userInput = document.getElementById('userInput');
    // const sendButton = document.getElementById('sendButton'); // Not directly used if form submits
    const loadingIndicator = document.getElementById('loadingIndicator');
    const apiKeyStatusSpan = document.getElementById('apiKeyStatus');
    const apiKeyStatusContainer = document.querySelector('.api-key-status-container') || apiKeyStatusSpan.parentElement;
    const loadExampleButton = document.getElementById('loadExampleButton');

    const backendUrl = 'http://127.0.0.1:5001';

    // --- Helper Function to Append Messages ---
    function appendMessage(messageContent, sender) {
        const messageDiv = document.createElement('div');
        messageDiv.classList.add('message', `message-${sender}`);

        if (sender === 'agent' && typeof messageContent === 'object' && messageContent !== null) {
            if (messageContent.text) {
                const textPart = document.createElement('p');
                textPart.textContent = messageContent.text;
                messageDiv.appendChild(textPart);
            }

            // Render Cards (Destinations or Generic)
            const cardDataKey = messageContent.destinations ? 'destinations' : (messageContent.cards ? 'cards' : null);
            if (cardDataKey && Array.isArray(messageContent[cardDataKey])) {
                const cardsContainer = document.createElement('div');
                cardsContainer.classList.add('cards-container'); // General class for horizontal scroll
                messageContent[cardDataKey].forEach(item => {
                    const card = document.createElement('div');
                    card.classList.add('destination-card');

                    if (item.image) {
                        const img = document.createElement('img');
                        img.src = item.image;
                        img.alt = `Image of ${item.name || item.title || 'item'}`;
                        card.appendChild(img);
                    }
                    const titleText = item.name || item.title;
                    if (titleText) {
                        const title = document.createElement('h4');
                        title.textContent = titleText;
                        if (item.country) title.textContent += `, ${item.country}`;
                        card.appendChild(title);
                    }
                    const descriptionText = item.highlights || item.description || (item.text && item.text.substring(0,100));
                    if (descriptionText) {
                        const description = document.createElement('p');
                        description.textContent = descriptionText;
                        card.appendChild(description);
                    }
                    if (item.rating) {
                        const rating = document.createElement('p');
                        rating.classList.add('rating');
                        rating.textContent = `Rating: ${item.rating} ★`;
                        card.appendChild(rating);
                    }
                    cardsContainer.appendChild(card);
                });
                messageDiv.appendChild(cardsContainer);
            }

            // Render Airbnb Listings
            if (messageContent.airbnb_listings && Array.isArray(messageContent.airbnb_listings)) {
                const airbnbContainer = document.createElement('div');
                // Reuse cards-container for horizontal scroll, or define airbnb-cards-container if different layout needed
                airbnbContainer.classList.add('cards-container', 'airbnb-cards-container');

                messageContent.airbnb_listings.forEach(listing => {
                    const card = document.createElement('div');
                    card.classList.add('destination-card', 'airbnb-card'); // Reuse destination-card styling

                    // Airbnb specific fields
                    if (listing.title) {
                        const title = document.createElement('h4');
                        title.textContent = listing.title;
                        card.appendChild(title);
                    }
                    if (listing.url) {
                        const link = document.createElement('a');
                        link.href = listing.url;
                        link.target = "_blank";
                        link.rel = "noopener noreferrer";
                        link.textContent = "View on Airbnb";
                        link.classList.add('card-button'); // Style as a button
                        card.appendChild(link);
                    }
                    if (listing.avgRatingA11yLabel) {
                        const rating = document.createElement('p');
                        rating.classList.add('rating');
                        rating.textContent = listing.avgRatingA11yLabel;
                        card.appendChild(rating);
                    }
                    if (listing.structuredDisplayPrice && listing.structuredDisplayPrice.primaryLine) {
                        const price = document.createElement('p');
                        price.textContent = listing.structuredDisplayPrice.primaryLine.accessibilityLabel;
                        card.appendChild(price);
                    }
                    // Add more fields as needed e.g. listing.listing.coordinate for a map link
                    airbnbContainer.appendChild(card);
                });
                messageDiv.appendChild(airbnbContainer);
                if(messageContent.airbnb_search_url){
                    const searchUrlDiv = document.createElement('div');
                    searchUrlDiv.style.marginTop = '10px';
                    const searchLink = document.createElement('a');
                    searchLink.href = messageContent.airbnb_search_url;
                    searchLink.target = "_blank";
                    searchLink.rel = "noopener noreferrer";
                    searchLink.textContent = "View all results on Airbnb";
                    searchUrlDiv.appendChild(searchLink);
                    messageDiv.appendChild(searchUrlDiv);
                }
            }

            // Render Map Data
            if (messageContent.map_data) {
                const mapData = messageContent.map_data;
                const mapDiv = document.createElement('div');
                mapDiv.classList.add('map-display-area');
                mapDiv.innerHTML = `
                    <p><strong>Map:</strong> Marker for "${mapData.marker_label || 'Location'}"</p>
                    <p>Lat: ${mapData.latitude}, Lon: ${mapData.longitude} (Zoom: ${mapData.zoom || 'N/A'})</p>
                    <a href="https://www.openstreetmap.org/?mlat=${mapData.latitude}&mlon=${mapData.longitude}#map=${mapData.zoom || 15}/${mapData.latitude}/${mapData.longitude}" target="_blank" rel="noopener noreferrer">
                        View on OpenStreetMap
                    </a>`;
                messageDiv.appendChild(mapDiv);
            }

            // Render Clickable Actions
            if (messageContent.actions && Array.isArray(messageContent.actions)) {
                const actionsContainer = document.createElement('div');
                actionsContainer.classList.add('actions-container');
                messageContent.actions.forEach(action => {
                    const button = document.createElement('button');
                    button.classList.add('action-button');
                    button.textContent = action.label;
                    button.addEventListener('click', () => {
                        userInput.value = action.query;
                        handleQuerySubmission(action.query); // Directly call with action.query
                    });
                    actionsContainer.appendChild(button);
                });
                messageDiv.appendChild(actionsContainer);
            }

            if (!messageContent.text && !cardDataKey && !messageContent.map_data && !messageContent.actions && !messageContent.airbnb_listings) {
                const pre = document.createElement('pre');
                pre.textContent = JSON.stringify(messageContent, null, 2);
                messageDiv.appendChild(pre);
            }

        } else if (typeof messageContent === 'string') {
            messageDiv.textContent = messageContent;
        } else {
            messageDiv.textContent = "Received complex or unexpected message structure.";
            console.warn("appendMessage received unexpected messageContent:", messageContent);
        }

        chatMessagesDiv.appendChild(messageDiv);
        chatMessagesDiv.scrollTop = chatMessagesDiv.scrollHeight;
    }

    async function handleQuerySubmission(queryText) {
        if (!queryText) return;
        if (!checkApiKeys()) {
            appendMessage('API Keys not set. Please set them via "Manage Keys" before sending messages.', 'error');
            return;
        }
        // Do not append user message here if it's from an action button, as it might be redundant.
        // Or, decide based on source. For now, only direct user input is appended before this call.
        // If called from action button, the action.query is the queryText.
        // The original user input that led to the action buttons is already displayed.

        // If userInput.value is the source, it means it's a fresh user typed message.
        if (userInput.value === queryText && queryText !== "") {
             appendMessage(queryText, 'user');
        } // else, it's from an action button, query already shown indirectly.

        userInput.value = '';
        loadingIndicator.style.display = 'block';
        const currentSessionId = localStorage.getItem('travelConciergeSessionId');

        try {
            const response = await fetch(`${backendUrl}/api/query`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ user_id: "default_user", query: queryText, session_id: currentSessionId }),
            });
            loadingIndicator.style.display = 'none';
            const data = await response.json();
            if (response.ok) {
                if (data.session_id) localStorage.setItem('travelConciergeSessionId', data.session_id);
                if (data.response) appendMessage(data.response, 'agent');
                else if (data.error) appendMessage(`Error from agent: ${data.error}`, 'error');
                else appendMessage("Received an empty response from the agent.", 'agent');
            } else {
                appendMessage(data.message || 'Error: Could not get response from the agent.', 'error');
            }
        } catch (error) {
            loadingIndicator.style.display = 'none';
            console.error('Error querying agent:', error);
            appendMessage('Network error or backend server is unavailable. Please try again later.', 'error');
        }
    }

    const checkApiKeys = ()_INTERNAL_STATE_DEBUG_PLACEHOLDER => {
        const placesKey = localStorage.getItem('googlePlacesApiKey');
        const geminiKey = localStorage.getItem('geminiApiKey');
        if (!placesKey || !geminiKey) {
            apiKeyStatusSpan.textContent = 'Not Set! Please set all keys.';
            apiKeyStatusSpan.style.color = '#dc3545';
            if(apiKeyStatusContainer) apiKeyStatusContainer.style.backgroundColor = 'rgba(220, 53, 69, 0.1)';
            return false;
        } else {
            apiKeyStatusSpan.textContent = 'Set';
            apiKeyStatusSpan.style.color = '#28a745';
            if(apiKeyStatusContainer) apiKeyStatusContainer.style.backgroundColor = 'rgba(40, 167, 69, 0.1)';
            return true;
        }
    };

    if (checkApiKeys()) {
        appendMessage('Welcome to the Travel Concierge! How can I help you plan your trip, or would you like to load an example?', 'agent');
    } else {
        appendMessage('Welcome! Please set your Google Places & Gemini API Keys via the "Manage Keys" link above to start chatting or load an example.', 'system');
    }
    loadingIndicator.style.display = 'none';

    if (loadExampleButton) {
        loadExampleButton.addEventListener('click', async () => {
            if (!checkApiKeys()) {
                appendMessage('Please ensure all API Keys are set via "Manage Keys" before loading an example.', 'error');
                return;
            }
            loadingIndicator.style.display = 'block';
            loadExampleButton.disabled = true;
            loadExampleButton.textContent = 'Loading Example...';
            try {
                const response = await fetch(`${backendUrl}/api/load_example_itinerary`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ user_id: "default_user" })
                });
                loadingIndicator.style.display = 'none';
                const data = await response.json();
                if (response.ok) {
                    if (data.session_id) localStorage.setItem('travelConciergeSessionId', data.session_id);
                    if (data.response) appendMessage(data.response, 'agent');
                    if (data.itinerary) console.log("Loaded Itinerary:", data.itinerary);
                    if (data.user_profile) console.log("Loaded Profile:", data.user_profile);
                    loadExampleButton.textContent = 'Example Loaded!';
                } else {
                    appendMessage(data.message || 'Error: Could not load example itinerary.', 'error');
                    loadExampleButton.disabled = false;
                    loadExampleButton.textContent = 'Load Seattle Adventure (Example)';
                }
            } catch (error) {
                loadingIndicator.style.display = 'none';
                console.error('Error loading example itinerary:', error);
                appendMessage('Network error or backend server is unavailable.', 'error');
                loadExampleButton.disabled = false;
                loadExampleButton.textContent = 'Load Seattle Adventure (Example)';
            }
        });
    }

    chatForm.addEventListener('submit', async (event) => {
        event.preventDefault();
        const messageText = userInput.value.trim();
        if (messageText) { // Only append user message if it's from direct input
            // appendMessage(messageText, 'user'); // This is now handled inside handleQuerySubmission if it's a direct input
        }
        handleQuerySubmission(messageText);
    });
});
