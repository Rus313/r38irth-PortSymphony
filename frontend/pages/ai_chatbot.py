"""
AI Chat Page
Interactive AI chatbot using MultiModelAIService
"""

import streamlit as st
from backend.ai_service import MultiModelAIService, AzureOpenAIConfig

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
# Render AI Chat Page
# -------------------------
def render():
    st.subheader("🤖 AI Chat")

    # Initialize chat history in session state
    if "history" not in st.session_state:
        st.session_state.history = []

    # Sidebar instructions (no model selection)
    st.sidebar.subheader("AI Chat Options")
    st.sidebar.markdown(
        """
        **Instructions**
        - Type your message in the input below.
        - Press Enter to get a response from the AI.
        - Clear Chat button is available below the chat.
        """
    )

    # -------------------------
    # Chat messages (full width)
    # -------------------------
    for msg in st.session_state.history:
        if msg["role"] == "user":
            st.chat_message("user").write(msg["content"])
        elif msg["role"] == "assistant":
            st.chat_message("assistant").write(msg["content"])
        else:
            st.markdown(f"<span style='color:red'>{msg['content']}</span>", unsafe_allow_html=True)

    # -------------------------
    # User input (must be top-level)
    # -------------------------
    user_input = st.chat_input("Type your message here...")
    if user_input:
        # Append user message
        st.session_state.history.append({"role": "user", "content": user_input})
        st.chat_message("user").write(user_input)

        # Get AI response using the service's default model
        try:
            ai_response = ai_service.chat(user_input, st.session_state.history)
            st.session_state.history.append({"role": "assistant", "content": ai_response})
            st.chat_message("assistant").write(ai_response)

        except Exception as e:
            error_msg = f"❌ Error: {e}"
            st.session_state.history.append({"role": "system", "content": error_msg})
            st.markdown(f"<span style='color:red'>{error_msg}</span>", unsafe_allow_html=True)

    # -------------------------
    # Inline Clear Chat button
    # -------------------------
    if st.button("Clear Chat"):
        st.session_state.history = []
        st.experimental_rerun()

    # -------------------------
    # Optional chat stats column
    # -------------------------
    stats_col1, stats_col2 = st.columns([3, 1])
    with stats_col2:
        st.subheader("Chat Info")
        st.info(f"Messages exchanged: {len(st.session_state.history)}")
