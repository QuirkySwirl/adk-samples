# Travel Concierge

This sample demonstrates the use of Agent Development Kit to deliver a new user experience for Travelers. A cohort of agents mimics the notion of having a personal travel concierge, taking care of a traveler's needs: from trip conception, planning and booking, to preparing for the trip, getting help to get from point A to B during the trip, while simultaneously acting as an informative guide.

This example includes illustrations with ADK supported tools such as Google Places API, Google Search Grounding and MCP.

---

## AI Travel Concierge Web Application

This project includes a web-based user interface (frontend and backend) for interacting with the Python-based Travel Concierge ADK agent. It provides an alternative way to experience the agent's capabilities through a chat interface in your browser.

**Overview:**

The web application allows users to:
*   Manage API keys (Google Places and Gemini) through a simple UI.
*   Engage in an interactive chat session with the Travel Concierge agent.
*   Experience a modern, glassmorphic UI design.
*   View rich agent responses, including:
    *   Destination suggestion cards.
    *   Placeholders for map data.
    *   Clickable action buttons for quick replies.
    *   Display of Airbnb listings (experimental, depends on agent's MCP configuration).
*   Load an example itinerary (e.g., a Seattle adventure) to quickly explore the agent's capabilities.

**Architecture:**

*   **Frontend:** Built with plain HTML, CSS, and JavaScript. No complex JavaScript frameworks are used, ensuring simplicity and ease of understanding.
    *   Located in the `frontend/` directory.
*   **Backend:** A Python Flask application that serves as an intermediary between the frontend and the agent service.
    *   Main file: `backend_app.py`.
*   **Agent Interaction:** The Flask backend communicates with the ADK agent via a service layer.
    *   Service file: `travel_agent_service.py`, which uses the ADK's `SessionRunner` to interact with the `root_agent`.

**Setup and Running the Web Application:**

For detailed prerequisites, setup instructions (including Poetry for Python dependencies), and comprehensive testing steps, please refer to the **[`testing_guide.md`](./testing_guide.md)** file.

A brief overview to get started:
1.  Navigate to the `python/agents/travel-concierge/` directory in your terminal.
2.  Install dependencies: `poetry install`
3.  Activate the virtual environment: `poetry shell` (or `eval $(poetry env activate)`)
4.  Run the backend server: `python backend_app.py`
    *   The server will typically run on `http://127.0.0.1:5001/`.
5.  Open the API key setup page in your web browser by navigating to the local file: `frontend/api_keys.html`.
    *   **It is crucial to set your Google Places API Key and Gemini API Key via this page first.** These keys are stored in your browser's local storage and sent to the backend as needed.
6.  Once keys are saved, navigate to `frontend/index.html` (or click the "Go to Travel Concierge" link) to start interacting with the agent.

**Key Files for the Web Application:**

*   `backend_app.py`: The main Flask application providing API endpoints.
*   `travel_agent_service.py`: The service layer that interfaces with the ADK Travel Concierge agent.
*   `frontend/`: Directory containing all frontend HTML, CSS, and JavaScript files.
    *   `frontend/index.html`: The main chat interface.
    *   `frontend/api_keys.html`: Page for managing API keys.
    *   `frontend/chat.js`, `frontend/api_keys.js`: JavaScript logic for the frontend.
    *   `frontend/style.css`, `frontend/chat_style.css`: CSS for styling.
*   `testing_guide.md`: Comprehensive guide for setting up, running, and testing this web application.
*   `travel_concierge/`: Directory containing the original ADK agent Python code.

**Dependencies for Full Functionality:**

*   **Google Places API Key:** Required for location-based services used by the agent.
*   **Gemini API Key (or equivalent Google AI Studio API Key):** Required for the generative AI models used by the ADK agent.
    *   These keys should be configured through the web UI (`frontend/api_keys.html`) for the web application to function correctly.

---

## Overview

A traveler's experience can be divided into two stages: pre-booking and post-booking. In this example, each stage involves the use of multiple specialized agents working together to provide the concierge experience.

During the pre-booking stage, different agents are constructed to help the traveler with vacation inspirations, activities planning, finding flights and hotels, and helps with booking payment processing. The pre-booking stage ends with an itinerary for a trip.

In the post-booking stage, given a concrete itinerary, a different set of agents support the traveler's needs before, during and after the trip. For example, the pre-trip agent checks for visa and medical requirements, travel advisory, and storm status. The in-trip agent monitors for any changes to bookings, with a day-of agent that helps the traveler getting from A to B during the trip. The post-trip agent helps collect feedback and identify additional preferences for future travel plans.


## Agent Details
The key features of the Travel Concierge include:

| Feature | Description |
| --- | --- |
| **Interaction Type:** | Conversational |
| **Complexity:**  | Advanced |
| **Agent Type:**  | Multi Agent |
| **Components:**  | Tools, AgentTools, Memory |
| **Vertical:**  | Travel |

See section [MCP](#mcp) for an example using Airbnb's MCP search tool.

### Agent Architecture
Travel Concierge Agents Architecture

<img src="travel-concierge-arch.png" alt="Travel Concierge's Multi-Agent Architecture" width="800"/>

### Component Details

Expand on the "Key Components" from above.
*   **Agents:**
    * `inspiration_agent` - Interacts with the user to make suggestions on destinations and activities, inspire the user to choose one.
    * `planning_agent` - Given a destination, start date, and duration, the planning agent helps the user select flights, seats and a hotel (mocked), then generate an itinerary containing the activities.
    * `booking_agent` - Given an itinerary, the booking agent will help process those items in the itinerary that requires payment.
    * `pre_trip_agent` - Intended to be invoked regularly before the trip starts; This agent fetches relevant trip information given its origin, destination, and the user's nationality.
    * `in_trip_agent`- Intended to be invoked frequently during the trip. This agent provide three services: monitor any changes in bookings (mocked), acts as an informative guide, and provides transit assistance.
    * `post_trip_agent` - In this example, the post trip agent asks the traveler about their experience and attempts to extract and store their various preferences based on the trip, so that the information could be useful in future interactions.
*   **Tools:**
    * `map_tool` - retrieves lat/long; geocoding an address with the Google Map API.
    * `memorize` - a function to memorize information from the dialog that are important to trip planning and to provide in-trip support.
*   **AgentTools:**  
    * `google_search_grounding` - used in the example for pre-trip information gather such as visa, medical, travel advisory...etc.
    * `what_to_pack` - suggests what to pack for the trip given the origin and destination.
    * `place_agent` - this recommends destinations.
    * `poi_agent` - this suggests activities given a destination.
    * `itinerary_agent` - called by the `planning_agent` to fully construct and represent an itinerary in JSON following a pydantic schema.
    * `day_of_agent` - called by the `in_trip_agent` to provide in_trip on the day and in the moment transit information, getting from A to B. Implemented using dynamic instructions.
    * `flight_search_agent` -  mocked flight search given origin, destination, outbound and return dates.
    * `flight_seat_selection_agent` -  mocked seat selection, some seats are not available.
    * `hotel_search_agent` - mocked hotel selection given destination, outbound and return dates.
    * `hotel_room_selection_agent` - mocked hotel room selection.
    * `confirm_reservation_agent` - mocked reservation.
    * `payment_choice` - mocked payment selection, Apple Pay will not succeed, Google Pay and Credit Card will.
    * `payment_agent` - mocked payment processing.
*   **Memory:** 
    * All agents and tools in this example use the Agent Development Kit's internal session state as memory.
    * The session state is used to store information such as the itinerary, and temporary AgentTools' responses.
    * There are a number of premade itineraries that can be loaded for test runs. See 'Running the Agent' below on how to run them.

## Setup and Installation (Original ADK Agent)

This section details setting up the core ADK agent if you intend to run it directly using `adk` commands or for deeper development on the agent itself. For running the Web Application, see the new section above and `testing_guide.md`.

### Folder Structure
The folder structure now includes the web application components:
```
.
├── README.md
├── travel-concierge-arch.png
├── pyproject.toml
├── frontend/                     <-- NEW Web Application UI
│   ├── index.html
│   ├── api_keys.html
│   └── ... (CSS, JS files)
├── backend_app.py                <-- NEW Web Application Backend
├── travel_agent_service.py       <-- NEW Web Application Service Layer
├── testing_guide.md              <-- NEW Web Application Test Guide
├── travel_concierge/
│   ├── shared_libraries/
│   ├── tools/
│   └── sub_agents/
│       ├── inspiration/
│       ├── planning/
│       ├── booking/
│       ├── pre_trip/
│       ├── in_trip/
│       └── post_trip/
├── tests/
│   └── unit/
├── eval/
│   └── data/
└── deployment/
```

### Prerequisites (Original ADK Agent)

- Python 3.11+
- Google Cloud Project (for Vertex AI integration)
- API Key for [Google Maps Platform Places API](https://developers.google.com/maps/documentation/places/web-service/get-api-key)
- Google Agent Development Kit 1.0+
- Poetry: Install Poetry by following the instructions on the official Poetry [website](https://python-poetry.org/docs/)

### Installation (Original ADK Agent)

1.  Clone the repository:

    ```bash
    git clone https://github.com/google/adk-samples.git
    cd adk-samples/python/agents/travel-concierge
    ```
    NOTE: From here on, all command-line instructions shall be executed under the directory  `travel-concierge/` unless otherwise stated.

2.  Install dependencies using Poetry or pip:

    ```bash
    poetry install
    ```

3.  Set up Google Cloud credentials:

    Otherwise:
    - At the top directory `travel-concierge/`, make a `.env` by copying `.env.example`
    - Set the following environment variables.
    - To use Vertex, make sure you have the Vertex AI API enabled in your project.
    ```
    # Choose Model Backend: 0 -> ML Dev, 1 -> Vertex
    GOOGLE_GENAI_USE_VERTEXAI=1
    # GOOGLE_API_KEY=YOUR_VALUE_HERE # For ML Dev or if GOOGLE_GENAI_USE_VERTEXAI=0

    # Vertex backend config
    GOOGLE_CLOUD_PROJECT=__YOUR_CLOUD_PROJECT_ID__
    GOOGLE_CLOUD_LOCATION=us-central1

    # Places API
    GOOGLE_PLACES_API_KEY=__YOUR_API_KEY_HERE__

    # GCS Storage Bucket name - for Agent Engine deployment test
    GOOGLE_CLOUD_STORAGE_BUCKET=YOUR_BUCKET_NAME_HERE

    # Sample Scenario Path - Default is an empty itinerary
    # This will be loaded upon first user interaction when running ADK directly.
    # For the Web Application, example loading is handled by a button in the UI.
    #
    # TRAVEL_CONCIERGE_SCENARIO=travel_concierge/profiles/itinerary_seattle_example.json
    TRAVEL_CONCIERGE_SCENARIO=travel_concierge/profiles/itinerary_empty_default.json
    ```
    *Note: When using the Web Application, API keys are managed via its UI, not primarily through these `.env` variables for the Flask server's direct use of the agent.*

4. Authenticate your GCloud account.
    ```bash
    gcloud auth application-default login
    ```

5. Activate the virtual environment set up by Poetry, run:
    ```bash
    eval $(poetry env activate)
    (travel-concierge-py3.12) $ # Virtualenv entered
    ```
    Repeat this command whenever you have a new shell, before running the commands in this README.

## Running the Agent (Original ADK Methods)

This section describes how to run the agent using ADK's built-in tools, which is different from running the Web Application described earlier.

### Using `adk`

ADK provides convenient ways to bring up agents locally and interact with them.
You may talk to the agent using the CLI:

```bash
# Under the travel-concierge directory:
adk run travel_concierge
```

or via its web interface:
```bash
# Under the travel-concierge directory:
adk web
```

This will start a local web server on your machine. You may open the URL, select "travel_concierge" in the top-left drop-down menu, and
a chatbot interface will appear on the right. 

The conversation is initially blank. For an outline on the concierge interaction, see the section [Sample Agent interaction](#sample-agent-interaction) 

Here is something to try: 
* "Need some destination ideas for the Americas"
* After interacting with the agents for a while, you may ask: "Go ahead to planning".


### Programmatic Access (ADK Server)

Below is an example of interacting with the agent as a server using Python with ADK's server.
First, establish an API server for the `travel_concierge` package:
```bash
adk api_server travel_concierge
```
This starts a FastAPI server at http://127.0.0.1:8000.
Example client:
```bash
python tests/programmatic_example.py
```
The `tests/programmatic_example.py` also illustrates how to handle events and different types of agent responses, which inspired some of the design for the Web Application's rich content display.


### Sample Agent interaction

Two example sessions are provided to illustrate how the Travel Concierge operates.
- Trip planning from inspiration to finalized bookings for a trip to Peru ([`tests/pre_booking_sample.md`](tests/pre_booking_sample.md)).
- In-trip experience for a short get away to Seattle, simulating the passage of time using a tool ([`tests/post_booking_sample.md`](tests/post_booking_sample.md)).

### Worth Trying (Direct ADK Interaction)

Instead of interacting with the concierge one turn at time. Try giving it the entire instruction, including decision making criteria, and watch it work, e.g.

  *"Find flights to London from JFK on April 20th for 4 days. Pick any flights and any seats; also Any hotels and room type. Make sure you pick seats for both flights. Go ahead and act on my behalf without my input, until you have selected everything, confirm with me before generating an itinerary."*

Without specifically optimizing for such usage, this cohort of agents seem to be able to operate by themselves on your behalf with very little input.


## Running Tests (Original ADK Agent)

To run the illustrative tests and evaluations for the core ADK agent, install the extra dependencies and run `pytest`:

```
poetry install --with dev
pytest
```

The different tests can also be run separately:

To run the unit tests, just checking all agents and tools responds:
```
pytest tests
```

To run agent trajectory tests:
```
pytest eval
```

## Deploying the Agent (Original ADK Agent to Vertex AI)

To deploy the agent to Vertex AI Agent Engine, run:

```bash
poetry install --with deployment
python deployment/deploy.py --create
```
When this command returns, if it succeeds it will print an AgentEngine resource
id that looks something like this:
```
projects/************/locations/us-central1/reasoningEngines/7737333693403889664
```

To quickly test that the agent has successfully deployed, 
run the following command for one turn with the agent "Looking for inspirations around the Americas":
```bash
python deployment/deploy.py --quicktest --resource_id=<RESOURCE_ID>
```
This will return a stream of JSON payload indicating the deployed agent is functional.

To delete the agent, run the following command (using the resource ID returned previously):
```bash
python3 deployment/deploy.py --delete --resource_id=<RESOURCE_ID>
```

## Application Development (Original ADK Agent)

### Callbacks and initial State

The `root_agent` in this demo currently has a `before_agent_callback` registered to load an initial state from a file (defined by `TRAVEL_CONCIERGE_SCENARIO`) into the session state. This is primarily for ease of use with ADK UIs and direct runs. For the Web Application, example loading is handled explicitly via an API endpoint.

### Memory vs States

This example uses session states as memory. In production, user profiles and itineraries would typically be persisted in external databases.

### MCP

An example using Airbnb's MCP server is included in `tests/mcp_abnb.py`. This test sets up an MCP server connection for the `planning_agent`. For the Web Application to display Airbnb results, the ADK agent it interacts with (via `travel_agent_service.py`) must be similarly configured and the MCP server must be accessible to it.

To try the `mcp_abnb.py` example directly:
1.  Ensure Node.js and npx are installed.
2.  Run from `travel-concierge/` directory: `python -m tests.mcp_abnb`

Making sure:
```
$ which node
/Users/USERNAME/.nvm/versions/node/v22.14.0/bin/node

$ which npx
/Users/USERNAME/.nvm/versions/node/v22.14.0/bin/npx
```

Then, under the `travel-concierge/` directory, run the test with:
```
python -m tests.mcp_abnb
```

You will see outputs on the console similar to the following:
```
[user]: Find me an airbnb in San Diego, April 9th, to april 13th, no flights nor itinerary needed. No need to confirm, simply return 5 choicess, remember to include urls.

( Setting up the agent and the tool ) 

Server started with options: ignore-robots-txt
Airbnb MCP Server running on stdio

Inserting Airbnb MCP tools into Travel-Concierge...
...
FOUND planning_agent

( Execute: Runner.run_async() ) 

[root_agent]: transfer_to_agent( {"agent_name": "planning_agent"} )
...
[planning_agent]: airbnb_search( {"checkout": "2025-04-13", "location": "San Diego", "checkin": "2025-04-09"} )

[planning_agent]: airbnb_search responds -> {
  "searchUrl": "https://www.airbnb.com/s/San%20Diego/homes?checkin=2025-04-09&checkout=2025-04-13&adults=1&children=0&infants=0&pets=0",
  "searchResults": [
    {
      "url": "https://www.airbnb.com/rooms/24669593",
      "listing": {
        "id": "24669593",
        "title": "Room in San Diego",
        "coordinate": {
          "latitude": 32.82952,
          "longitude": -117.22201
        },
        "structuredContent": {
          "mapCategoryInfo": "Stay with Stacy, Hosting for 7 years"
        }
      },
      "avgRatingA11yLabel": "4.91 out of 5 average rating,  211 reviews",
      "listingParamOverrides": {
        "categoryTag": "Tag:8678",
        "photoId": "1626723618",
        "amenities": ""
      },
      "structuredDisplayPrice": {
        "primaryLine": {
          "accessibilityLabel": "$9,274 TWD for 4 nights"
        },
        "explanationData": {
          "title": "Price details",
          "priceDetails": "$2,319 TWD x 4 nights: $9,274 TWD"
        }
      }
    },
    ...
    ...
  ]
}

[planning_agent]: Here are 5 Airbnb options in San Diego for your trip from April 9th to April 13th, including the URLs:

1.  Room in San Diego: [https://www.airbnb.com/rooms/24669593](https://www.airbnb.com/rooms/24669593)
2.  Room in San Diego: [https://www.airbnb.com/rooms/5360158](https://www.airbnb.com/rooms/5360158)
3.  Room in San Diego: [https://www.airbnb.com/rooms/1374944285472373029](https://www.airbnb.com/rooms/1374944285472373029)
4.  Apartment in San Diego: [https://www.airbnb.com/rooms/808814447273523115](https://www.airbnb.com/rooms/808814447273523115)
5.  Room in San Diego: [https://www.airbnb.com/rooms/53010806](https://www.airbnb.com/rooms/53010806)
```

### GUI (Considerations for Rich Output - relevant to Web App)

The section in the original README about "GUI" and handling different agent responses (cards, maps, etc.) via ADK Events is highly relevant to how the Web Application's `chat.js` and `travel_agent_service.py` attempt to parse and render rich content. The `tests/programmatic_example.py` was a key reference.

## Customization (Original ADK Agent)

Ideas for customizing the core ADK agent:

*   Load different premade itineraries (see `.env` and `TRAVEL_CONCIERGE_SCENARIO`).
*   Create your own itineraries based on `types.py`.
*   Integrate with real external APIs for flights, hotels, etc.
*   Refine agent logic for more complex scenarios.

## Troubleshoot (Original ADK Agent)

Common issues when interacting directly with the ADK agent:
- "Malformed" function calls/responses: Try telling the agent to "try again".
- Agent calling wrong tools: Try "wrong tool, try again".
- Agent stops mid-action: Nudge with "what's next".
These are less relevant when using the Web Application, as the interaction is mediated.

## Disclaimer

This agent sample (both the core ADK agent and the Web Application) is provided for illustrative purposes only and is not intended for production use. It serves as a basic example and a foundational starting point. Users are responsible for further development, testing, and security.