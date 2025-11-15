"""Homes Data Cleaning, Processing & Analysing functions."""


def normalize_items(items: list[dict]) -> list[dict]:
    """Extract consistent fields from Zillow scraper results."""
    normalized = []

    for item in items:
        h = item
        hd = h.get("hdpData", {}).get("homeInfo", {})

        normalized.append({
            "zpid": h.get("zpid"),
            "url": h.get("detailUrl"),
            "address": h.get("address"),
            "city": h.get("addressCity"),
            "state": h.get("addressState"),
            "zip": h.get("addressZipcode"),
            "price": h.get("unformattedPrice") or hd.get("price"),
            "beds": h.get("beds") or hd.get("bedrooms"),
            "baths": h.get("baths") or hd.get("bathrooms"),
            "sqft": h.get("area") or hd.get("livingArea"),
            "lat": h.get("latLong", {}).get("latitude"),
            "lng": h.get("latLong", {}).get("longitude"),
            "img": h.get("imgSrc"),
            "zestimate": h.get("zestimate") or hd.get("zestimate"),
            "broker": h.get("brokerName") or hd.get("listing_sub_type"),
        })

    return normalized

def compute_kpis(data: list[dict]) -> dict:
    prices = [i["price"] for i in data if i["price"]]
    sqfts = [i["sqft"] for i in data if i["sqft"]]

    return {
        "count": len(data),
        "avg_price": round(sum(prices) / len(prices)) if prices else None,
        "min_price": min(prices, default=None),
        "max_price": max(prices, default=None),
        "avg_sqft": sum(sqfts) / len(sqfts) if sqfts else None,
    }

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

from collections import defaultdict

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
            "avg_price": sum(prices)/len(prices) if prices else None
        })

    return sorted(summary, key=lambda x: x["count"], reverse=True)

def bed_bath_distribution(data: list[dict]):
    beds = defaultdict(int)
    baths = defaultdict(int)

    for i in data:
        if i["beds"]:
            beds[i["beds"]] += 1
        if i["baths"]:
            baths[i["baths"]] += 1

    return dict(beds), dict(baths)
