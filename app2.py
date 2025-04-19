import streamlit as st
import os
from serpapi import GoogleSearch
from geopy.geocoders import Nominatim
import folium
from streamlit_folium import st_folium

# --- Configuration ---
SERPAPI_KEY = 
# --- Function to explore destinations ---
def explore_destinations(city: str, departure_date: str, return_date: str, limit: int = 8):
    """
    Calls SerpAPI's Google Travel Explore engine to fetch popular nearby destinations with prices.
    """
    try:
        params = {
            "engine": "google_travel_explore",
            "q": city,
            "departure_date": departure_date,
            "return_date": return_date,
            "hl": "en",
            "currency": "INR",
            "api_key": SERPAPI_KEY
        }
        search = GoogleSearch(params)
        data = search.get_dict()
        places = data.get("places", [])[:limit]
        return places
    except Exception as e:
        st.error(f"Error fetching data from SerpAPI: {e}")
        return []

# --- Streamlit UI Setup ---
st.set_page_config(page_title="🗺️ Nearby Destination Explorer", layout="wide")
st.title("🗺️ Explore Nearby Destinations")

# User inputs
city = st.text_input("Enter your current city:", value="New Delhi")
dep_date = st.date_input("Departure Date")
ret_date = st.date_input("Return Date")

# Main action\
if st.button("🔍 Show Suggestions"):
    # 1. Fetch & display textual list
    with st.spinner("Fetching suggestions…"):
        suggestions = explore_destinations(city, str(dep_date), str(ret_date))

    if not suggestions:
        st.warning("No suggestions returned. Check your API key or network connection.")
    else:
        st.subheader("📋 Suggestions List")
        for i, place in enumerate(suggestions, start=1):
            dest = place.get("destination", "Unknown")
            price = place.get("price", "N/A")
            st.write(f"{i}. **{dest}** — ₹{price}")

        # 2. Geocode origin
        with st.spinner(f"Geocoding '{city}'..."):
            geo = Nominatim(user_agent="travel_app")
            origin = None
            try:
                origin = geo.geocode(city)
            except Exception as e:
                st.error(f"Geocoding error: {e}")

        if not origin:
            st.error("Could not find coordinates for your city. Please check the name.")
        else:
            # 3. Initialize map & add origin marker
            m = folium.Map(location=[origin.latitude, origin.longitude], zoom_start=6)
            folium.Marker(
                [origin.latitude, origin.longitude],
                popup=f"You are here: {city}",
                icon=folium.Icon(color="blue", icon="home")
            ).add_to(m)

            # 4. Sequentially add destinations
            st.subheader("🗺 Loading Destinations on Map")
            progress = st.progress(0)
            for idx, place in enumerate(suggestions):
                dest = place.get("destination")
                price = place.get("price")
                try:
                    loc = geo.geocode(dest)
                except Exception:
                    continue
                if not loc:
                    continue
                folium.Marker(
                    [loc.latitude, loc.longitude],
                    popup=f"{dest}: ₹{price}",
                    icon=folium.Icon(color="green", icon="info-sign")
                ).add_to(m)

                progress.progress((idx + 1) / len(suggestions))
                time.sleep(1)

            # 5. Render the map
            st.subheader(f"Popular Destinations Near {city}")
            st_folium(m, width=800, height=500)
else:
    st.info("Enter your city and dates, then click '🔍 Show Suggestions'.")
