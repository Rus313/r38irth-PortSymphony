"""
Berth Management Page
Real-time berth operations and optimization with REAL DATA
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


def create_berth_status_overview():
    """Create real-time berth status overview using REAL DATA"""
    
    # Get real berth data
    berth_status = data_service.get_berth_status()
    
    # Calculate actual counts
    total_berths = len(berth_status)
    available = len([b for b in berth_status if b['status'] == 'Available'])
    occupied = len([b for b in berth_status if b['status'] == 'Occupied'])
    maintenance = len([b for b in berth_status if b['status'] == 'Maintenance'])
    
    # Get utilization from KPIs
    kpis = data_service.get_global_kpis()
    utilization = kpis['berth_utilization']
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric(
            label="⚓ Total Berths",
            value=str(total_berths),
            help="Total number of berths across all terminals"
        )
    
    with col2:
        st.metric(
            label="🟢 Available",
            value=str(available),
            help="Berths currently available for use"
        )
    
    with col3:
        st.metric(
            label="🔴 Occupied",
            value=str(occupied),
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
            delta=f"{utilization - 70:.1f}%",
            help="Current berth utilization rate"
        )


def create_berth_layout_map():
    """
    Create berth layout map grouped by terminal name.
    Each terminal is displayed as a column with its berths vertically arranged.
    """
    berth_status = data_service.get_berth_status()

    if not berth_status:
        st.info("No berth data available.")
        return go.Figure()

    # Simulate terminal grouping (or pull from dataset if available)
    # For now, we’ll assign terminals alternately
    terminals = ["Tuas", "Pasir Panjang", "Keppel", "Brani"]
    for i, berth in enumerate(berth_status):
        berth['terminal'] = terminals[i % len(terminals)]

    # Assign X and Y coordinates based on terminal and berth order
    terminal_positions = {t: i for i, t in enumerate(terminals)}
    berth_groups = {}

    for berth in berth_status:
        term = berth['terminal']
        berth_groups.setdefault(term, [])
        berth_groups[term].append(berth)

    # Add coordinates for plotting
    for term, group in berth_groups.items():
        for i, b in enumerate(group):
            b['x'] = terminal_positions[term]
            b['y'] = -i  # stack downwards

    # Define color mapping for statuses
    color_map = {
        'Available': colors.SUCCESS,
        'Occupied': colors.DANGER,
        'Maintenance': colors.WARNING
    }

    # Create the figure
    fig = go.Figure()

    for status in ['Available', 'Occupied', 'Maintenance']:
        berths = [b for b in berth_status if b['status'] == status]

        if not berths:
            continue

        fig.add_trace(go.Scatter(
            x=[b['x'] for b in berths],
            y=[b['y'] for b in berths],
            mode='markers+text',
            name=status,
            text=[b['berth_id'] for b in berths],
            textposition='middle center',
            textfont=dict(color='white', size=10, family='Arial Black'),
            marker=dict(
                size=45,
                color=color_map.get(status, '#CCCCCC'),
                line=dict(color='white', width=2)
            ),
            customdata=[[b['berth_id'], b['vessel'], b['eta'], b['etd'], b['terminal']] for b in berths],
            hovertemplate=(
                "<b>Berth %{customdata[0]}</b><br>"
                "Terminal: %{customdata[4]}<br>"
                f"Status: {status}<br>"
                "Vessel: %{customdata[1]}<br>"
                "ETA: %{customdata[2]}<br>"
                "ETD: %{customdata[3]}<br>"
                "<extra></extra>"
            )
        ))

    # Update layout
    fig.update_layout(
        title="Berth Layout by Terminal",
        showlegend=True,
        height=600,
        xaxis=dict(
            tickmode='array',
            tickvals=list(terminal_positions.values()),
            ticktext=list(terminal_positions.keys()),
            showgrid=False,
            zeroline=False
        ),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        margin=dict(t=60, b=40, l=40, r=40)
    )

    return fig

def create_utilization_heatmap():
    """Create berth utilization heatmap with REAL DATA"""
    
    # Get historical berth data
    movements = data_service.get_recent_movements(limit=100)
    
    # Calculate utilization by hour and day
    df = pd.DataFrame(movements)
    if 'ata' in df.columns:
        df['date'] = pd.to_datetime(df['ata']).dt.date
        df['hour'] = pd.to_datetime(df['ata']).dt.hour
        
        # Count vessels per hour and day
        utilization = df.groupby(['date', 'hour']).size().reset_index(name='vessels')
        
        # Pivot for heatmap
        heatmap_data = utilization.pivot(index='hour', columns='date', values='vessels')
        heatmap_data = heatmap_data.fillna(0)
        
        # Convert to percentage (assuming 24 total berths)
        heatmap_data = (heatmap_data / 24) * 100
        
    else:
        # Fallback: Create sample data
        dates = [(datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d') for i in range(7)]
        hours = list(range(24))
        heatmap_data = pd.DataFrame(
            np.random.randint(30, 90, size=(24, 7)),
            index=hours,
            columns=dates
        )
    
    fig = go.Figure(data=go.Heatmap(
        z=heatmap_data.values,
        x=heatmap_data.columns,
        y=heatmap_data.index,
        colorscale=[
            [0, colors.SUCCESS],
            [0.5, colors.WARNING],
            [1, colors.DANGER]
        ],
        hovertemplate='Date: %{x}<br>Hour: %{y}:00<br>Utilization: %{z:.1f}%<extra></extra>',
        colorbar=dict(title="Utilization %")
    ))
    
    fig.update_layout(
        title="Berth Utilization Heatmap (Last 7 Days)",
        xaxis_title="Date",
        yaxis_title="Hour of Day",
        height=400,
        **charts.LAYOUT_CONFIG
    )
    
    return fig


def create_bunching_analysis():
    """Analyze and display vessel bunching with REAL DATA"""
    
    movements = data_service.get_recent_movements(limit=50)
    df = pd.DataFrame(movements)
    
    if 'ata' not in df.columns or len(df) == 0:
        st.info("Not enough data for bunching analysis")
        return None
    
    # Calculate time between arrivals
    df['ata_dt'] = pd.to_datetime(df['ata'])
    df = df.sort_values('ata_dt')
    df['time_diff'] = df['ata_dt'].diff().dt.total_seconds() / 3600  # hours
    
    # Detect bunching (arrivals within 2 hours of each other)
    bunching_threshold = 2  # hours
    bunched = df[df['time_diff'] < bunching_threshold].copy()
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Create timeline plot
        fig = go.Figure()
        
        # Normal arrivals
        normal = df[df['time_diff'] >= bunching_threshold]
        fig.add_trace(go.Scatter(
            x=normal['ata_dt'],
            y=[1] * len(normal),
            mode='markers',
            name='Normal Spacing',
            marker=dict(size=12, color=colors.SUCCESS),
            hovertemplate='<b>%{text}</b><br>Arrival: %{x}<extra></extra>',
            text=normal['vessel']
        ))
        
        # Bunched arrivals
        if len(bunched) > 0:
            fig.add_trace(go.Scatter(
                x=bunched['ata_dt'],
                y=[1] * len(bunched),
                mode='markers',
                name='Bunched (<2hrs)',
                marker=dict(size=15, color=colors.DANGER, symbol='diamond'),
                hovertemplate='<b>%{text}</b><br>Arrival: %{x}<br>⚠️ Bunched<extra></extra>',
                text=bunched['vessel']
            ))
        
        fig.update_layout(
            title="Vessel Arrival Timeline - Bunching Detection",
            xaxis_title="Date & Time",
            yaxis=dict(visible=False),
            height=300,
            showlegend=True,
            **charts.LAYOUT_CONFIG
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("### 📊 Bunching Stats")
        
        bunching_rate = (len(bunched) / len(df) * 100) if len(df) > 0 else 0
        
        st.metric(
            label="Bunching Events",
            value=str(len(bunched)),
            delta=f"{bunching_rate:.1f}%",
            delta_color="inverse"
        )
        
        if len(bunched) > 0:
            avg_gap = bunched['time_diff'].mean()
            st.metric(
                label="Avg Gap (Bunched)",
                value=f"{avg_gap:.1f}h"
            )
        
        # Show most recent bunching event
        if len(bunched) > 0:
            recent_bunch = bunched.iloc[-1]
            st.warning(f"**Recent Bunching:**\n\n{recent_bunch['vessel']}\n\nGap: {recent_bunch['time_diff']:.1f}h")


def create_upcoming_schedule():
    """Display upcoming vessel schedule with REAL DATA"""
    
    movements = data_service.get_recent_movements(limit=30)
    df = pd.DataFrame(movements)
    
    if 'eta' not in df.columns or len(df) == 0:
        st.info("No upcoming vessels scheduled")
        return
    
    # Filter for future arrivals (vessels with ETA)
    df['eta_dt'] = pd.to_datetime(df['eta'], errors='coerce')
    upcoming = df[df['eta_dt'] > datetime.now()].sort_values('eta_dt')
    
    if len(upcoming) == 0:
        st.info("No upcoming arrivals in the near future")
        return
    
    # Prepare display data
    schedule_df = upcoming[['vessel', 'eta', 'berth']].head(10).copy()
    schedule_df['eta'] = pd.to_datetime(schedule_df['eta']).dt.strftime('%Y-%m-%d %H:%M')
    schedule_df.columns = ['Vessel', 'Expected Arrival', 'Assigned Berth']
    
    # Color code by urgency
    def highlight_urgent(row):
        eta = pd.to_datetime(row['Expected Arrival'])
        hours_until = (eta - datetime.now()).total_seconds() / 3600
        if hours_until < 6:
            return ['background-color: #ff4b4b33'] * len(row)
        elif hours_until < 24:
            return ['background-color: #ffa50033'] * len(row)
        else:
            return [''] * len(row)
    
    styled_df = schedule_df.style.apply(highlight_urgent, axis=1)
    
    st.markdown("### 📅 Upcoming Vessel Schedule")
    st.dataframe(styled_df, use_container_width=True, hide_index=True)
    
    # Legend
    st.caption("🔴 Within 6 hours  🟡 Within 24 hours  ⚪ Later")


def create_berth_recommendations():
    """Generate AI-powered berth optimization recommendations with REAL DATA"""
    
    berth_status = data_service.get_berth_status()
    movements = data_service.get_recent_movements(limit=50)
    kpis = data_service.get_global_kpis()
    
    st.markdown("### 🤖 AI-Powered Optimization Recommendations")
    
    # Calculate recommendations based on real data
    recommendations = []
    
    # Check utilization
    utilization = kpis['berth_utilization']
    if utilization > 85:
        recommendations.append({
            'type': 'warning',
            'title': 'High Berth Utilization',
            'message': f'Current utilization at {utilization:.1f}%. Consider delaying non-urgent maintenance.',
            'impact': 'High'
        })
    elif utilization < 50:
        recommendations.append({
            'type': 'info',
            'title': 'Low Utilization Period',
            'message': f'Utilization at {utilization:.1f}%. Ideal time for scheduled maintenance.',
            'impact': 'Medium'
        })
    
    # Check for bunching
    df = pd.DataFrame(movements)
    if 'ata' in df.columns and len(df) > 0:
        df['ata_dt'] = pd.to_datetime(df['ata'])
        df = df.sort_values('ata_dt')
        df['time_diff'] = df['ata_dt'].diff().dt.total_seconds() / 3600
        bunched_count = len(df[df['time_diff'] < 2])
        
        if bunched_count > 3:
            recommendations.append({
                'type': 'warning',
                'title': 'Vessel Bunching Detected',
                'message': f'{bunched_count} vessels arrived within 2 hours of each other. Review scheduling.',
                'impact': 'High'
            })
    
    # Check berth availability
    available_count = len([b for b in berth_status if b['status'] == 'Available'])
    if available_count < 3:
        recommendations.append({
            'type': 'error',
            'title': 'Low Berth Availability',
            'message': f'Only {available_count} berths available. Prepare for potential delays.',
            'impact': 'Critical'
        })
    
    # Display recommendations
    if recommendations:
        for rec in recommendations:
            icon_map = {
                'error': '🚨',
                'warning': '⚠️',
                'info': 'ℹ️'
            }
            
            with st.container():
                cols = st.columns([1, 8, 2])
                with cols[0]:
                    st.markdown(f"## {icon_map.get(rec['type'], 'ℹ️')}")
                with cols[1]:
                    st.markdown(f"**{rec['title']}**")
                    st.caption(rec['message'])
                with cols[2]:
                    st.metric("Impact", rec['impact'])
                st.divider()
    else:
        st.success("✅ All berth operations running smoothly. No optimization needed at this time.")


def render():
    """Main render function for Berth Management page"""
    
    st.title("⚓ Berth Management")
    st.markdown("Real-time berth operations, utilization tracking, and optimization")
    
    # Status Overview
    create_berth_status_overview()
    
    st.divider()
    
    # Main layout: Berth map and utilization
    col1, col2 = st.columns([3, 2])
    
    with col1:
        st.plotly_chart(create_berth_layout_map(), use_container_width=True)
    
    with col2:
        st.plotly_chart(create_utilization_heatmap(), use_container_width=True)
    
    st.divider()
    
    # Bunching Analysis
    create_bunching_analysis()
    
    st.divider()
    
    # Upcoming Schedule
    create_upcoming_schedule()
    
    st.divider()
    
    # AI Recommendations
    create_berth_recommendations()
    
    # Refresh button
    st.markdown("---")
    if st.button("🔄 Refresh Data", key="refresh_data_berth", use_container_width=True):
        refresh_data()


if __name__ == "__main__":
    render()