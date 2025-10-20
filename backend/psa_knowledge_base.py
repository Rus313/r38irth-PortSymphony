"""
PSA Maritime Operations Knowledge Base
Domain-specific rules, thresholds, and operational knowledge
"""

# ============================================
# PERFORMANCE THRESHOLDS
# ============================================

PERFORMANCE_THRESHOLDS = {
    "wait_time": {
        "excellent": (0, 2),      # 0-2 hours: Excellent
        "good": (2, 4),           # 2-4 hours: Good
        "concerning": (4, 6),     # 4-6 hours: Concerning
        "critical": (6, float('inf'))  # >6 hours: Critical
    },
    "arrival_accuracy": {
        "excellent": (95, 100),   # 95-100%: Excellent
        "good": (90, 95),         # 90-95%: Good
        "needs_improvement": (85, 90),  # 85-90%: Needs improvement
        "poor": (0, 85)           # <85%: Poor
    },
    "berth_utilization": {
        "optimal": (75, 85),      # 75-85%: Optimal
        "underutilized": (0, 75), # <75%: Underutilized
        "congested": (85, 100)    # >85%: Risk of congestion
    },
    "carbon_performance": {
        "excellent": (20, float('inf')),  # >20% reduction: Excellent
        "good": (15, 20),                  # 15-20%: Good
        "acceptable": (10, 15),            # 10-15%: Acceptable
        "poor": (0, 10)                    # <10%: Poor
    }
}

# ============================================
# BERTH CHARACTERISTICS
# ============================================

BERTH_CHARACTERISTICS = {
    "B01": {
        "terminal": "Terminal 1",
        "type": "container",
        "capacity": "large",
        "max_vessel_size": 20000,
        "max_draft": 16.0,
        "equipment": "4 gantry cranes"
    },
    "B02": {
        "terminal": "Terminal 1",
        "type": "container",
        "capacity": "large",
        "max_vessel_size": 20000,
        "max_draft": 16.0,
        "equipment": "4 gantry cranes"
    },
    "B03": {
        "terminal": "Terminal 2",
        "type": "container",
        "capacity": "medium",
        "max_vessel_size": 18000,
        "max_draft": 15.5,
        "equipment": "3 gantry cranes"
    },
    "B04": {
        "terminal": "Terminal 2",
        "type": "container",
        "capacity": "medium",
        "max_vessel_size": 18000,
        "max_draft": 15.5,
        "equipment": "3 gantry cranes"
    },
    "B05": {
        "terminal": "Terminal 3",
        "type": "container",
        "capacity": "large",
        "max_vessel_size": 22000,
        "max_draft": 17.0,
        "equipment": "5 gantry cranes"
    },
    "B06": {
        "terminal": "Terminal 3",
        "type": "container",
        "capacity": "large",
        "max_vessel_size": 22000,
        "max_draft": 17.0,
        "equipment": "5 gantry cranes"
    },
    "B07": {
        "terminal": "Terminal 4",
        "type": "container",
        "capacity": "small",
        "max_vessel_size": 15000,
        "max_draft": 14.0,
        "equipment": "2 gantry cranes"
    },
    "B08": {
        "terminal": "Terminal 4",
        "type": "container",
        "capacity": "small",
        "max_vessel_size": 15000,
        "max_draft": 14.0,
        "equipment": "2 gantry cranes"
    }
}

# ============================================
# OPERATIONAL INSIGHTS
# ============================================

OPERATIONAL_INSIGHTS = {
    "peak_hours": "08:00-12:00 and 14:00-18:00 local time",
    "average_berth_time": "24 hours",
    "turnaround_target": "18-20 hours",
    "wait_time_target": "< 2 hours",
    "arrival_accuracy_target": "> 90%",
    "berth_utilization_target": "75-85%",
    "carbon_reduction_target": "15-20% annually",
    "port_capacity": "24 berths across 4 terminals",
    "typical_vessel_size": "15,000-22,000 TEU",
    "average_vessels_per_day": "45-60"
}

# ============================================
# STAKEHOLDER CONTEXT
# ============================================

