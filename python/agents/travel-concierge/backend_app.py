import os
from flask import Flask, request, jsonify
import json

try:
    # Added load_example_itinerary_agent to imports
    from travel_agent_service import invoke_travel_agent, load_example_itinerary_agent
except ImportError:
    import sys
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    try:
        from travel_agent_service import invoke_travel_agent, load_example_itinerary_agent
    except ImportError as e:
        print(f"Critical Import Error: Could not import agent services: {e}")
        def invoke_travel_agent(*args, **kwargs):
            return {
                "response": "Error: travel_agent_service not available (invoke).",
                "session_id": kwargs.get("session_id"), "user_profile": None, "itinerary": None,
                "error": "invoke_travel_agent could not be imported."
            }
        def load_example_itinerary_agent(*args, **kwargs):
            return {
                "response": "Error: travel_agent_service not available (load_example).",
                "session_id": str(os.urandom(16).hex()), "user_profile": None, "itinerary": None,
                "error": "load_example_itinerary_agent could not be imported."
            }

app = Flask(__name__)

api_keys_store: dict = {}
session_store: dict = {}

@app.route('/api/set_api_key', methods=['POST'])
def set_api_key():
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        keys_to_set = data.get('keys')

        if not user_id or not isinstance(keys_to_set, list):
            return jsonify({"status": "error", "message": "Missing user_id or keys array"}), 400

        if user_id not in api_keys_store:
            api_keys_store[user_id] = {}

        processed_keys_names = []
        for key_obj in keys_to_set:
            if isinstance(key_obj, dict) and 'name' in key_obj and 'api_key' in key_obj:
                api_keys_store[user_id][key_obj['name']] = key_obj['api_key']
                processed_keys_names.append(key_obj['name'])
            else:
                return jsonify({"status": "error", "message": "Invalid key object format in keys array"}), 400

        return jsonify({"status": "success", "message": f"API keys ({', '.join(processed_keys_names)}) set for user {user_id}"}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/load_example_itinerary', methods=['POST']) # Changed to POST to accept user_id in body
def handle_load_example_itinerary():
    try:
        data = request.get_json()
        user_id = data.get('user_id', 'default_user') # Default if not provided, though frontend sends it

        user_keys = api_keys_store.get(user_id, {})
        google_places_api_key = user_keys.get('google_places')
        gemini_api_key = user_keys.get('gemini')

        if not google_places_api_key or not gemini_api_key:
            return jsonify({"status": "error", "message": "API keys (Google Places and Gemini) not found for user. Please set them first."}), 401

        # Call the new service function
        agent_response_data = load_example_itinerary_agent(
            user_id=user_id, # Though not strictly needed by service if scenario is fixed
            google_places_api_key=google_places_api_key,
            gemini_api_key=gemini_api_key
        )

        new_session_id = agent_response_data.get('session_id')
        if new_session_id: # Save the new session state
            session_store[new_session_id] = {
                'user_profile': agent_response_data.get('user_profile'),
                'itinerary': agent_response_data.get('itinerary')
            }

        client_response = {
            "response": agent_response_data.get("response"),
            "session_id": new_session_id,
            "user_profile": agent_response_data.get("user_profile"), # Send profile back
            "itinerary": agent_response_data.get("itinerary"),     # Send itinerary back
            "error": agent_response_data.get("error")
        }
        return jsonify(client_response), 200

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route('/api/query', methods=['POST'])
def query_agent():
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        user_query = data.get('query')
        session_id_from_request = data.get('session_id')

        if not all([user_id, user_query]):
            return jsonify({"status": "error", "message": "Missing user_id or query"}), 400

        user_keys = api_keys_store.get(user_id, {})
        google_places_api_key = user_keys.get('google_places')
        gemini_api_key = user_keys.get('gemini')

        if not google_places_api_key:
            return jsonify({"status": "error", "message": "Google Places API key not found for user."}), 401
        if not gemini_api_key:
            return jsonify({"status": "error", "message": "Gemini API key not found for user."}), 401

        user_profile = None
        itinerary = None
        current_session_id = session_id_from_request

        if current_session_id and current_session_id in session_store:
            session_data = session_store[current_session_id]
            user_profile = session_data.get('user_profile')
            itinerary = session_data.get('itinerary')

        agent_response_data = invoke_travel_agent(
            user_query=user_query,
            google_places_api_key=google_places_api_key,
            gemini_api_key=gemini_api_key,
            session_id=current_session_id,
            user_profile=user_profile,
            itinerary=itinerary
        )

        new_session_id = agent_response_data.get('session_id')
        if new_session_id:
            session_store[new_session_id] = {
                'user_profile': agent_response_data.get('user_profile'),
                'itinerary': agent_response_data.get('itinerary')
            }
            if session_id_from_request and session_id_from_request != new_session_id and session_id_from_request in session_store:
                del session_store[session_id_from_request]

        client_response = {
            "response": agent_response_data.get("response"),
            "session_id": new_session_id,
            # Optionally return updated profile/itinerary on every query, or only when they change significantly
            # "user_profile": agent_response_data.get("user_profile"),
            # "itinerary": agent_response_data.get("itinerary"),
            "error": agent_response_data.get("error")
        }

        return jsonify(client_response), 200

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == "__main__":
    if not os.environ.get("FLASK_APP"):
        os.environ["FLASK_APP"] = "backend_app.py"
    app.run(debug=True, port=5001)
