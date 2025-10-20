"""
Vessel Performance Page
Individual vessel analytics and performance tracking
"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from frontend.config import colors, charts
from data.demo_dataset import get_demo_dataset  # ✅ Import demo dataset


def create_vessel_selector():
    """Create vessel search and selection interface"""
    
    # ✅ Use demo dataset
    demo = get_demo_dataset()
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        # Get vessel list from demo data
        vessel_options = [
            f"{row['vessel_name']} (IMO: {row['imo_number']})"
            for _, row in demo.vessels.iterrows()
        ]
        
        selected_vessel = st.selectbox(
            "🚢 Select Vessel",
            vessel_options,
            help="Search by vessel name or IMO number"
        )
        
        # Extract IMO number
        imo = selected_vessel.split("IMO: ")[1].rstrip(")")
        
    with col2:
        if st.button("🔍 Search", use_container_width=True, type="primary"):
            st.success(f"Loading data for {selected_vessel.split(' (')[0]}")
    
    return selected_vessel, imo


def create_vessel_info_card(vessel_name: str, imo: str):
    """Display vessel information card"""
    
    # ✅ Get vessel info from demo data
    demo = get_demo_dataset()
    vessel_info = demo.vessels[demo.vessels['imo_number'] == imo]
    
    if not vessel_info.empty:
        vessel = vessel_info.iloc[0]
        operator = vessel['operator']
        service = vessel['service']
        status = vessel['status']
        status_color = '#06D6A0' if status == 'At Berth' else '#00B4D8'
    else:
        operator = "MSC"
        service = "Asia-Europe"
        status = "At Berth"
        status_color = '#06D6A0'
    
    st.markdown(f"""
        <div style='background: linear-gradient(135deg, rgba(0, 102, 204, 0.2), rgba(0, 180, 216, 0.2));
                    padding: 1.5rem;
                    border-radius: 12px;
                    border: 1px solid rgba(0, 180, 216, 0.3);
                    margin-bottom: 1rem;'>
            <h2 style='color: white; margin: 0 0 1rem 0;'>{vessel_name}</h2>
            <div style='display: grid; grid-template-columns: repeat(4, 1fr); gap: 1rem;'>
                <div>
                    <p style='color: #A0A0A0; font-size: 0.8rem; margin: 0;'>IMO Number</p>
                    <p style='color: white; font-size: 1.1rem; font-weight: 600; margin: 0.25rem 0 0 0;'>{imo}</p>
                </div>
                <div>
                    <p style='color: #A0A0A0; font-size: 0.8rem; margin: 0;'>Operator</p>
                    <p style='color: white; font-size: 1.1rem; font-weight: 600; margin: 0.25rem 0 0 0;'>{operator}</p>
                </div>
                <div>
                    <p style='color: #A0A0A0; font-size: 0.8rem; margin: 0;'>Service</p>
                    <p style='color: white; font-size: 1.1rem; font-weight: 600; margin: 0.25rem 0 0 0;'>{service}</p>
                </div>
                <div>
                    <p style='color: #A0A0A0; font-size: 0.8rem; margin: 0;'>Current Status</p>
                    <p style='color: {status_color}; font-size: 1.1rem; font-weight: 600; margin: 0.25rem 0 0 0;'>{status}</p>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)


def create_performance_summary():
    """Create performance summary metrics"""
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric(
            label="🎯 Arrival Accuracy",
            value="94.2%",
            delta="+2.8%",
            help="Percentage of arrivals within 4-hour window"
        )
    
    with col2:
        st.metric(
            label="⏱️ Avg Wait Time",
            value="1.8 hrs",
            delta="-0.6 hrs",
            delta_color="inverse",
            help="Average waiting time before berthing"
        )
    
    with col3:
        st.metric(
            label="⚓ Berth Efficiency",
            value="23.4 hrs",
            delta="-2.1 hrs",
            delta_color="inverse",
            help="Average time at berth"
        )
    
    with col4:
        st.metric(
            label="🌱 Carbon Saved",
            value="45.2 tonnes",
            delta="+12.4 tonnes",
            help="Carbon emissions saved through optimization"
        )
    
    with col5:
        st.metric(
            label="💰 Bunker Savings",
            value="$18.5K",
            delta="+$4.2K",
            help="Cost savings from reduced fuel consumption"
        )


def create_arrival_accuracy_trend():
    """Create arrival accuracy trend chart"""
    
    # ✅ Use demo dataset
    demo = get_demo_dataset()
    df = demo.performance.tail(60)
    
    fig = go.Figure()
    
    # Actual accuracy
    fig.add_trace(go.Scatter(
        x=df['date'],
        y=df['avg_arrival_accuracy'],
        name='Actual Accuracy',
        line=dict(color=colors.PRIMARY, width=3),
        fill='tonexty',
        fillcolor='rgba(0, 102, 204, 0.1)',
        mode='lines+markers',
        marker=dict(size=6)
    ))
    
    # Target line
    fig.add_trace(go.Scatter(
        x=df['date'],
        y=[90] * len(df),
        name='Target (90%)',
        line=dict(color=colors.WARNING, width=2, dash='dash'),
        mode='lines'
    ))
    
    fig.update_layout(
        **charts.LAYOUT_CONFIG,
        height=400,
        title={
            'text': '📈 Arrival Accuracy Trend (Last 60 Days)',
            'font': {'size': 20, 'color': 'white'},
            'x': 0.5,
            'xanchor': 'center'
        },
        xaxis_title='Date',
        yaxis_title='Accuracy (%)',
        yaxis=dict(range=[75, 105]),
        legend=dict(
            orientation='h',
            yanchor='bottom',
            y=1.02,
            xanchor='right',
            x=1
        )
    )
    
    return fig


