import streamlit as st
import requests
from anthropic import Anthropic

client = Anthropic()
st.set_page_config(page_title="Optimist 3000", layout="centered")
st.title("🌤️ Optimist 3000")
st.markdown("*Your weather-powered motivational sidekick*")
st.divider()

col1, col2 = st.columns(2)
with col1:
    city = st.text_input("📍 Enter a city:", placeholder="e.g., Denver")
with col2:
    friend_name = st.text_input("👋 Friend's name:", placeholder="e.g., Sarah")

def get_weather(city):
    try:
        geo_url = f"https://geocoding-api.open-meteo.com/v1/search?name={city}&count=1&language=en&format=json"
        geo_response = requests.get(geo_url, timeout=5)
        geo_data = geo_response.json()
        if not geo_data.get("results"):
            return None, "City not found"
        location = geo_data["results"][0]
        lat, lon = location["latitude"], location["longitude"]
        weather_url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current=temperature_2m,relative_humidity_2m,weather_code"
        weather_response = requests.get(weather_url, timeout=5)
        weather_data = weather_response.json()
        current = weather_data["current"]
        return {"city": city, "temperature": current["temperature_2m"], "humidity": current["relative_humidity_2m"], "condition": current["weather_code"]}, None
    except Exception as e:
        return None, f"Error: {str(e)}"

def get_motivation(city, friend_name, weather_data):
    prompt = f"""You are Optimist 3000. Generate ONE ridiculous motivational sentence for {friend_name} in {city} (temp: {weather_data['temperature']}°C, humidity: {weather_data['humidity']}%). Make it funny, absurd, weather-related, under 20 words."""
    message = client.messages.create(model="claude-3-5-haiku-20241022", max_tokens=100, messages=[{"role": "user", "content": prompt}])
    return message.content[0].text.strip()

if st.button("🚀 Generate Motivation", use_container_width=True, type="primary"):
    if not city or not friend_name:
        st.warning("⚠️ Enter city and name!")
    else:
        with st.spinner("Brewing motivation..."):
            weather_data, error = get_weather(city)
            if error:
                st.error(f"❌ {error}")
            else:
                motivation = get_motivation(city, friend_name, weather_data)
                st.success("✨ Done!")
                st.divider()
                col1, col2 = st.columns([1, 3])
                with col1:
                    st.metric("Temp", f"{weather_data['temperature']}°C")
                with col2:
                    st.markdown(f"**Humidity:** {weather_data['humidity']}%")
                st.markdown(f"### 💬 For {friend_name}:")
                st.write(motivation)