STAKEHOLDER_PROFILES = {
    "top_management": {
        "focus": ["KPIs", "ROI", "strategic impact", "cost savings", "efficiency gains"],
        "language": "high-level, strategic, percentage-based",
        "interests": ["overall performance", "trends", "benchmarks", "competitive advantage"]
    },
    "middle_management": {
        "focus": ["operational efficiency", "resource allocation", "process optimization", "team performance"],
        "language": "tactical, actionable, metric-driven",
        "interests": ["bottlenecks", "improvement opportunities", "capacity planning"]
    },
    "frontline_operations": {
        "focus": ["immediate actions", "specific vessels", "berth assignments", "schedule adherence"],
        "language": "direct, specific, actionable",
        "interests": ["current status", "next steps", "problem resolution", "real-time updates"]
    }
}

# ============================================
# INTERPRETATION FUNCTIONS
# ============================================

def interpret_wait_time(hours: float) -> dict:
    """
    Interpret wait time with industry context
    
    Args:
        hours: Wait time in hours
        
    Returns:
        Dictionary with interpretation details
    """
    for level, (min_val, max_val) in PERFORMANCE_THRESHOLDS["wait_time"].items():
        if min_val <= hours < max_val:
            icons = {
                "excellent": "✅",
                "good": "✅", 
                "concerning": "⚠️",
                "critical": "🚨"
            }
            
            messages = {
                "excellent": f"Wait time of {hours:.1f} hours is excellent - well below the 2-hour target",
                "good": f"Wait time of {hours:.1f} hours is acceptable but trending toward target limit",
                "concerning": f"Wait time of {hours:.1f} hours exceeds target (2 hours) - attention needed",
                "critical": f"Wait time of {hours:.1f} hours is CRITICAL - immediate action required"
            }
            
            return {
                "level": level,
                "icon": icons[level],
                "message": messages[level],
                "action_needed": level in ["concerning", "critical"],
                "severity": level
            }
    
    return {"level": "unknown", "icon": "❓", "message": "Wait time data unavailable"}


def interpret_arrival_accuracy(accuracy: float) -> dict:
    """
    Interpret arrival accuracy with industry benchmarks
    
    Args:
        accuracy: Arrival accuracy percentage (0-100)
        
    Returns:
        Dictionary with interpretation details
    """
    for level, (min_val, max_val) in PERFORMANCE_THRESHOLDS["arrival_accuracy"].items():
        if min_val <= accuracy <= max_val:
            icons = {
                "excellent": "✅",
                "good": "✅",
                "needs_improvement": "⚠️",
                "poor": "🔴"
            }
            
            messages = {
                "excellent": f"Arrival accuracy of {accuracy:.1f}% is excellent - exceeding 95% target",
                "good": f"Arrival accuracy of {accuracy:.1f}% is good - meeting 90% target",
                "needs_improvement": f"Arrival accuracy of {accuracy:.1f}% needs improvement - below 90% target",
                "poor": f"Arrival accuracy of {accuracy:.1f}% is poor - significantly below 90% target"
            }
            
            return {
                "level": level,
                "icon": icons[level],
                "message": messages[level],
                "action_needed": level in ["needs_improvement", "poor"],
                "severity": level
            }
    
    return {"level": "unknown", "icon": "❓", "message": "Arrival accuracy data unavailable"}


def interpret_berth_utilization(utilization: float) -> dict:
    """
    Interpret berth utilization rate
    
    Args:
        utilization: Utilization percentage (0-100)
        
    Returns:
        Dictionary with interpretation details
    """
    for level, (min_val, max_val) in PERFORMANCE_THRESHOLDS["berth_utilization"].items():
        if min_val <= utilization <= max_val:
            icons = {
                "optimal": "✅",
                "underutilized": "📉",
                "congested": "⚠️"
            }
            
            messages = {
                "optimal": f"Berth utilization of {utilization:.1f}% is optimal (target: 75-85%)",
                "underutilized": f"Berth utilization of {utilization:.1f}% indicates underutilization - opportunity to increase throughput",
                "congested": f"Berth utilization of {utilization:.1f}% is high - risk of congestion and delays"
            }
            
            return {
                "level": level,
                "icon": icons[level],
                "message": messages[level],
                "action_needed": level != "optimal",
                "severity": level
            }
    
    return {"level": "unknown", "icon": "❓", "message": "Utilization data unavailable"}


