import streamlit as st
import requests
import json

# Your unique Webhook URL from n8n
# N8N_WEBHOOK_URL = st.secrets["N8N_PRODUCTION_WEBHOOK_URL"] 
N8N_WEBHOOK_URL = st.secrets["N8N_TEST_WEBHOOK_URL"] 

# UI
st.title("🏠 Zillow Search Assistant")
st.write("*What kind of home you’re looking for?*")

# Initialize chat history
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "last_query_sent" not in st.session_state:
    st.session_state.last_query_sent = ""

# Capture new user input
user_query = st.chat_input("e.g.: Multi family homes in NY with 2 baths & 3 bedroom...")

if user_query:
    # Append user message
    st.session_state.chat_history.append({"role": "user", "message": user_query})

# Render full chat history first
for msg in st.session_state.chat_history:
    if msg["role"] == "user":
        st.chat_message("user").write(msg["message"])
    else:
        st.chat_message("assistant").write(msg["message"])

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
                st.session_state.chat_history.append({"role": "assistant", "message": "Your scrape started at this URL:"})
                st.session_state.chat_history.append({"role": "assistant", "message": search_url})

            # Mark as processed
            st.session_state.last_query_sent = last_user_msg

            except Exception as e:
                st.chat_message("assistant").write(f"Error fetching URL: {e}")
                search_url = None

        if search_url:
            # Display URL nicely
            st.chat_message("assistant").write("Your scrape started at this URL:")
            st.chat_message("assistant").text_area("Search URL", value=search_url, height=50)
            st.chat_message("assistant").write("Is this the final URL you want? If not, please modify the filters.")

            # Initialize state
            if "confirmed" not in st.session_state:
                st.session_state.confirmed = None
            if "final_url" not in st.session_state:
                st.session_state.final_url = None
            
           # Two buttons for confirmation
            col1, col2 = st.columns(2)
            with col1:
                if st.button("Yes, it's final"):
                    st.session_state.confirmed = True
                    st.session_state.final_url = search_url

            with col2:
                if st.button("No, I'll modify it"):
                    st.session_state.confirmed = False

            # Handle logic after button click
            if st.session_state.confirmed is True:
                st.chat_message("assistant").write(f"Great! Scraping will start for:\n{st.session_state.final_url}")

            elif st.session_state.confirmed is False:
                # Let user enter modified URL
                final_url_input = st.chat_input("Please enter your final URL:")
                if final_url_input:
                    st.session_state.final_url = final_url_input
                    st.chat_message("user").write(final_url_input)
                    st.chat_message("assistant").write(f"Final URL updated to:\n{st.session_state.final_url}")


    except requests.exceptions.Timeout:
        st.chat_message("assistant").error("The request timed out. The scraping process may be taking too long.")
    except Exception as e:
        st.chat_message("assistant").error(f"Error Occured: {e}")
        