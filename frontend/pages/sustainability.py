"""
Sustainability Page
Carbon tracking and environmental impact analysis
Frontend Engineer: UI/UX Specialist
"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from frontend.config import colors, charts


def create_carbon_kpis():
    """Create carbon-focused KPI metrics"""
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric(
            label="🌱 Total Carbon Saved",
            value="1,245 tonnes",
            delta="+285 tonnes",
            help="Total CO₂ emissions saved this month"
        )
    
    with col2:
        st.metric(
            label="💰 Bunker Savings",
            value="$287K",
            delta="+$62K",
            help="Cost savings from reduced fuel consumption"
        )
    
    with col3:
        st.metric(
            label="📉 Emissions Reduction",
            value="18.5%",
            delta="+3.2%",
            help="Percentage reduction vs baseline"
        )
    
    with col4:
        st.metric(
            label="🌳 Trees Equivalent",
            value="58,000",
            delta="+13,200",
            help="Equivalent trees planted for carbon offset"
        )
    
    with col5:
        st.metric(
            label="🎯 Monthly Target",
            value="89%",
            delta="+12%",
            help="Progress toward monthly carbon reduction goal"
        )


def create_carbon_trend_chart():
    """Create carbon emissions trend chart"""
    
    # Generate sample data
    dates = pd.date_range(end=datetime.now(), periods=180, freq='D')
    df = pd.DataFrame({
        'Date': dates,
        'Emissions': np.random.normal(850, 50, 180) - np.linspace(0, 150, 180),
        'Baseline': [1000] * 180,
        'Target': [750] * 180,
        'Savings': np.random.normal(150, 20, 180) + np.linspace(0, 100, 180)
    })
    
    fig = go.Figure()
    
    # Baseline
    fig.add_trace(go.Scatter(
        x=df['Date'],
        y=df['Baseline'],
        name='Baseline',
        line=dict(color='rgba(255, 255, 255, 0.3)', width=2, dash='dot'),
        mode='lines'
    ))
    
    # Actual emissions
    fig.add_trace(go.Scatter(
        x=df['Date'],
        y=df['Emissions'],
        name='Actual Emissions',
        line=dict(color=colors.DANGER, width=3),
        fill='tonexty',
        fillcolor='rgba(239, 71, 111, 0.1)',
        mode='lines'
    ))
    
    # Target
    fig.add_trace(go.Scatter(
        x=df['Date'],
        y=df['Target'],
        name='Target',
        line=dict(color=colors.SUCCESS, width=2, dash='dash'),
        mode='lines'
    ))
    
    # Savings (on secondary axis)
    fig.add_trace(go.Scatter(
        x=df['Date'],
        y=df['Savings'],
        name='Savings',
        line=dict(color=colors.SUCCESS, width=2),
        yaxis='y2',
        fill='tozeroy',
        fillcolor='rgba(6, 214, 160, 0.2)'
    ))
    
    fig.update_layout(
        **charts.LAYOUT_CONFIG,
        height=450,
        title={
            'text': '📊 Carbon Emissions & Savings Trend (6 Months)',
            'font': {'size': 20, 'color': 'white'},
            'x': 0.5,
            'xanchor': 'center'
        },
        xaxis_title='Date',
        yaxis_title='Emissions (tonnes CO₂)',
        yaxis2=dict(
            title='Savings (tonnes CO₂)',
            overlaying='y',
            side='right',
            showgrid=False,
            titlefont=dict(color=colors.SUCCESS),
            tickfont=dict(color=colors.SUCCESS)
        ),
        legend=dict(
            orientation='h',
            yanchor='bottom',
            y=1.02,
            xanchor='right',
            x=1
        )
    )
    
    return fig


def create_vessel_emissions_breakdown():
    """Create vessel-by-vessel emissions breakdown"""
    
    # Sample data
    vessels = pd.DataFrame({
        'Vessel': ['MSC Diana', 'Ever Given', 'CMA CGM Antoine', 'Maersk Essex', 
                   'COSCO Shipping', 'Hapag-Lloyd Berlin', 'ONE Innovation', 'Others'],
        'Emissions': [245, 312, 198, 276, 231, 189, 167, 587],
        'Savings': [45, 38, 52, 41, 48, 55, 61, 123],
        'Efficiency': [84.5, 79.2, 88.6, 82.1, 85.3, 89.7, 91.2, 81.4]
    })
    
    # Calculate percentage
    vessels['Emissions_Pct'] = (vessels['Emissions'] / vessels['Emissions'].sum() * 100).round(1)
    
    fig = go.Figure()
    
    # Emissions bar
    fig.add_trace(go.Bar(
        name='Emissions',
        x=vessels['Vessel'],
        y=vessels['Emissions'],
        marker_color=colors.DANGER,
        text=vessels['Emissions_Pct'].apply(lambda x: f'{x}%'),
        textposition='outside',
        hovertemplate='<b>%{x}</b><br>Emissions: %{y} tonnes<br>%{text} of total<extra></extra>'
    ))
    
    # Savings bar
    fig.add_trace(go.Bar(
        name='Savings',
        x=vessels['Vessel'],
        y=vessels['Savings'],
        marker_color=colors.SUCCESS,
        hovertemplate='<b>%{x}</b><br>Savings: %{y} tonnes<extra></extra>'
    ))
    
    fig.update_layout(
        **charts.LAYOUT_CONFIG,
        height=400,
        title={
            'text': '🚢 Emissions by Vessel (This Month)',
            'font': {'size': 20, 'color': 'white'},
            'x': 0.5,
            'xanchor': 'center'
        },
        xaxis_title='Vessel',
        yaxis_title='Tonnes CO₂',
        barmode='group',
        legend=dict(
            orientation='h',
            yanchor='bottom',
            y=1.02,
            xanchor='right',
            x=1
        )
    )
    
    return fig


def create_optimization_waterfall():
    """Create waterfall chart showing optimization breakdown"""
    
    categories = ['Baseline', 'Speed Optimization', 'Route Optimization', 
                  'Berth Scheduling', 'Weather Routing', 'Idle Time Reduction', 'Total Savings']
    values = [1000, -182, -145, -98, -67, -53, -545]
    
    fig = go.Figure(go.Waterfall(
        x=categories,
        y=values,
        measure=['relative', 'relative', 'relative', 'relative', 'relative', 'relative', 'total'],
        text=[f'{abs(v)} t' for v in values],
        textposition='outside',
        connector={'line': {'color': 'rgb(100, 100, 100)'}},
        increasing={'marker': {'color': colors.DANGER}},
        decreasing={'marker': {'color': colors.SUCCESS}},
        totals={'marker': {'color': colors.SECONDARY}},
        hovertemplate='<b>%{x}</b><br>%{y} tonnes CO₂<extra></extra>'
    ))
    
    fig.update_layout(
        **charts.LAYOUT_CONFIG,
        height=450,
        title={
            'text': '💡 Carbon Reduction Breakdown',
            'font': {'size': 20, 'color': 'white'},
            'x': 0.5,
            'xanchor': 'center'
        },
        xaxis_title='Optimization Method',
        yaxis_title='Tonnes CO₂',
        showlegend=False
    )
    
    return fig


def create_emissions_heatmap():
    """Create emissions intensity heatmap by route and time"""
    
    # Sample data
    routes = ['SG-RTM', 'SG-LAX', 'SHA-LAX', 'RTM-SG', 'LAX-SHA']
    months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun']
    
    # Random emissions data
    np.random.seed(42)
    data = np.random.randint(150, 350, size=(len(routes), len(months)))
    
    fig = go.Figure(data=go.Heatmap(
        z=data,
        x=months,
        y=routes,
        colorscale=[
            [0, colors.SUCCESS],
            [0.5, colors.WARNING],
            [1, colors.DANGER]
        ],
        text=data,
        texttemplate='%{text} t',
        textfont={'size': 12},
        hovertemplate='<b>%{y}</b><br>%{x}: %{z} tonnes CO₂<extra></extra>',
        colorbar=dict(
            title='Tonnes CO₂',
            titleside='right'
        )
    ))
    
    fig.update_layout(
        **charts.LAYOUT_CONFIG,
        height=350,
        title={
            'text': '🔥 Emissions Intensity Heatmap',
            'font': {'size': 20, 'color': 'white'},
            'x': 0.5,
            'xanchor': 'center'
        },
        xaxis_title='Month',
        yaxis_title='Route'
    )
    
    return fig


def create_efficiency_gauge(current_value: float, target: float):
    """Create gauge chart for carbon efficiency"""
    
    fig = go.Figure(go.Indicator(
        mode='gauge+number+delta',
        value=current_value,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': 'Carbon Efficiency Score', 'font': {'size': 20, 'color': 'white'}},
        delta={'reference': target, 'increasing': {'color': colors.SUCCESS}},
        gauge={
            'axis': {'range': [None, 100], 'tickcolor': 'white'},
            'bar': {'color': colors.SECONDARY},
            'bgcolor': 'rgba(0,0,0,0)',
            'borderwidth': 2,
            'bordercolor': 'white',
            'steps': [
                {'range': [0, 60], 'color': colors.DANGER},
                {'range': [60, 80], 'color': colors.WARNING},
                {'range': [80, 100], 'color': colors.SUCCESS}
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


def create_environmental_impact_card():
    """Create environmental impact equivalents card"""
    
    st.markdown("""
        <div style='background: linear-gradient(135deg, rgba(6, 214, 160, 0.2), rgba(6, 214, 160, 0.1));
                    padding: 2rem;
                    border-radius: 12px;
                    border: 1px solid rgba(6, 214, 160, 0.3);'>
            <h3 style='color: #06D6A0; margin: 0 0 1.5rem 0;'>🌍 Environmental Impact Equivalents</h3>
            <div style='display: grid; grid-template-columns: repeat(2, 1fr); gap: 1.5rem;'>
                <div style='background: rgba(0, 0, 0, 0.3); padding: 1rem; border-radius: 8px;'>
                    <div style='font-size: 2rem; margin-bottom: 0.5rem;'>🌳</div>
                    <div style='font-size: 1.5rem; font-weight: 700; color: white; margin-bottom: 0.25rem;'>58,000</div>
                    <div style='color: #A0A0A0; font-size: 0.9rem;'>Trees Planted Equivalent</div>
                </div>
                <div style='background: rgba(0, 0, 0, 0.3); padding: 1rem; border-radius: 8px;'>
                    <div style='font-size: 2rem; margin-bottom: 0.5rem;'>🚗</div>
                    <div style='font-size: 1.5rem; font-weight: 700; color: white; margin-bottom: 0.25rem;'>270</div>
                    <div style='color: #A0A0A0; font-size: 0.9rem;'>Cars Off Road for 1 Year</div>
                </div>
                <div style='background: rgba(0, 0, 0, 0.3); padding: 1rem; border-radius: 8px;'>
                    <div style='font-size: 2rem; margin-bottom: 0.5rem;'>⚡</div>
                    <div style='font-size: 1.5rem; font-weight: 700; color: white; margin-bottom: 0.25rem;'>145,000</div>
                    <div style='color: #A0A0A0; font-size: 0.9rem;'>kWh Energy Saved</div>
                </div>
                <div style='background: rgba(0, 0, 0, 0.3); padding: 1rem; border-radius: 8px;'>
                    <div style='font-size: 2rem; margin-bottom: 0.5rem;'>🏠</div>
                    <div style='font-size: 1.5rem; font-weight: 700; color: white; margin-bottom: 0.25rem;'>62</div>
                    <div style='color: #A0A0A0; font-size: 0.9rem;'>Homes Powered for 1 Year</div>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)


