import os
import uuid
import asyncio
from typing import Dict, Any, Union

from google.adk.runtime.runner import SessionRunner
from travel_agent_core.agent import root_agent
from travel_agent_core.shared_libraries import constants

ENV_GOOGLE_API_KEY = "GOOGLE_API_KEY"
ENV_GOOGLE_PLACES_API_KEY = "GOOGLE_PLACES_API_KEY"
ENV_GOOGLE_GENAI_USE_VERTEXAI = "GOOGLE_GENAI_USE_VERTEXAI"
ENV_TRAVEL_CONCIERGE_SCENARIO = "TRAVEL_CONCIERGE_SCENARIO"

def _extract_agent_output_from_events(events: list) -> Union[str, Dict[str, Any]]:
    if not events:
        return "No response from agent."

    final_text_parts = []
    structured_response: Dict[str, Any] = {}

    for event in events:
        # Debug: print(f"Event: {event.name}, Outputs: {event.outputs}")
        if event.name == "agent_says" and event.outputs:
            if "text" in event.outputs and event.outputs["text"]:
                final_text_parts.append(event.outputs["text"])

            # Agent might embed structured data directly in 'agent_says'
            if "destinations" in event.outputs and isinstance(event.outputs["destinations"], list):
                structured_response["destinations"] = event.outputs["destinations"]
            if "cards" in event.outputs and isinstance(event.outputs["cards"], list):
                structured_response["cards"] = event.outputs["cards"]
            if "map_data" in event.outputs and isinstance(event.outputs["map_data"], dict):
                structured_response["map_data"] = event.outputs["map_data"]
            if "actions" in event.outputs and isinstance(event.outputs["actions"], list):
                structured_response["actions"] = event.outputs["actions"]

        # Look for tool responses, specifically for Airbnb
        # Based on mcp_abnb.py, this might be a 'function_response' named 'airbnb_search'
        # The actual JSON is in event.outputs.response (or event.outputs.result.content[0].text if it was stringified)
        elif event.name == "function_response" and event.outputs and event.outputs.get("name") == "airbnb_search":
            # The mcp_abnb.py example shows the response is in event.outputs.response
            # And within that, it might be further nested if the tool itself wraps its output.
            # For airbnb_search, it seems the direct response IS the JSON we need.
            tool_resp_data = event.outputs.get("response")
            if isinstance(tool_resp_data, dict) and "searchResults" in tool_resp_data:
                structured_response["airbnb_listings"] = tool_resp_data["searchResults"]
                if "searchUrl" in tool_resp_data:
                    structured_response["airbnb_search_url"] = tool_resp_data["searchUrl"]
                # If the agent also says something about these listings, that text will be captured
                # by an 'agent_says' event. We might want to associate it.
                if "text" not in structured_response and final_text_parts: # Add any preceding text
                    structured_response["text"] = " ".join(final_text_parts)
                elif "text" not in structured_response:
                    structured_response["text"] = "Here are some Airbnb listings I found:"


    # Assemble the final response
    if final_text_parts and "text" not in structured_response:
        structured_response["text"] = " ".join(final_text_parts)

    if any(key in structured_response for key in ["destinations", "cards", "map_data", "actions", "airbnb_listings"]):
        if "text" not in structured_response:
            # Default text if a structure is present but no specific text was found for it
            structured_response["text"] = "Please see the information below:" if not final_text_parts else " ".join(final_text_parts)
        return structured_response

    if final_text_parts:
        return " ".join(final_text_parts)

    if events and events[-1].outputs and "text" in events[-1].outputs: # Fallback
        return events[-1].outputs["text"]

    return "Agent did not provide a recognizable output."


