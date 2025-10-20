import streamlit as st
from frontend.pages import ai_chatbot

# Optional: hide everything else
st.set_page_config(layout="wide", initial_sidebar_state="collapsed")

ai_chatbot.render()
