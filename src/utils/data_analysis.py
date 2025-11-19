"""Homes Data Cleaning, Processing & Analysing functions."""
import re
import pandas as pd
import numpy as np
import streamlit as st
import altair as alt
from collections import Counter, defaultdict


#-------------- Clean ----------------#
def safe_price(h, hd):
    # 1) best field
    if h.get("unformattedPrice") is not None:
        return int(h["unformattedPrice"])

    # 2) check both price sources
    raw = h.get("price") or hd.get("price")
    if raw:
        cleaned = re.sub(r"[^\d]", "", raw)
        if cleaned.isdigit():
            return int(cleaned)

    # fallback
    return 0

def normalize_items(items: list[dict]) -> list[dict]:
    """Extract consistent fields from Zillow scraper results."""
    normalized = []
    warning_already_shown = False

    for item in items:
        try:
            h = item
            hd = h.get("hdpData", {}).get("homeInfo", {})

            normalized.append({
                "zpid": h.get("zpid"),
                "url": h.get("detailUrl"),
                "address": h.get("address"),
                "city": h.get("addressCity"),
                "state": h.get("addressState"),
                "zip": h.get("addressZipcode"),
                "price": safe_price(h, hd),
                "beds": h.get("beds") or hd.get("bedrooms"),
                "baths": h.get("baths") or hd.get("bathrooms"),
                "sqft": h.get("area") or hd.get("livingArea"),
                "lat": h.get("latLong", {}).get("latitude"),
                "lng": h.get("latLong", {}).get("longitude"),
                "img": h.get("imgSrc"),
                "zestimate": h.get("zestimate") or hd.get("zestimate"),
                "broker": h.get("brokerName") or hd.get("listing_sub_type"),
                "days_listed": hd.get("daysOnZillow"),
            })
        except Exception as e:
            if not warning_already_shown:
                st.warning("💡 I was unable to process some homes due to data inconsistency, I've skipped them.")
                warning_already_shown = True

    return normalized

#-------------- Analyze ----------------#
def compute_kpis(data: list[dict], user_max_price: int | None = None) -> dict:
    prices = [i["price"] for i in data if i["price"]]
    sqfts = [i["sqft"] for i in data if i["sqft"]]
    beds = [i["beds"] for i in data if i["beds"]]

    # --- Avg price per bedroom ---
    price_per_bed = defaultdict(list)
    for item in data:
        if item["price"] and item["beds"]:
            price_per_bed[item["beds"]].append(item["price"])

    price_per_bed = {
        b: round(sum(v)/len(v)) for b, v in price_per_bed.items()
    }

    # --- Budget match ---
    percent_in_budget = None
    if user_max_price:
        percent_in_budget = round(
            (sum(p <= user_max_price for p in prices) / len(prices)) * 100, 2
        )

    return {
        "count": len(data),
        "avg_price": round(sum(prices)/len(prices)) if prices else None,
        "median_price": float(np.median(prices)) if prices else None,
        "min_price": min(prices, default=None),
        "max_price": max(prices, default=None),
        "avg_sqft": round(sum(sqfts)/len(sqfts)) if sqfts else None,
        "price_buckets": compute_price_buckets(prices),
        "most_common_beds": Counter(beds).most_common(1)[0][0] if beds else None,
        "avg_price_per_bedroom": price_per_bed,
        "percent_in_budget": percent_in_budget,
    }

def compute_dynamic_buckets(prices, num_buckets=5):
    if not prices:
        return {}

    mn = min(prices)
    mx = max(prices)
    # uniform bucket size
    step = (mx - mn) / num_buckets

    buckets = {}
    edges = [mn + i * step for i in range(num_buckets + 1)]

    # prepare labels
    for i in range(num_buckets):
        low = int(edges[i])
        high = int(edges[i + 1])
        label = f"${low:,} - ${high:,}"
        buckets[label] = 0

    # assign prices
    for p in prices:
        # find which bucket
        idx = min(int((p - mn) / step), num_buckets - 1)
        low = int(edges[idx])
        high = int(edges[idx + 1])
        label = f"${low:,} - ${high:,}"
        buckets[label] += 1

    return buckets

def top_cheapest(data, limit=5):
    return sorted(data, key=lambda x: x["price"] or float("inf"))[:limit]

def top_expensive(data, limit=5):
    return sorted(data, key=lambda x: -(x["price"] or 0))[:limit]

