import streamlit as st
import requests
import json
import time
import uuid

# Constants
# N8N_WEBHOOK_URL = st.secrets["N8N_PRODUCTION_WEBHOOK_URL"]
N8N_WEBHOOK_URL = st.secrets["N8N_TEST_WEBHOOK_URL"]
REQUEST_LIMIT_SECONDS = 5


# ---------- UI SETUP ----------
def setup_ui():
    st.title("🏠 Zillow Homes Finder")
    st.write("*What kind of home you’re looking for?*")

# ---------- SESSION STATE INIT ----------
def init_session_state():
    defaults = {
        "chat_history": [],
        "last_query_sent": "",
        "last_msg_index": 0,
        "last_request_time": 0,
        "session_id": str(uuid.uuid4()),
        "chatting_to_get_url": True,
        "final_url": '',
    }
    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val

# ---------- RENDER CHAT ----------
def render_chat():
    """Render all chat messages in current session."""
    for msg in st.session_state.chat_history:
        st.chat_message(msg["role"]).write(msg["message"])

def render_message(role: str, message: str):
    """Add a message to the chat history."""
    st.session_state.chat_history.append({"role": role, "message": message})
    st.session_state.last_msg_index += 1
    st.chat_message(role).write(message)

# ---------- GETTERS ----------
def get_last_user_message():  # sourcery skip: use-next
    """Return the most recent user message."""
    for msg in reversed(st.session_state.chat_history):
        if msg["role"] == "user":
            return msg["message"]
    return None

# ---------- HELPER ----------
def user_sends_too_often():
    """Add a delay between messages to avoid rate limits by AI"""
    # Calculate time since last message
    current_time = time.time()
    time_since_last_request = round(current_time - st.session_state.last_request_time)
    
    if time_since_last_request < REQUEST_LIMIT_SECONDS:
        # remaining time in sec before user can send another message & handled by AI
        remaining_time = REQUEST_LIMIT_SECONDS - time_since_last_request
        # Block the request and show an error
        st.warning(f"Please wait **{remaining_time} seconds** before sending another request.")
        return True
    else:
        # Cooldown passed. Update the timestamp BEFORE sending the request.
        st.session_state.last_request_time = current_time
        return False

# ---------- CALLBACK ----------
def send_request_to_n8n(user_message: str):
    """Send user's message to the n8n webhook and process the response."""
    with st.spinner("Generating your search URL..."):
        try:
            session_id = st.session_state.session_id
            payload = {"search_query_message": user_message, 'session_id': session_id}
            response = requests.post(N8N_WEBHOOK_URL, json=payload, timeout=30)
            response.raise_for_status()

            data = response.json()
            search_url = data.get("search_url")
            error = data.get("error_message")

            if error:
                render_message("assistant", error)
            elif search_url:
                render_message(
                    "assistant",
                    f"🔗 Is this your [Search URL]({search_url})?\n\n"
                    "If not, modify the filters and paste the final URL here.\n"
                    "Or simply reply with **yes** to confirm!",
                )

            # mark as processed
            st.session_state.last_query_sent = user_message
            st.session_state.last_request_time = time.time()

        except Exception as e:
            render_message("assistant", f"Error: {e}")



# ---------- CHAT MODES ----------
def chat_to_get_url():
    """Chatbot interacts with user until we get the final search URL"""

    # Always render full chat before processing new message
    render_chat()

    # Handle new message input
    user_query = st.chat_input("e.g.: Multi family homes in NY with 2 baths & 3 bedroom...")
    if user_query:
        render_message("user", user_query)

    last_msg = get_last_user_message()

    # Send only if new message and not repeated
    if last_msg and last_msg != st.session_state.last_query_sent and not user_sends_too_often():
        send_request_to_n8n(last_msg)

def scraping():
    """Render UI after scraping has started"""
    render_chat()

    with st.spinner("### 🔍 Great! Searching homes for you..."):
        st.write(f"Your Scrape started at [This Page]('https://example.com)")
        time.sleep(4)

# ---------- MAIN CHAT FLOW ----------
def main():
    setup_ui()
    init_session_state()

    if st.session_state.chatting_to_get_url:
        chat_to_get_url()
        return
    
    scraping()


if __name__ == "__main__":
    main()
