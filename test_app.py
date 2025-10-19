import streamlit as st
import requests
import configkeys  # your config file

st.set_page_config(page_title="PSA Hackathon AI Chat", page_icon="🛳️")

st.title("PSA Hackathon AI Chat 🛳️")

# Initialize chat history
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
    # Add user message to history
    st.session_state.history.append({"role": "user", "content": user_input})
    st.chat_message("user").write(user_input)

    # Prepare REST API request
    url = f"{configkeys.AZURE_OPENAI_ENDPOINT}openai/deployments/{configkeys.DEPLOYMENT_ID}/chat/completions?api-version={configkeys.AZURE_OPENAI_API_VERSION}"
    headers = {"Content-Type": "application/json", "api-key": configkeys.AZURE_OPENAI_API_KEY}
    payload = {"messages": st.session_state.history, "temperature": 0.7}

    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        data = response.json()
        ai_message = data["choices"][0]["message"]["content"]

        # Add AI response to history
        st.session_state.history.append({"role": "assistant", "content": ai_message})
        st.chat_message("assistant").write(ai_message)

    except Exception as e:
        st.session_state.history.append({"role": "system", "content": f"❌ Error: {e}"})
        st.markdown(f"<span style='color:red'>❌ Error: {e}</span>", unsafe_allow_html=True)
