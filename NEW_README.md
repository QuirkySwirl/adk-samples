# AI Travel Concierge Web Application (Standalone)

This project provides a standalone web interface for interacting with the Python-based AI Travel Concierge agent. It allows users to manage API keys, chat with the agent, and view rich, interactive responses for travel planning.

## Key Features

*   **Web-Based UI:** Modern and intuitive interface built with HTML, CSS, and vanilla JavaScript.
*   **API Key Management:** Securely store Google Places and Gemini API keys locally in your browser via a dedicated setup page.
*   **Interactive Chat:** Converse with the Travel Concierge agent to get travel inspiration, plan itineraries, and more.
*   **Glassmorphic Design:** Aesthetically pleasing UI with frosted glass effects.
*   **Rich Agent Responses:** Displays destination cards, map placeholders (non-interactive), and clickable action buttons.
*   **Example Itinerary:** Load a sample Seattle itinerary to quickly explore agent capabilities.
*   **Experimental Airbnb Support:** UI is ready to display Airbnb listings if the agent is configured with MCP tools and provides the data.

## Architecture

*   **Frontend:** HTML, CSS, JavaScript (located in the `frontend/` directory).
*   **Backend:** Python Flask application (`backend_app.py`).
*   **Agent Core:** The core ADK-based Travel Concierge agent logic (located in the `travel_agent_core/` directory).
*   **Service Layer:** A Python service (`travel_agent_service.py`) that bridges the backend app and the agent core.

## Setup and Running the Application

Follow these steps to set up and run the application:

1.  **Clone the Repository:**
    Clone the branch containing this standalone application.
    ```bash
    # Replace with the actual command to clone the specific branch
    git clone <repository_url> --branch <branch_name> travel-concierge-standalone
    cd travel-concierge-standalone
    ```

2.  **Install Dependencies:**
    This project uses Poetry for dependency management. Ensure you have Poetry installed.
    ```bash
    poetry install
    ```

3.  **Activate Virtual Environment:**
    ```bash
    poetry shell
    ```
    (Alternatively, you can use `eval $(poetry env activate)`)

4.  **Run the Backend Server:**
    ```bash
    python backend_app.py
    ```
    The backend server will start, typically on `http://127.0.0.1:5001/`.

5.  **Access the Frontend:**
    Open the `frontend/index.html` file in your web browser.
    *Example: `file:///path/to/your/travel-concierge-standalone/frontend/index.html`*

6.  **Set API Keys:**
    *   The application will likely redirect you or prompt you to set API keys first. Navigate to `frontend/api_keys.html` (or click the "Manage Keys" link).
    *   Enter your **Google Places API Key** and your **Gemini API Key**.
    *   Click "Save API Key(s)". These keys are stored in your browser's local storage.

7.  **Start Chatting:**
    Navigate back to `frontend/index.html` (or click "Go to Travel Concierge" from the API keys page). You can now interact with the agent or load the example itinerary.

## Project Structure

*   `backend_app.py`: Main Flask application.
*   `travel_agent_service.py`: Handles interaction with the ADK agent.
*   `travel_agent_core/`: The core ADK agent logic.
*   `frontend/`: All frontend HTML, CSS, and JavaScript files.
*   `pyproject.toml`: Project dependencies and package configuration.
*   `README.md`: This file.
*   `testing_guide.md`: Comprehensive guide for testing the application.
*   `.env.example`: Example for environment variables (primarily `TRAVEL_CONCIERGE_SCENARIO` if needed for default loading behavior, though API keys are handled by UI).

## Dependencies

*   Python 3.11+
*   Poetry
*   Active API keys for Google Places and a Gemini-compatible generative AI service.
