"""
Berth Management Page
Real-time berth operations and optimization
Frontend Engineer: UI/UX Specialist
"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from frontend.config import colors, charts


def create_berth_status_overview():
    """Create real-time berth status overview"""
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric(
            label="⚓ Total Berths",
            value="24",
            help="Total number of berths across all terminals"
        )
    
    with col2:
        st.metric(
            label="🟢 Available",
            value="8",
            delta="+2",
            help="Berths currently available for use"
        )
    
    with col3:
        st.metric(
            label="🔴 Occupied",
            value="14",
            delta="-2",
            delta_color="inverse",
            help="Berths currently in use"
        )
    
    with col4:
        st.metric(
            label="🟡 Maintenance",
            value="2",
            help="Berths under maintenance"
        )
    
    with col5:
        st.metric(
            label="📊 Utilization",
            value="73.2%",
            delta="+4.1%",
            help="Average berth utilization rate"
        )


def create_berth_status_grid():
    """Create visual grid of berth statuses"""
    
    berths = [
        {'id': 'B01', 'status': 'Available', 'terminal': 'T1', 'vessel': None},
        {'id': 'B02', 'status': 'Occupied', 'terminal': 'T1', 'vessel': 'MSC Diana'},
        {'id': 'B03', 'status': 'Occupied', 'terminal': 'T1', 'vessel': 'Ever Given'},
        {'id': 'B04', 'status': 'Available', 'terminal': 'T1', 'vessel': None},
        {'id': 'B05', 'status': 'Occupied', 'terminal': 'T2', 'vessel': 'CMA CGM Antoine'},
        {'id': 'B06', 'status': 'Maintenance', 'terminal': 'T2', 'vessel': None},
        {'id': 'B07', 'status': 'Available', 'terminal': 'T2', 'vessel': None},
        {'id': 'B08', 'status': 'Occupied', 'terminal': 'T2', 'vessel': 'Maersk Essex'},
        {'id': 'B09', 'status': 'Occupied', 'terminal': 'T3', 'vessel': 'COSCO Shipping'},
        {'id': 'B10', 'status': 'Occupied', 'terminal': 'T3', 'vessel': 'Hapag-Lloyd'},
        {'id': 'B11', 'status': 'Available', 'terminal': 'T3', 'vessel': None},
        {'id': 'B12', 'status': 'Occupied', 'terminal': 'T3', 'vessel': 'ONE Innovation'},
        {'id': 'B13', 'status': 'Occupied', 'terminal': 'T4', 'vessel': 'Yang Ming'},
        {'id': 'B14', 'status': 'Available', 'terminal': 'T4', 'vessel': None},
        {'id': 'B15', 'status': 'Occupied', 'terminal': 'T4', 'vessel': 'MSK Melbourne'},
        {'id': 'B16', 'status': 'Available', 'terminal': 'T4', 'vessel': None},
    ]
    
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
    
    for idx, berth in enumerate(berths):
        col_idx = idx % 4  # Which column (0-3)
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

def create_berth_gantt_chart():
    """Create Gantt chart for berth schedule"""
    
    # Sample schedule data
    schedule = pd.DataFrame({
        'Berth': ['B02', 'B02', 'B03', 'B03', 'B05', 'B05', 'B08', 'B08', 
                  'B09', 'B10', 'B12', 'B13', 'B15'],
        'Vessel': ['MSC Diana', 'Ever Given', 'Ever Given', 'CMA CGM Antoine', 
                   'CMA CGM Antoine', 'Maersk Essex', 'Maersk Essex', 'COSCO Shipping',
                   'COSCO Shipping', 'Hapag-Lloyd', 'ONE Innovation', 'Yang Ming', 'MSK Melbourne'],
        'Start': [
            datetime.now() - timedelta(hours=4),
            datetime.now() + timedelta(hours=20),
            datetime.now() - timedelta(hours=2),
            datetime.now() + timedelta(hours=22),
            datetime.now() - timedelta(hours=6),
            datetime.now() + timedelta(hours=18),
            datetime.now() - timedelta(hours=3),
            datetime.now() + timedelta(hours=21),
            datetime.now() - timedelta(hours=5),
            datetime.now() - timedelta(hours=7),
            datetime.now() - timedelta(hours=8),
            datetime.now() - timedelta(hours=2),
            datetime.now() - timedelta(hours=1)
        ],
        'End': [
            datetime.now() + timedelta(hours=20),
            datetime.now() + timedelta(hours=44),
            datetime.now() + timedelta(hours=22),
            datetime.now() + timedelta(hours=46),
            datetime.now() + timedelta(hours=18),
            datetime.now() + timedelta(hours=42),
            datetime.now() + timedelta(hours=21),
            datetime.now() + timedelta(hours=45),
            datetime.now() + timedelta(hours=19),
            datetime.now() + timedelta(hours=17),
            datetime.now() + timedelta(hours=16),
            datetime.now() + timedelta(hours=22),
            datetime.now() + timedelta(hours=23)
        ]
    })
    
    fig = px.timeline(
        schedule,
        x_start='Start',
        x_end='End',
        y='Berth',
        color='Vessel',
        title='⚓ Berth Utilization Timeline (Next 48 Hours)',
        color_discrete_sequence=colors.CHART_COLORS
    )
    
    fig.update_layout(
        **charts.LAYOUT_CONFIG,
        height=500,
        xaxis_title='Time',
        yaxis_title='Berth',
        showlegend=True,
        legend=dict(
            orientation='v',
            yanchor='top',
            y=1,
            xanchor='left',
            x=1.01
        )
    )
    
    fig.update_xaxes(
        range=[datetime.now() - timedelta(hours=12), datetime.now() + timedelta(hours=48)]
    )
    
    return fig


def create_bunching_heatmap():
    """Create heatmap showing vessel bunching"""
    
    # Sample bunching data
    berths = [f'B{i:02d}' for i in range(1, 17)]
    time_slots = ['00-04', '04-08', '08-12', '12-16', '16-20', '20-24']
    
    np.random.seed(42)
    data = np.random.randint(0, 5, size=(len(berths), len(time_slots)))
    
    fig = go.Figure(data=go.Heatmap(
        z=data,
        x=time_slots,
        y=berths,
        colorscale=[
            [0, colors.SUCCESS],
            [0.3, colors.WARNING],
            [1, colors.DANGER]
        ],
        text=data,
        texttemplate='%{text}',
        textfont={'size': 10},
        hovertemplate='<b>%{y}</b><br>Time: %{x}:00<br>Vessels: %{z}<extra></extra>',
        colorbar=dict(
            title='Vessels',
            titleside='right'
        )
    ))
    
    fig.update_layout(
        **charts.LAYOUT_CONFIG,
        height=450,
        title={
            'text': '🔥 Vessel Bunching Analysis (Today)',
            'font': {'size': 20, 'color': 'white'},
            'x': 0.5,
            'xanchor': 'center'
        },
        xaxis_title='Time Slot',
        yaxis_title='Berth'
    )
    
    return fig


def create_utilization_trend():
    """Create berth utilization trend chart"""
    
    # Generate sample data
    dates = pd.date_range(end=datetime.now(), periods=30, freq='D')
    df = pd.DataFrame({
        'Date': dates,
        'Terminal 1': np.random.normal(75, 5, 30).clip(60, 90),
        'Terminal 2': np.random.normal(72, 4, 30).clip(60, 90),
        'Terminal 3': np.random.normal(78, 6, 30).clip(60, 90),
        'Terminal 4': np.random.normal(70, 5, 30).clip(60, 90),
        'Target': [75] * 30
    })
    
    fig = go.Figure()
    
    terminals = ['Terminal 1', 'Terminal 2', 'Terminal 3', 'Terminal 4']
    terminal_colors = [colors.PRIMARY, colors.SECONDARY, colors.SUCCESS, colors.WARNING]
    
    for terminal, color in zip(terminals, terminal_colors):
        fig.add_trace(go.Scatter(
            x=df['Date'],
            y=df[terminal],
            name=terminal,
            line=dict(color=color, width=2),
            mode='lines+markers',
            marker=dict(size=5)
        ))
    
    # Target line
    fig.add_trace(go.Scatter(
        x=df['Date'],
        y=df['Target'],
        name='Target (75%)',
        line=dict(color='white', width=2, dash='dash'),
        mode='lines'
    ))
    
    fig.update_layout(
        **charts.LAYOUT_CONFIG,
        height=400,
        title={
            'text': '📊 Berth Utilization Trend by Terminal',
            'font': {'size': 20, 'color': 'white'},
            'x': 0.5,
            'xanchor': 'center'
        },
        xaxis_title='Date',
        yaxis_title='Utilization (%)',
        yaxis=dict(range=[50, 95]),
        legend=dict(
            orientation='h',
            yanchor='bottom',
            y=1.02,
            xanchor='right',
            x=1
        )
    )
    
    return fig


def create_waiting_vessels_table():
    """Create table of vessels waiting for berth"""
    
    waiting = pd.DataFrame({
        'Vessel': ['CMA CGM Paris', 'MSC Mediterranean', 'Maersk Tokyo', 'ONE Harmony'],
        'ETA': [
            (datetime.now() + timedelta(hours=2)).strftime('%Y-%m-%d %H:%M'),
            (datetime.now() + timedelta(hours=4)).strftime('%Y-%m-%d %H:%M'),
            (datetime.now() + timedelta(hours=6)).strftime('%Y-%m-%d %H:%M'),
            (datetime.now() + timedelta(hours=8)).strftime('%Y-%m-%d %H:%M')
        ],
        'Requested Berth': ['B04', 'B07', 'B11', 'B14'],
        'Wait Time (est)': ['2.1 hrs', '4.3 hrs', '1.8 hrs', '3.5 hrs'],
        'Priority': ['🔴 High', '🟡 Medium', '🟢 Low', '🟡 Medium'],
        'Status': ['Assigned', 'Waiting', 'Assigned', 'Waiting']
    })
    
    def highlight_priority(row):
        if row['Priority'] == '🔴 High':
            return ['background-color: rgba(239, 71, 111, 0.2)'] * len(row)
        elif row['Priority'] == '🟡 Medium':
            return ['background-color: rgba(255, 214, 10, 0.2)'] * len(row)
        return [''] * len(row)
    
    styled_df = waiting.style.apply(highlight_priority, axis=1)
    
    return styled_df


def create_berth_recommendations():
    """Create AI-powered berth assignment recommendations"""
    
    st.markdown("""
        <div style='background: linear-gradient(135deg, rgba(0, 180, 216, 0.2), rgba(138, 56, 236, 0.2));
                    padding: 1.5rem;
                    border-radius: 12px;
                    border: 1px solid rgba(0, 180, 216, 0.3);'>
            <h3 style='color: #00B4D8; margin: 0 0 1rem 0;'>🤖 AI-Powered Berth Recommendations</h3>
            <div style='display: grid; gap: 1rem;'>
                <div style='background: rgba(0, 0, 0, 0.3); padding: 1rem; border-radius: 8px; border-left: 4px solid #06D6A0;'>
                    <div style='font-weight: 600; color: white; margin-bottom: 0.5rem;'>✅ Optimal Assignment</div>
                    <div style='color: #A0A0A0; font-size: 0.9rem;'>
                        Assign <strong style='color: white;'>CMA CGM Paris</strong> to <strong style='color: white;'>Berth B04</strong><br>
                        • Reduces wait time by 1.2 hours<br>
                        • Saves $2,400 in operational costs<br>
                        • No schedule conflicts
                    </div>
                </div>
                <div style='background: rgba(0, 0, 0, 0.3); padding: 1rem; border-radius: 8px; border-left: 4px solid #FFD60A;'>
                    <div style='font-weight: 600; color: white; margin-bottom: 0.5rem;'>⚠️ Bunching Alert</div>
                    <div style='color: #A0A0A0; font-size: 0.9rem;'>
                        3 vessels scheduled at <strong style='color: white;'>Terminal 4</strong> between 14:00-16:00<br>
                        • Recommend staggering arrivals by 45 minutes<br>
                        • Contact <strong style='color: white;'>MSC Mediterranean</strong> for delay coordination
                    </div>
                </div>
                <div style='background: rgba(0, 0, 0, 0.3); padding: 1rem; border-radius: 8px; border-left: 4px solid #00B4D8;'>
                    <div style='font-weight: 600; color: white; margin-bottom: 0.5rem;'>💡 Efficiency Opportunity</div>
                    <div style='color: #A0A0A0; font-size: 0.9rem;'>
                        <strong style='color: white;'>Berth B12</strong> will be available 2 hours early<br>
                        • Can accommodate <strong style='color: white;'>Maersk Tokyo</strong> ahead of schedule<br>
                        • Potential to reduce port congestion by 15%
                    </div>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)


def render():
    """Render the Berth Management page"""
    
    # ✅ ADD: Permission check
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
