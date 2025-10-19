import streamlit as st
from frontend.components.chat_overlay import chat_overlay # import the overlay

st.title("My Main Streamlit App")

# Your existing interface here
st.write("This is my main interface...")

# Add chat overlay
chat_overlay()
