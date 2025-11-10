import streamlit as st
import requests
import json

# Your unique Webhook URL from n8n
N8N_WEBHOOK_URL = st.secrets["N8N_PRODUCTION_WEBHOOK_URL"] 
# N8N_WEBHOOK_URL = st.secrets["N8N_TEST_WEBHOOK_URL"] 

# UI
st.title("🏠 Zillow Homes Finder")
st.write("*What kind of home you’re looking for?*")

# Initialize chat history
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "last_query_sent" not in st.session_state:
    st.session_state.last_query_sent = ""
if "last_msg_index" not in st.session_state:
    st.session_state.last_msg_index = 0

# Capture new user input
user_query = st.chat_input("e.g.: Multi family homes in NY with 2 baths & 3 bedroom...")

if user_query:
    # Append user message
    st.session_state.chat_history.append({"role": "user", "message": user_query})

# Render full chat history once without touching last_msg_index
for msg in st.session_state.chat_history:
    st.chat_message(msg['role']).write(msg['message'])

# Get last message
last_user_msg = next(
    (
        msg["message"]
        for msg in reversed(st.session_state.chat_history)
        if msg["role"] == "user"
    ),
    None,
)

# Only send to n8n if this query hasn't been sent yet
if last_user_msg and last_user_msg != st.session_state.get("last_query_sent", ""):
    with st.spinner("Generating your search URL..."):
        try:
            # Send to LLM to check if valid homes search criteria
            payload = {"search_query_message": last_user_msg}
            response = requests.post(N8N_WEBHOOK_URL, json=payload, timeout=30)
            response.raise_for_status()
            results_data = response.json()
            # results_data has {'search_url': ...} or error_message if AI determines it's invalid
            search_url = results_data.get("search_url")
            error_message = results_data.get("error_message")

            # Early skip if invalid filters
            if error_message:
                st.session_state.chat_history.append({"role": "assistant", "message": error_message})
            elif search_url:
                # Display URL nicely
                st.session_state.chat_history.append(
                    {"role": "assistant", "message": f"🔗 Is this your [Search URL]({search_url})?\n\n"
                     "If not, You can modify the filters then copy & paste the final URL here. "
                     "Or simply reply with 'yes' to this!"
                    }
                )

            # Mark as processed
            st.session_state.last_query_sent = last_user_msg

        except Exception as e:
            st.session_state.chat_history.append({"role": "assistant", "message": f"Error: {e}"})
    
# Display most recent messages
recent_msgs = st.session_state.chat_history[st.session_state.last_msg_index +1 :]
for msg in recent_msgs:
    st.chat_message(msg['role']).write(msg['message'])
# Reset index
st.session_state.last_msg_index = len(st.session_state.chat_history)
