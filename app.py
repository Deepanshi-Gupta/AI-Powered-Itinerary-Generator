import os
import google.generativeai as genai
import streamlit as st
from datetime import datetime, timedelta

from serpapi import GoogleSearch 
from agno.agent import Agent
from agno.tools.serpapi import SerpApiTools
from agno.models.google import Gemini
# Function to fetch flight data
def fetch_flights(source, destination, departure_date, return_date):
    params = {
        "engine": "google_flights",
        "departure_id": source,
        "arrival_id": destination,
        "outbound_date": str(departure_date),
        "return_date": str(return_date),
        "currency": "INR",
        "hl": "en",
        "api_key": SERPAPI_KEY
    }
    search = GoogleSearch(params)
    results = search.get_dict()
    return results

# Function to extract top 3 cheapest flights
def extract_cheapest_flights(flight_data):
    best_flights = flight_data.get("best_flights", [])
    sorted_flights = sorted(best_flights, key=lambda x: x.get("price", float("inf")))[:3]  # Get top 3 cheapest
    return sorted_flights

SERPAPI_KEY = "0b94868e78d63bfec41dcee02f7d89f0fb6dadc4fbf679a02349c1428072610a" 
# Configure API key for Gemini 2.2 using an environment variable for better security
API_KEY = "AIzaSyAw04tZ7jDVeAE7VhGYrzrWXiJIUtyCee0"
genai.configure(api_key=API_KEY)

# Create the model configuration for Gemini 2.2
generation_config = {
    "temperature": 1,
    "top_p": 0.95,
    "top_k": 40,
    "max_output_tokens": 8192,
    "response_mime_type": "text/plain",
}

# Initialize the model
model = genai.GenerativeModel(
    model_name="gemini-2.0-flash-exp",
    generation_config=generation_config,
)

##st.title("Itinerary Generator")

# Initialize session state defaults if not set
if "step" not in st.session_state:
    st.session_state.step = 1

# Sidebar: Show current progress
st.sidebar.header("Progress")
st.sidebar.write(f"Current Step: {st.session_state.step}")
if st.session_state.step >= 2:
    st.sidebar.write(f"From: {st.session_state.get('source_location', 'N/A')} To: {st.session_state.get('destination', 'N/A')}")
if st.session_state.step >= 3:
    st.sidebar.write(f"Trip Dates: {st.session_state.get('start_date', 'N/A')} to {st.session_state.get('end_date', 'N/A')}")
if st.session_state.step >= 4:
    st.sidebar.write("Itinerary Generated!")

# Step 1: Basic Trip Details
if st.session_state.step == 1:
    st.header("Enter Trip Details")
    source_location = st.text_input("Enter your current location:")
    destination = st.text_input("Enter your destination location:")
    
    if st.button("Select Dates", key="btn_step1") and source_location and destination:
        st.session_state.source_location = source_location
        st.session_state.destination = destination
        st.session_state.step = 2
        
    

# Step 2: Date Selection using columns for a clean layout
elif st.session_state.step == 2:
    st.header("Select Travel Dates")
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input("Select the start date for your trip:", value=datetime.today())
    with col2:
        max_end_date = start_date + timedelta(days=30)
        end_date = st.date_input("Select the end date for your trip:",
                                 value=start_date + timedelta(days=1),
                                 min_value=start_date,
                                 max_value=max_end_date)
    days = (end_date - start_date).days
    st.write(f"Trip Duration: {days} day(s)")
    
    if st.button("Confirm Dates", key="btn_step2"):
        st.session_state.start_date = start_date
        st.session_state.end_date = end_date
        st.session_state.days = days
        st.session_state.step = 3
        

