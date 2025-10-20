"""
AI Chat Page
Interactive AI chatbot with dashboard interpretation capabilities
Uses DashboardAgent with function calling and domain expertise
"""
import streamlit as st
from backend.dashboard_agent import DashboardAgent
from backend.dashboard_data_access import DashboardDataAccess
from data.pdf_loader import get_data_loader

# -------------------------
# Initialize Smart Agent
# -------------------------
@st.cache_resource
def init_smart_agent():
    """Initialize the smart dashboard agent with domain expertise"""
    db = get_data_loader()
    data_access = DashboardDataAccess(db)
    agent = DashboardAgent(data_access)
    return agent

agent = init_smart_agent()

# -------------------------
# Render AI Chat Page
# -------------------------
def render():
    st.subheader("🤖 AI Dashboard Assistant")
    st.caption("I'm an expert maritime analyst with real-time access to your dashboard data!")
    
    # Initialize chat history in session state
    if "history" not in st.session_state:
        st.session_state.history = []
    
    if "stakeholder_role" not in st.session_state:
        st.session_state.stakeholder_role = "middle_management"
    
    # -------------------------
    # Sidebar options
    # -------------------------
    st.sidebar.subheader("🎭 Communication Settings")
    
    # Stakeholder role selector
    role_options = {
        "Top Management (Strategic)": "top_management",
        "Middle Management (Tactical)": "middle_management",
        "Frontline Operations (Immediate)": "frontline_operations"
    }
    
    selected_role = st.sidebar.selectbox(
        "I'm speaking to:",
        list(role_options.keys()),
        index=1,
        help="The AI will tailor its communication style to your role"
    )
    st.session_state.stakeholder_role = role_options[selected_role]
    
    st.sidebar.markdown("---")
    st.sidebar.subheader("💡 What I Can Do")
    st.sidebar.markdown("""
    **Real-Time Data Access:**
    - ✅ Read live dashboard data
    - ✅ Filter by berth, time, vessel
    - ✅ Analyze delays and patterns
    - ✅ Generate recommendations
    
    **Domain Expertise:**
    - 🎯 Performance interpretation
    - ⚠️ Issue identification
    - 💡 Actionable insights
    - 📊 Trend analysis
    """)
    
    st.sidebar.markdown("---")
    st.sidebar.subheader("🚀 Quick Actions")
    
    # Quick action buttons in sidebar
    if st.sidebar.button("📊 Dashboard Summary", use_container_width=True):
        st.session_state.pending_query = "Give me a comprehensive summary of what's currently on the dashboard."
    
    if st.sidebar.button("⏰ Check Delays", use_container_width=True):
        st.session_state.pending_query = "Are there any delays right now? What's causing them?"
    
    if st.sidebar.button("🎯 Get Recommendations", use_container_width=True):
        st.session_state.pending_query = "Based on current data, what actions should I take to improve efficiency?"
    
    if st.sidebar.button("📈 Performance Status", use_container_width=True):
        st.session_state.pending_query = "How is our overall performance? Any concerns?"
    
    if st.sidebar.button("🔥 Critical Issues", use_container_width=True):
        st.session_state.pending_query = "What are the most critical issues I need to address immediately?"
    
    if st.sidebar.button("⚓ Berth Status", use_container_width=True):
        st.session_state.pending_query = "Show me the current status of all berths."
    
    if st.sidebar.button("🌱 Carbon Impact", use_container_width=True):
        st.session_state.pending_query = "What's our carbon performance and environmental impact?"
    
    if st.sidebar.button("🚢 Vessel Queue", use_container_width=True):
        st.session_state.pending_query = "Which vessels are waiting and for how long?"
    
    # -------------------------
    # Main Chat Area
    # -------------------------
    
    # Show example queries
    with st.expander("💬 Example Questions"):
        st.markdown("""
        **Performance Questions:**
        - "What's the current situation on the dashboard?"
        - "How are we performing against targets?"
        - "Which vessels have the best/worst performance?"
        
        **Specific Queries:**
        - "Show me delays at Berth B02 in the last 3 hours"
        - "What's the wait time for vessels at Terminal 1?"
        - "Which berth has the most congestion?"
        
        **Analysis:**
        - "Analyze delays across all berths"
        - "What patterns do you see in the data?"
        - "Compare Terminal 1 vs Terminal 3 performance"
        
        **Recommendations:**
        - "What should I focus on to improve efficiency?"
        - "How can we reduce carbon emissions?"
        - "What's the best way to optimize berth utilization?"
        """)
    
    # Chat messages
    for idx, msg in enumerate(st.session_state.history):
        if msg["role"] == "user":
            st.chat_message("user").write(msg["content"])
        elif msg["role"] == "assistant":
            with st.chat_message("assistant"):
                st.write(msg["content"])
                
                # Show function calls if available
                if msg.get("functions_called"):
                    with st.expander(f"🔧 Data Sources Used ({len(msg['functions_called'])} functions)"):
                        for func in msg["functions_called"]:
                            st.caption(f"✓ **{func['function']}**")
                            if func.get('arguments'):
                                st.json(func['arguments'])
        else:
            st.markdown(f"<span style='color:red'>{msg['content']}</span>", unsafe_allow_html=True)
    
    # -------------------------
    # User input
    # -------------------------
    
    # Always show chat input
    chatbox_input = st.chat_input("Ask me anything about the dashboard...")

    # Determine which input to process this run
    user_input = None
    if st.session_state.get('pending_query'):
        user_input = st.session_state.pending_query
        st.session_state.pending_query = None
    elif chatbox_input:
        user_input = chatbox_input
    
    if user_input:
        # Append user message
        st.session_state.history.append({"role": "user", "content": user_input})
        
        # Show user message
        with st.chat_message("user"):
            st.write(user_input)
        
        # Get AI response using smart agent
        with st.chat_message("assistant"):
            with st.spinner("🤖 Analyzing dashboard data with domain expertise..."):
                try:
                    result = agent.process_query(
                        user_input, 
                        st.session_state.history,
                        st.session_state.stakeholder_role
                    )
                    
                    # Display response
                    st.write(result["response"])
                    
                    # Show function calls
                    if result.get("functions_called"):
                        with st.expander(f"🔧 Data Sources Used ({len(result['functions_called'])} functions)"):
                            st.caption("The AI accessed these real-time data sources:")
                            for func in result["functions_called"]:
                                st.caption(f"✓ **{func['function']}**")
                                if func.get('arguments'):
                                    st.json(func['arguments'])
                    
                    # Add to history
                    st.session_state.history.append({
                        "role": "assistant",
                        "content": result["response"],
                        "functions_called": result.get("functions_called", [])
                    })
                    
                except Exception as e:
                    error_msg = f"❌ Error: {str(e)}"
                    st.error(error_msg)
                    st.session_state.history.append({"role": "system", "content": error_msg})
        
        # # 🩹 Fix: clear pending query BEFORE rerun
        # st.session_state.pending_query = None
        # st.rerun()
    
    # -------------------------
    # Chat controls
    # -------------------------
    st.markdown("---")
    
    col1, col2 = st.columns([2, 2])
    
    with col1:
        if st.button("🗑️ Clear Chat", use_container_width=True):
            st.session_state.history = []
            st.rerun()
    
    with col2:
        # Export chat
        if st.button("💾 Export Chat", use_container_width=True):
            import json
            chat_export = json.dumps(st.session_state.history, indent=2)
            st.download_button(
                label="Download JSON",
                data=chat_export,
                file_name="chat_history.json",
                mime="application/json"
            )
    
    # with col3:
    #     # Show stats
    #     if st.session_state.history:
    #         total_messages = len(st.session_state.history)
    #         user_messages = len([m for m in st.session_state.history if m["role"] == "user"])
    #         st.metric("Messages", f"{total_messages} ({user_messages} from you)")
    
    # -------------------------
    # Chat statistics
    # -------------------------
    if st.session_state.history:
        with st.expander("📊 Chat Statistics"):
            col1, col2, col3 = st.columns(3)
            
            with col1:
                user_msgs = len([m for m in st.session_state.history if m["role"] == "user"])
                st.metric("Your Questions", user_msgs)
            
            with col2:
                ai_msgs = len([m for m in st.session_state.history if m["role"] == "assistant"])
                st.metric("AI Responses", ai_msgs)
            
            with col3:
                # Count function calls
                total_functions = sum(
                    len(m.get("functions_called", [])) 
                    for m in st.session_state.history 
                    if m["role"] == "assistant"
                )
                st.metric("Data Queries", total_functions)
            
            # Show function usage breakdown
            if total_functions > 0:
                st.markdown("**Data Sources Used:**")
                function_counts = {}
                for msg in st.session_state.history:
                    if msg["role"] == "assistant" and msg.get("functions_called"):
                        for func in msg["functions_called"]:
                            fname = func["function"]
                            function_counts[fname] = function_counts.get(fname, 0) + 1
                
                for fname, count in function_counts.items():
                    st.caption(f"• {fname}: {count} times")