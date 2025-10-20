import streamlit as st
from datetime import datetime

def render_header():
    """Render page header with branding, time, and chatbot toggle"""

    # Get current page
    current_page = st.session_state.get('current_page', 'Global Insights')

    header_col1, header_col2, header_col3 = st.columns([3, 1, 0.5])

    with header_col1:
        # Page title
        st.markdown(f"""
            <div style='padding: 1rem 0;'>
                <h1 style='color: white; margin: 0; font-size: 2.5rem;'>
                    {current_page}
                </h1>
                <p style='color: #A0A0A0; margin: 0.5rem 0 0 0; font-size: 1rem;'>
                    {st.session_state.get('user_department', 'Operations')} Department View
                </p>
            </div>
        """, unsafe_allow_html=True)

    with header_col2:
        # Date + Time
        st.markdown(f"""
            <div style='text-align: right; padding: 1rem 0;'>
                <p style='color: #A0A0A0; margin: 0; font-size: 0.8rem;'>
                    {datetime.now().strftime('%A, %B %d, %Y')}
                </p>
                <p style='color: white; margin: 0.25rem 0 0 0; font-size: 1.2rem; font-weight: 600;'>
                    {datetime.now().strftime('%H:%M')}
                </p>
            </div>
        """, unsafe_allow_html=True)

    with header_col3:
        # ✅ Only show chat button if NOT on AI Chatbot page
        if current_page != "AI Chatbot":
            st.markdown(
                """
                <style>
                .chat-header-btn {
                    background-color: #0078ff;
                    color: white;
                    border: none;
                    border-radius: 50%;
                    width: 50px;
                    height: 50px;
                    font-size: 22px;
                    cursor: pointer;
                    box-shadow: 0px 4px 10px rgba(0,0,0,0.25);
                    transition: all 0.2s ease-in-out;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    margin-top: 10px;
                }
                .chat-header-btn:hover {
                    transform: scale(1.1);
                    background-color: #005ecc;
                }
                </style>
                """,
                unsafe_allow_html=True
            )

            if st.button("🤖", key="header_chat_button"):
                st.session_state.show_chat_popup = not st.session_state.get("show_chat_popup", False)

    st.divider()