# Step 3: Ask for Additional Preferences or Generate Itinerary
elif st.session_state.step == 3:
    st.header("Additional Preferences")
    
    # Ask if the user wants to add additional preferences
    add_preferences = st.radio(
        "Do you want to add additional preferences?",
        options=["Yes", "No"],
        key="add_preferences"
    )
    
    if add_preferences == "Yes":
        # 1. Budget Considerations using a slider
        st.subheader("Budget Considerations")
        budget_value = st.slider("Select your budget (in Rupees)",
                                 min_value=2000, max_value=20000, value=1000, step=100,
                                 key="budget_slider")
        
        # 2. Accommodation Preferences
        st.subheader("Accommodation Preferences")
        accommodation_choice = st.multiselect(
            "Choose your preferred types of accommodation:",
            options=[
                "Hotels (5-star, boutique, budget)",
                "Airbnb/apartment rentals",
                "Resorts & Villas"
            ]
        )
        
        # 3. Travel Style
        st.subheader("Travel Style")
        travel_style = st.radio(
            "Select your travel style:",
            options=[
                "Relaxed & slow travel",
                "Fast-paced, packed schedule",
                "Solo travel",
                "Family-friendly",
                "Group travel"
            ],
            key="travel_style"
        )
        
        # 4. Transportation Preferences
        st.subheader("Transportation Preferences")
        transportation = st.radio(
            "Select your preferred transportation:",
            options=[
                "Private transport (car rentals, taxis)",
                "Public transport (buses, trains, metros)",
                "Walking & biking tours"
            ],
            key="transportation"
        )
        
        if st.button("Generate Itinerary", key="btn_generate_itinerary"):
            # Store responses in session state
            st.session_state["user_budget_value"] = budget_value
            st.session_state["accommodation_choice"] = accommodation_choice
            st.session_state["user_travel_style"] = travel_style
            st.session_state["user_transportation"] = transportation
            
            st.session_state.step = 4
            
    else:
        if st.button("Generate Itinerary Without Preferences", key="btn_generate_itinerary_no_prefs"):
            # Skip additional preferences and proceed
            st.session_state.step = 4
            

# Step 4: Generate and Display Itinerary
elif st.session_state.step == 4:
    st.header("Generating the Itinerary")
    # Build the prompt using session state values (use get() for safety)
    prompt = (
    f"You are a travel expert coordinating a comprehensive travel plan for {st.session_state.get('destination')}. "
    f"The journey begins from {st.session_state.get('source_location')} and spans {st.session_state.get('days')} days, "
    f"starting on {st.session_state.get('start_date')} and ending on {st.session_state.get('end_date')}. "
    f"The budget allocated is Rupees {st.session_state.get('user_budget_value', 'N/A')}. "
    f"Your tasks include:\n\n"
    f"1. **Researcher**: Identify the destination's key features, climate, culture, and safety tips. Find popular attractions, "
    f"landmarks, and activities that match the traveler’s interests.\n\n"
    f"2. **Planner**: Gather details on the traveler's preferences and budget. Create a detailed itinerary with scheduled activities, "
    f"estimated costs, and transportation options. Optimize the schedule for convenience and enjoyment.\n\n"
    f"3. **Hotel & Restaurant Finder**: Identify key locations in the itinerary. Search for highly rated hotels and top-rated "
    f"restaurants based on cuisine preferences and proximity. Provide booking links or reservation options where possible.\n\n"
    f"Consider the traveler's accommodation preferences: {st.session_state.get('accommodation_choice', 'Not specified')}, "
    f"travel style: {st.session_state.get('user_travel_style', 'Not specified')}, and local transportation preferences: "
    f"{st.session_state.get('user_transportation', 'Not specified')}."
    )


    # Generate the itinerary using the model
    chat_session = model.start_chat(
        history=[{"role": "user", "parts": ["AI powered Itinerary generator\n"]},
                 {"role": "model", "parts": [prompt]}]
    )
    response = chat_session.send_message("Generate itinerary based on the input.")
    itinerary_text = response.candidates[0].content.parts[0].text
    st.markdown("### Your Itinerary")
    st.markdown(itinerary_text)