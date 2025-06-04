# Travel Concierge Application - Testing Guide

This guide provides instructions on how to set up, run, and test the Travel Concierge application, covering the backend Flask service and the HTML/JS/CSS frontend.

## 1. Prerequisites

*   **Python:** Version 3.11 or higher installed.
*   **Poetry:** Python dependency management tool. Installation: [https://python-poetry.org/docs/](https://python-poetry.org/docs/).
*   **Web Browser:** A modern web browser (e.g., Chrome, Firefox, Safari, Edge) with developer tools for inspection.
*   **Node.js & npx:** (Optional, but Recommended for Airbnb testing) Required if you intend to test live Airbnb MCP integration, as the ADK agent might need to run an MCP server via npx.

## 2. Setup Instructions

1.  **Navigate to Project Directory:**
    ```bash
    cd path/to/your/repo/python/agents/travel-concierge
    ```

2.  **Install Python Dependencies:**
    ```bash
    poetry install
    ```
    This installs Flask and other Python packages. For live MCP features, ensure any related Node.js dependencies are met locally if you're running the MCP server component.

3.  **Activate Virtual Environment:**
    ```bash
    poetry shell
    ```
    This command starts a new shell with the project's virtual environment activated.

## 3. Running the Backend Application

1.  **Start Flask Server:**
    From the `python/agents/travel-concierge` directory (with the virtual environment active):
    ```bash
    python backend_app.py
    ```

2.  **Expected Output:**
    ```
     * Serving Flask app 'backend_app'
     * Debug mode: on
     * Running on http://127.0.0.1:5001 (Press CTRL+C to quit)
    ```
    The backend is now ready. Keep this terminal window open.

## 4. Frontend Testing

Open your web browser and navigate to the frontend files. The main entry point for users after initial setup is `index.html`, but API key setup is first.

### 4.1. API Key Management (`frontend/api_keys.html`)

1.  **Open Page:** Navigate to `file:///path/to/your/repo/python/agents/travel-concierge/frontend/api_keys.html`.

2.  **Testing Scenarios:**
    *   **Initial State:**
        *   Verify input fields for "Google Places API Key" and "Gemini API Key" are present.
        *   Verify "Go to Travel Concierge" link is hidden or inactive.
        *   Status message should prompt for key entry.
    *   **Saving Keys:**
        *   **Both Keys Empty:** Click "Save API Keys". Expected: Error message "Both ... keys are required."
        *   **One Key Empty:** Enter one key, leave the other empty. Click "Save API Keys". Expected: Same error.
        *   **Valid Keys:** Enter dummy/test keys for both (e.g., "PLACES_TEST_KEY", "GEMINI_TEST_KEY"). Click "Save API Keys".
            *   Expected: Success message "API Keys saved successfully!".
            *   Input fields should retain the values.
            *   "Go to Travel Concierge" link becomes active and points to `index.html`.
            *   Check browser's Local Storage (Developer Tools -> Application -> Local Storage): `googlePlacesApiKey` and `geminiApiKey` should be stored.
    *   **Loading Existing Keys:**
        *   After successful save, reload `api_keys.html`.
        *   Expected: Input fields are pre-populated with keys from Local Storage. "Go to Travel Concierge" link is active. Status message indicates keys loaded.
    *   **Clearing and Re-adding:**
        *   Manually clear keys from Local Storage. Reload `api_keys.html`.
        *   Expected: Page is in its initial state.
        *   Re-add keys and verify functionality.
    *   Click "Go to Travel Concierge" to proceed to the chat page.

### 4.2. Main Chat Interface (`frontend/index.html`)

1.  **Open Page:** Navigate from `api_keys.html` or directly via `file:///path/to/your/repo/python/agents/travel-concierge/frontend/index.html`.

2.  **Testing Scenarios:**

    *   **API Key Status:**
        *   **Keys Set:** If keys were set via `api_keys.html`, the status line at the top should show "API Key: Set" (in green).
        *   **Keys Missing:** Clear keys from Local Storage and reload `index.html`.
            *   Expected: Status "Not Set! Please set all keys." (in red). A system message in chat prompts to set keys. Chat input might be disabled or show an alert if trying to send.
    *   **Landing Page & Example Itinerary:**
        *   The "Welcome to the AI Travel Concierge!" section should be visible.
        *   Click "Load Seattle Adventure (Example)" button:
            *   Requires API keys to be set. If not, it should prompt to set them.
            *   Expected (if keys set): Loading indicator appears. Button may disable. Agent responds with a summary of the Seattle itinerary. This might include text and/or cards if the agent is configured to produce them for the loaded scenario.
            *   Verify `session_id` is created/updated in Local Storage.
            *   The button might change text to "Example Loaded!" or become disabled.
        *   **Context Persistence after Load:** Send a follow-up query related to Seattle (e.g., "What's near the Space Needle?"). The agent should respond in the context of the loaded Seattle itinerary.
        *   **Loading Multiple Times:** Test clicking the button again. Current implementation might just reload/restart the scenario in a new session or append to the current chat. Observe behavior.
    *   **Live Agent Interaction (Core Chat):**
        Ensure API keys are set. Use diverse queries:
        *   **Simple Greetings:** "Hi", "Hello there". Expected: Simple, polite text response.
        *   **Inspiration:** "Inspire me with some destinations for a summer holiday." Expected: Should trigger destination cards if the agent supports it (current `travel_agent_service.py` with real agent might not yet, but mock data did).
        *   **Map Data:** "Where is the Eiffel Tower in Paris?" Expected: Text response. If agent produces `map_data`, a map placeholder with link should appear.
        *   **Clickable Actions:** "What are my options for a trip to London?" Expected: Text response. If agent produces `actions`, clickable buttons should appear.
        *   **Follow-up Questions:** After a response, ask a relevant follow-up, e.g., after destination cards, "Tell me more about the first one."
        *   **Complex Queries:** "I want a family-friendly trip to a warm beach destination in Southeast Asia for 2 weeks in July, with a budget of $5000, including flights from San Francisco."
        *   **Agent Errors / "I don't know":** "What is the meaning of life?" or highly specific, out-of-domain questions. Expected: Graceful fallback message.
        *   **Checking API Key Usage:** If agent responses are consistently very generic or fail, it might indicate an issue with the Gemini API key (e.g., invalid, expired, or not authorized for the model). Places API key issues might manifest in lack of location-specific details.
    *   **Rich GUI Elements Rendering:**
        *   **Destination/Generic Cards:** If agent returns `destinations` or `cards`, verify they render as a horizontal scrollable list with images (if provided), titles, and text.
        *   **Map Placeholders:** If agent returns `map_data`, verify the text "Map: Marker at [lat], [lon] for [label]" and the OpenStreetMap link appear and are correct.
        *   **Action Buttons:** If agent returns `actions`, verify buttons appear with correct labels. Click each button:
            *   Expected: The `action.query` associated with the button is sent as a new message from the user. The agent responds to this new query.
    *   **Airbnb MCP Integration (Experimental):**
        *   **Prerequisites:** As noted previously, this requires a fully configured ADK agent with MCP tools for Airbnb and potentially a running MCP server.
        *   **Test Query:** "Find me an airbnb in San Diego, April 9th, to april 13th".
        *   **Expected (MCP Working):** Agent text response + horizontally scrollable Airbnb listing cards (title, link, rating, price). A "View all results on Airbnb" link may also appear.
        *   **Expected (MCP Not Working/Configured):** Standard text response from agent (e.g., "I can't book Airbnbs yet," or a generic search result if it falls back to web search). No Airbnb cards.
    *   **Error Handling:**
        *   **Backend Down:** Stop the Flask server (`Ctrl+C` in its terminal). Try sending a message or loading the example. Expected: Frontend shows a network error message in the chat.
        *   **Invalid Inputs:** Test sending messages with special characters or very long text (observe behavior, no specific error handling for this is built in beyond what the browser/agent does).
    *   **Session Management:**
        *   **Context:** Verify conversation context is maintained across several turns.
        *   **`session_id`:** Check Local Storage for `travelConciergeSessionId`. It should be created on the first interaction (or example load) and reused for subsequent messages.
        *   **Clearing `session_id`:** Delete `travelConciergeSessionId` from Local Storage and send a message. Expected: A new session starts; the agent should not have context from the previous session.

## 5. Troubleshooting

*   **Flask Server Not Running/Accessible:**
    *   Ensure `python backend_app.py` was started successfully.
    *   Check for any error messages in the Flask console.
    *   Verify no other application is using port 5001.
*   **API Keys Not Saved/Retrieved:**
    *   Open browser developer tools (usually F12).
    *   Go to Application -> Local Storage. Check if `googlePlacesApiKey` and `geminiApiKey` are present and correct after saving.
    *   Check Flask console logs for `/api/set_api_key` requests and any errors.
*   **Agent Responses are Errors or Very Generic:**
    *   **Verify API Keys:** Double-check that the Gemini API key is correct, active, and has the necessary permissions (e.g., for the Gemini models used by the ADK agent). The Places API key should also be valid.
    *   **Backend Logs:** Examine the Flask console output. `travel_agent_service.py` prints errors during agent invocation. These can indicate issues with environment variables, ADK setup, or the agent itself.
    *   **ADK Agent Configuration:** The underlying ADK agent (`travel_concierge.agent`) must be correctly configured to use the provided Gemini API key for its language model.
*   **Cards/Rich Elements Not Rendering (or errors in console):**
    *   **Browser Console:** Open developer tools (F12) -> Console. Look for JavaScript errors in `chat.js` related to `appendMessage` or rendering.
    *   **Network Tab:** Open developer tools -> Network. Inspect the response from `/api/query`. Verify the JSON structure:
        *   Is the `response` field a string or an object?
        *   If an object, does it contain the expected keys (`text`, `destinations`, `map_data`, `actions`, `airbnb_listings`)?
        *   Are the contents of these keys correctly formatted (e.g., arrays of objects)?
    *   This helps determine if the issue is in the frontend parsing/rendering or if the backend/agent is not sending the expected structured data.
*   **General Debugging:**
    *   **Flask Console:** Provides backend request logs and error messages from Python.
    *   **Browser Developer Console:** Provides frontend JavaScript error messages, network request details, and allows inspection of HTML/CSS.

This comprehensive guide should help in thoroughly testing the application.