def get_recommendations_for_wait_time(wait_time: float, berth: str = None, vessel_count: int = 0) -> list:
    """
    Generate specific recommendations based on wait time
    
    Args:
        wait_time: Average wait time in hours
        berth: Specific berth (optional)
        vessel_count: Number of vessels affected
        
    Returns:
        List of actionable recommendations
    """
    recommendations = []
    berth_str = f" at {berth}" if berth else ""
    
    if wait_time > 6:
        recommendations.append(f"🚨 CRITICAL: {wait_time:.1f}h wait time{berth_str} - Expedite current operations immediately")
        recommendations.append(f"Emergency actions: Fast-track departures, consider reassignment to alternative berths")
        if vessel_count > 3:
            recommendations.append(f"Multiple vessels affected ({vessel_count}) - coordinate with port authority for emergency capacity")
    
    elif wait_time > 4:
        recommendations.append(f"⚠️ HIGH PRIORITY: {wait_time:.1f}h wait time{berth_str} - Monitor closely and accelerate operations")
        recommendations.append(f"Consider: Optimizing berth allocation, adjusting vessel arrival schedule")
        if berth:
            berth_info = BERTH_CHARACTERISTICS.get(berth, {})
            if berth_info.get('capacity') == 'small':
                recommendations.append(f"Note: {berth} has limited capacity - consider redirecting to larger berths (B01, B02, B05, B06)")
    
    elif wait_time > 2:
        recommendations.append(f"Monitor {berth if berth else 'operations'} - wait time trending above 2-hour target")
        recommendations.append(f"Preventive action: Review upcoming schedule for potential congestion")
    
    else:
        recommendations.append(f"✅ Wait time within target - maintain current operations")
    
    return recommendations


def get_recommendations_for_accuracy(accuracy: float, vessel_name: str = None) -> list:
    """
    Generate recommendations for arrival accuracy improvement
    
    Args:
        accuracy: Arrival accuracy percentage
        vessel_name: Specific vessel (optional)
        
    Returns:
        List of recommendations
    """
    recommendations = []
    vessel_str = f" for {vessel_name}" if vessel_name else ""
    
    if accuracy < 85:
        recommendations.append(f"🔴 POOR PERFORMANCE: {accuracy:.1f}% arrival accuracy{vessel_str}")
        recommendations.append(f"Root cause analysis needed: Check ETA prediction models, weather routing, communication protocols")
        recommendations.append(f"Immediate actions: Improve vessel-port communication, enhance traffic monitoring")
    
    elif accuracy < 90:
        recommendations.append(f"⚠️ BELOW TARGET: {accuracy:.1f}% arrival accuracy{vessel_str} - target is 90%+")
        recommendations.append(f"Suggestions: Review ETA calculation methods, improve weather forecast integration")
    
    elif accuracy < 95:
        recommendations.append(f"✅ GOOD: {accuracy:.1f}% arrival accuracy - slight room for improvement")
        recommendations.append(f"Fine-tuning opportunity: Optimize last-mile navigation, refine berth allocation timing")
    
    else:
        recommendations.append(f"✅ EXCELLENT: {accuracy:.1f}% arrival accuracy - maintain current practices")
    
    return recommendations


def get_recommendations_for_utilization(utilization: float) -> list:
    """
    Generate recommendations for berth utilization
    
    Args:
        utilization: Utilization percentage
        
    Returns:
        List of recommendations
    """
    recommendations = []
    
    if utilization > 90:
        recommendations.append(f"⚠️ HIGH UTILIZATION: {utilization:.1f}% - risk of congestion")
        recommendations.append(f"Actions: Implement arrival time windows, optimize turnaround times, prepare overflow plans")
        recommendations.append(f"Consider: Dynamic berth allocation, express lanes for fast turnaround vessels")
    
    elif utilization > 85:
        recommendations.append(f"⚠️ APPROACHING CAPACITY: {utilization:.1f}% utilization")
        recommendations.append(f"Monitor closely and prepare contingency plans")
    
    elif utilization < 70:
        recommendations.append(f"📉 UNDERUTILIZED: {utilization:.1f}% - opportunity to increase throughput")
        recommendations.append(f"Opportunities: Attract additional vessel calls, reduce turnaround time, optimize scheduling")
        gap = 80 - utilization
        recommendations.append(f"Potential gain: {gap:.1f}% capacity available = ~{int(gap/4)} additional vessels per day")
    
    else:
        recommendations.append(f"✅ OPTIMAL: {utilization:.1f}% utilization - maintain current balance")
    
    return recommendations


