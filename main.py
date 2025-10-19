"""
PSA Global Insights Dashboard - Main Entry Point
Frontend Implementation by Senior Frontend Engineer
"""

import streamlit as st
from pathlib import Path
import sys
from frontend.components.chat_overlay import chat_overlay

# Add project root to path
sys.path.append(str(Path(__file__).parent))

from frontend.config import PageConfig
from frontend.components.sidebar import render_sidebar
from frontend.components.header import render_header
from frontend.pages import (
    global_insights,
    vessel_performance,
    sustainability,
    berth_management
)

# Page configuration
st.set_page_config(
    page_title=PageConfig.PAGE_TITLE,
    page_icon=PageConfig.PAGE_ICON,
    layout=PageConfig.LAYOUT,
    initial_sidebar_state=PageConfig.SIDEBAR_STATE
)

# Custom CSS for enhanced UI/UX
def load_custom_css():
    st.markdown("""
        <style>
        /* Modern color scheme */
        :root {
            --primary-color: #0066CC;
            --secondary-color: #00B4D8;
            --success-color: #06D6A0;
            --warning-color: #FFD60A;
            --danger-color: #EF476F;
            --dark-bg: #1E1E1E;
            --card-bg: #2D2D2D;
        }
        
        /* Main container styling */
        .main {
            padding: 2rem;
            background: linear-gradient(135deg, #0f0f1e 0%, #1a1a2e 100%);
        }
        
        /* Card styling */
        .stMetric {
            background: var(--card-bg);
            padding: 1.5rem;
            border-radius: 12px;
            border: 1px solid rgba(255, 255, 255, 0.1);
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
            transition: transform 0.2s ease, box-shadow 0.2s ease;
        }
        
        .stMetric:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 12px rgba(0, 180, 216, 0.3);
        }
        
        /* Metric label styling */
        .stMetric label {
            font-size: 0.9rem !important;
            font-weight: 600 !important;
            color: #A0A0A0 !important;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        
        /* Metric value styling */
        .stMetric [data-testid="stMetricValue"] {
            font-size: 2rem !important;
            font-weight: 700 !important;
            color: #FFFFFF !important;
        }
        
        /* Chat message styling */
        .stChatMessage {
            background: var(--card-bg);
            border-radius: 12px;
            padding: 1rem;
            margin-bottom: 1rem;
            border: 1px solid rgba(255, 255, 255, 0.1);
        }
        
        /* Button styling */
        .stButton button {
            background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
            color: white;
            border: none;
            border-radius: 8px;
            padding: 0.75rem 2rem;
            font-weight: 600;
            transition: all 0.3s ease;
            box-shadow: 0 4px 6px rgba(0, 102, 204, 0.3);
        }
        
        .stButton button:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 12px rgba(0, 102, 204, 0.5);
        }
        
        /* Sidebar styling */
        section[data-testid="stSidebar"] {
            background: linear-gradient(180deg, #1a1a2e 0%, #16213e 100%);
            border-right: 1px solid rgba(255, 255, 255, 0.1);
        }
        
        /* Tab styling */
        .stTabs [data-baseweb="tab-list"] {
            gap: 8px;
            background-color: transparent;
        }
        
        .stTabs [data-baseweb="tab"] {
            background-color: var(--card-bg);
            border-radius: 8px;
            padding: 0.75rem 1.5rem;
            border: 1px solid rgba(255, 255, 255, 0.1);
            color: #A0A0A0;
            font-weight: 600;
        }
        
        .stTabs [aria-selected="true"] {
            background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
            color: white;
            border: none;
        }
        
        /* Expander styling */
        .streamlit-expanderHeader {
            background-color: var(--card-bg);
            border-radius: 8px;
            border: 1px solid rgba(255, 255, 255, 0.1);
            font-weight: 600;
        }
        
        /* Dataframe styling */
        .stDataFrame {
            border-radius: 8px;
            overflow: hidden;
        }
        
        /* Input styling */
        .stTextInput input, .stSelectbox select {
            background-color: var(--card-bg);
            border: 1px solid rgba(255, 255, 255, 0.2);
            border-radius: 8px;
            color: white;
            padding: 0.75rem;
        }
        
        /* Alert styling */
        .stAlert {
            border-radius: 8px;
            border: none;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.2);
        }
        
        /* Success alert */
        .stAlert[data-baseweb="notification"] {
            background-color: rgba(6, 214, 160, 0.1);
            border-left: 4px solid var(--success-color);
        }
        
        /* Info alert */
        .stInfo {
            background-color: rgba(0, 180, 216, 0.1);
            border-left: 4px solid var(--secondary-color);
        }
        
        /* Warning alert */
        .stWarning {
            background-color: rgba(255, 214, 10, 0.1);
            border-left: 4px solid var(--warning-color);
        }
        
        /* Hide Streamlit branding */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        
        /* Smooth scrolling */
        html {
            scroll-behavior: smooth;
        }
        
        /* Loading spinner */
        .stSpinner > div {
            border-color: var(--secondary-color) transparent transparent transparent;
        }
        </style>
    """, unsafe_allow_html=True)

def initialize_session_state():
    """Initialize all session state variables"""
    if 'current_page' not in st.session_state:
        st.session_state.current_page = 'Global Insights'
    
    if 'user_department' not in st.session_state:
        st.session_state.user_department = 'Operations'
    
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    
    if 'selected_vessels' not in st.session_state:
        st.session_state.selected_vessels = []
    
    if 'date_range' not in st.session_state:
        st.session_state.date_range = None
    
    if 'theme' not in st.session_state:
        st.session_state.theme = 'dark'

def main():
    """Main application entry point"""
    
    chat_overlay()

    # Load custom CSS
    load_custom_css()
    
    # Initialize session state
    initialize_session_state()
    
    # Render header
    render_header()
    
    # Render sidebar and get selected page
    selected_page = render_sidebar()
    
    # Route to appropriate page
    page_routing = {
        'Global Insights': global_insights.render,
        'Vessel Performance': vessel_performance.render,
        'Sustainability': sustainability.render,
        'Berth Management': berth_management.render
    }
    
    # Render selected page
    if selected_page in page_routing:
        page_routing[selected_page]()
    else:
        st.error(f"Page '{selected_page}' not found")

if __name__ == "__main__":
    main()