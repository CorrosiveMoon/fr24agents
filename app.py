import streamlit as st
from langchain_core.messages import HumanMessage, AIMessage
from main import graph
from utils.fr24_api import fetch_flight_status
import folium
from streamlit_folium import st_folium

st.set_page_config(page_title="Flight Assistant", page_icon="✈️")
st.title("FR24 Aviation Assistant")

# Chat history
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Track last flight code for use in follow-ups
if "last_flight_code" not in st.session_state:
    st.session_state.last_flight_code = None

# Input field
user_input = st.chat_input("Ask a flight-related question...")

if user_input:
    st.session_state.chat_history.append(HumanMessage(content=user_input))
    state = {"messages": st.session_state.chat_history}
    result = graph.invoke(state)
    ai_response = result["messages"][-1]
    st.session_state.chat_history.append(ai_response)

    # Attempt to extract a flight code from input
    import re
    flight_match = re.search(r"\b([A-Z]{2,3}\d{2,4})\b", user_input.upper())
    if flight_match:
        st.session_state.last_flight_code = flight_match.group(1)

#Displaying conversation
for msg in st.session_state.chat_history:
    if isinstance(msg, HumanMessage):
        with st.chat_message("user"):
            st.markdown(msg.content)
    elif isinstance(msg, AIMessage):
        with st.chat_message("assistant"):
            st.markdown(msg.content)

#flight position if we have a last flight code using folium
if st.session_state.last_flight_code:
    rec = fetch_flight_status(st.session_state.last_flight_code)
    if rec and rec.get("lat") and rec.get("lon"):
        st.subheader(f"🌍 Live Location: {rec.get('callsign', st.session_state.last_flight_code)}")

        # Create map with folium
        m = folium.Map(location=[rec["lat"], rec["lon"]], zoom_start=4)
        folium.Marker(
            location=[rec["lat"], rec["lon"]],
            popup=f"Flight {rec.get('callsign')}<br>Altitude: {rec.get('alt')} ft",
            tooltip="Click for info",
            icon=folium.Icon(color="blue", icon="plane", prefix='fa')
        ).add_to(m)

        # Render it
        st_folium(m, width=700, height=500)
