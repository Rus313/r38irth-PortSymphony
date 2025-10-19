"""
KPI Cards and Alerts Components
Reusable metric cards and notification system
Frontend Engineer: UI/UX Specialist
"""

import streamlit as st
from typing import Optional, List, Dict
from datetime import datetime


# ============================================
# KPI CARDS COMPONENT
# ============================================

def create_kpi_card(
    label: str,
    value: str,
    delta: Optional[str] = None,
    delta_color: str = "normal",
    icon: str = "📊",
    help_text: Optional[str] = None,
    trend_data: Optional[List[float]] = None
):
    """
    Create an enhanced KPI metric card with optional trend sparkline
    
    Args:
        label: Metric label
        value: Current value
        delta: Change indicator (e.g., "+5.2%")
        delta_color: "normal", "inverse", or "off"
        icon: Emoji icon for the metric
        help_text: Tooltip help text
        trend_data: Optional list of values for sparkline
    """
    # Determine delta color
    delta_html = ""
    if delta:
        if delta_color == "inverse":
            # Negative is good
            delta_bg = "#06D6A0" if delta.startswith('-') else "#EF476F"
        else:
            # Positive is good
            delta_bg = "#06D6A0" if delta.startswith('+') else "#EF476F"
        
        delta_html = f"""
            <div style='display: inline-block;
                        background: {delta_bg};
                        color: white;
                        padding: 0.25rem 0.5rem;
                        border-radius: 6px;
                        font-size: 0.75rem;
                        font-weight: 600;
                        margin-left: 0.5rem;'>
                {delta}
            </div>
        """
    
    # Create sparkline if trend data provided
    sparkline_html = ""
    if trend_data and len(trend_data) > 1:
        # Simple SVG sparkline
        max_val = max(trend_data)
        min_val = min(trend_data)
        range_val = max_val - min_val if max_val != min_val else 1
        
        points = []
        for i, val in enumerate(trend_data):
            x = (i / (len(trend_data) - 1)) * 100
            y = 30 - ((val - min_val) / range_val * 25)
            points.append(f"{x},{y}")
        
        polyline = " ".join(points)
        
        sparkline_html = f"""
            <svg width="100%" height="35" style="margin-top: 0.5rem;">
                <polyline
                    fill="none"
                    stroke="rgba(0, 180, 216, 0.6)"
                    stroke-width="2"
                    points="{polyline}"
                />
            </svg>
        """
    
    # Render card
    st.markdown(f"""
        <div style='background: linear-gradient(135deg, rgba(0, 102, 204, 0.1), rgba(0, 180, 216, 0.1));
                    padding: 1.5rem;
                    border-radius: 12px;
                    border: 1px solid rgba(255, 255, 255, 0.1);
                    transition: transform 0.2s ease, box-shadow 0.2s ease;
                    height: 100%;'
             onmouseover='this.style.transform="translateY(-4px)"; this.style.boxShadow="0 8px 16px rgba(0, 180, 216, 0.3)"'
             onmouseout='this.style.transform="translateY(0)"; this.style.boxShadow="none"'>
            
            <div style='display: flex; align-items: center; gap: 0.5rem; margin-bottom: 0.75rem;'>
                <span style='font-size: 1.5rem;'>{icon}</span>
                <div style='color: #A0A0A0; 
                            font-size: 0.85rem; 
                            font-weight: 600; 
                            text-transform: uppercase; 
                            letter-spacing: 0.5px;'>
                    {label}
                </div>
            </div>
            
            <div style='display: flex; align-items: baseline;'>
                <div style='color: white; 
                            font-size: 2rem; 
                            font-weight: 700;'>
                    {value}
                </div>
                {delta_html}
            </div>
            
            {sparkline_html}
            
        </div>
    """, unsafe_allow_html=True)


