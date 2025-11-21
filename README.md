---
title: HomeFinder AI
emoji: 🚀
colorFrom: red
colorTo: red
sdk: docker
app_port: 8501
tags:
- streamlit
pinned: false
short_description: Find Zillow homes then Extracts their details for further an
---

# 🏡 HomeFinder AI

HomeFinder AI is an innovative, AI-powered tool designed to revolutionize the residential property search process in the United States. By replacing traditional, form-based searching with a conversational chat interface, the application quickly converts natural language housing requests into actionable, analyzed market data.

---

## 🚀 Overview

Tired of endless clicks and confusing search filters? HomeFinder AI uses cutting-edge language models to understand your ideal home description, automates the complex data collection process via Apify, and presents the key market insights you need to make the best decision.

## ✨ Core Features

* **Conversational Interface:** Simply chat with the AI about your dream home (e.g., "I need a 3-bedroom house near a park in Miami under $500k").
* **Intelligent Query Construction:** The AI extracts specific keywords and details from your text, then automatically constructs a precise search URL for platforms like Zillow.
* **User Confirmation & Editing:** The constructed URL is presented to you for confirmation or modification before launching the scrape.
* **Automated Data Scraping:** Utilizing a specialized **[Zillow Scraper on Apify](https://apify.com/mido_99/zillow-scraper)**, the tool performs a robust data collection run on the finalized search parameters.
* **Analytical Dashboard:** Once the scrape is complete, results are displayed in a clean, modern web interface featuring:
    * Quick Analytics (Best Deals, Cheapest/Most Expensive properties, etc...).
    * Key property distribution analysis (beds, baths, price ranges).
    * Nicely formatted, easy-to-read property listings.

![HomePage](https://i.ibb.co/84gHX9fW/Screenshot-2025-11-20-203522.png)
*Homepage*

---

## 🧠 How It Works (More Technical)

The application leverages a modern, multi-tool backend for orchestration and delivery:

1. **Frontend Interaction (Streamlit)**: The user interacts entirely through a Streamlit interface, which provides a convenient and modern web chat environment. User input (the home query) is captured here.

2. **Intent Detection & Orchestration (n8n AI Agent Workflow):**
   - The Streamlit frontend relays the user's message to a dedicated n8n AI Agent Workflow running in the background.
   - This workflow utilizes AI to determine the user's intent: Is the user starting a general topic, asking to construct a URL from scratch, modifying an existing URL, or ready to launch a scrape?
   - Based on the intent, the n8n agent constructs the appropriate Zillow search URL.

3. **Confirmation & Action Delegation:** The generated URL is sent back to the Streamlit UI for the user to confirm or edit.

4. **Data Fetching Workflow (Apify):**
   - user confirmation, the n8n workflow triggers a specific data fetching process by initiating a run on  [My Zillow Scraper](https://apify.com/mido_99/zillow-scraper).
   - The application monitors the Apify run until completion, guaranteeing the return of a comprehensive, structured dataset.

5. **Analysis & Visualization (Streamlit):**
   - returned data is ingested directly by the Streamlit application.
   - Quick analytical and statistical calculations are performed on the raw data (e.g., calculating price-per-square-foot, determining distribution of beds/baths).
   - The results are visualized nicely using Streamlit's built-in charting and data display capabilities, providing an immediate, insightful dashboard.

---

## 🌐 Live Application

➡️ You can try **HomeFinder AI** hosted on my [HuggingFace](https://mido-99-home-finder.hf.space/):

---

## 💬 Use Example

![Chat](https://i.ibb.co/r28V74b2/Screenshot-2025-11-20-223059.png)
*You may chat in human language of course :) I just used this for the example*

---

![Prices Buckets](https://i.ibb.co/W4C7pzj6/Screenshot-2025-11-20-223303.png)
*Prices Buckets*

---

![Best Deals](https://i.ibb.co/LhhzTQMD/Screenshot-2025-11-20-223323.png)
*Best Deals*

---

![Cheapest & Most expensive Homes](https://i.ibb.co/wkFhP45/Screenshot-2025-11-20-223343.png)
*Cheapest & Most expensive Homes*

---

*Cheapest & Most expensive Homes*
![Beds & Baths Distribution](https://i.ibb.co/7tFhsL4y/Screenshot-2025-11-20-223359.png)
*Beds & Baths Distribution*

