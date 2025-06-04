## Frontend Design for Travel Concierge

**Overall Style:** Glassmorphic (frosted glass effect for cards and key UI elements), modern, clean, and intuitive.

**Color Palette:**
*   Primary Background: A subtle gradient or a high-quality travel-themed image (slightly blurred).
*   Card Background: Semi-transparent white/light grey with blur effect (`backdrop-filter: blur(10px); background-color: rgba(255, 255, 255, 0.1);`).
*   Text Color: Dark grey or black for readability, with a lighter secondary color.
*   Accent Color: A vibrant color (e.g., teal, coral, or a warm blue) for buttons, icons, and highlights.

**Typography:**
*   Use a clean, sans-serif font family (e.g., Inter, Roboto, Open Sans).

### Part 1: API Key Management Screen (`api_keys.html`)

**Layout:**
*   Centered content on the page.
*   A single glassmorphic card containing the form.
*   App Title/Logo at the top.

**Elements within the card:**
1.  **Title:** "Setup Your API Keys"
2.  **Instructional Text:** "Please provide your API keys to enable full functionality of the Travel Concierge. Your keys will be stored locally in your browser."
3.  **Input Field for Google Places API Key:**
    *   Label: "Google Places API Key"
    *   Input type: `text` or `password` (for basic obfuscation, though local storage is still accessible).
    *   Placeholder: "Enter your Google Places API Key"
4.  **Save Button:**
    *   Text: "Save API Key"
    *   Style: Accent color background, rounded corners.
5.  **Status Message Area:** Below the button, to display success ("API Key Saved!") or error messages.
6.  **Link/Button to Chat:** "Go to Travel Concierge" (becomes active/visible once a key is saved).

**User Flow:**
1.  User visits the page.
2.  Enters their Google Places API Key.
3.  Clicks "Save API Key".
4.  Key is saved to browser's local storage.
5.  Success message is displayed.
6.  User can then navigate to the chat interface.

### Part 2: Main Chat Interface Screen (`index.html`)

**Layout:**
*   Full-height chat interface.
*   Header (optional, could just be a title within the chat area).
*   Chat messages area (scrollable).
*   Fixed input area at the bottom.

**Elements:**
1.  **Chat Messages Area:**
    *   Will display a chronological list of user messages and agent responses.
    *   User messages: Simple text bubbles, perhaps aligned to the right, different background color.
    *   Agent responses:
        *   **Text responses:** Displayed in glassmorphic cards, aligned to the left.
        *   **Structured responses (e.g., destination suggestions, itinerary items):**
            *   Each item (destination, flight, hotel, activity) will be a separate glassmorphic card within the agent's message bubble or as a horizontal carousel of cards if multiple items are returned.
            *   **Destination Card Example:**
                *   Image (if available from API response)
                *   Title (e.g., "Malé, Maldives")
                *   Short description/highlights
                *   Rating (if available)
                *   "View Details" or "Select" button (for future interactivity)
            *   **Itinerary Item Card Example:**
                *   Icon representing type (flight, hotel, activity)
                *   Title (e.g., "Flight to SFO", "Stay at Grand Hyatt")
                *   Key details (dates, times, confirmation # if available)
    2.  **Chat Input Area (Bottom):**
        *   Glassmorphic styled bar.
        *   Text input field: "Ask your travel question..."
        *   Send button (icon or text).
    3.  **API Key Status/Link (Optional, in a corner or settings menu):**
        *   Indicates if API key is set.
        *   Link to `api_keys.html` to update the key.
    4.  **Loading Indicator:** Visible when the agent is processing a query.

**User Flow:**
1.  User visits `index.html`.
2.  If API key is not set in local storage, they might be prompted or shown a message to set it up (with a link to `api_keys.html`).
3.  User types a question in the input field and hits send.
4.  Message appears in the chat area.
5.  Loading indicator appears while waiting for the agent.
6.  Agent's response appears in the chat area, formatted as text or structured cards.
7.  Conversation continues.

---
This document outlines the visual and structural design for the frontend. Actual implementation will translate these concepts into HTML, CSS, and JavaScript.
