import streamlit as st
from backend.ai_service import MultiModelAIService, AzureOpenAIConfig

# st.set_page_config(page_title="PSA Hackathon AI Chat", page_icon="🛳️")
# st.title("PSA Hackathon AI Chat 🛳️")

# -------------------------
# Initialize AI service
# -------------------------
@st.cache_resource
def init_backend():
    config = AzureOpenAIConfig()
    ai_service = MultiModelAIService(config)
    return ai_service

ai_service = init_backend()

# -------------------------
# Chat history
# -------------------------
if "history" not in st.session_state:
    st.session_state.history = []

# Sidebar: Clear chat
if st.sidebar.button("Clear Chat"):
    st.session_state.history = []

# Display chat messages
for msg in st.session_state.history:
    if msg["role"] == "user":
        st.chat_message("user").write(msg["content"])
    elif msg["role"] == "assistant":
        st.chat_message("assistant").write(msg["content"])
    else:
        st.markdown(f"<span style='color:red'>{msg['content']}</span>", unsafe_allow_html=True)

# User input
user_input = st.chat_input("Type your message here...")

if user_input:
    # Prevent duplicate AI response on rerun
    if "last_user_input" not in st.session_state:
        st.session_state.last_user_input = ""

    if user_input != st.session_state.last_user_input:
        st.session_state.last_user_input = user_input

        # Add user message
        st.session_state.history.append({"role": "user", "content": user_input})
        st.chat_message("user").write(user_input)

        # Get AI response from your service
        try:
            ai_response = ai_service.chat(user_input, st.session_state.history)
            st.session_state.history.append({"role": "assistant", "content": ai_response})
            st.chat_message("assistant").write(ai_response)
        except Exception as e:
            st.session_state.history.append({"role": "system", "content": f"❌ Error: {e}"})
            st.markdown(f"<span style='color:red'>❌ Error: {e}</span>", unsafe_allow_html=True)
