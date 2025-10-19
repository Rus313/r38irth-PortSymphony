"""
Visualization Module
Advanced Plotly charts for maritime analytics
Visualization Engineer: Data Viz Specialist
"""

import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from typing import List, Dict, Optional
from datetime import datetime, timedelta
from frontend.config import colors, charts


class MaritimeCharts:
    """
    Collection of specialized maritime visualization charts
    """
    
    @staticmethod
    def create_global_port_map(
        vessels_data: pd.DataFrame,
        ports_data: pd.DataFrame
    ) -> go.Figure:
        """
        Interactive world map with ports and vessel routes
        
        Args:
            vessels_data: DataFrame with vessel movements
            ports_data: DataFrame with port locations
            
        Returns:
            Plotly Figure
        """
        fig = go.Figure()
        
        # Add port markers
        fig.add_trace(go.Scattergeo(
            lon=ports_data['longitude'],
            lat=ports_data['latitude'],
            text=ports_data['port_name'],
            customdata=np.column_stack((
                ports_data['vessel_count'],
                ports_data['country']
            )),
            mode='markers+text',
            marker=dict(
                size=ports_data['vessel_count'] * 2,
                color=colors.SECONDARY,
                line=dict(width=2, color='white'),
                sizemode='diameter',
                opacity=0.8
            ),
            textposition='top center',
            textfont=dict(size=10, color='white', family='Inter'),
            name='Ports',
            hovertemplate=(
                '<b>%{text}</b><br>'
                'Vessels: %{customdata[0]}<br>'
                'Country: %{customdata[1]}<br>'
                'Lat: %{lat:.2f}<br>'
                'Lon: %{lon:.2f}'
                '<extra></extra>'
            )
        ))
        
        # Add vessel routes
        route_colors = [colors.PRIMARY, colors.SUCCESS, colors.WARNING, colors.DANGER]
        for idx, (_, route) in enumerate(vessels_data.iterrows()):
            color = route_colors[idx % len(route_colors)]
            
            fig.add_trace(go.Scattergeo(
                lon=[route['from_lon'], route['to_lon']],
                lat=[route['from_lat'], route['to_lat']],
                mode='lines',
                line=dict(width=3, color=color),
                opacity=0.5,
                name=route['vessel_name'],
                hovertemplate=(
                    f"<b>{route['vessel_name']}</b><br>"
                    f"{route['from_port']} → {route['to_port']}<br>"
                    f"ETA: {route.get('eta', 'N/A')}"
                    "<extra></extra>"
                )
            ))
        
        # Update layout
        fig.update_layout(
            **charts.LAYOUT_CONFIG,
            height=600,
            geo=dict(
                projection_type='natural earth',
                showland=True,
                landcolor='rgb(20, 20, 30)',
                coastlinecolor='rgb(100, 100, 120)',
                showlakes=True,
                lakecolor='rgb(10, 10, 20)',
                showcountries=True,
                countrycolor='rgb(80, 80, 100)',
                bgcolor='rgba(0,0,0,0)',
                oceancolor='rgb(10, 10, 20)'
            ),
            title={
                'text': '🌍 Global Port Network & Active Vessel Routes',
                'font': {'size': 24, 'color': 'white'},
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
    
    @staticmethod
    def create_berth_gantt(berth_data: pd.DataFrame) -> go.Figure:
        """
        Gantt chart showing berth utilization timeline
        
        Args:
            berth_data: DataFrame with berth occupancy data
            
        Returns:
            Plotly Figure
        """
        fig = px.timeline(
            berth_data,
            x_start='atb',
            x_end='atu',
            y='berth',
            color='vessel_name',
            title='⚓ Berth Utilization Timeline',
            labels={'vessel_name': 'Vessel'},
            color_discrete_sequence=colors.CHART_COLORS
        )
        
        fig.update_layout(
            **charts.LAYOUT_CONFIG,
            height=500,
            xaxis_title='Time',
            yaxis_title='Berth',
            hovermode='closest'
        )
        
        fig.update_traces(
            hovertemplate=(
                '<b>%{customdata[0]}</b><br>'
                'Berth: %{y}<br>'
                'Arrival: %{base}<br>'
                'Departure: %{x}<br>'
                '<extra></extra>'
            )
        )
        
        return fig
    
    @staticmethod
    def create_performance_trends(performance_data: pd.DataFrame) -> go.Figure:
        """
        Multi-line chart showing performance trends over time
        
        Args:
            performance_data: DataFrame with performance metrics
            
        Returns:
            Plotly Figure
        """
        fig = go.Figure()
        
        metrics = {
            'arrival_accuracy': {'name': 'Arrival Accuracy', 'color': colors.PRIMARY},
            'berth_utilization': {'name': 'Berth Utilization', 'color': colors.SUCCESS},
            'on_time_performance': {'name': 'On-Time Performance', 'color': colors.SECONDARY}
        }
        
        for metric_key, metric_info in metrics.items():
            if metric_key in performance_data.columns:
                fig.add_trace(go.Scatter(
                    x=performance_data['date'],
                    y=performance_data[metric_key],
                    name=metric_info['name'],
                    line=dict(color=metric_info['color'], width=3),
                    mode='lines+markers',
                    marker=dict(size=8),
                    hovertemplate=(
                        f'<b>{metric_info["name"]}</b><br>'
                        'Date: %{x|%b %d, %Y}<br>'
                        'Value: %{y:.1f}%'
                        '<extra></extra>'
                    )
                ))
        
        # Add target line
        fig.add_hline(
            y=90,
            line_dash='dash',
            line_color=colors.WARNING,
            annotation_text='Target: 90%',
            annotation_position='right'
        )
        
        fig.update_layout(
            **charts.LAYOUT_CONFIG,
            height=450,
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
            hovermode='x unified'
        )
        
        return fig
    
    @staticmethod
    def create_carbon_waterfall(carbon_data: pd.DataFrame) -> go.Figure:
        """
        Waterfall chart showing carbon savings breakdown
        
        Args:
            carbon_data: DataFrame with carbon metrics
            
        Returns:
            Plotly Figure
        """
        categories = carbon_data['category'].tolist()
        values = carbon_data['value'].tolist()
        
        fig = go.Figure(go.Waterfall(
            x=categories,
            y=values,
            measure=['relative'] * (len(values) - 1) + ['total'],
            text=[f'{v:+.1f}' for v in values],
            textposition='outside',
            connector={'line': {'color': 'rgb(100, 100, 100)'}},
            increasing={'marker': {'color': colors.SUCCESS}},
            decreasing={'marker': {'color': colors.DANGER}},
            totals={'marker': {'color': colors.SECONDARY}}
        ))
        
        fig.update_layout(
            **charts.LAYOUT_CONFIG,
            height=400,
            title={
                'text': '🌱 Carbon Abatement Breakdown',
                'font': {'size': 20, 'color': 'white'},
                'x': 0.5,
                'xanchor': 'center'
            },
            xaxis_title='Category',
            yaxis_title='Tonnes CO₂',
            showlegend=False
        )
        
        return fig
    
    @staticmethod
    def create_vessel_status_sunburst(status_data: pd.DataFrame) -> go.Figure:
        """
        Sunburst chart showing vessel status distribution by operator
        
        Args:
            status_data: DataFrame with vessel status by operator
            
        Returns:
            Plotly Figure
        """
        fig = go.Figure(go.Sunburst(
            labels=status_data['label'],
            parents=status_data['parent'],
            values=status_data['value'],
            branchvalues='total',
            marker=dict(
                colors=status_data['color'],
                line=dict(color='white', width=2)
            ),
            hovertemplate=(
                '<b>%{label}</b><br>'
                'Vessels: %{value}<br>'
                'Percentage: %{percentParent:.1%}'
                '<extra></extra>'
            )
        ))
        
        fig.update_layout(
            **charts.LAYOUT_CONFIG,
            height=500,
            title={
                'text': '🚢 Vessel Status Distribution',
                'font': {'size': 20, 'color': 'white'},
                'x': 0.5,
                'xanchor': 'center'
            }
        )
        
        return fig
    
    @staticmethod
    def create_bunching_heatmap(bunching_data: pd.DataFrame) -> go.Figure:
        """
        Heatmap showing vessel bunching by berth and time
        
        Args:
            bunching_data: DataFrame with bunching analysis
            
        Returns:
            Plotly Figure
        """
        # Pivot data for heatmap
        heatmap_data = bunching_data.pivot(
            index='berth',
            columns='time_slot',
            values='vessel_count'
        ).fillna(0)
        
        fig = go.Figure(data=go.Heatmap(
            z=heatmap_data.values,
            x=heatmap_data.columns,
            y=heatmap_data.index,
            colorscale=[
                [0, colors.SUCCESS],
                [0.5, colors.WARNING],
                [1, colors.DANGER]
            ],
            hovertemplate=(
                'Berth: %{y}<br>'
                'Time: %{x}<br>'
                'Vessels: %{z}<br>'
                '<extra></extra>'
            ),
            colorbar=dict(
                title='Vessel Count',
                titleside='right',
                tickmode='linear',
                tick0=0,
                dtick=1
            )
        ))
        
        fig.update_layout(
            **charts.LAYOUT_CONFIG,
            height=400,
            title={
                'text': '🔥 Vessel Bunching Analysis',
                'font': {'size': 20, 'color': 'white'},
                'x': 0.5,
                'xanchor': 'center'
            },
            xaxis_title='Time Slot',
            yaxis_title='Berth'
        )
        
        return fig
    
    @staticmethod
    def create_arrival_accuracy_funnel(accuracy_data: pd.DataFrame) -> go.Figure:
        """
        Funnel chart showing arrival accuracy by business unit
        
        Args:
            accuracy_data: DataFrame with accuracy by business unit
            
        Returns:
            Plotly Figure
        """
        fig = go.Figure(go.Funnel(
            y=accuracy_data['business_unit'],
            x=accuracy_data['accuracy'],
            textposition='inside',
            textinfo='value+percent initial',
            marker=dict(
                color=colors.CHART_COLORS[:len(accuracy_data)]
            ),
            hovertemplate=(
                '<b>%{y}</b><br>'
                'Accuracy: %{x:.1f}%<br>'
                '<extra></extra>'
            )
        ))
        
        fig.update_layout(
            **charts.LAYOUT_CONFIG,
            height=400,
            title={
                'text': '🎯 Arrival Accuracy by Business Unit',
                'font': {'size': 20, 'color': 'white'},
                'x': 0.5,
                'xanchor': 'center'
            }
        )
        
        return fig
    
    @staticmethod
    def create_wait_time_distribution(wait_data: pd.DataFrame) -> go.Figure:
        """
        Box plot showing wait time distribution
        
        Args:
            wait_data: DataFrame with wait times
            
        Returns:
            Plotly Figure
        """
        fig = go.Figure()
        
        for business_unit in wait_data['business_unit'].unique():
            unit_data = wait_data[wait_data['business_unit'] == business_unit]
            
            fig.add_trace(go.Box(
                y=unit_data['wait_time'],
                name=business_unit,
                marker_color=colors.CHART_COLORS[hash(business_unit) % len(colors.CHART_COLORS)],
                boxmean='sd',
                hovertemplate=(
                    f'<b>{business_unit}</b><br>'
                    'Wait Time: %{y:.2f} hrs<br>'
                    '<extra></extra>'
                )
            ))
        
        fig.update_layout(
            **charts.LAYOUT_CONFIG,
            height=450,
            title={
                'text': '⏱️ Wait Time Distribution by Business Unit',
                'font': {'size': 20, 'color': 'white'},
                'x': 0.5,
                'xanchor': 'center'
            },
            yaxis_title='Wait Time (hours)',
            showlegend=True
        )
        
        return fig
    
    @staticmethod
    def create_emissions_gauge(current_emissions: float, target: float) -> go.Figure:
        """
        Gauge chart showing emissions vs target
        
        Args:
            current_emissions: Current emissions value
            target: Target emissions value
            
        Returns:
            Plotly Figure
        """
        percentage = (current_emissions / target) * 100
        
        fig = go.Figure(go.Indicator(
            mode='gauge+number+delta',
            value=current_emissions,
            domain={'x': [0, 1], 'y': [0, 1]},
            title={'text': 'Carbon Emissions (tonnes)', 'font': {'size': 20, 'color': 'white'}},
            delta={'reference': target, 'increasing': {'color': colors.DANGER}},
            gauge={
                'axis': {'range': [None, target * 1.5], 'tickcolor': 'white'},
                'bar': {'color': colors.SECONDARY},
                'bgcolor': 'rgba(0,0,0,0)',
                'borderwidth': 2,
                'bordercolor': 'white',
                'steps': [
                    {'range': [0, target * 0.7], 'color': colors.SUCCESS},
                    {'range': [target * 0.7, target], 'color': colors.WARNING},
                    {'range': [target, target * 1.5], 'color': colors.DANGER}
                ],
                'threshold': {
                    'line': {'color': 'white', 'width': 4},
                    'thickness': 0.75,
                    'value': target
                }
            }
        ))
        
        fig.update_layout(
            **charts.LAYOUT_CONFIG,
            height=300
        )
        
        return fig


# Utility functions for data preparation

def prepare_sample_port_data() -> pd.DataFrame:
    """Generate sample port data for visualization"""
    return pd.DataFrame({
        'port_name': ['Singapore', 'Rotterdam', 'Shanghai', 'Los Angeles', 'Antwerp'],
        'latitude': [1.3521, 51.9225, 31.2304, 33.7701, 51.2194],
        'longitude': [103.8198, 4.47917, 121.4737, -118.1937, 4.4025],
        'vessel_count': [45, 32, 38, 28, 25],
        'country': ['Singapore', 'Netherlands', 'China', 'USA', 'Belgium']
    })


def prepare_sample_vessel_routes() -> pd.DataFrame:
    """Generate sample vessel route data"""
    return pd.DataFrame({
        'vessel_name': ['MSC Diana', 'Ever Given', 'CMA CGM Antoine', 'Maersk Essex'],
        'from_port': ['Singapore', 'Shanghai', 'Rotterdam', 'Los Angeles'],
        'to_port': ['Rotterdam', 'Los Angeles', 'Singapore', 'Shanghai'],
        'from_lat': [1.3521, 31.2304, 51.9225, 33.7701],
        'from_lon': [103.8198, 121.4737, 4.47917, -118.1937],
        'to_lat': [51.9225, 33.7701, 1.3521, 31.2304],
        'to_lon': [4.47917, -118.1937, 103.8198, 121.4737],
        'eta': ['2024-11-15 14:30', '2024-11-16 08:45', '2024-11-15 22:00', '2024-11-17 11:15']
    })


def prepare_sample_bunching_data() -> pd.DataFrame:
    """Generate sample bunching data for heatmap"""
    berths = ['Berth 1', 'Berth 2', 'Berth 3', 'Berth 4', 'Berth 5']
    time_slots = ['00:00-04:00', '04:00-08:00', '08:00-12:00', '12:00-16:00', '16:00-20:00', '20:00-24:00']
    
    data = []
    for berth in berths:
        for time_slot in time_slots:
            vessel_count = np.random.randint(0, 5)
            data.append({
                'berth': berth,
                'time_slot': time_slot,
                'vessel_count': vessel_count
            })
    
    return pd.DataFrame(data)


def prepare_sample_carbon_waterfall() -> pd.DataFrame:
    """Generate sample carbon waterfall data"""
    return pd.DataFrame({
        'category': ['Baseline', 'Speed Optimization', 'Route Optimization', 
                    'Berth Scheduling', 'Weather Routing', 'Total Savings'],
        'value': [1000, -150, -120, -80, -50, -400]
    })
