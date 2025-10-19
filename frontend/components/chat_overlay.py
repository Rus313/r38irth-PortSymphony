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
# Collapsible Right-Column Chat (with duplication fix)
# -------------------------
def chat_overlay():
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    if "chat_open" not in st.session_state:
        st.session_state.chat_open = True
    if "last_user_input" not in st.session_state:
        st.session_state.last_user_input = ""

    col_main, col_chat = st.columns([4, 1])

    with col_chat:
        # Toggle button
        toggle_text = "💬" if not st.session_state.chat_open else "❌"
        if st.button(toggle_text, key="chat_toggle"):
            st.session_state.chat_open = not st.session_state.chat_open

        if st.session_state.chat_open:
            st.markdown("""
            <style>
            .chat-container {
                max-height: 80vh;
                overflow-y: auto;
                padding: 10px;
                background-color: #1E1E1E;
                border-radius: 12px;
            }
            .chat-messages { display: flex; flex-direction: column; }
            .user-bubble, .bot-bubble {
                display: flex;
                align-items: flex-start;
                margin: 4px 0;
                max-width: 90%;
                word-wrap: break-word;
            }
            .user-bubble { justify-content: flex-end; align-self: flex-end; }
            .bot-bubble { justify-content: flex-start; align-self: flex-start; }
            .bubble-content {
                padding: 10px 14px;
                border-radius: 18px;
                font-size: 14px;
                line-height: 1.4;
            }
            .user-bubble .bubble-content {
                background-color: #0B93F6;
                color: white;
                border-radius: 18px 18px 0 18px;
            }
            .bot-bubble .bubble-content {
                background-color: #2C2C2C;
                color: white;
                border-radius: 18px 18px 18px 0;
            }
            .avatar { width: 28px; height: 28px; border-radius: 50%; margin: 0 8px; }
            .chat-input {
                border-radius: 20px;
                border: 1px solid #444;
                background-color: #2C2C2C;
                color: white;
                padding: 8px 14px;
                width: 100%;
                margin-top: 8px;
            }
            </style>
            """, unsafe_allow_html=True)

            st.markdown('<div class="chat-container">', unsafe_allow_html=True)
            st.markdown('<div class="chat-messages">', unsafe_allow_html=True)

            # Display messages
            for msg in st.session_state.chat_history:
                if msg["role"] == "user":
                    st.markdown(f"""
                    <div class="user-bubble">
                        <div class="bubble-content">{msg['content']}</div>
                        <img class="avatar" src="https://i.imgur.com/2yaf2wb.png" alt="user">
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                    <div class="bot-bubble">
                        <img class="avatar" src="https://i.imgur.com/q5tK3tB.png" alt="bot">
                        <div class="bubble-content">{msg['content']}</div>
                    </div>
                    """, unsafe_allow_html=True)

            st.markdown('</div>', unsafe_allow_html=True)  # close messages

            # Input for new message
            user_input = st.text_input("Type a message...", key="chat_input")

            if user_input and user_input != st.session_state.last_user_input:
                # Prevent duplicate responses
                st.session_state.last_user_input = user_input

                # Append user message
                st.session_state.chat_history.append({"role": "user", "content": user_input})
                # Get AI response
                ai_response = ai_service.chat(user_input, st.session_state.chat_history)
                st.session_state.chat_history.append({"role": "assistant", "content": ai_response})

                st.experimental_rerun()

            st.markdown('</div>', unsafe_allow_html=True)  # close container
