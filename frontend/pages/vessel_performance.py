"""
Vessel Performance Page
Individual vessel analytics and performance tracking
Frontend Engineer: UI/UX Specialist
"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from frontend.config import colors, charts


def create_vessel_selector():
    """Create vessel search and selection interface"""
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        # Sample vessel list
        vessels = [
            "MSC Diana (IMO: 9876543)",
            "Ever Given (IMO: 9811000)",
            "CMA CGM Antoine (IMO: 9454436)",
            "Maersk Essex (IMO: 9632101)",
            "COSCO Shipping (IMO: 9793241)",
            "Hapag-Lloyd Berlin (IMO: 9234567)",
            "ONE Innovation (IMO: 9345678)",
            "Yang Ming Excellence (IMO: 9456789)"
        ]
        
        selected_vessel = st.selectbox(
            "🚢 Select Vessel",
            vessels,
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
                    <p style='color: white; font-size: 1.1rem; font-weight: 600; margin: 0.25rem 0 0 0;'>MSC</p>
                </div>
                <div>
                    <p style='color: #A0A0A0; font-size: 0.8rem; margin: 0;'>Service</p>
                    <p style='color: white; font-size: 1.1rem; font-weight: 600; margin: 0.25rem 0 0 0;'>Asia-Europe</p>
                </div>
                <div>
                    <p style='color: #A0A0A0; font-size: 0.8rem; margin: 0;'>Current Status</p>
                    <p style='color: #06D6A0; font-size: 1.1rem; font-weight: 600; margin: 0.25rem 0 0 0;'>At Berth</p>
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
    
    # Generate sample data
    dates = pd.date_range(end=datetime.now(), periods=60, freq='D')
    df = pd.DataFrame({
        'Date': dates,
        'Accuracy': np.random.normal(92, 3, 60).clip(80, 100),
        'Target': [90] * 60
    })
    
    fig = go.Figure()
    
    # Actual accuracy
    fig.add_trace(go.Scatter(
        x=df['Date'],
        y=df['Accuracy'],
        name='Actual Accuracy',
        line=dict(color=colors.PRIMARY, width=3),
        fill='tonexty',
        fillcolor='rgba(0, 102, 204, 0.1)',
        mode='lines+markers',
        marker=dict(size=6)
    ))
    
    # Target line
    fig.add_trace(go.Scatter(
        x=df['Date'],
        y=df['Target'],
        name='Target (90%)',
        line=dict(color=colors.WARNING, width=2, dash='dash'),
        mode='lines'
    ))
    
    # Add trend line
    z = np.polyfit(range(len(df)), df['Accuracy'], 1)
    p = np.poly1d(z)
    fig.add_trace(go.Scatter(
        x=df['Date'],
        y=p(range(len(df))),
        name='Trend',
        line=dict(color=colors.SUCCESS, width=2, dash='dot'),
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
    
    # Sample data
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


def create_route_efficiency_map():
    """Create route efficiency visualization"""
    
    # Sample route data
    routes = pd.DataFrame({
        'From': ['Singapore', 'Shanghai', 'Rotterdam', 'Los Angeles'],
        'To': ['Rotterdam', 'Los Angeles', 'Singapore', 'Shanghai'],
        'from_lat': [1.3521, 31.2304, 51.9225, 33.7701],
        'from_lon': [103.8198, 121.4737, 4.47917, -118.1937],
        'to_lat': [51.9225, 33.7701, 1.3521, 31.2304],
        'to_lon': [4.47917, -118.1937, 103.8198, 121.4737],
        'efficiency': [95, 88, 92, 85],
        'trips': [12, 8, 10, 6]
    })
    
    fig = go.Figure()
    
    # Add routes
    for _, route in routes.iterrows():
        # Determine color based on efficiency
        if route['efficiency'] >= 90:
            color = colors.SUCCESS
        elif route['efficiency'] >= 85:
            color = colors.WARNING
        else:
            color = colors.DANGER
        
        fig.add_trace(go.Scattergeo(
            lon=[route['from_lon'], route['to_lon']],
            lat=[route['from_lat'], route['to_lat']],
            mode='lines+markers',
            line=dict(width=3, color=color),
            marker=dict(size=10, color=color),
            name=f"{route['From']} → {route['To']}",
            text=f"Efficiency: {route['efficiency']}%<br>Trips: {route['trips']}",
            hoverinfo='text'
        ))
    
    fig.update_layout(
        **charts.LAYOUT_CONFIG,
        height=500,
        geo=dict(
            projection_type='natural earth',
            showland=True,
            landcolor='rgb(20, 20, 30)',
            coastlinecolor='rgb(100, 100, 120)',
            showlakes=True,
            lakecolor='rgb(10, 10, 20)',
            showcountries=True,
            countrycolor='rgb(80, 80, 100)',
            bgcolor='rgba(0,0,0,0)'
        ),
        title={
            'text': '🗺️ Route Efficiency Analysis',
            'font': {'size': 20, 'color': 'white'},
            'x': 0.5,
            'xanchor': 'center'
        },
        showlegend=True,
        legend=dict(
            yanchor='top',
            y=0.99,
            xanchor='left',
            x=0.01,
            bgcolor='rgba(0,0,0,0.5)'
        )
    )
    
    return fig


def create_comparison_radar():
    """Create performance comparison radar chart"""
    
    categories = ['Arrival Accuracy', 'Berth Efficiency', 'Carbon Performance', 
                  'Cost Efficiency', 'Schedule Reliability']
    
    fig = go.Figure()
    
    # This vessel
    fig.add_trace(go.Scatterpolar(
        r=[94, 88, 92, 85, 90],
        theta=categories,
        fill='toself',
        name='This Vessel',
        line=dict(color=colors.PRIMARY, width=2),
        fillcolor='rgba(0, 102, 204, 0.2)'
    ))
    
    # Fleet average
    fig.add_trace(go.Scatterpolar(
        r=[87, 82, 85, 80, 83],
        theta=categories,
        fill='toself',
        name='Fleet Average',
        line=dict(color=colors.WARNING, width=2, dash='dash'),
        fillcolor='rgba(255, 214, 10, 0.1)'
    ))
    
    # Top performer
    fig.add_trace(go.Scatterpolar(
        r=[98, 95, 96, 92, 94],
        theta=categories,
        fill='toself',
        name='Top Performer',
        line=dict(color=colors.SUCCESS, width=2, dash='dot'),
        fillcolor='rgba(6, 214, 160, 0.1)'
    ))
    
    fig.update_layout(
        **charts.LAYOUT_CONFIG,
        height=450,
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 100],
                showline=False,
                gridcolor='rgba(255, 255, 255, 0.2)'
            ),
            angularaxis=dict(
                gridcolor='rgba(255, 255, 255, 0.2)'
            ),
            bgcolor='rgba(0,0,0,0)'
        ),
        title={
            'text': '📊 Performance Comparison',
            'font': {'size': 20, 'color': 'white'},
            'x': 0.5,
            'xanchor': 'center'
        },
        showlegend=True,
        legend=dict(
            orientation='h',
            yanchor='bottom',
            y=-0.2,
            xanchor='center',
            x=0.5
        )
    )
    
    return fig


def create_movement_history_table():
    """Create recent movement history table"""
    
    # Sample data
    movements = pd.DataFrame({
        'Date': pd.date_range(end=datetime.now(), periods=10, freq='7D')[::-1],
        'From': ['Singapore', 'Rotterdam', 'Shanghai', 'Singapore', 'Los Angeles',
                 'Singapore', 'Rotterdam', 'Shanghai', 'Singapore', 'Los Angeles'],
        'To': ['Rotterdam', 'Singapore', 'Los Angeles', 'Shanghai', 'Singapore',
               'Rotterdam', 'Shanghai', 'Singapore', 'Rotterdam', 'Shanghai'],
        'Berth': ['B02', 'B05', 'B03', 'B07', 'B04', 'B02', 'B08', 'B05', 'B02', 'B06'],
        'Wait (hrs)': [1.2, 2.1, 0.8, 1.5, 3.2, 1.8, 1.0, 2.5, 1.4, 2.0],
        'Accuracy (%)': [95.5, 92.3, 98.2, 91.0, 88.5, 94.2, 96.8, 89.5, 95.0, 93.2],
        'Carbon (t)': [12.4, 15.2, 10.8, 13.5, 18.2, 12.1, 11.5, 14.8, 12.7, 13.9],
        'Status': ['✅ Complete', '✅ Complete', '✅ Complete', '✅ Complete', '✅ Complete',
                   '✅ Complete', '✅ Complete', '✅ Complete', '✅ Complete', '⏸️ Current']
    })
    
    movements['Date'] = movements['Date'].dt.strftime('%Y-%m-%d')
    
    # Style the dataframe
    def highlight_current(row):
        if row['Status'] == '⏸️ Current':
            return ['background-color: rgba(0, 180, 216, 0.2)'] * len(row)
        return [''] * len(row)
    
    styled_df = movements.style.apply(highlight_current, axis=1)
    
    return styled_df


def render():
    """Render the Vessel Performance page"""

    # ✅ ADD: Permission check
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
    
    # Route efficiency
    st.subheader("🗺️ Route Performance")
    st.plotly_chart(create_route_efficiency_map(), use_container_width=True)
    
    st.divider()
    
    # Comparison and history
    comp_col1, comp_col2 = st.columns([1, 1])
    
    with comp_col1:
        st.plotly_chart(create_comparison_radar(), use_container_width=True)
    
    with comp_col2:
        st.subheader("📋 Recent Movement History")
        st.dataframe(
            create_movement_history_table(),
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