def create_wait_time_breakdown():
    """Create wait time breakdown chart"""
    
    # Sample data for wait time causes
    categories = ['Port Congestion', 'Weather Delays', 'Berth Unavailable', 
                  'Documentation', 'Pilot Delays', 'Other']
    values = [35, 20, 25, 10, 8, 2]
    
    fig = go.Figure(data=[go.Bar(
        x=categories,
        y=values,
        marker=dict(
            color=values,
            colorscale=[colors.SUCCESS, colors.WARNING, colors.DANGER],
            showscale=True,
            colorbar=dict(title='Hours')
        ),
        text=[f'{v}%' for v in values],
        textposition='outside',
        hovertemplate='<b>%{x}</b><br>%{y}% of total wait time<extra></extra>'
    )])
    
    fig.update_layout(
        **charts.LAYOUT_CONFIG,
        height=400,
        title={
            'text': '⏱️ Wait Time Breakdown by Cause',
            'font': {'size': 20, 'color': 'white'},
            'x': 0.5,
            'xanchor': 'center'
        },
        xaxis_title='Delay Cause',
        yaxis_title='Percentage (%)',
        showlegend=False
    )
    
    return fig


def create_movement_history_table(imo: str):
    """Create recent movement history table"""
    
    # ✅ Use demo dataset
    demo = get_demo_dataset()
    
    # Get movements for this vessel
    vessel_movements = demo.movements[demo.movements['imo_number'] == imo].tail(10)
    
    if not vessel_movements.empty:
        movements = pd.DataFrame({
            'Date': vessel_movements['date'].dt.strftime('%Y-%m-%d'),
            'From': vessel_movements['from_port'],
            'To': vessel_movements['to_port'],
            'Berth': vessel_movements['berth'],
            'Wait (hrs)': vessel_movements['wait_time_atb_btr'].round(1),
            'Accuracy (%)': vessel_movements['arrival_accuracy_final_btr'].round(1),
            'Carbon (t)': vessel_movements['carbon_abatement_tonnes'].round(1),
            'Status': '✅ Complete'
        })
        
        # Mark the most recent as current
        if len(movements) > 0:
            movements.loc[movements.index[-1], 'Status'] = '⏸️ Current'
    else:
        # Fallback if no data
        movements = pd.DataFrame({
            'Date': [(datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d') for i in range(10, 0, -1)],
            'From': ['Singapore', 'Rotterdam'] * 5,
            'To': ['Rotterdam', 'Singapore'] * 5,
            'Berth': [f'B{i:02d}' for i in range(1, 11)],
            'Wait (hrs)': np.random.uniform(1, 3, 10).round(1),
            'Accuracy (%)': np.random.uniform(88, 98, 10).round(1),
            'Carbon (t)': np.random.uniform(10, 15, 10).round(1),
            'Status': ['✅ Complete'] * 9 + ['⏸️ Current']
        })
    
    # Style the dataframe
    def highlight_current(row):
        if row['Status'] == '⏸️ Current':
            return ['background-color: rgba(0, 180, 216, 0.2)'] * len(row)
        return [''] * len(row)
    
    styled_df = movements.style.apply(highlight_current, axis=1)
    
    return styled_df


def render():
    """Render the Vessel Performance page"""

    # ✅ Permission check
    from config.permissions import Permission, require_permission
    require_permission(Permission.VIEW_VESSELS)
    
    # Vessel selector
    selected_vessel, imo = create_vessel_selector()
    vessel_name = selected_vessel.split(" (")[0]
    
    st.divider()
    
    # Vessel info card
    create_vessel_info_card(vessel_name, imo)
    
    # Performance summary metrics
    st.subheader("📊 Performance Summary")
    create_performance_summary()
    
    st.divider()
    
    # Performance charts
    st.subheader("📈 Performance Analysis")
    
    chart_col1, chart_col2 = st.columns(2)
    
    with chart_col1:
        st.plotly_chart(create_arrival_accuracy_trend(), use_container_width=True)
    
    with chart_col2:
        st.plotly_chart(create_wait_time_breakdown(), use_container_width=True)
    
    st.divider()
    
    # Movement history
    st.subheader("📋 Recent Movement History")
    st.dataframe(
        create_movement_history_table(imo),
        use_container_width=True,
        height=400
    )
    
    st.divider()
    
    # AI Insights
    st.subheader("🤖 AI-Generated Insights")
    
    insight_col1, insight_col2 = st.columns(2)
    
    with insight_col1:
        st.success("""
        **🎯 Strong Performance**
        
        This vessel consistently outperforms fleet average by 7.2%.
        
        **Key Strengths:**
        - Excellent arrival accuracy (94.2%)
        - Low wait times compared to similar routes
        - Strong carbon performance
        
        **Recommendation:** Use as benchmark for route optimization.
        """)
    
    with insight_col2:
        st.info("""
        **💡 Optimization Opportunity**
        
        Detected pattern: Higher wait times on Los Angeles route (avg 2.8 hrs vs 1.6 hrs other routes).
        
        **Root Cause:** Port congestion (35% of delays)
        
        **Action:** Adjust arrival schedule by -3 hours to avoid peak congestion.
        
        **Est. Impact:** Reduce wait time by 45%, save $2,100/trip.
        """)