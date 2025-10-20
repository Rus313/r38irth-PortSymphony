"""
Real-time data access for dashboard interpretation
This ACTUALLY reads your data, not hardcoded
"""

import pandas as pd
from typing import Dict, List, Any
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class DashboardDataAccess:
    """
    Provides REAL data to the AI agent
    """
    
    def __init__(self, db_manager):
        self.db = db_manager
    
    def get_current_state(self) -> Dict[str, Any]:
        """
        Get ACTUAL current dashboard state
        This is what the AI "sees"
        """
        try:
            # Get REAL data from database/PDF
            recent_vessels = self.db.get_recent_vessels(limit=100)
            performance_metrics = self.db.get_current_metrics()
            berth_status = self.db.get_berth_availability()
            
            # Convert to AI-readable format
            state = {
                "timestamp": datetime.now().isoformat(),
                "vessels": {
                    "total_count": len(recent_vessels),
                    "by_status": self._group_by_status(recent_vessels),
                    "by_berth": self._group_by_berth(recent_vessels),
                    "recent_movements": [
                        {
                            "vessel_name": v.get('vessel_name'),
                            "berth": v.get('berth'),
                            "status": v.get('status'),
                            "wait_time": v.get('wait_time_atb_btr'),
                            "arrival_time": str(v.get('atb'))
                        }
                        for v in recent_vessels[:10]
                    ]
                },
                "performance": {
                    "avg_arrival_accuracy": float(performance_metrics.get('avg_arrival_accuracy', 0)),
                    "avg_wait_time": float(performance_metrics.get('avg_wait_time', 0)),
                    "total_carbon_saved": float(performance_metrics.get('total_carbon_saved', 0)),
                    "total_movements": int(performance_metrics.get('total_movements', 0))
                },
                "berths": {
                    "available": [b['berth_id'] for b in berth_status if b['status'] == 'Available'],
                    "occupied": [
                        {
                            "berth_id": b['berth_id'],
                            "vessel": b.get('current_vessel_imo')
                        }
                        for b in berth_status if b['status'] == 'Occupied'
                    ],
                    "total_utilization": self._calculate_utilization(berth_status)
                }
            }
            
            logger.info(f"Dashboard state captured: {len(recent_vessels)} vessels, {len(berth_status)} berths")
            return state
            
        except Exception as e:
            logger.error(f"Error getting dashboard state: {e}")
            return {"error": str(e)}
    
    def filter_data(self, filters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute ACTUAL database query based on AI's filter request
        
        Example filters:
        {
            "berth": "B02",
            "time_window_hours": 3,
            "status": "Delayed",
            "vessel_name": "MSC Diana"
        }
        """
        try:
            # Get base data
            all_vessels = self.db.get_recent_vessels(limit=1000)
            
            # Convert to DataFrame for easier filtering
            df = pd.DataFrame(all_vessels)
            
            if df.empty:
                return {"count": 0, "data": [], "summary": {}}
            
            # Apply filters
            if 'berth' in filters and filters['berth']:
                df = df[df['berth'] == filters['berth']]
            
            if 'time_window_hours' in filters:
                cutoff_time = datetime.now() - timedelta(hours=int(filters['time_window_hours']))
                if 'atb' in df.columns:
                    df['atb'] = pd.to_datetime(df['atb'])
                    df = df[df['atb'] >= cutoff_time]
            
            if 'status' in filters and filters['status']:
                df = df[df['status'] == filters['status']]
            
            if 'vessel_name' in filters and filters['vessel_name']:
                df = df[df['vessel_name'].str.contains(filters['vessel_name'], case=False, na=False)]
            
            # Calculate summary statistics
            summary = {
                "count": len(df),
                "avg_wait_time": float(df['wait_time_atb_btr'].mean()) if 'wait_time_atb_btr' in df.columns and not df.empty else 0,
                "max_wait_time": float(df['wait_time_atb_btr'].max()) if 'wait_time_atb_btr' in df.columns and not df.empty else 0,
                "total_carbon_saved": float(df['carbon_abatement_tonnes'].sum()) if 'carbon_abatement_tonnes' in df.columns and not df.empty else 0,
                "delayed_count": len(df[df['wait_time_atb_btr'] > 4]) if 'wait_time_atb_btr' in df.columns else 0
            }
            
            # Convert to records (limit to 50 for API response size)
            records = df.head(50).to_dict('records')
            
            # Clean up the records for JSON serialization
            for record in records:
                for key, value in record.items():
                    if pd.isna(value):
                        record[key] = None
                    elif isinstance(value, (pd.Timestamp, datetime)):
                        record[key] = str(value)
            
            result = {
                "count": len(df),
                "data": records,
                "summary": summary,
                "filters_applied": filters
            }
            
            logger.info(f"Filtered data: {len(df)} records matching {filters}")
            return result
            
        except Exception as e:
            logger.error(f"Error filtering data: {e}")
            return {"error": str(e), "count": 0, "data": []}
    
    def analyze_delays(self, berth: str = None, time_period: str = "24h") -> Dict[str, Any]:
        """
        Analyze delay patterns and root causes
        """
        try:
            # Parse time period
            hours = int(time_period.replace('h', ''))
            
            filters = {"time_window_hours": hours}
            if berth:
                filters["berth"] = berth
            
            filtered_data = self.filter_data(filters)
            
            if filtered_data['count'] == 0:
                return {
                    "total_delays": 0,
                    "message": f"No delays found for {berth if berth else 'any berth'} in last {hours} hours"
                }
            
            df = pd.DataFrame(filtered_data['data'])
            
            # Identify delays (wait time > 2 hours is considered delay)
            if 'wait_time_atb_btr' in df.columns:
                delays = df[df['wait_time_atb_btr'] > 2]
            else:
                delays = df[df['status'] == 'Delayed'] if 'status' in df.columns else pd.DataFrame()
            
            # Analyze patterns
            analysis = {
                "total_delays": len(delays),
                "avg_delay_time": float(delays['wait_time_atb_btr'].mean()) if 'wait_time_atb_btr' in delays.columns and not delays.empty else 0,
                "worst_delays": [
                    {
                        "vessel": row['vessel_name'],
                        "berth": row['berth'],
                        "wait_time": float(row['wait_time_atb_btr'])
                    }
                    for _, row in delays.nlargest(5, 'wait_time_atb_btr').iterrows()
                ] if 'wait_time_atb_btr' in delays.columns and not delays.empty else [],
                "delays_by_berth": delays.groupby('berth').size().to_dict() if 'berth' in delays.columns and not delays.empty else {},
                "causes": self._analyze_delay_causes(delays),
                "time_period": time_period,
                "berth_analyzed": berth if berth else "All berths"
            }
            
            logger.info(f"Delay analysis: {analysis['total_delays']} delays found")
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing delays: {e}")
            return {"error": str(e)}
    
    def get_recommendations(self, focus_area: str) -> List[str]:
        """
        Generate REAL recommendations based on ACTUAL data
        """
        try:
            state = self.get_current_state()
            recommendations = []
            
            if focus_area == "delays":
                waiting_count = state['vessels']['by_status'].get('Waiting', 0)
                if waiting_count > 5:
                    recommendations.append(f"⚠️ {waiting_count} vessels currently waiting. Consider staggering arrivals.")
                
                if state['performance']['avg_wait_time'] > 3:
                    recommendations.append(f"📊 Average wait time is {state['performance']['avg_wait_time']:.1f} hours. Target is <2 hours.")
            
            elif focus_area == "utilization":
                util = state['berths']['total_utilization']
                if util < 70:
                    recommendations.append(f"📈 Berth utilization at {util:.1f}% - opportunity to increase throughput by {80-util:.1f}%")
                elif util > 90:
                    recommendations.append(f"⚠️ Berth utilization at {util:.1f}% - risk of congestion")
            
            elif focus_area == "carbon":
                total_saved = state['performance']['total_carbon_saved']
                recommendations.append(f"🌱 {total_saved:.0f} tonnes CO2 saved so far. Continue optimizing vessel speeds and routes.")
            
            elif focus_area == "efficiency":
                accuracy = state['performance']['avg_arrival_accuracy']
                if accuracy < 90:
                    recommendations.append(f"🎯 Arrival accuracy at {accuracy:.1f}%. Improve ETA predictions.")
            
            if not recommendations:
                recommendations.append("✅ Operations are running smoothly. No immediate actions needed.")
            
            logger.info(f"Generated {len(recommendations)} recommendations for {focus_area}")
            return recommendations
            
        except Exception as e:
            logger.error(f"Error generating recommendations: {e}")
            return [f"Error generating recommendations: {str(e)}"]
    
    # Helper methods
    def _group_by_status(self, vessels: List[Dict]) -> Dict[str, int]:
        """Count vessels by status"""
        status_counts = {}
        for vessel in vessels:
            status = vessel.get('status', 'Unknown')
            status_counts[status] = status_counts.get(status, 0) + 1
        return status_counts
    
    def _group_by_berth(self, vessels: List[Dict]) -> Dict[str, List[str]]:
        """Group vessels by berth"""
        berth_vessels = {}
        for vessel in vessels:
            berth = vessel.get('berth', 'Unknown')
            if berth not in berth_vessels:
                berth_vessels[berth] = []
            berth_vessels[berth].append(vessel.get('vessel_name'))
        return berth_vessels
    
    def _calculate_utilization(self, berth_status: List[Dict]) -> float:
        """Calculate ACTUAL utilization percentage"""
        if not berth_status:
            return 0.0
        
        occupied = len([b for b in berth_status if b['status'] == 'Occupied'])
        return (occupied / len(berth_status)) * 100
    
    def _analyze_delay_causes(self, delays_df: pd.DataFrame) -> List[str]:
        """Analyze ACTUAL delay causes from data"""
        if delays_df.empty:
            return ["No delays to analyze"]
        
        causes = []
        
        # Check for congestion
        if len(delays_df) > 3:
            causes.append("High vessel congestion detected")
        
        # Check for berth-specific issues
        if 'berth' in delays_df.columns:
            berth_delays = delays_df.groupby('berth').size()
            if berth_delays.max() > 2:
                worst_berth = berth_delays.idxmax()
                causes.append(f"Berth {worst_berth} has recurring delays")
        
        # Check wait times
        if 'wait_time_atb_btr' in delays_df.columns:
            avg_wait = delays_df['wait_time_atb_btr'].mean()
            if avg_wait > 4:
                causes.append("Port capacity constraints - wait times exceeding 4 hours")
        
        return causes if causes else ["Normal operational delays"]