def create_optimization_opportunities_table():
    """Create table of carbon optimization opportunities"""
    
    opportunities = pd.DataFrame({
        'Opportunity': [
            '🚢 Speed Optimization - MSC Diana',
            '🗺️ Route Adjustment - Ever Given',
            '⚓ Berth Scheduling - CMA CGM Antoine',
            '🌤️ Weather Routing - Maersk Essex',
            '⏱️ Idle Time Reduction - COSCO Shipping'
        ],
        'Potential Savings (tonnes)': [45.2, 38.7, 28.5, 32.1, 25.8],
        'Cost Savings (USD)': ['$18,200', '$15,600', '$11,500', '$12,900', '$10,400'],
        'Implementation': ['Easy', 'Medium', 'Easy', 'Medium', 'Easy'],
        'Timeframe': ['Immediate', '2-3 days', 'Immediate', '1-2 days', 'Immediate'],
        'Status': ['🟢 Ready', '🟡 Planning', '🟢 Ready', '🟡 Planning', '🟢 Ready']
    })
    
    # Style implementation difficulty
    def color_implementation(val):
        if val == 'Easy':
            return 'background-color: rgba(6, 214, 160, 0.2)'
        elif val == 'Medium':
            return 'background-color: rgba(255, 214, 10, 0.2)'
        else:
            return 'background-color: rgba(239, 71, 111, 0.2)'
    
    styled_df = opportunities.style.applymap(
        color_implementation, 
        subset=['Implementation']
    )
    
    return styled_df


