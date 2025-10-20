"""
Berth Management Page
Real-time berth operations and optimization
"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from frontend.config import colors, charts
from data.demo_dataset import get_demo_dataset  # ✅ Import demo dataset


def create_berth_status_overview():
    """Create real-time berth status overview"""
    
    # ✅ Use demo dataset
    demo = get_demo_dataset()
    berths = demo.berths
    
    # Count by status
    total = len(berths)
    available = len(berths[berths['status'] == 'Available'])
    occupied = len(berths[berths['status'] == 'Occupied'])
    maintenance = len(berths[berths['status'] == 'Maintenance'])
    utilization = (occupied / total * 100) if total > 0 else 0
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric(
            label="⚓ Total Berths",
            value=str(total),
            help="Total number of berths across all terminals"
        )
    
    with col2:
        st.metric(
            label="🟢 Available",
            value=str(available),
            delta="+2",
            help="Berths currently available for use"
        )
    
    with col3:
        st.metric(
            label="🔴 Occupied",
            value=str(occupied),
            delta="-2",
            delta_color="inverse",
            help="Berths currently in use"
        )
    
    with col4:
        st.metric(
            label="🟡 Maintenance",
            value=str(maintenance),
            help="Berths under maintenance"
        )
    
    with col5:
        st.metric(
            label="📊 Utilization",
            value=f"{utilization:.1f}%",
            delta="+4.1%",
            help="Average berth utilization rate"
        )


def create_berth_status_grid():
    """Create visual grid of berth statuses"""
    
    # ✅ Use demo dataset
    demo = get_demo_dataset()
    berths_df = demo.berths
    
    # Get vessel names for occupied berths
    berth_data = []
    for _, berth in berths_df.iterrows():
        vessel_name = None
        if berth['status'] == 'Occupied' and berth['current_vessel_imo']:
            vessel_info = demo.vessels[demo.vessels['imo_number'] == berth['current_vessel_imo']]
            if not vessel_info.empty:
                vessel_name = vessel_info.iloc[0]['vessel_name']
        
        berth_data.append({
            'id': berth['berth_id'],
            'status': berth['status'],
            'terminal': berth['terminal'],
            'vessel': vessel_name
        })
    
    status_colors = {
        'Available': '#06D6A0',
        'Occupied': '#EF476F',
        'Maintenance': '#FFD60A'
    }
    
    status_icons = {
        'Available': '✓',
        'Occupied': '🚢',
        'Maintenance': '🔧'
    }
    
    # Create 4 columns for grid layout
    cols = st.columns(4)
    
    for idx, berth in enumerate(berth_data):
        col_idx = idx % 4
        color = status_colors[berth['status']]
        icon = status_icons[berth['status']]
        
        with cols[col_idx]:
            vessel_info = f"<div style='font-size: 0.75rem; color: #A0A0A0; margin-top: 0.25rem;'>{berth['vessel']}</div>" if berth['vessel'] else ""
            
            st.markdown(f"""
                <div style='background: rgba(0, 0, 0, 0.3); 
                            padding: 1rem; 
                            border-radius: 8px; 
                            border-left: 4px solid {color};
                            margin-bottom: 1rem;'>
                    <div style='font-size: 0.7rem; color: #A0A0A0;'>{berth['terminal']}</div>
                    <div style='font-size: 1.2rem; font-weight: 700; color: white; margin: 0.25rem 0;'>{berth['id']}</div>
                    <div style='font-size: 0.85rem; color: {color};'>{icon} {berth['status']}</div>
                    {vessel_info}
                </div>
            """, unsafe_allow_html=True)


def render():
    """Render the Berth Management page"""

    # ✅ Permission check
    from config.permissions import Permission, require_permission
    require_permission(Permission.VIEW_BERTH_MANAGEMENT)

    # Berth status overview
    st.subheader("⚓ Berth Status Overview")
    create_berth_status_overview()
    
    st.divider()
    
    # Berth status grid
    st.subheader("🔲 Live Berth Status")
    create_berth_status_grid()
    
    st.divider()
    
    # Gantt chart
    st.subheader("📅 Berth Schedule")
    st.plotly_chart(create_berth_gantt_chart(), use_container_width=True)
    
    st.divider()
    
    # Bunching and utilization
    chart_col1, chart_col2 = st.columns(2)
    
    with chart_col1:
        st.plotly_chart(create_bunching_heatmap(), use_container_width=True)
    
    with chart_col2:
        st.plotly_chart(create_utilization_trend(), use_container_width=True)
    
    st.divider()
    
    # Waiting vessels and recommendations
    wait_col1, wait_col2 = st.columns([2, 1])
    
    with wait_col1:
        st.subheader("⏳ Vessels Waiting for Berth")
        st.dataframe(
            create_waiting_vessels_table(),
            use_container_width=True,
            height=220
        )
    
    with wait_col2:
        st.subheader("📊 Queue Statistics")
        st.metric("Total Waiting", "4 vessels", delta="-2")
        st.metric("Avg Wait Time", "2.9 hrs", delta="-0.4 hrs", delta_color="inverse")
        st.metric("Queue Efficiency", "87.3%", delta="+5.2%")
    
    st.divider()
    
    # AI Recommendations
    st.subheader("🤖 Smart Berth Management")
    create_berth_recommendations()
    
    st.divider()
    
    # Quick Actions
    st.subheader("⚡ Quick Actions")
    
    action_col1, action_col2, action_col3, action_col4 = st.columns(4)
    
    with action_col1:
        if st.button("🔄 Refresh Status", use_container_width=True, type="primary"):
            st.success("Berth status refreshed!")
    
    with action_col2:
        if st.button("📊 Generate Report", use_container_width=True):
            st.info("Generating berth utilization report...")
    
    with action_col3:
        if st.button("⚠️ View Alerts", use_container_width=True):
            st.warning("3 active alerts - check bunching at Terminal 4")
    
    with action_col4:
        if st.button("📅 Optimize Schedule", use_container_width=True):
            st.success("AI optimization complete - 12% efficiency gain possible")
