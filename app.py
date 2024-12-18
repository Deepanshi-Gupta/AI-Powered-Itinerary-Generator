import os
import google.generativeai as genai
import streamlit as st
from ics import Calendar, Event
from datetime import datetime, timedelta
import json
import base64

# Configure API key for Gemini 2.2
API_KEY = ""
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

# Streamlit app title and user input
st.title("Itinerary Generator")
city = st.text_input("Enter the city you're visiting:")
col1, col2 = st.columns(2)
with col1:
    start_date = st.date_input("Select the start date for your trip:", value=datetime.today())

# Set the maximum end date to 30 days after the start date
max_end_date = start_date + timedelta(days=30)

# Select the end date for the trip in the second column
with col2:
    end_date = st.date_input(
        "Select the end date for your trip:",
        value=start_date + timedelta(days=1),
        min_value=start_date,
        max_value=max_end_date
    )


# Calculate the number of days between start_date and end_date
days = (end_date - start_date).days
# Generate itinerary button
if st.button("Generate Itinerary"):
    if True :
        # Create a prompt based on user input
        prompt = (f"You are a travel expert. Generate a detailed travel itinerary for {city} "
                f"for {days} days. Each day starts at 10 AM and ends at 8 PM with a 30-minute "
                f"lunch break. Include the following details for each activity: title, description, "
                f"location, start time, end time, and a relevant link.")
        print('Prompt created',prompt)
         # Start chat session with model
        chat_session = model.start_chat(
            history=[
                {"role": "user", "parts": ["AI powered Itinerary generator\n"]},
                {"role": "model", "parts": [prompt]},
            ]
        )
        # Get the response from the model
        response = chat_session.send_message("Generate itinerary based on the input.")  
        st.markdown(response.candidates[0].content.parts[0].text)
