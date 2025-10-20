"""
PSA Global Insights Dashboard - Main Entry Point
Frontend Implementation by Senior Frontend Engineer
"""

import streamlit as st
from frontend.config import PageConfig

# Page configuration
st.set_page_config(
    page_title=PageConfig.PAGE_TITLE,
    page_icon=PageConfig.PAGE_ICON,
    layout=PageConfig.LAYOUT,
    initial_sidebar_state=PageConfig.SIDEBAR_STATE
)


from pathlib import Path
import sys
# from frontend.components.chat_overlay import chat_overlay

# Add project root to path
sys.path.append(str(Path(__file__).parent))

from data.pdf_loader import get_data_loader
from frontend.components.sidebar import render_sidebar
from frontend.components.header import render_header
from frontend.pages import (
    global_insights,
    vessel_performance,
    sustainability,
    berth_management,
    ai_chatbot
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
            max-height: 60% !important; 
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
        
        /* Floating chat button */
        .chat-button {
            position: fixed;
            bottom: 25px;
            right: 25px;
            background-color: #0078ff;
            color: white;
            border: none;
            border-radius: 50%;
            width: 60px;
            height: 60px;
            font-size: 28px;
            cursor: pointer;
            box-shadow: 0px 4px 12px rgba(0,0,0,0.3);
            z-index: 1000;
            transition: all 0.2s ease-in-out;
        }
        .chat-button:hover {
            transform: scale(1.1);
            background-color: #005ecc;
        }

        /* Chat popup */
        .chat-popup {
            position: fixed;
            bottom: 10px;
            right: 25px;
            width: 300px;
            height: 450px;
            background-color: #0e1117;
            border: 1px solid #444;
            border-radius: 12px;
            z-index: 1001;
            overflow: hidden;
        }
        .chat-popup iframe {
            width: 100%;
            height: 100%;
            border: none;
            background-color: #0e1117;
        }        

        /* Hide Streamlit branding */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        
        /* Smooth scrolling */
        html {
            scroll-behavior: smooth;
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
    
    if 'show_chat_popup' not in st.session_state:
        st.session_state.show_chat_popup = False

@st.cache_resource
def init_data_source():
    """Initialize data source from PDF"""
    try:
        return get_data_loader('data/ship_movements.pdf')
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return None

def show_login_page():
    """
    Display login page
    """
    from security.auth import AuthManager
    
    # DON'T call st.set_page_config() here - it's already called at the top!
    
    # Center the login form
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.title("🚢 PSA Global Insights")
        st.subheader("Please log in to continue")
        
        # Login form
        with st.form("login_form"):
            username = st.text_input("Username", placeholder="Enter your username")
            password = st.text_input("Password", type="password", placeholder="Enter your password")
            submit = st.form_submit_button("Login", use_container_width=True, type="primary")
            
            if submit:
                if not username or not password:
                    st.error("Please enter both username and password")
                else:
                    # Attempt login
                    auth = AuthManager()
                    success, message, user_info = auth.login(username, password)
                    
                    if success:
                        st.success(message)
                        st.rerun()  # Reload page to show main app
                    else:
                        st.error(message)
        
        # Help text
        st.divider()
        st.caption("🔒 Your connection is secure")
        
        # Temporary: Show test credentials (REMOVE IN PRODUCTION!)
        with st.expander("📝 Test Credentials (Development Only)"):
            st.info("""
            **Admin Account:**
            - Username: `admin`
            - Password: `admin123`
            
            **Operations User:**
            - Username: `operations_user`
            - Password: `ops123`
            
            **Viewer:**
            - Username: `viewer`
            - Password: `view123`
            
            ⚠️ **IMPORTANT:** Change these passwords in production!
            """)

def main():
    """Main application entry point"""
    
    # Check if user needs to log in
    from security.auth import AuthManager
    from security.session_manager import validate_session
    
    auth = AuthManager()
    
    # Check if user is authenticated
    if not auth.is_authenticated():
        # Show login page
        show_login_page()
        return  # Stop here until logged in
    
    # Validate session (check timeouts)
    validate_session()

    # Load custom CSS
    load_custom_css()
    
    # Initialize session state
    initialize_session_state()

    data_source = init_data_source()
    if data_source is None:
        st.error("Failed to load data. Please check your PDF file.")
        st.stop()
    
    # Render header
    render_header()
    
    # Render sidebar and get selected page
    selected_page = render_sidebar()

    # -------------------------
    # Handle AI Chat Popup (via iframe page)
    # -------------------------
    query_params = st.experimental_get_query_params()
    if query_params.get("page") == ["ai_chat_popup"]:
        ai_chatbot.render()
        return

    # Normal routing
    page_routing = {
        'Global Insights': global_insights.render,
        'Vessel Performance': vessel_performance.render,
        'Sustainability': sustainability.render,
        'Berth Management': berth_management.render,
        'AI Chatbot': ai_chatbot.render
    }

    if selected_page in page_routing:
        page_routing[selected_page]()
    else:
        st.error(f"Page '{selected_page}' not found")

    # -------------------------
    # Floating Chat Button
    # -------------------------
    # Show button only if not on dedicated AI Chatbot page
    if selected_page != 'AI Chatbot':
        # Toggle popup via Streamlit button
        if st.button("🤖", key="open_chat_button"):
            st.session_state.show_chat_popup = not st.session_state.show_chat_popup

        # Render popup
        if st.session_state.show_chat_popup:
            st.markdown("""
            <div class="chat-popup">
                <iframe src="?page=ai_chat_popup"></iframe>
            </div>
            """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()