async def _run_agent_turn_async_helper(
    user_query: str,
    session_id: str,
    session_state: Dict[str, Any],
    scenario_path: str = None
) -> Dict[str, Any]:

    original_scenario_env = os.environ.get(ENV_TRAVEL_CONCIERGE_SCENARIO)
    if scenario_path:
        os.environ[ENV_TRAVEL_CONCIERGE_SCENARIO] = scenario_path

    try:
        session_runner = SessionRunner(agent=root_agent)
        agent_inputs = {"text": user_query}

        events = []
        async for event in session_runner.run_turn_async(
            session_id=session_id, inputs=agent_inputs, state=session_state
        ):
            events.append(event)

    finally:
        if original_scenario_env is None:
            if ENV_TRAVEL_CONCIERGE_SCENARIO in os.environ: del os.environ[ENV_TRAVEL_CONCIERGE_SCENARIO]
        else:
            os.environ[ENV_TRAVEL_CONCIERGE_SCENARIO] = original_scenario_env

    return {"events": events, "updated_session_state": session_state}


def _invoke_agent_core(
    user_query: str,
    google_places_api_key: str,
    gemini_api_key: str,
    session_id: str = None,
    user_profile: Dict[str, Any] = None,
    itinerary: Dict[str, Any] = None,
    scenario_path: str = None
) -> Dict[str, Any]:
    original_places_key = os.environ.get(ENV_GOOGLE_PLACES_API_KEY)
    original_google_api_key = os.environ.get(ENV_GOOGLE_API_KEY)
    original_use_vertexai = os.environ.get(ENV_GOOGLE_GENAI_USE_VERTEXAI)

    os.environ[ENV_GOOGLE_PLACES_API_KEY] = google_places_api_key
    os.environ[ENV_GOOGLE_API_KEY] = gemini_api_key
    os.environ[ENV_GOOGLE_GENAI_USE_VERTEXAI] = "0"

    current_session_id = session_id or str(uuid.uuid4())

    session_state = {
        constants.PROF_KEY: user_profile or {},
        constants.ITIN_KEY: itinerary or {}
    }
    if scenario_path and not itinerary and not user_profile:
        session_state[constants.ITIN_INITIALIZED] = False
    elif itinerary:
        session_state[constants.ITIN_INITIALIZED] = True


    agent_response_content: Union[str, Dict[str, Any]]
    error_message = None
    updated_session_state = session_state

    try:
        result = asyncio.run(
             _run_agent_turn_async_helper(user_query, current_session_id, session_state, scenario_path)
        )

        raw_events = result.get("events", [])
        agent_response_content = _extract_agent_output_from_events(raw_events)
        updated_session_state = result.get("updated_session_state", session_state)

    except Exception as e:
        print(f"Error invoking ADK agent: {e}")
        agent_response_content = f"Error during agent execution: {e}"
        error_message = str(e)
    finally:
        if original_places_key is None:
            if ENV_GOOGLE_PLACES_API_KEY in os.environ: del os.environ[ENV_GOOGLE_PLACES_API_KEY]
        else:
            os.environ[ENV_GOOGLE_PLACES_API_KEY] = original_places_key

        if original_google_api_key is None:
            if ENV_GOOGLE_API_KEY in os.environ: del os.environ[ENV_GOOGLE_API_KEY]
        else:
            os.environ[ENV_GOOGLE_API_KEY] = original_google_api_key

        if original_use_vertexai is None:
            if ENV_GOOGLE_GENAI_USE_VERTEXAI in os.environ: del os.environ[ENV_GOOGLE_GENAI_USE_VERTEXAI]
        else:
            os.environ[ENV_GOOGLE_GENAI_USE_VERTEXAI] = original_use_vertexai

    return {
        "response": agent_response_content,
        "session_id": current_session_id,
        "user_profile": updated_session_state.get(constants.PROF_KEY, {}),
        "itinerary": updated_session_state.get(constants.ITIN_KEY, {}),
        "error": error_message
    }

def invoke_travel_agent(
    user_query: str,
    google_places_api_key: str,
    gemini_api_key: str,
    session_id: str = None,
    user_profile: Dict[str, Any] = None,
    itinerary: Dict[str, Any] = None,
) -> Dict[str, Any]:
    return _invoke_agent_core(
        user_query, google_places_api_key, gemini_api_key,
        session_id, user_profile, itinerary, scenario_path=None
    )

