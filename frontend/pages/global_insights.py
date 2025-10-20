"""
Global Insights Page - COMPLETE REAL DATA VERSION
Overview dashboard with key metrics and visualizations
All data comes from UnifiedDataService
"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from frontend.config import colors, charts
from data.unified_data_service import get_data_service

# Initialize data service
data_service = get_data_service()

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

def create_port_map(port_data: pd.DataFrame):
    """Create interactive port map with REAL DATA"""
    
    if port_data.empty:
        return None
    
    fig = go.Figure()
    
    # Add port markers with REAL data
    fig.add_trace(go.Scattergeo(
        lon=port_data['lon'],
        lat=port_data['lat'],
        text=port_data['port'] + '<br>Vessels: ' + port_data['vessel_count'].astype(str),
        mode='markers+text',
        marker=dict(
            size=port_data['vessel_count'] / 2,
            color=colors.SECONDARY,
            line=dict(width=2, color='white'),
            sizemode='diameter'
        ),
        textposition='top center',
        textfont=dict(size=10, color='white'),
        name='Ports',
        hovertemplate='<b>%{text}</b><br>Lat: %{lat}<br>Lon: %{lon}<extra></extra>'
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

def create_performance_chart(perf_data: pd.DataFrame):
    """Create performance trend chart with REAL DATA"""
    
    if perf_data.empty:
        return None
    
    fig = go.Figure()
    
    # Find available metric columns
    metric_columns = []
    
    # Check for accuracy columns
    for col in ['avg_accuracy', 'avg_arrival_accuracy', 'arrival_accuracy_final_btr']:
        if col in perf_data.columns:
            metric_columns.append((col, 'Arrival Accuracy', colors.PRIMARY))
            break
    
    # Check for wait time
    for col in ['avg_wait_time', 'wait_time_atb_btr']:
        if col in perf_data.columns:
            # Convert to percentage scale (inverse: lower is better)
            metric_columns.append((col, 'Wait Time Efficiency', colors.SUCCESS))
            break
    
    # Check for berth time
    for col in ['avg_berth_time', 'berth_time_hours']:
        if col in perf_data.columns:
            metric_columns.append((col, 'Berth Efficiency', colors.SECONDARY))
            break
    
    # Plot available metrics
    for col, name, color in metric_columns[:3]:  # Max 3 metrics
        if col in perf_data.columns:
            values = perf_data[col]
            
            # For wait time, convert to efficiency score
            if 'wait' in col.lower():
                # Inverse scale: 0 hours = 100%, 10 hours = 0%
                values = 100 - (values * 10).clip(0, 100)
            
            fig.add_trace(go.Scatter(
                x=perf_data['date'],
                y=values,
                name=name,
                line=dict(color=color, width=3),
                mode='lines+markers',
                marker=dict(size=6),
                hovertemplate=f'<b>{name}</b><br>%{{x}}<br>%{{y:.1f}}<extra></extra>'
            ))
    
    # Add target line if we have accuracy
    if metric_columns:
        fig.add_hline(
            y=90,
            line_dash='dash',
            line_color=colors.WARNING,
            annotation_text='Target: 90%',
            annotation_position='right'
        )
    
    fig.update_layout(
        **charts.LAYOUT_CONFIG,
        height=400,
        title={
            'text': f'📈 Performance Trends (Last {len(perf_data)} Days)',
            'font': {'size': 20, 'color': 'white'},
            'x': 0.5,
            'xanchor': 'center'
        },
        xaxis_title='Date',
        yaxis_title='Performance Score',
        yaxis=dict(range=[0, 100]),
        legend=dict(
            orientation='h',
            yanchor='bottom',
            y=1.02,
            xanchor='right',
            x=1
        )
    )
    
    return fig

def create_carbon_chart(carbon_data: pd.DataFrame):
    """Create carbon savings chart with REAL DATA"""
    
    if carbon_data.empty:
        return None
    
    # Prepare data - group by month
    carbon_data = carbon_data.copy()
    carbon_data['date'] = pd.to_datetime(carbon_data['date'])
    carbon_data['month'] = carbon_data['date'].dt.to_period('M').astype(str)
    
    monthly = carbon_data.groupby('month')['savings'].sum().reset_index()
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=monthly['month'],
        y=monthly['savings'],
        name='Carbon Saved',
        marker_color=colors.SUCCESS,
        hovertemplate='<b>%{x}</b><br>%{y:.1f} tonnes<extra></extra>'
    ))
    
    # Add trend line if we have enough data
    if len(monthly) > 2:
        fig.add_trace(go.Scatter(
            x=monthly['month'],
            y=monthly['savings'],
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

def create_vessel_status_chart(status_dist: dict):
    """Create vessel status distribution with REAL DATA"""
    
    if not status_dist:
        return None
    
    statuses = list(status_dist.keys())
    values = list(status_dist.values())
    
    # Assign colors
    status_colors_map = {
        'At Berth': colors.SUCCESS,
        'Waiting': colors.WARNING,
        'In Transit': colors.SECONDARY,
        'Departed': colors.PRIMARY,
        'DEPARTED': colors.PRIMARY,
        'Delayed': colors.DANGER
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
    """Render the Global Insights page with REAL DATA"""

    # Permission check
    from config.permissions import Permission, require_permission
    require_permission(Permission.VIEW_DASHBOARD)
    
    # GET REAL DATA
    with st.spinner("Loading dashboard data..."):
        kpis = data_service.get_global_kpis()
        deltas = data_service.get_kpi_deltas()
    
    # KPI Metrics Row - REAL DATA
    st.subheader("📊 Key Performance Indicators")
    
    kpi_col1, kpi_col2, kpi_col3, kpi_col4, kpi_col5 = st.columns(5)
    
    with kpi_col1:
        create_kpi_card(
            "Arrival Accuracy", 
            f"{kpis['arrival_accuracy']:.1f}%", 
            deltas['arrival_accuracy'], 
            "🎯"
        )
    
    with kpi_col2:
        create_kpi_card(
            "Avg Wait Time", 
            f"{kpis['avg_wait_time']:.1f} hrs", 
            deltas['avg_wait_time'], 
            "⏱️"
        )
    
    with kpi_col3:
        create_kpi_card(
            "Berth Utilization", 
            f"{kpis['berth_utilization']:.1f}%", 
            deltas['berth_utilization'], 
            "⚓"
        )
    
    with kpi_col4:
        create_kpi_card(
            "Carbon Saved", 
            f"{kpis['carbon_saved']:.0f} tonnes", 
            deltas['carbon_saved'], 
            "🌱"
        )
    
    with kpi_col5:
        create_kpi_card(
            "Bunker Savings", 
            f"${kpis['bunker_savings']/1000:.1f}K", 
            deltas['bunker_savings'], 
            "💰"
        )
    
    st.divider()
    
    # Main visualizations - REAL DATA
    st.subheader("🌍 Global Network Overview")
    
    # Port map with REAL data
    port_data = data_service.get_port_data()
    if not port_data.empty:
        port_map = create_port_map(port_data)
        if port_map:
            st.plotly_chart(port_map, use_container_width=True)
        else:
            st.info("📍 Port map unavailable - no location data")
    else:
        st.info("📍 No port data available in current dataset")
    
    st.divider()
    
    # Charts row - REAL DATA
    chart_col1, chart_col2 = st.columns(2)
    
    with chart_col1:
        perf_data = data_service.get_performance_trends(days=30)
        if not perf_data.empty:
            perf_chart = create_performance_chart(perf_data)
            if perf_chart:
                st.plotly_chart(perf_chart, use_container_width=True)
            else:
                st.info("📊 Performance chart unavailable")
        else:
            st.info("📊 No performance trend data available")
    
    with chart_col2:
        carbon_data = data_service.get_carbon_trends(days=180)
        if not carbon_data.empty:
            carbon_chart = create_carbon_chart(carbon_data)
            if carbon_chart:
                st.plotly_chart(carbon_chart, use_container_width=True)
            else:
                st.info("🌱 Carbon chart unavailable")
        else:
            st.info("🌱 No carbon trend data available")
    
    st.divider()
    
    # Additional insights row - REAL DATA
    insight_col1, insight_col2 = st.columns([2, 1])
    
    with insight_col1:
        st.subheader("📋 Recent Vessel Movements")
        recent = data_service.get_recent_movements(limit=10)
        
        if not recent.empty:
            # Format for display
            display_cols = ['vessel_name', 'from_port', 'to_port', 'status', 'wait_time_atb_btr', 'carbon_abatement_tonnes']
            available_cols = [col for col in display_cols if col in recent.columns]
            
            if available_cols:
                display_df = recent[available_cols].copy()
                
                # Rename columns
                rename_map = {
                    'vessel_name': 'Vessel',
                    'from_port': 'From',
                    'to_port': 'To',
                    'status': 'Status',
                    'wait_time_atb_btr': 'Wait (hrs)',
                    'carbon_abatement_tonnes': 'Carbon (t)'
                }
                display_df = display_df.rename(columns={k: v for k, v in rename_map.items() if k in display_df.columns})
                
                # Color-code status
                def color_status(row):
                    if 'Status' not in row.index:
                        return [''] * len(row)
                    
                    status = row['Status']
                    colors_map = {
                        'At Berth': 'background-color: rgba(6, 214, 160, 0.2)',
                        'In Transit': 'background-color: rgba(0, 180, 216, 0.2)',
                        'Waiting': 'background-color: rgba(255, 214, 10, 0.2)',
                        'Departed': 'background-color: rgba(160, 160, 160, 0.2)',
                        'DEPARTED': 'background-color: rgba(160, 160, 160, 0.2)'
                    }
                    color = colors_map.get(status, '')
                    return [color] * len(row)
                
                styled_df = display_df.style.apply(color_status, axis=1)
                st.dataframe(styled_df, use_container_width=True, height=250)
            else:
                st.info("No displayable columns in recent movements")
        else:
            st.info("📋 No recent movements available")
    
    with insight_col2:
        status_dist = data_service.get_vessel_status_distribution()
        if status_dist:
            status_chart = create_vessel_status_chart(status_dist)
            if status_chart:
                st.plotly_chart(status_chart, use_container_width=True)
            else:
                st.info("🚢 Status chart unavailable")
        else:
            st.info("🚢 No status data available")
    
    st.divider()
    
    # AI Insights Section - DYNAMIC BASED ON REAL DATA
    st.subheader("🤖 AI-Generated Insights")
    
    insights_col1, insights_col2 = st.columns(2)
    
    with insights_col1:
        # Dynamic insight based on actual wait times
        if kpis['avg_wait_time'] > 3:
            st.warning(f"""
            **⚠️ Wait Time Alert**
            
            Current average wait time of {kpis['avg_wait_time']:.1f} hours exceeds the 2-hour target.
            
            **Impact:** Potential delays affecting {kpis['active_vessels']} active vessels.
            
            **Recommendation:** Review berth allocation and consider staggering arrivals.
            """)
        elif kpis['arrival_accuracy'] < 85:
            st.info(f"""
            **📊 Accuracy Alert**
            
            Arrival accuracy at {kpis['arrival_accuracy']:.1f}% is below target (90%).
            
            **Recommendation:** Review ETA prediction models and vessel communication protocols.
            """)
        else:
            st.success(f"""
            **✅ Strong Performance**
            
            Operations running smoothly with {kpis['arrival_accuracy']:.1f}% arrival accuracy.
            
            **Highlights:**
            - Wait time within target: {kpis['avg_wait_time']:.1f} hrs
            - Berth utilization optimal: {kpis['berth_utilization']:.1f}%
            - {kpis['total_vessels']} vessels processed
            """)
    
    with insights_col2:
        # Dynamic carbon insight
        carbon_metrics = data_service.get_carbon_metrics()
        st.success(f"""
        **🌱 Sustainability Win**
        
        Your optimizations have saved {carbon_metrics['total_saved']:.0f} tonnes of CO₂ emissions:
        
        - 🌳 Equivalent to planting {carbon_metrics['trees_equivalent']:,} trees
        - 🚗 {carbon_metrics['cars_equivalent']} cars off the road for a year
        
        **Impact:** ${kpis['bunker_savings']/1000:.1f}K in bunker cost savings
        """)
    
    # Alerts row - DYNAMIC
    st.divider()
    st.subheader("⚠️ Active Alerts")
    
    alert_col1, alert_col2, alert_col3 = st.columns(3)
    
    # Generate dynamic alerts based on real data
    alerts_shown = 0
    
    with alert_col1:
        if kpis['berth_utilization'] > 85:
            st.warning(f"""
            **High Utilization**
            
            Berth utilization at {kpis['berth_utilization']:.1f}% - approaching capacity limit.
            
            Consider optimizing schedule to prevent congestion.
            """)
            alerts_shown += 1
        elif alerts_shown == 0:
            st.info("""
            **System Status**
            
            All berth operations within normal parameters.
            """)
    
    with alert_col2:
        if kpis['avg_wait_time'] > 4:
            st.error(f"""
            **Critical Wait Times**
            
            Average wait time {kpis['avg_wait_time']:.1f} hours exceeds critical threshold.
            
            Immediate action recommended.
            """)
            alerts_shown += 1
        elif alerts_shown == 0:
            st.info("""
            **Queue Status**
            
            Vessel queue processing efficiently.
            """)
    
    with alert_col3:
        if kpis['arrival_accuracy'] < 80:
            st.error(f"""
            **Accuracy Issue**
            
            Arrival accuracy {kpis['arrival_accuracy']:.1f}% significantly below target.
            
            Review vessel tracking systems.
            """)
            alerts_shown += 1
        else:
            st.info("""
            **Performance**
            
            Arrival accuracy within acceptable range.
            """)
    
    # Footer stats
    st.divider()
    st.caption(f"📊 Dashboard showing data for {kpis['total_vessels']} total vessels | Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")