def create_comparison_kpi(
    label: str,
    current_value: float,
    target_value: float,
    unit: str = "",
    icon: str = "📊",
    inverse: bool = False
):
    """
    Create KPI card with progress bar comparing current vs target
    
    Args:
        label: Metric label
        current_value: Current metric value
        target_value: Target/goal value
        unit: Unit of measurement
        icon: Emoji icon
        inverse: If True, lower is better
    """
    # Calculate percentage
    if target_value != 0:
        percentage = (current_value / target_value) * 100
    else:
        percentage = 0
    
    # Determine color based on performance
    if inverse:
        # Lower is better (e.g., wait time, emissions)
        if percentage <= 80:
            color = "#06D6A0"  # Green - excellent
        elif percentage <= 100:
            color = "#FFD60A"  # Yellow - good
        else:
            color = "#EF476F"  # Red - needs improvement
    else:
        # Higher is better (e.g., accuracy, utilization)
        if percentage >= 100:
            color = "#06D6A0"
        elif percentage >= 85:
            color = "#FFD60A"
        else:
            color = "#EF476F"
    
    # Status text
    if percentage >= 100:
        status = "✅ Exceeded" if not inverse else "⚠️ Above Target"
    elif percentage >= 85:
        status = "✓ On Track"
    else:
        status = "⚠️ Below Target" if not inverse else "✓ Under Target"
    
    st.markdown(f"""
        <div style='background: rgba(45, 45, 45, 0.5);
                    padding: 1.5rem;
                    border-radius: 12px;
                    border: 1px solid rgba(255, 255, 255, 0.1);'>
            
            <div style='display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;'>
                <div style='display: flex; align-items: center; gap: 0.5rem;'>
                    <span style='font-size: 1.5rem;'>{icon}</span>
                    <span style='color: #A0A0A0; font-size: 0.85rem; font-weight: 600;'>{label}</span>
                </div>
                <div style='color: {color}; font-size: 0.75rem; font-weight: 600;'>{status}</div>
            </div>
            
            <div style='display: flex; justify-content: space-between; margin-bottom: 0.5rem;'>
                <div>
                    <div style='color: #A0A0A0; font-size: 0.75rem;'>Current</div>
                    <div style='color: white; font-size: 1.5rem; font-weight: 700;'>{current_value}{unit}</div>
                </div>
                <div style='text-align: right;'>
                    <div style='color: #A0A0A0; font-size: 0.75rem;'>Target</div>
                    <div style='color: white; font-size: 1.5rem; font-weight: 700;'>{target_value}{unit}</div>
                </div>
            </div>
            
            <div style='width: 100%; background: rgba(0, 0, 0, 0.3); border-radius: 10px; height: 8px; overflow: hidden;'>
                <div style='width: {min(percentage, 100)}%; 
                            background: {color}; 
                            height: 100%;
                            border-radius: 10px;
                            transition: width 0.5s ease;'></div>
            </div>
            
            <div style='color: {color}; font-size: 0.75rem; margin-top: 0.5rem; text-align: right;'>
                {percentage:.1f}% of target
            </div>
        </div>
    """, unsafe_allow_html=True)


# ============================================
# ALERTS COMPONENT
# ============================================

