import traceback
import streamlit as st
import requests
import time
import uuid
import pandas as pd
import os
from dotenv import load_dotenv
from typing import Literal

from templates.messages import empty_area_msg
from utils.data_analysis import (
    normalize_items, compute_kpis, rank_best_value, summarize_by_city, top_cheapest, top_expensive, 
    fancy_display_deals, display_bed_bath_distribution, plot_price_buckets
)

load_dotenv()
# Constants
CHAT_URL = os.getenv("N8N_PRODUCTION_CHAT")
# CHAT_URL = os.getenv("N8N_TEST_CHAT")
ANALYSIS_URL = os.getenv("N8N_PRODUCTION_HOMES_ANALYSIS")
REQUEST_LIMIT_SECONDS = 10


# ---------- SETUP UI ----------
def chat_ui():
    st.set_page_config(page_title="US Homes Finder", page_icon="🏠")
    st.title("🏡 HomeFinder AI ")

# ---------- SESSION STATE INIT ----------
def init_session_state():
    defaults = {
        "current_mode": 'chatting_to_get_url',
        "chat_history": [],
        "last_query_sent": '',
        "last_msg_index": 0,
        "last_request_time": 0,
        "session_id": str(uuid.uuid4()),
        "run_data": {},
        "pending_url": '',
        "ai_message": '',
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
def get_last_message(role: Literal['ai', 'assistant', 'user'] = 'user'):  # sourcery skip: use-next
    """Return the most recent message by role.
    
    Ex: to get last user message:
    ```python
    get_last_message('user')
    ```
    """
    for msg in reversed(st.session_state.chat_history):
        if msg["role"] == role:
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
            # mark as processed
            st.session_state.last_query_sent = user_message
            st.session_state.last_request_time = time.time()

            # Sent to n8n
            session_id = st.session_state.session_id
            pending_url = st.session_state.pending_url
            payload = {"search_query_message": user_message, 'session_id': session_id, 'pending_url': pending_url}
            response = requests.post(CHAT_URL, json=payload, timeout=60)
            response.raise_for_status()

            data = response.json()
            search_url = data.get("search_url")
            empty_area = data.get("empty_area")
            error = data.get("error_message")
            run_data = data.get("run_data")
            ai_message = data.get("ai_message")

            if error:
                render_message("ai", error)

            elif empty_area:
                render_message(
                    "ai",
                    empty_area_msg(search_url)
                )

            elif search_url:
                st.session_state.pending_url = search_url
                render_message(
                    "ai",
                    f"🔗 Is this your [Search URL]({search_url})?\n\n"
                    "If not, modify the filters and paste the final URL here.\n"
                    "Or simply reply with **yes** to confirm!",
                )

            elif run_data:
                st.session_state.run_data = run_data
                st.session_state.ai_message = ai_message
                st.session_state.current_mode = 'scraping'
                st.rerun()
            
            else:
                render_message('assistant', f"else cuaght the response data: {data}")

        except Exception as e:
            render_message("ai", f"Error: {e}")

def analyze_data(homes, user_max_price=None):
    """Show homes results after cleaning & analysis."""
    
    normalized = normalize_items(homes)

    # --- KPIs ---
    kpis = compute_kpis(normalized, user_max_price=user_max_price)
    st.header("📊 Market Insights")
    k1, k2, k3, k4 = st.columns(4)
    k1.metric("🏠 Homes Found", kpis["count"])
    k2.metric("⚖️ Avg Price", f"${kpis['avg_price']:,}" if kpis["avg_price"] else "N/A")
    k3.metric("⏱ Median Price", f"${kpis['median_price']:,}" if kpis["median_price"] else "N/A")
    k4.metric("💰 Max Price", f"${kpis['max_price']:,}" if kpis["max_price"] else "N/A")
    if kpis.get("percent_in_budget") is not None:
        st.info(f"🎯 **{kpis['percent_in_budget']}%** of homes match your budget")

    # --- Price Buckets ---
    st.subheader("💵 Price Distribution")
    plot_price_buckets(kpis["price_buckets"])

    # --- Avg price per bedroom ---
    if kpis["avg_price_per_bedroom"]:
        st.subheader("🛌 Average Price per Bedroom")
        st.dataframe(
            pd.DataFrame(
                [{"beds": b, "avg_price": p} for b, p in kpis["avg_price_per_bedroom"].items()]
            )
        )

    # --- Best deals ---
    st.subheader("🏆 Best Deals (Lowest $/sqft)")
    best = rank_best_value(normalized)
    fancy_display_deals(best)
    st.divider()

    # --- Top cheapest / expensive ---
    st.subheader("💸 Cheapest Homes")
    fancy_display_deals(top_cheapest(normalized))
    st.divider()

    st.subheader("💎 Most Expensive Homes")
    fancy_display_deals(top_expensive(normalized))
    st.divider()

    # --- City summary ---
    st.subheader("📍 Homes by City")
    city_stats = summarize_by_city(normalized)
    st.dataframe(city_stats)

    # --- Bed / Bath distribution ---
    st.subheader("🚿 Bed & Bath Counts")
    display_bed_bath_distribution(normalized)


# ---------- CHAT MODES ----------
def chat_to_get_url():
    """Chatbot interacts with user until we get the final search URL"""
    
    chat_ui()
    st.write("*What kind of home you’re looking for?*")

    # Always render full chat before processing new message
    render_chat()

    # Handle new message input
    user_query = st.chat_input("e.g.: Multi family homes in NY with 2 baths & 3 bedroom...")
    if user_query:
        render_message("user", user_query)

    last_msg = get_last_message("user")
    # Send only if new message and not repeated
    if last_msg and last_msg != st.session_state.last_query_sent and not user_sends_too_often():
        send_request_to_n8n(last_msg)


def scraping():  # sourcery skip: extract-method
    """Data Scraping and Analysis mode"""
    chat_ui()
    render_chat()

    # Load run data
    run_data = st.session_state.run_data
    # run_data = {
    #     'run_id': 'hdhW11Ye8vnIhCRbi',
    #     'run_url': 'https://console.apify.com/actors/runs/hdhW11Ye8vnIhCRbi#output'
    # }
    run_id, run_url, run_status = run_data.get('run_id'),  run_data.get('run_url'), run_data.get('status')

    with st.spinner("### 🔍 Searching homes for you..."):
        render_message("ai", st.session_state.ai_message)
        render_message(
            'assistant', 
            f"You can check your run [here]({run_url}).\n\n"
            "Once the run finishes, I'll show you a nice brief analysis on your data."
            )
        
        try:
            # Poll Run
            session_id = st.session_state.session_id
            payload = {"run_data": run_data, 'session_id': session_id}
            response = requests.post(ANALYSIS_URL, json=payload, timeout=None)
            response.raise_for_status()

            data = response.json()[0]
            homes = data.get('homes')
            error = data.get('error')

            if error:
                render_message('assistant', error['message'])
            
            elif homes:
                st.write('### 🔥 Here We Go')
                # Data Analysis
                analyze_data(homes)
        
        except Exception as e:
            st.error(traceback.format_exc())

# ---------- MAIN APP FLOW ----------
def main():
    
    init_session_state()

    if st.session_state.current_mode == 'chatting_to_get_url':
        chat_to_get_url()
        
    elif st.session_state.current_mode == 'scraping':
        scraping()
    
    #! For debug only
    # st.info(st.session_state)


if __name__ == "__main__":
    main()
