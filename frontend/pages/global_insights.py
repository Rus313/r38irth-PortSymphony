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
from data.demo_dataset import get_demo_dataset  # ✅ Import demo dataset

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
    # ✅ Use demo dataset
    demo = get_demo_dataset()
    ports = demo.ports
    
    # Create vessel routes from recent movements
    recent_moves = demo.movements.tail(4)
    
    fig = go.Figure()
    
    # Add port markers
    fig.add_trace(go.Scattergeo(
        lon=ports['longitude'],
        lat=ports['latitude'],
        text=ports['port_name'] + '<br>Vessels: ' + ports['vessel_count'].astype(str),
        mode='markers+text',
        marker=dict(
            size=ports['vessel_count'] / 2,
            color=colors.SECONDARY,
            line=dict(width=2, color='white'),
            sizemode='diameter'
        ),
        textposition='top center',
        textfont=dict(size=10, color='white'),
        name='Ports',
        hovertemplate='<b>%{text}</b><br>Lat: %{lat}<br>Lon: %{lon}<extra></extra>'
    ))
    
    # Add sample routes (simplified - just showing concept)
    route_colors = [colors.PRIMARY, colors.SUCCESS, colors.WARNING, colors.DANGER]
    
    for i in range(min(4, len(recent_moves))):
        move = recent_moves.iloc[i]
        from_port = ports[ports['port_name'] == move['from_port']]
        to_port = ports[ports['port_name'] == move['to_port']]
        
        if not from_port.empty and not to_port.empty:
            fig.add_trace(go.Scattergeo(
                lon=[from_port.iloc[0]['longitude'], to_port.iloc[0]['longitude']],
                lat=[from_port.iloc[0]['latitude'], to_port.iloc[0]['latitude']],
                mode='lines',
                line=dict(width=2, color=route_colors[i % 4]),
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
    # ✅ Use demo dataset
    demo = get_demo_dataset()
    df = demo.performance.tail(30)
    
    fig = go.Figure()
    
    metrics = [
        ('avg_arrival_accuracy', 'Arrival Accuracy', colors.PRIMARY),
        ('berth_utilization', 'Berth Utilization', colors.SUCCESS),
        ('on_time_performance', 'On-Time Performance', colors.SECONDARY)
    ]
    
    for col, name, color in metrics:
        if col in df.columns:
            fig.add_trace(go.Scatter(
                x=df['date'],
                y=df[col],
                name=name,
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
    # ✅ Use demo dataset
    demo = get_demo_dataset()
    carbon_df = demo.carbon.tail(6)
    
    # Group by month
    carbon_df['month'] = carbon_df['date'].dt.strftime('%b')
    monthly = carbon_df.groupby('month')['carbon_saved'].sum().reset_index()
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=monthly['month'],
        y=monthly['carbon_saved'],
        name='Carbon Saved',
        marker_color=colors.SUCCESS,
        hovertemplate='<b>%{x}</b><br>%{y:.0f} tonnes<extra></extra>'
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
        barmode='group'
    )
    
    return fig

def create_vessel_status_chart():
    """Create vessel status distribution"""
    # ✅ Use demo dataset
    demo = get_demo_dataset()
    
    # Count vessels by status
    status_counts = demo.vessels['status'].value_counts()
    
    statuses = status_counts.index.tolist()
    values = status_counts.values.tolist()
    
    status_colors_map = {
        'At Berth': colors.SUCCESS,
        'Waiting': colors.WARNING,
        'In Transit': colors.SECONDARY,
        'Departed': colors.PRIMARY
    }
    
    chart_colors = [status_colors_map.get(s, colors.PRIMARY) for s in statuses]
    
    fig = go.Figure(data=[go.Pie(
        labels=statuses,
        values=values,
        marker=dict(colors=chart_colors),
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

    # ✅ Permission check
    from config.permissions import Permission, require_permission
    require_permission(Permission.VIEW_DASHBOARD)
    
    # ✅ Load demo data
    demo = get_demo_dataset()
    metrics = demo.get_current_metrics()
    
    # KPI Metrics Row
    st.subheader("📊 Key Performance Indicators")
    
    kpi_col1, kpi_col2, kpi_col3, kpi_col4, kpi_col5 = st.columns(5)
    
    with kpi_col1:
        create_kpi_card(
            "Arrival Accuracy", 
            f"{metrics['avg_arrival_accuracy']:.1f}%", 
            "+3.2%", 
            "🎯"
        )
    
    with kpi_col2:
        create_kpi_card(
            "Avg Wait Time", 
            f"{metrics['avg_wait_time']:.1f} hrs", 
            "-0.8 hrs", 
            "⏱️"
        )
    
    with kpi_col3:
        create_kpi_card(
            "Berth Utilization", 
            f"{metrics['berth_utilization']:.1f}%", 
            "+5.4%", 
            "⚓"
        )
    
    with kpi_col4:
        create_kpi_card(
            "Carbon Saved", 
            f"{metrics['total_carbon_saved']:.0f} tonnes", 
            "+45 tonnes", 
            "🌱"
        )
    
    with kpi_col5:
        create_kpi_card(
            "Bunker Savings", 
            f"${metrics['total_bunker_saved']/1000:.1f}K", 
            "+$12.1K", 
            "💰"
        )
    
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
        # Recent activity table - ✅ Use demo data
        st.subheader("📋 Recent Vessel Movements")
        
        recent_data = pd.DataFrame(demo.get_recent_vessels(5))
        
        if not recent_data.empty:
            # Select and rename columns for display
            display_cols = {
                'vessel_name': 'Vessel',
                'from_port': 'From',
                'to_port': 'To',
                'status': 'Status',
                'wait_time_atb_btr': 'Wait (hrs)',
                'carbon_abatement_tonnes': 'Carbon (t)'
            }
            
            display_data = recent_data[list(display_cols.keys())].rename(columns=display_cols)
            display_data['Wait (hrs)'] = display_data['Wait (hrs)'].round(1)
            display_data['Carbon (t)'] = display_data['Carbon (t)'].round(1)
            
            # Color-code status
            def color_status(val):
                colors_map = {
                    'At Berth': 'background-color: rgba(6, 214, 160, 0.2)',
                    'In Transit': 'background-color: rgba(0, 180, 216, 0.2)',
                    'Waiting': 'background-color: rgba(255, 214, 10, 0.2)',
                    'DEPARTED': 'background-color: rgba(160, 160, 160, 0.2)'
                }
                return colors_map.get(val, '')
            
            st.dataframe(
                display_data.style.applymap(color_status, subset=['Status']),
                use_container_width=True,
                height=250
            )
        else:
            st.info("No recent vessel movements")
    
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
        
        MSC Mediterranean (IMO: 9567890) delayed by 6.2 hours due to port congestion.
        
        Berth #7 now available ahead of schedule.
        """)
    
    with alert_col3:
        st.info("""
        **Optimization Opportunity**
        
        Berth #12 utilization at 45% this week.
        
        Potential to reassign 2 vessels for better efficiency.
        """)