def rank_best_value(data: list[dict], min_sqft=200):
    """Return homes ranked by value (lower $/sqft is better)."""
    deals = []

    for i in data:
        if not i["price"] or not i["sqft"]:
            continue
        if i["sqft"] < min_sqft:
            continue

        i["price_per_sqft"] = round(i["price"] / i["sqft"], 2)
        deals.append(i)

    return sorted(deals, key=lambda x: x["price_per_sqft"])

def summarize_by_city(data: list[dict]):
    stats = defaultdict(lambda: {"count": 0, "prices": []})

    for i in data:
        city = i["city"] or "Unknown"
        stats[city]["count"] += 1
        if i["price"]:
            stats[city]["prices"].append(i["price"])

    summary = []
    for city, s in stats.items():
        prices = s["prices"]
        summary.append({
            "city": city,
            "count": s["count"],
            "avg_price": round(sum(prices)/len(prices)) if prices else None,
            "median_price": float(np.median(prices)) if prices else None,
        })

    return sorted(summary, key=lambda x: x["count"], reverse=True)

def bed_bath_distribution(data: list[dict]):
    
    beds = defaultdict(int)
    baths = defaultdict(int)

    for i in data:
        if i.get("beds"):
            beds[i["beds"]] += 1
        if i.get("baths"):
            baths[i["baths"]] += 1

    return dict(beds), dict(baths)

#-------------- Display ----------------#
def display_best_deals(normalized_data):
    """Nicely Display best deals"""

    best = rank_best_value(normalized_data)[:10]

    # Prepare dataframe with selected columns
    df = pd.DataFrame(best)
    df_display = df[["img", "price", "address", "city", "state", "beds", "baths", "sqft", "url"]]

    # Convert img URLs to Markdown so Streamlit renders thumbnails
    df_display["price"] = df_display["price"].apply(lambda x: f"$**{x:,}**")
    
    # Convert img URLs to Markdown so Streamlit renders thumbnails
    df_display["img"] = df_display["img"].apply(lambda x: f"![img]({x})")
    # Convert URL to clickable links
    df_display["url"] = df_display["url"].apply(lambda x: f"[Link]({x})")

    # Show as Streamlit table
    st.subheader("🏆 Best Deals (Lowest $/sqft)")
    st.write("Showing top 10 homes based on $/sqft value")
    st.write(df_display.to_markdown(index=False), unsafe_allow_html=True)

def fancy_display_deals(best):
    for house in best:
        cols = st.columns([1,3])
        cols[0].image(house["img"], width=100)
        cols[1].markdown(f"""
    **{house['address']}, {house['city']} {house['state']}**  
    Beds: {house['beds']} | Baths: {house['baths']} | {house['sqft']} sqft  
    Price: ${house['price']:,} | [Link]({house['url']})
    """)

def display_bed_bath_distribution(normalized_data):
    
    beds, baths = bed_bath_distribution(normalized_data)

    # Convert to DataFrame
    df_beds = pd.DataFrame(list(beds.items()), columns=["Beds", "Count"])
    df_baths = pd.DataFrame(list(baths.items()), columns=["Baths", "Count"])

    # Bed chart
    bed_chart = alt.Chart(df_beds).mark_bar(color="skyblue").encode(
        x=alt.X("Beds:N", title="Number of Beds"),
        y=alt.Y("Count:Q", title="Number of Homes"),
        tooltip=["Beds", "Count"]
    ).properties(title="🏠 Bed Distribution")
    st.altair_chart(bed_chart, width='stretch')

    # Bath chart
    bath_chart = alt.Chart(df_baths).mark_bar(color="orange").encode(
        x=alt.X("Baths:N", title="Number of Baths"),
        y=alt.Y("Count:Q", title="Number of Homes"),
        tooltip=["Baths", "Count"]
    ).properties(title="🛁 Bath Distribution")
    st.altair_chart(bath_chart, width='stretch')

def plot_price_buckets(price_buckets: dict):
    # Convert to DataFrame
    df = pd.DataFrame(list(price_buckets.items()), columns=["PriceRange", "Count"])
    
    # Sort by Count descending
    df = df.sort_values("Count", ascending=False)

    # Altair chart
    chart = (
        alt.Chart(df)
        .mark_bar(color='violet')
        .encode(
            x=alt.X("PriceRange:N", title="Price Range"),
            y=alt.Y("Count:Q", title="Number of Homes"),
            tooltip=["Count"],  # only show the number on hover
            order=alt.Order("Count", sort="descending")
        )
        .properties(width=600, height=400)
    )

    st.altair_chart(chart)