def create_sustainability_score_breakdown():
    """Create sustainability score breakdown chart"""
    
    categories = ['Carbon Efficiency', 'Fuel Optimization', 'Route Planning', 
                  'Berth Management', 'Weather Adaptation']
    scores = [88, 85, 92, 78, 90]
    targets = [85, 85, 85, 85, 85]
    
    fig = go.Figure()
    
    # Actual scores
    fig.add_trace(go.Bar(
        name='Actual Score',
        x=categories,
        y=scores,
        marker=dict(
            color=[colors.SUCCESS if s >= 85 else colors.WARNING for s in scores]
        ),
        text=[f'{s}%' for s in scores],
        textposition='outside'
    ))
    
    # Target line
    fig.add_trace(go.Scatter(
        name='Target (85%)',
        x=categories,
        y=targets,
        mode='lines+markers',
        line=dict(color='white', width=2, dash='dash'),
        marker=dict(size=8, color='white')
    ))
    
    fig.update_layout(
        **charts.LAYOUT_CONFIG,
        height=400,
        title={
            'text': '⭐ Sustainability Score Breakdown',
            'font': {'size': 20, 'color': 'white'},
            'x': 0.5,
            'xanchor': 'center'
        },
        xaxis_title='Category',
        yaxis_title='Score (%)',
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


def render():
    """Render the Sustainability page"""

     # ✅ ADD: Permission check
    from config.permissions import Permission, require_permission
    require_permission(Permission.VIEW_SUSTAINABILITY)
    
    # Carbon KPIs
    st.subheader("🌱 Carbon Performance Overview")
    create_carbon_kpis()
    
    st.divider()
    
    # Main trend chart
    st.subheader("📊 Emissions & Savings Analysis")
    st.plotly_chart(create_carbon_trend_chart(), use_container_width=True)
    
    st.divider()
    
    # Vessel breakdown and optimization waterfall
    chart_col1, chart_col2 = st.columns(2)
    
    with chart_col1:
        st.plotly_chart(create_vessel_emissions_breakdown(), use_container_width=True)
    
    with chart_col2:
        st.plotly_chart(create_optimization_waterfall(), use_container_width=True)
    
    st.divider()
    
    # Environmental impact and efficiency
    impact_col1, impact_col2 = st.columns([2, 1])
    
    with impact_col1:
        create_environmental_impact_card()
    
    with impact_col2:
        st.plotly_chart(create_efficiency_gauge(85.3, 85), use_container_width=True)
    
    st.divider()
    
    # Heatmap and score breakdown
    heat_col1, heat_col2 = st.columns(2)
    
    with heat_col1:
        st.plotly_chart(create_emissions_heatmap(), use_container_width=True)
    
    with heat_col2:
        st.plotly_chart(create_sustainability_score_breakdown(), use_container_width=True)
    
    st.divider()
    
    # Optimization opportunities
    st.subheader("💡 Carbon Reduction Opportunities")
    
    opp_col1, opp_col2 = st.columns([2, 1])
    
    with opp_col1:
        st.dataframe(
            create_optimization_opportunities_table(),
            use_container_width=True,
            height=250
        )
    
    with opp_col2:
        st.info("""
        **📈 Total Potential**
        
        **Carbon Savings:** 170.3 tonnes
        
        **Cost Savings:** $68,600
        
        **Quick Wins:** 3 opportunities ready for immediate implementation
        
        **Timeline:** All opportunities can be implemented within 3 days
        """)
    
    st.divider()
    
    # AI Insights
    st.subheader("🤖 AI-Powered Recommendations")
    
    insight_col1, insight_col2, insight_col3 = st.columns(3)
    
    with insight_col1:
        st.success("""
        **🎯 Top Priority**
        
        Speed optimization on MSC Diana's Singapore-Rotterdam route shows highest ROI.
        
        **Impact:**
        - 45.2 tonnes CO₂ saved
        - $18,200 cost reduction
        - No schedule impact
        
        **Action:** Reduce speed to 18 knots.
        """)
    
    with insight_col2:
        st.warning("""
        **⚠️ Attention Needed**
        
        Berth idle time at Terminal 4 is 15% above target.
        
        **Impact:**
        - 25.8 tonnes excess emissions
        - $10,400 unnecessary costs
        
        **Action:** Implement just-in-time berthing schedule.
        """)
    
    with insight_col3:
        st.info("""
        **📊 Trend Analysis**
        
        Carbon efficiency improved 18.5% over last 6 months.
        
        **Key Drivers:**
        - Weather routing (+8.2%)
        - Speed optimization (+6.1%)
        - Route planning (+4.2%)
        
        **Target:** On track for 20% by year-end.
        """)