def create_alert(
    title: str,
    message: str,
    alert_type: str = "info",
    icon: Optional[str] = None,
    dismissible: bool = True,
    action_label: Optional[str] = None,
    action_key: Optional[str] = None
):
    """
    Create alert notification
    
    Args:
        title: Alert title
        message: Alert message
        alert_type: "success", "info", "warning", "error", "critical"
        icon: Custom emoji icon
        dismissible: Whether alert can be dismissed
        action_label: Label for action button
        action_key: Unique key for action button
    """
    # Alert configurations
    alert_configs = {
        "success": {
            "color": "#06D6A0",
            "bg": "rgba(6, 214, 160, 0.1)",
            "border": "rgba(6, 214, 160, 0.3)",
            "icon": icon or "✅"
        },
        "info": {
            "color": "#00B4D8",
            "bg": "rgba(0, 180, 216, 0.1)",
            "border": "rgba(0, 180, 216, 0.3)",
            "icon": icon or "ℹ️"
        },
        "warning": {
            "color": "#FFD60A",
            "bg": "rgba(255, 214, 10, 0.1)",
            "border": "rgba(255, 214, 10, 0.3)",
            "icon": icon or "⚠️"
        },
        "error": {
            "color": "#EF476F",
            "bg": "rgba(239, 71, 111, 0.1)",
            "border": "rgba(239, 71, 111, 0.3)",
            "icon": icon or "❌"
        },
        "critical": {
            "color": "#EF476F",
            "bg": "rgba(239, 71, 111, 0.2)",
            "border": "rgba(239, 71, 111, 0.5)",
            "icon": icon or "🚨"
        }
    }
    
    config = alert_configs.get(alert_type, alert_configs["info"])
    
    # Create unique key for dismiss button
    dismiss_key = f"dismiss_{hash(title + message)}"
    
    # Check if alert was dismissed
    if dismiss_key in st.session_state and st.session_state[dismiss_key]:
        return
    
    # Render alert
    alert_col1, alert_col2 = st.columns([20, 1])
    
    with alert_col1:
        st.markdown(f"""
            <div style='background: {config["bg"]};
                        padding: 1.25rem;
                        border-radius: 12px;
                        border-left: 4px solid {config["color"]};
                        border: 1px solid {config["border"]};
                        margin-bottom: 1rem;'>
                
                <div style='display: flex; align-items: start; gap: 1rem;'>
                    <div style='font-size: 1.5rem; line-height: 1;'>{config["icon"]}</div>
                    <div style='flex: 1;'>
                        <div style='color: {config["color"]}; 
                                    font-weight: 700; 
                                    font-size: 1rem; 
                                    margin-bottom: 0.5rem;'>
                            {title}
                        </div>
                        <div style='color: rgba(255, 255, 255, 0.8); 
                                    font-size: 0.9rem; 
                                    line-height: 1.5;'>
                            {message}
                        </div>
                    </div>
                </div>
            </div>
        """, unsafe_allow_html=True)
    
    with alert_col2:
        if dismissible:
            if st.button("✕", key=dismiss_key, help="Dismiss alert"):
                st.session_state[dismiss_key] = True
                st.rerun()
    
    # Action button if provided
    if action_label and action_key:
        if st.button(action_label, key=action_key, type="primary"):
            return True
    
    return False


def create_alert_banner(
    message: str,
    alert_type: str = "info",
    icon: Optional[str] = None,
    link_text: Optional[str] = None,
    link_url: Optional[str] = None
):
    """
    Create full-width banner alert (for critical notifications)
    
    Args:
        message: Alert message
        alert_type: "success", "info", "warning", "error", "critical"
        icon: Custom emoji icon
        link_text: Optional link text
        link_url: Optional link URL
    """
    alert_configs = {
        "success": {"color": "#06D6A0", "bg": "rgba(6, 214, 160, 0.2)", "icon": icon or "✅"},
        "info": {"color": "#00B4D8", "bg": "rgba(0, 180, 216, 0.2)", "icon": icon or "ℹ️"},
        "warning": {"color": "#FFD60A", "bg": "rgba(255, 214, 10, 0.2)", "icon": icon or "⚠️"},
        "error": {"color": "#EF476F", "bg": "rgba(239, 71, 111, 0.2)", "icon": icon or "❌"},
        "critical": {"color": "#EF476F", "bg": "rgba(239, 71, 111, 0.3)", "icon": icon or "🚨"}
    }
    
    config = alert_configs.get(alert_type, alert_configs["info"])
    
    link_html = ""
    if link_text and link_url:
        link_html = f"""
            <a href='{link_url}' 
               style='color: {config["color"]}; 
                      text-decoration: underline; 
                      margin-left: 1rem;
                      font-weight: 600;'>
                {link_text} →
            </a>
        """
    
    st.markdown(f"""
        <div style='background: {config["bg"]};
                    padding: 1rem 2rem;
                    border-radius: 8px;
                    border: 2px solid {config["color"]};
                    margin-bottom: 1.5rem;
                    text-align: center;'>
            <span style='font-size: 1.2rem; margin-right: 0.5rem;'>{config["icon"]}</span>
            <span style='color: white; font-size: 1rem; font-weight: 600;'>{message}</span>
            {link_html}
        </div>
    """, unsafe_allow_html=True)


