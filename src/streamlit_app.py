import streamlit as st
import requests
import json

# Your unique Webhook URL from n8n
N8N_WEBHOOK_URL = st.secrets["N8N_PRODUCTION_WEBHOOK_URL"] 

user_query = st.chat_input("Enter your real estate search criteria...")

if user_query:
    st.chat_message("user").write(user_query)
    
    try:

        with st.spinner("Generating your search URL..."):
            payload = {"search_query_message": user_query}
            try:
                response = requests.post(N8N_WEBHOOK_URL, json=payload, timeout=30)
                response.raise_for_status()
                results_data = response.json()

                # Assume results_data has {'search_url': ...}
                search_url = results_data.get("search_url", "URL not found")

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
        