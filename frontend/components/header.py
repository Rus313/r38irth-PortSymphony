"""
Header Component
Page header with title and quick stats
"""

import streamlit as st
from datetime import datetime

def render_header():
    """Render page header with branding and quick stats"""
    
    # Create header container
    header_col1, header_col2 = st.columns([3, 1])
    
    with header_col1:
        # Page title with current page
        current_page = st.session_state.get('current_page', 'Global Insights')
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
        # Quick stats / notifications
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
    
    st.divider()
