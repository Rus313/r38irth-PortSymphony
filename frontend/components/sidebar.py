"""
Sidebar Component
Navigation and filters
"""

import streamlit as st
from datetime import datetime, timedelta
from frontend.config import departments

def render_sidebar() -> str:
    """Render sidebar with navigation and filters"""
    
    with st.sidebar:
        # Logo and title
        st.markdown("""
            <div style='text-align: center; padding: 1rem 0;'>
                <h1 style='color: #00B4D8; font-size: 2rem; margin: 0;'>🚢</h1>
                <h2 style='color: white; font-size: 1.2rem; margin: 0.5rem 0;'>PSA Global</h2>
                <p style='color: #A0A0A0; font-size: 0.8rem; margin: 0;'>Insights Dashboard</p>
            </div>
        """, unsafe_allow_html=True)
        
        st.divider()
        
        # Department Selection
        st.subheader("👤 Department")
        selected_dept = st.selectbox(
            "Select your department",
            options=list(departments.DEPARTMENTS.keys()),
            index=list(departments.DEPARTMENTS.keys()).index(st.session_state.user_department),
            label_visibility="collapsed"
        )
        st.session_state.user_department = selected_dept
        
        # Show department-specific info
        dept_info = departments.DEPARTMENTS[selected_dept]
        st.markdown(f"""
            <div style='background: rgba(0, 180, 216, 0.1); 
                        padding: 1rem; 
                        border-radius: 8px; 
                        border-left: 4px solid {dept_info["color"]};
                        margin-bottom: 1rem;'>
                <p style='color: #A0A0A0; font-size: 0.8rem; margin: 0;'>Available Modules:</p>
                <p style='color: white; margin: 0.5rem 0 0 0; font-size: 0.9rem;'>
                    {', '.join(dept_info['modules'])}
                </p>
            </div>
        """, unsafe_allow_html=True)
        
        st.divider()
        
        # Navigation
        st.subheader("🧭 Navigation")
        
        pages = [
            ('Global Insights', '🌍'),
            ('Vessel Performance', '🚢'),
            ('Sustainability', '🌱'),
            ('Berth Management', '⚓'),
            ('AI Chatbot', '🤖')
        ]
        
        # Create navigation buttons
        for page_name, icon in pages:
            is_current = st.session_state.current_page == page_name
            
            if st.button(
                f"{icon} {page_name}",
                key=f"nav_{page_name}",
                use_container_width=True,
                type="primary" if is_current else "secondary"
            ):
                st.session_state.current_page = page_name
                st.rerun()
        
        st.divider()
        
        # Filters
        st.subheader("🔍 Filters")
        
        # Date Range Filter
        with st.expander("📅 Date Range", expanded=True):
            date_preset = st.selectbox(
                "Quick Select",
                ["Today", "Last 7 Days", "Last 30 Days", "This Month", "Custom"],
                label_visibility="collapsed"
            )
            
            if date_preset == "Custom":
                col1, col2 = st.columns(2)
                with col1:
                    start_date = st.date_input(
                        "Start",
                        value=datetime.now() - timedelta(days=7)
                    )
                with col2:
                    end_date = st.date_input(
                        "End",
                        value=datetime.now()
                    )
                st.session_state.date_range = (start_date, end_date)
            else:
                # Auto-calculate date range based on preset
                end_date = datetime.now()
                if date_preset == "Today":
                    start_date = end_date
                elif date_preset == "Last 7 Days":
                    start_date = end_date - timedelta(days=7)
                elif date_preset == "Last 30 Days":
                    start_date = end_date - timedelta(days=30)
                else:  # This Month
                    start_date = end_date.replace(day=1)
                
                st.session_state.date_range = (start_date, end_date)
                st.caption(f"📅 {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")
        
        # Vessel Filter
        with st.expander("🚢 Vessels", expanded=False):
            vessel_filter = st.multiselect(
                "Select vessels",
                ["All Vessels", "MSC Diana", "Ever Given", "CMA CGM Antoine", 
                 "Maersk Essex", "COSCO Shipping"],
                default=["All Vessels"],
                label_visibility="collapsed"
            )
            st.session_state.selected_vessels = vessel_filter
        
        # Port Filter
        with st.expander("🌍 Ports", expanded=False):
            port_filter = st.multiselect(
                "Select ports",
                ["All Ports", "Singapore", "Rotterdam", "Shanghai", 
                 "Los Angeles", "Antwerp"],
                default=["All Ports"],
                label_visibility="collapsed"
            )
        
        # Status Filter
        with st.expander("📊 Status", expanded=False):
            status_filter = st.multiselect(
                "Select status",
                ["All Status", "At Berth", "Waiting", "In Transit", 
                 "Departed", "Delayed"],
                default=["All Status"],
                label_visibility="collapsed"
            )
        
        st.divider()
        
        # Quick Actions
        st.subheader("⚡ Quick Actions")
        
        if st.button("🔄 Refresh Data", use_container_width=True):
            st.cache_data.clear()
            st.success("Data refreshed!")
            st.rerun()
        
        if st.button("📥 Export Report", use_container_width=True):
            st.info("Export functionality coming soon!")
        
        if st.button("⚙️ Settings", use_container_width=True):
            st.info("Settings panel coming soon!")
        
        st.divider()
        
        # System Status
        st.subheader("💡 System Status")
        st.markdown("""
            <div style='background: rgba(6, 214, 160, 0.1); 
                        padding: 0.75rem; 
                        border-radius: 8px;
                        border-left: 4px solid #06D6A0;'>
                <p style='color: #06D6A0; margin: 0; font-size: 0.9rem;'>
                    ✓ All Systems Operational
                </p>
            </div>
        """, unsafe_allow_html=True)
        
        st.divider()  # ← MOVED INSIDE (this was at line 179, outside the block)
        
        st.caption(f"Last updated: {datetime.now().strftime('%H:%M:%S')}")
        
        st.divider()
        
        # ✅ ADD: User info and logout
        from security.auth import AuthManager
        from security.session_manager import get_session_info
        
        auth = AuthManager()
        user_info = auth.get_current_user()
        session_info = get_session_info()
        
        if user_info:
            st.subheader("👤 User Info")
            st.markdown(f"""
                <div style='background: rgba(0, 180, 216, 0.1); 
                            padding: 1rem; 
                            border-radius: 8px;'>
                    <p style='margin: 0; color: white;'><strong>User:</strong> {user_info['username']}</p>
                    <p style='margin: 0; color: white;'><strong>Role:</strong> {user_info['role']}</p>
                    <p style='margin: 0; color: white;'><strong>Department:</strong> {user_info['department']}</p>
                </div>
            """, unsafe_allow_html=True)
            
            # Session info - with None checks
            if session_info:
                with st.expander("⏱️ Session Info"):
                    # Check if logged_in_since exists and is not None
                    if session_info.get('logged_in_since'):
                        st.caption(f"Logged in: {session_info['logged_in_since'].strftime('%H:%M:%S')}")
                    
                    # Check if other fields exist
                    if session_info.get('session_expires_in'):
                        st.caption(f"Session expires in: {session_info['session_expires_in']}")
                    
                    if session_info.get('idle_expires_in'):
                        st.caption(f"Idle timeout in: {session_info['idle_expires_in']}")
            
            # Logout button
            if st.button("🚪 Logout", use_container_width=True, type="secondary"):
                auth.logout()
                st.success("Logged out successfully")
                st.rerun()
    
    return st.session_state.current_page