def create_notification_panel(notifications: List[Dict]):
    """
    Create expandable notification panel with multiple alerts
    
    Args:
        notifications: List of notification dicts with keys: title, message, type, timestamp, priority
    """
    # Sort by priority (critical first)
    priority_order = {"critical": 0, "error": 1, "warning": 2, "info": 3, "success": 4}
    sorted_notifications = sorted(
        notifications, 
        key=lambda x: priority_order.get(x.get("type", "info"), 5)
    )
    
    # Count by type
    counts = {
        "critical": sum(1 for n in notifications if n.get("type") == "critical"),
        "error": sum(1 for n in notifications if n.get("type") == "error"),
        "warning": sum(1 for n in notifications if n.get("type") == "warning"),
        "info": sum(1 for n in notifications if n.get("type") == "info"),
    }
    
    # Header with counts
    st.markdown(f"""
        <div style='background: rgba(45, 45, 45, 0.5);
                    padding: 1rem 1.5rem;
                    border-radius: 12px 12px 0 0;
                    border: 1px solid rgba(255, 255, 255, 0.1);
                    display: flex;
                    justify-content: space-between;
                    align-items: center;'>
            <div style='color: white; font-weight: 600; font-size: 1.1rem;'>
                🔔 Notifications ({len(notifications)})
            </div>
            <div style='display: flex; gap: 1rem; font-size: 0.85rem;'>
                {f'<span style="color: #EF476F;">🚨 {counts["critical"]}</span>' if counts["critical"] > 0 else ''}
                {f'<span style="color: #EF476F;">❌ {counts["error"]}</span>' if counts["error"] > 0 else ''}
                {f'<span style="color: #FFD60A;">⚠️ {counts["warning"]}</span>' if counts["warning"] > 0 else ''}
                {f'<span style="color: #00B4D8;">ℹ️ {counts["info"]}</span>' if counts["info"] > 0 else ''}
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    # Notifications container
    with st.container():
        for idx, notification in enumerate(sorted_notifications):
            with st.expander(
                f"{notification.get('title', 'Notification')} - {notification.get('timestamp', 'Now')}",
                expanded=(idx < 2)  # Expand first 2 by default
            ):
                create_alert(
                    title=notification.get("title", "Notification"),
                    message=notification.get("message", ""),
                    alert_type=notification.get("type", "info"),
                    dismissible=False
                )


def create_stats_grid(stats: List[Dict]):
    """
    Create grid of small stat cards
    
    Args:
        stats: List of dicts with keys: label, value, icon, color
    """
    cols = st.columns(len(stats))
    
    for idx, (col, stat) in enumerate(zip(cols, stats)):
        with col:
            color = stat.get("color", "#00B4D8")
            st.markdown(f"""
                <div style='background: rgba(45, 45, 45, 0.5);
                            padding: 1rem;
                            border-radius: 8px;
                            border-top: 3px solid {color};
                            text-align: center;'>
                    <div style='font-size: 2rem; margin-bottom: 0.5rem;'>{stat.get("icon", "📊")}</div>
                    <div style='color: white; font-size: 1.5rem; font-weight: 700; margin-bottom: 0.25rem;'>
                        {stat.get("value", "0")}
                    </div>
                    <div style='color: #A0A0A0; font-size: 0.75rem; text-transform: uppercase;'>
                        {stat.get("label", "Metric")}
                    </div>
                </div>
            """, unsafe_allow_html=True)


# ============================================
# EXAMPLE USAGE
# ============================================

if __name__ == "__main__":
    st.title("KPI Cards & Alerts Demo")
    
    # KPI Cards Demo
    st.header("📊 KPI Cards")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        create_kpi_card(
            label="Arrival Accuracy",
            value="94.2%",
            delta="+3.2%",
            icon="🎯",
            help_text="Percentage within 4-hour window",
            trend_data=[88, 89, 91, 90, 92, 94.2]
        )
    
    with col2:
        create_kpi_card(
            label="Wait Time",
            value="2.1 hrs",
            delta="-0.6 hrs",
            delta_color="inverse",
            icon="⏱️",
            trend_data=[3.2, 3.0, 2.8, 2.5, 2.3, 2.1]
        )
    
    with col3:
        create_kpi_card(
            label="Carbon Saved",
            value="1,245 t",
            delta="+285 t",
            icon="🌱",
            trend_data=[800, 900, 1000, 1100, 1200, 1245]
        )
    
    st.divider()
    
    # Comparison KPIs
    st.header("📈 Comparison KPIs")
    
    comp_col1, comp_col2 = st.columns(2)
    
    with comp_col1:
        create_comparison_kpi(
            label="Berth Utilization",
            current_value=87.3,
            target_value=85.0,
            unit="%",
            icon="⚓",
            inverse=False
        )
    
    with comp_col2:
        create_comparison_kpi(
            label="Average Emissions",
            current_value=745,
            target_value=850,
            unit=" tonnes",
            icon="🌱",
            inverse=True
        )
    
    st.divider()
    
    # Alerts Demo
    st.header("🔔 Alerts")
    
    create_alert_banner(
        message="System maintenance scheduled for tonight 23:00-01:00 SGT",
        alert_type="warning",
        link_text="View Details",
        link_url="#"
    )
    
    create_alert(
        title="Bunching Detected",
        message="3 vessels scheduled to arrive at Terminal 4 within 2-hour window. Recommend staggering arrivals.",
        alert_type="warning",
        action_label="View Details",
        action_key="bunching_action"
    )
    
    create_alert(
        title="Optimization Complete",
        message="Carbon optimization saved 45 tonnes CO₂ this week. Great work!",
        alert_type="success"
    )
    
    create_alert(
        title="Weather Advisory",
        message="Strong winds expected at Rotterdam tomorrow. 3 vessels may be affected.",
        alert_type="info"
    )
    
    st.divider()
    
    # Notification Panel Demo
    st.header("📋 Notification Panel")
    
    sample_notifications = [
        {
            "title": "Critical: System Error",
            "message": "Database connection lost. Attempting reconnection...",
            "type": "critical",
            "timestamp": "2 min ago"
        },
        {
            "title": "Vessel Delay",
            "message": "MSC Diana delayed by 2 hours due to port congestion",
            "type": "warning",
            "timestamp": "15 min ago"
        },
        {
            "title": "Optimization Applied",
            "message": "Berth schedule optimized - 12% efficiency gain",
            "type": "success",
            "timestamp": "1 hour ago"
        },
        {
            "title": "Weather Update",
            "message": "Forecast updated for next 48 hours",
            "type": "info",
            "timestamp": "2 hours ago"
        }
    ]
    
    create_notification_panel(sample_notifications)
    
    st.divider()
    
    # Stats Grid Demo
    st.header("📊 Stats Grid")
    
    stats = [
        {"label": "Active Vessels", "value": "45", "icon": "🚢", "color": "#0066CC"},
        {"label": "Available Berths", "value": "8", "icon": "⚓", "color": "#06D6A0"},
        {"label": "Pending Arrivals", "value": "12", "icon": "⏳", "color": "#FFD60A"},
        {"label": "Alerts", "value": "3", "icon": "⚠️", "color": "#EF476F"}
    ]
    
    create_stats_grid(stats)
