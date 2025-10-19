"""
Global Insights Page
Overview dashboard with key metrics and visualizations
"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from frontend.config import colors, charts

def create_kpi_card(label: str, value: str, delta: str = None, icon: str = "📊"):
    """Create a KPI metric card"""
    delta_color = "normal"
    if delta:
        if delta.startswith('+'):
            delta_color = "normal"
        elif delta.startswith('-'):
            delta_color = "inverse"
    
    st.metric(
        label=f"{icon} {label}",
        value=value,
        delta=delta,
        delta_color=delta_color
    )

def create_port_map():
    """Create interactive port and vessel route map"""
    # Sample port data
    ports = pd.DataFrame({
        'port': ['Singapore', 'Rotterdam', 'Shanghai', 'Los Angeles', 'Antwerp'],
        'lat': [1.3521, 51.9225, 31.2304, 33.7701, 51.2194],
        'lon': [103.8198, 4.47917, 121.4737, -118.1937, 4.4025],
        'vessels': [45, 32, 38, 28, 25],
        'country': ['Singapore', 'Netherlands', 'China', 'USA', 'Belgium']
    })
    
    # Create figure
    fig = go.Figure()
    
    # Add port markers
    fig.add_trace(go.Scattergeo(
        lon=ports['lon'],
        lat=ports['lat'],
        text=ports['port'] + '<br>Vessels: ' + ports['vessels'].astype(str),
        mode='markers+text',
        marker=dict(
            size=ports['vessels'] / 2,
            color=colors.SECONDARY,
            line=dict(width=2, color='white'),
            sizemode='diameter'
        ),
        textposition='top center',
        textfont=dict(size=10, color='white'),
        name='Ports',
        hovertemplate='<b>%{text}</b><br>Lat: %{lat}<br>Lon: %{lon}<extra></extra>'
    ))
    
    # Add sample routes
    routes = [
        {'from': 0, 'to': 1, 'color': colors.PRIMARY},
        {'from': 0, 'to': 2, 'color': colors.SUCCESS},
        {'from': 1, 'to': 3, 'color': colors.WARNING},
        {'from': 2, 'to': 3, 'color': colors.DANGER}
    ]
    
    for route in routes:
        fig.add_trace(go.Scattergeo(
            lon=[ports.iloc[route['from']]['lon'], ports.iloc[route['to']]['lon']],
            lat=[ports.iloc[route['from']]['lat'], ports.iloc[route['to']]['lat']],
            mode='lines',
            line=dict(width=2, color=route['color']),
            opacity=0.6,
            showlegend=False,
            hoverinfo='skip'
        ))
    
    # Update layout
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
            'text': '🌍 Global Port Network & Active Routes',
            'font': {'size': 20, 'color': 'white'},
            'x': 0.5,
            'xanchor': 'center'
        }
    )
    
    return fig

def create_performance_chart():
    """Create performance trend chart"""
    # Generate sample data
    dates = pd.date_range(end=datetime.now(), periods=30, freq='D')
    df = pd.DataFrame({
        'Date': dates,
        'Arrival Accuracy': np.random.normal(85, 5, 30).clip(70, 100),
        'Berth Utilization': np.random.normal(78, 4, 30).clip(60, 95),
        'On-Time Performance': np.random.normal(82, 6, 30).clip(65, 98)
    })
    
    fig = go.Figure()
    
    metrics = ['Arrival Accuracy', 'Berth Utilization', 'On-Time Performance']
    metric_colors = [colors.PRIMARY, colors.SUCCESS, colors.SECONDARY]
    
    for metric, color in zip(metrics, metric_colors):
        fig.add_trace(go.Scatter(
            x=df['Date'],
            y=df[metric],
            name=metric,
            line=dict(color=color, width=3),
            mode='lines+markers',
            marker=dict(size=6),
            hovertemplate='<b>%{fullData.name}</b><br>%{x|%b %d}<br>%{y:.1f}%<extra></extra>'
        ))
    
    fig.update_layout(
        **charts.LAYOUT_CONFIG,
        height=400,
        title={
            'text': '📈 Performance Trends (Last 30 Days)',
            'font': {'size': 20, 'color': 'white'},
            'x': 0.5,
            'xanchor': 'center'
        },
        xaxis_title='Date',
        yaxis_title='Percentage (%)',
        yaxis=dict(range=[0, 100]),
        legend=dict(
            orientation='h',
            yanchor='bottom',
            y=1.02,
            xanchor='right',
            x=1
        ),
    )
    
    return fig

def create_carbon_chart():
    """Create carbon savings chart"""
    categories = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun']
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=categories,
        y=[234, 289, 312, 298, 356, 401],
        name='Carbon Saved',
        marker_color=colors.SUCCESS,
        hovertemplate='<b>%{x}</b><br>%{y} tonnes<extra></extra>'
    ))
    
    fig.add_trace(go.Scatter(
        x=categories,
        y=[234, 289, 312, 298, 356, 401],
        name='Trend',
        mode='lines',
        line=dict(color=colors.WARNING, width=3, dash='dash'),
        yaxis='y2',
        showlegend=False
    ))
    
    fig.update_layout(
        **charts.LAYOUT_CONFIG,
        height=400,
        title={
            'text': '🌱 Carbon Abatement Trend',
            'font': {'size': 20, 'color': 'white'},
            'x': 0.5,
            'xanchor': 'center'
        },
        xaxis_title='Month',
        yaxis_title='Tonnes CO₂',
        yaxis2=dict(
            overlaying='y',
            side='right',
            showgrid=False
        ),
        barmode='group'
    )
    
    return fig

def create_vessel_status_chart():
    """Create vessel status distribution"""
    statuses = ['At Berth', 'Waiting', 'In Transit', 'Departed']
    values = [28, 12, 45, 83]
    status_colors = [colors.SUCCESS, colors.WARNING, colors.SECONDARY, colors.PRIMARY]
    
    fig = go.Figure(data=[go.Pie(
        labels=statuses,
        values=values,
        marker=dict(colors=status_colors),
        hole=0.4,
        textposition='outside',
        textinfo='label+percent',
        hovertemplate='<b>%{label}</b><br>%{value} vessels<br>%{percent}<extra></extra>'
    )])
    
    fig.update_layout(
        **charts.LAYOUT_CONFIG,
        height=400,
        title={
            'text': '🚢 Vessel Status Distribution',
            'font': {'size': 20, 'color': 'white'},
            'x': 0.5,
            'xanchor': 'center'
        },
        showlegend=True,
        legend=dict(
            orientation='v',
            yanchor='middle',
            y=0.5,
            xanchor='left',
            x=1.1
        )
    )
    
    return fig

def render():
    """Render the Global Insights page"""
    
    # KPI Metrics Row
    st.subheader("📊 Key Performance Indicators")
    
    kpi_col1, kpi_col2, kpi_col3, kpi_col4, kpi_col5 = st.columns(5)
    
    with kpi_col1:
        create_kpi_card("Arrival Accuracy", "87.3%", "+3.2%", "🎯")
    
    with kpi_col2:
        create_kpi_card("Avg Wait Time", "2.4 hrs", "-0.8 hrs", "⏱️")
    
    with kpi_col3:
        create_kpi_card("Berth Utilization", "82.1%", "+5.4%", "⚓")
    
    with kpi_col4:
        create_kpi_card("Carbon Saved", "401 tonnes", "+45 tonnes", "🌱")
    
    with kpi_col5:
        create_kpi_card("Bunker Savings", "$87.2K", "+$12.1K", "💰")
    
    st.divider()
    
    # Main visualizations
    st.subheader("🌍 Global Network Overview")
    
    # Port map (full width)
    st.plotly_chart(create_port_map(), use_container_width=True)
    
    st.divider()
    
    # Charts row
    chart_col1, chart_col2 = st.columns(2)
    
    with chart_col1:
        st.plotly_chart(create_performance_chart(), use_container_width=True)
    
    with chart_col2:
        st.plotly_chart(create_carbon_chart(), use_container_width=True)
    
    st.divider()
    
    # Additional insights row
    insight_col1, insight_col2 = st.columns([2, 1])
    
    with insight_col1:
        # Recent activity table
        st.subheader("📋 Recent Vessel Movements")
        
        recent_data = pd.DataFrame({
            'Vessel': ['MSC Diana', 'Ever Given', 'CMA CGM Antoine', 'Maersk Essex', 'COSCO Shipping'],
            'From': ['Singapore', 'Shanghai', 'Rotterdam', 'Los Angeles', 'Antwerp'],
            'To': ['Rotterdam', 'Los Angeles', 'Singapore', 'Shanghai', 'Singapore'],
            'Status': ['At Berth', 'In Transit', 'Waiting', 'Departed', 'In Transit'],
            'ETA': ['2h ago', '12h', '4h', 'Completed', '18h'],
            'Carbon (t)': [12.4, 45.2, 8.7, 32.1, 23.8]
        })
        
        # Color-code status
        def color_status(val):
            colors_map = {
                'At Berth': 'background-color: rgba(6, 214, 160, 0.2)',
                'In Transit': 'background-color: rgba(0, 180, 216, 0.2)',
                'Waiting': 'background-color: rgba(255, 214, 10, 0.2)',
                'Departed': 'background-color: rgba(160, 160, 160, 0.2)'
            }
            return colors_map.get(val, '')
        
        st.dataframe(
            recent_data.style.applymap(color_status, subset=['Status']),
            use_container_width=True,
            height=250
        )
    
    with insight_col2:
        st.plotly_chart(create_vessel_status_chart(), use_container_width=True)
    
    st.divider()
    
    # AI Insights Section
    st.subheader("🤖 AI-Generated Insights")
    
    insights_col1, insights_col2 = st.columns(2)
    
    with insights_col1:
        st.info("""
        **📊 Bunching Alert**
        
        3 vessels scheduled to arrive at Singapore Terminal 4 between 14:00-16:00 today.
        
        **Recommendation:** Stagger arrivals by 45 minutes to optimize berth utilization.
        
        **Impact:** Reduce wait time by ~2.1 hours, save $4,200 in bunker costs.
        """)
    
    with insights_col2:
        st.success("""
        **🌱 Sustainability Win**
        
        Your optimizations this week saved 45 tonnes of CO₂ emissions - equivalent to:
        - 🚗 Taking 9 cars off the road for a year
        - 🌳 Planting 2,100 trees
        
        **Target Progress:** 89% of monthly goal
        """)
    
    # Alerts row
    st.divider()
    st.subheader("⚠️ Active Alerts")
    
    alert_col1, alert_col2, alert_col3 = st.columns(3)
    
    with alert_col1:
        st.warning("""
        **Weather Advisory**
        
        Strong winds (35 knots) expected at Rotterdam port tomorrow 08:00-14:00.
        
        3 affected vessels - consider schedule adjustment.
        """)
    
    with alert_col2:
        st.error("""
        **Delayed Arrival**
        
        MSC Mediterranean (IMO: 9876543) delayed by 6.2 hours due to port congestion.
        
        Berth #7 now available ahead of schedule.
        """)
    
    with alert_col3:
        st.info("""
        **Optimization Opportunity**
        
        Berth #12 utilization at 45% this week.
        
        Potential to reassign 2 vessels for better efficiency.
        """)
