import streamlit as st
import requests
import sys
import os

# Ensure configkeys can be imported from root
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if PROJECT_ROOT not in sys.path:
    sys.path.append(PROJECT_ROOT)

import configkeys

def chat_overlay():
    """
    Fully floating bottom-right chatbot overlay using HTML/CSS.
    All messages and input are inside the overlay.
    """

    if "chat_open" not in st.session_state:
        st.session_state.chat_open = False
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    # Toggle button for overlay
    toggle_text = "💬 Chat" if not st.session_state.chat_open else "❌ Close Chat"
    if st.button(toggle_text):
        st.session_state.chat_open = not st.session_state.chat_open

    if st.session_state.chat_open:
        # Overlay HTML
        overlay_html = """
        <div class="chat-overlay">
            <div class="chat-messages" id="chat-messages">
        """

        # Render chat messages
        for msg in st.session_state.chat_history:
            if msg["role"] == "user":
                overlay_html += f'''
                <div style="
                    background-color:#DCF8C6;
                    padding:8px;
                    border-radius:10px;
                    margin:5px;
                    text-align:right;
                    max-width:80%;
                    clear:both;
                    float:right;">
                    {msg["content"]}
                </div>
                '''
            elif msg["role"] == "assistant":
                overlay_html += f'''
                <div style="
                    background-color:#F1F0F0;
                    padding:8px;
                    border-radius:10px;
                    margin:5px;
                    text-align:left;
                    max-width:80%;
                    clear:both;
                    float:left;">
                    {msg["content"]}
                </div>
                '''
            else:
                overlay_html += f'<div style="color:red;">{msg["content"]}</div>'

        overlay_html += """
            </div>
            <form action="" method="post">
                <input type="text" name="user_input" id="user_input" placeholder="Type a message..." 
                    style="width:80%; padding:5px; border-radius:5px; border:1px solid #ccc;">
                <input type="submit" value="Send" 
                    style="padding:5px 10px; border-radius:5px; background-color:#007bff; color:white; border:none;">
            </form>
        </div>
        """

        # Overlay CSS
        st.markdown("""
        <style>
        .chat-overlay {
            position: fixed;
            bottom: 20px;
            right: 20px;
            width: 350px;
            max-height: 500px;
            background-color: white;
            border: 1px solid #ccc;
            border-radius: 10px;
            box-shadow: 0px 4px 12px rgba(0,0,0,0.15);
            padding: 10px;
            z-index: 9999;
            overflow: hidden;
        }
        .chat-messages {
            max-height: 400px;
            overflow-y: auto;
            margin-bottom: 10px;
        }
        </style>
        """, unsafe_allow_html=True)

        # Render overlay HTML
        st.markdown(overlay_html, unsafe_allow_html=True)

        # Handle form submission
        submitted_input = st.experimental_get_query_params().get("user_input", [""])[0]
        if submitted_input:
            user_message = submitted_input.strip()
            if user_message:
                st.session_state.chat_history.append({"role": "user", "content": user_message})

                # Call Azure OpenAI
                url = f"{configkeys.AZURE_OPENAI_ENDPOINT}openai/deployments/{configkeys.DEPLOYMENT_ID}/chat/completions?api-version={configkeys.AZURE_OPENAI_API_VERSION}"
                headers = {"Content-Type": "application/json", "api-key": configkeys.AZURE_OPENAI_API_KEY}
                payload = {"messages": st.session_state.chat_history, "temperature": 0.7}

                try:
                    response = requests.post(url, headers=headers, json=payload)
                    response.raise_for_status()
                    data = response.json()
                    ai_message = data["choices"][0]["message"]["content"]

                    st.session_state.chat_history.append({"role": "assistant", "content": ai_message})

                except Exception as e:
                    st.session_state.chat_history.append({"role": "system", "content": f"❌ Error: {e}"})

        # Auto-scroll JS
        st.markdown("""
        <script>
        var chatContainer = window.document.getElementsByClassName('chat-messages')[0];
        if (chatContainer) { chatContainer.scrollTop = chatContainer.scrollHeight; }
        </script>
        """, unsafe_allow_html=True)