def get_berth_specific_insights(berth_id: str) -> dict:
    """
    Get specific insights about a berth
    
    Args:
        berth_id: Berth identifier (e.g., 'B02')
        
    Returns:
        Dictionary with berth characteristics and insights
    """
    berth_info = BERTH_CHARACTERISTICS.get(berth_id, {})
    
    if not berth_info:
        return {"error": f"Berth {berth_id} not found in database"}
    
    # Generate insights
    insights = {
        "id": berth_id,
        "characteristics": berth_info,
        "capabilities": f"Can handle vessels up to {berth_info.get('max_vessel_size', 0):,} TEU with max draft {berth_info.get('max_draft', 0)}m",
        "equipment": berth_info.get('equipment', 'Unknown'),
        "capacity_class": berth_info.get('capacity', 'Unknown').upper(),
        "terminal": berth_info.get('terminal', 'Unknown')
    }
    
    # Add recommendations based on capacity
    if berth_info.get('capacity') == 'large':
        insights['best_for'] = "Ultra-large container vessels (ULCV), priority shipments"
    elif berth_info.get('capacity') == 'medium':
        insights['best_for'] = "Standard container vessels, regional services"
    else:
        insights['best_for'] = "Smaller vessels, feeder services, quick turnarounds"
    
    return insights


def get_carbon_insights(carbon_saved: float, period_days: int = 30) -> dict:
    """
    Provide context on carbon savings
    
    Args:
        carbon_saved: Tonnes of CO2 saved
        period_days: Time period in days
        
    Returns:
        Dictionary with carbon insights and equivalents
    """
    # Calculate equivalents
    trees_equivalent = int(carbon_saved * 46.5)  # 1 tonne CO2 = ~46.5 trees annually
    cars_equivalent = int(carbon_saved / 4.6)     # 1 car = ~4.6 tonnes CO2/year
    
    # Calculate daily rate
    daily_rate = carbon_saved / period_days
    annual_projection = daily_rate * 365
    
    insights = {
        "carbon_saved": carbon_saved,
        "period_days": period_days,
        "equivalents": {
            "trees_planted": f"{trees_equivalent:,} trees planted",
            "cars_off_road": f"{cars_equivalent} cars off the road for a year",
            "households": f"{int(carbon_saved / 7.5)} homes' energy for a year"
        },
        "projections": {
            "daily_rate": f"{daily_rate:.1f} tonnes/day",
            "annual_projection": f"{annual_projection:.0f} tonnes/year"
        }
    }
    
    # Performance assessment
    target_reduction = 0.17  # 17% annual target (mid-range of 15-20%)
    if annual_projection >= carbon_saved * 12 * 0.20:  # 20%+ reduction
        insights['performance'] = "✅ EXCELLENT - Exceeding 20% reduction target"
    elif annual_projection >= carbon_saved * 12 * 0.15:  # 15-20% reduction
        insights['performance'] = "✅ GOOD - Meeting 15-20% reduction target"
    else:
        insights['performance'] = "⚠️ BELOW TARGET - Additional optimization needed"
    
    return insights


# ============================================
# CONTEXT BUILDERS
# ============================================

def build_stakeholder_context(role: str = "middle_management") -> str:
    """
    Build context prompt based on stakeholder role
    
    Args:
        role: Stakeholder role (top_management, middle_management, frontline_operations)
        
    Returns:
        Context string for AI prompt
    """
    profile = STAKEHOLDER_PROFILES.get(role, STAKEHOLDER_PROFILES["middle_management"])
    
    context = f"""
STAKEHOLDER CONTEXT: {role.replace('_', ' ').title()}

Focus areas: {', '.join(profile['focus'])}
Communication style: {profile['language']}
Key interests: {', '.join(profile['interests'])}

Tailor your responses accordingly.
"""
    return context