def load_example_itinerary_agent(
    user_id: str,
    google_places_api_key: str,
    gemini_api_key: str,
) -> Dict[str, Any]:
    # This path will be relative to where the agent core logic is,
    # so if travel_agent_core is the top-level package, this path needs to be valid from there.
    # Assuming the profiles are part of the travel_agent_core package.
    scenario_file_path = 'travel_agent_core/profiles/itinerary_seattle_example.json'
    initial_query = "Describe my loaded itinerary and suggest some initial actions."

    return _invoke_agent_core(
        initial_query, google_places_api_key, gemini_api_key,
        session_id=None, user_profile=None, itinerary=None,
        scenario_path=scenario_file_path
    )

if __name__ == '__main__':
    print("Testing travel_agent_service.py with ADK SessionRunner...")

    test_places_key = os.environ.get("TEST_GOOGLE_PLACES_API_KEY")
    test_gemini_key = os.environ.get("TEST_GEMINI_API_KEY")
    is_mock_mode = not (test_places_key and test_gemini_key)

    original_invoke_agent_core = _invoke_agent_core
    if is_mock_mode:
        print("\nWARNING: TEST_GOOGLE_PLACES_API_KEY and/or TEST_GEMINI_API_KEY environment variables not set.")
        print("Service will use placeholder responses for testing without actual agent calls.\n")

        def _mock_invoke_travel_agent_core(user_query, **kwargs):
            mock_response_content = f"Mock Response: Agent not called (missing keys). Query: {user_query}"
            if "inspire" in user_query.lower() or "destinations" in user_query.lower():
                mock_response_content = {"text": "Mock: Here are some travel destination ideas:", "destinations": [{"name": "Mock Paris", "country": "France", "highlights": "City of Lights"}]}
            elif "map" in user_query.lower():
                 mock_response_content = {"text": "Mock: Showing a map for Eiffel Tower.", "map_data": {"latitude": 48.8584, "longitude": 2.2945, "zoom": 15, "marker_label": "Eiffel Tower"}}
            elif "actions" in user_query.lower():
                mock_response_content = {"text": "Mock: What would you like to do next?", "actions": [{"label": "Mock Hotels", "query": "Find mock hotels"}, {"label": "Mock Restaurants", "query": "Find mock restaurants"}]}
            elif "airbnb" in user_query.lower():
                mock_response_content = {
                    "text": "Mock: Here are some Airbnb listings:",
                    "airbnb_listings": [
                        {"id": "mock123", "title": "Cozy Mock Apartment", "url": "http://example.com/mock123", "avgRatingA11yLabel": "4.5 stars", "structuredDisplayPrice": {"primaryLine": {"accessibilityLabel": "$100 per night"}}},
                        {"id": "mock456", "title": "Sunny Mock Studio", "url": "http://example.com/mock456", "avgRatingA11yLabel": "4.8 stars", "structuredDisplayPrice": {"primaryLine": {"accessibilityLabel": "$120 per night"}}}
                    ],
                    "airbnb_search_url": "http://example.com/search"
                }
            return {"response": mock_response_content, "session_id": kwargs.get("session_id") or str(uuid.uuid4()), "user_profile": kwargs.get("user_profile") or {}, "itinerary": kwargs.get("itinerary") or {}, "error": "Test API keys not provided."}
        _invoke_agent_core = _mock_invoke_travel_agent_core

    import json

    print("\nTest 1: Query for Airbnb listings (Mock or Real)")
    airbnb_query_result = invoke_travel_agent(
        user_query="Find me an airbnb in San Diego",
        google_places_api_key=test_places_key or "dummy_places_key",
        gemini_api_key=test_gemini_key or "dummy_gemini_key"
    )
    print("Airbnb Query Response:")
    print(json.dumps(airbnb_query_result, indent=2))

    if is_mock_mode:
        _invoke_agent_core = original_invoke_agent_core # Restore original function

    print("\nNote: If testing with real agent, ensure it's configured (including MCP for Airbnb) and API keys are valid.")
