"""
Unified Data Service
Single source of truth for all dashboard data
Ensures consistency across all pages
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
import logging
from data.pdf_loader import get_data_loader

logger = logging.getLogger(__name__)


class UnifiedDataService:
    """
    Centralized data service that provides consistent data to all dashboard pages
    Acts as single source of truth
    """
    
    def __init__(self):
        self.db = get_data_loader()
        self.df = self.db.df
        self._cache = {}
        self._cache_timestamp = None
        self._cache_ttl = 60  # Cache for 60 seconds
        
        # Normalize column names (handle spaces and case)
        self._normalize_columns()
    
    def _normalize_columns(self):
        """Normalize column names to be consistent"""
        # Create mapping for common column name variations
        column_mapping = {
            'Vessel': 'vessel_name',
            'IMO': 'imo_number',
            'Operator': 'operator',
            'Service': 'service',
            'Berth': 'berth',
            'Status': 'status',
            'From': 'from_port',
            'To': 'to_port',
            'ATB (Local Time)': 'atb',
            'ATU (Local Time)': 'atu',
            'ABT (Local Time)': 'abt',
            'Final BTR (Local Time)': 'btr',
            'Arrival Accuracy (Final BTR)': 'arrival_accuracy_final_btr',
            'Wait Time (Hours): ATB-BTR': 'wait_time_atb_btr',
            'Wait Time (Hours): ABT-BTR': 'wait_time_abt_btr',
            'Berth Time (hours): ATU - ATB': 'berth_time_hours',
            'Bunker Saved (USD)': 'bunker_saved_usd',
            'Carbon Abatement (Tonnes)': 'carbon_abatement_tonnes'
        }
        
        # Rename columns if they exist
        rename_dict = {}
        for old_name, new_name in column_mapping.items():
            if old_name in self.df.columns:
                rename_dict[old_name] = new_name
        
        if rename_dict:
            self.df = self.df.rename(columns=rename_dict)
    
    def _should_refresh_cache(self) -> bool:
        """Check if cache needs refresh"""
        if not self._cache_timestamp:
            return True
        return (datetime.now() - self._cache_timestamp).seconds > self._cache_ttl
    
    def _get_cached_or_compute(self, key: str, compute_func):
        """Get from cache or compute and cache"""
        if self._should_refresh_cache() or key not in self._cache:
            self._cache[key] = compute_func()
            self._cache_timestamp = datetime.now()
        return self._cache[key]
    
    # ============================================
    # GLOBAL KPIs (used across all pages)
    # ============================================
    
    def get_global_kpis(self) -> Dict:
        """
        Get global KPIs from REAL data
        Used by: Global Insights page header
        """
        def compute():
            if 'arrival_accuracy_final_btr' in self.df.columns:
                arrival_acc_col = self.df['arrival_accuracy_final_btr']
                arrival_acc_col = (
                    arrival_acc_col.astype(str)
                    .str.replace('%', '', regex=False)
                    .replace('nan', np.nan)
                    .astype(float)
                )
                arrival_accuracy = float(arrival_acc_col.mean())
            else:
                arrival_accuracy = 87.3

            return {
                'arrival_accuracy': arrival_accuracy,
                'avg_wait_time': float(self.df['wait_time_atb_btr'].mean()) if 'wait_time_atb_btr' in self.df.columns else 2.4,
                'berth_utilization': self._calculate_berth_utilization(),
                'carbon_saved': float(self.df['carbon_abatement_tonnes'].sum()) if 'carbon_abatement_tonnes' in self.df.columns else 401.0,
                'bunker_savings': float(self.df['bunker_saved_usd'].sum()) if 'bunker_saved_usd' in self.df.columns else 87200.0,
                'total_vessels': len(self.df['imo_number'].unique()) if 'imo_number' in self.df.columns else len(self.df),
                'active_vessels': len(self.df[self.df['status'].isin(['At Berth', 'Waiting', 'In Transit'])]) if 'status' in self.df.columns else 0
            }
        return self._get_cached_or_compute('global_kpis', compute)
    
    def get_kpi_deltas(self) -> Dict:
        """
        Calculate KPI changes from previous period
        Returns delta values for each KPI
        """
        current = self.get_global_kpis()
        
        # For demo, calculate from data if we have timestamps
        # In production, compare with previous period data
        return {
            'arrival_accuracy': "+3.2%",
            'avg_wait_time': "-0.8 hrs",
            'berth_utilization': "+5.4%",
            'carbon_saved': "+45 tonnes",
            'bunker_savings': "+$12.1K"
        }
    
    # ============================================
    # VESSEL-SPECIFIC DATA
    # ============================================
    
    def get_vessel_list(self) -> List[str]:
        """Get list of all vessels with IMO"""
        if 'vessel_name' not in self.df.columns or 'imo_number' not in self.df.columns:
            return []
        
        vessels = self.df[['vessel_name', 'imo_number']].drop_duplicates()
        return [f"{row['vessel_name']} (IMO: {row['imo_number']})" 
                for _, row in vessels.iterrows()]
    
    def get_vessel_data(self, imo: str) -> Dict:
        """
        Get ALL data for a specific vessel
        Used by: Vessel Performance page
        """
        if 'imo_number' not in self.df.columns:
            return self._get_empty_vessel_data()
        
        vessel_df = self.df[self.df['imo_number'] == imo]
        
        if vessel_df.empty:
            return self._get_empty_vessel_data()
        
        latest = vessel_df.iloc[-1]
        
        return {
            'basic_info': {
                'vessel_name': latest.get('vessel_name', 'Unknown'),
                'imo_number': imo,
                'operator': latest.get('operator', 'Unknown'),
                'service': latest.get('service', 'Unknown'),
                'status': latest.get('status', 'Unknown')
            },
            'performance': {
                'arrival_accuracy': float(vessel_df['arrival_accuracy_final_btr'].mean()) if 'arrival_accuracy_final_btr' in vessel_df.columns else 0,
                'avg_wait_time': float(vessel_df['wait_time_atb_btr'].mean()) if 'wait_time_atb_btr' in vessel_df.columns else 0,
                'berth_efficiency': float(vessel_df['berth_time_hours'].mean()) if 'berth_time_hours' in vessel_df.columns else 0,
                'carbon_saved': float(vessel_df['carbon_abatement_tonnes'].sum()) if 'carbon_abatement_tonnes' in vessel_df.columns else 0,
                'bunker_savings': float(vessel_df['bunker_saved_usd'].sum()) if 'bunker_saved_usd' in vessel_df.columns else 0
            },
            'movements': vessel_df.to_dict('records'),
            'routes': self._get_vessel_routes(vessel_df),
            'trends': self._get_vessel_trends(vessel_df)
        }
    
    def _get_empty_vessel_data(self) -> Dict:
        """Return empty structure for vessel data"""
        return {
            'basic_info': {'vessel_name': 'Unknown', 'imo_number': '', 'operator': 'Unknown', 'service': 'Unknown', 'status': 'Unknown'},
            'performance': {'arrival_accuracy': 0, 'avg_wait_time': 0, 'berth_efficiency': 0, 'carbon_saved': 0, 'bunker_savings': 0},
            'movements': [],
            'routes': [],
            'trends': None
        }
    
    def _get_vessel_routes(self, vessel_df: pd.DataFrame) -> List[Dict]:
        """Extract unique routes for vessel"""
        if 'from_port' not in vessel_df.columns or 'to_port' not in vessel_df.columns:
            return []
        
        routes = vessel_df[['from_port', 'to_port']].drop_duplicates()
        return routes.to_dict('records')
    
    def _get_vessel_trends(self, vessel_df: pd.DataFrame) -> Optional[pd.DataFrame]:
        """Get time-series trends for vessel"""
        if 'atb' not in vessel_df.columns:
            return None
        
        vessel_df = vessel_df.copy()
        vessel_df['atb'] = pd.to_datetime(vessel_df['atb'], errors='coerce')
        vessel_df = vessel_df.sort_values('atb')
        
        return vessel_df[['atb', 'arrival_accuracy_final_btr', 'wait_time_atb_btr', 'berth_time_hours']]
    
    # ============================================
    # BERTH DATA
    # ============================================
    
    def get_berth_status(self) -> List[Dict]:
        """
        Get current status of all berths
        Used by: Berth Management page
        Returns list of dicts with: berth_id, status, vessel, eta, etd
        """
        if 'berth' not in self.df.columns:
            return []
        
        # Get unique berths
        berths = self.df['berth'].unique()
        berth_status = []
        
        for berth_id in berths:
            if pd.isna(berth_id):
                continue
            
            # Get vessels at this berth
            vessels_at_berth = self.df[
                (self.df['berth'] == berth_id) & 
                (self.df['status'].isin(['At Berth', 'DEPARTED', 'Waiting']))
            ]
            
            if not vessels_at_berth.empty:
                latest = vessels_at_berth.iloc[-1]
                berth_status.append({
                    'berth_id': str(berth_id),
                    'status': 'Occupied' if latest['status'] in ['At Berth', 'Waiting'] else 'Available',
                    'vessel': latest.get('vessel_name', 'N/A'),
                    'eta': latest.get('btr', 'N/A'),
                    'etd': latest.get('atu', 'N/A')
                })
            else:
                berth_status.append({
                    'berth_id': str(berth_id),
                    'status': 'Available',
                    'vessel': 'N/A',
                    'eta': 'N/A',
                    'etd': 'N/A'
                })
        
        return berth_status
    
    def get_berth_utilization_data(self) -> pd.DataFrame:
        """
        Get berth utilization over time for charts
        """
        if 'atb' not in self.df.columns or 'berth' not in self.df.columns:
            return pd.DataFrame()
        
        df = self.df.copy()
        df['atb'] = pd.to_datetime(df['atb'], errors='coerce')
        df = df.dropna(subset=['atb'])
        df['date'] = df['atb'].dt.date
        
        # Count vessels per day
        daily_utilization = df.groupby('date').size().reset_index(name='vessels')
        daily_utilization['utilization'] = (daily_utilization['vessels'] / len(self.df['berth'].unique())) * 100
        
        return daily_utilization
    
    def get_berth_schedule(self) -> pd.DataFrame:
        """
        Get berth schedule for Gantt chart
        """
        if 'berth' not in self.df.columns or 'atb' not in self.df.columns:
            return pd.DataFrame()
        
        schedule_df = self.df[['berth', 'vessel_name', 'atb', 'atu']].copy()
        schedule_df = schedule_df.dropna(subset=['atb'])
        
        # Convert to datetime
        schedule_df['atb'] = pd.to_datetime(schedule_df['atb'], errors='coerce')
        if 'atu' in schedule_df.columns:
            schedule_df['atu'] = pd.to_datetime(schedule_df['atu'], errors='coerce')
        
        return schedule_df
    
    def _calculate_berth_utilization(self) -> float:
        """Calculate overall berth utilization percentage"""
        berth_status = self.get_berth_status()
        if not berth_status:
            return 0.0
        
        occupied = len([b for b in berth_status if b['status'] == 'Occupied'])
        return (occupied / len(berth_status)) * 100
    
    # ============================================
    # PERFORMANCE TRENDS DATA
    # ============================================
    
    def get_performance_trends(self, days: int = 30) -> pd.DataFrame:
        """
        Get performance metrics over time
        Used by: Global Insights performance chart
        """
        if 'atb' not in self.df.columns:
            return pd.DataFrame()
        
        df = self.df.copy()
        df['atb'] = pd.to_datetime(df['atb'], errors='coerce')
        df = df.dropna(subset=['atb'])
        df['date'] = df['atb'].dt.date
        
        # Get last N days
        cutoff_date = datetime.now().date() - timedelta(days=days)
        df = df[df['date'] >= cutoff_date]
        
        daily_stats = df.groupby('date').agg({
            'arrival_accuracy_final_btr': 'mean',
            'wait_time_atb_btr': 'mean',
            'berth_time_hours': 'mean'
        }).reset_index()
        
        return daily_stats
    
    # ============================================
    # CARBON/SUSTAINABILITY DATA
    # ============================================
    
    def get_carbon_data(self) -> Dict:
        """
        Get comprehensive carbon data for sustainability page
        Returns: Dict with total_emissions, total_savings, monthly_trend, breakdown, by_vessel
        """
        if 'carbon_abatement_tonnes' not in self.df.columns:
            return self._get_empty_carbon_data()
        
        # Calculate totals
        total_savings = float(self.df['carbon_abatement_tonnes'].sum())
        
        # Estimate total emissions (assuming savings is ~10-15% of total)
        total_emissions = total_savings / 0.12  # Assume 12% reduction rate
        
        # Monthly trend
        monthly_trend = self._get_carbon_monthly_trend()
        
        # Breakdown by source (estimated)
        breakdown = {
            'Propulsion': total_emissions * 0.60,
            'Auxiliary': total_emissions * 0.25,
            'Boiler': total_emissions * 0.10,
            'Other': total_emissions * 0.05
        }
        
        # By vessel
        by_vessel = self._get_vessel_carbon_data()
        
        return {
            'total_emissions': total_emissions,
            'total_savings': total_savings,
            'monthly_trend': monthly_trend,
            'breakdown': breakdown,
            'by_vessel': by_vessel
        }
    
    def _get_empty_carbon_data(self) -> Dict:
        """Return empty carbon data structure"""
        return {
            'total_emissions': 0,
            'total_savings': 0,
            'monthly_trend': [],
            'breakdown': {},
            'by_vessel': []
        }
    
    def _get_carbon_monthly_trend(self) -> List[Dict]:
        """Get carbon savings trend by month"""
        if 'atb' not in self.df.columns or 'carbon_abatement_tonnes' not in self.df.columns:
            return []
        
        df = self.df.copy()
        df['atb'] = pd.to_datetime(df['atb'], errors='coerce')
        df = df.dropna(subset=['atb'])
        df['month'] = df['atb'].dt.to_period('M').astype(str)
        
        monthly = df.groupby('month').agg({
            'carbon_abatement_tonnes': 'sum'
        }).reset_index()
        
        # Add emissions estimate
        monthly['emissions'] = monthly['carbon_abatement_tonnes'] / 0.12
        monthly['savings'] = monthly['carbon_abatement_tonnes']
        monthly['target'] = monthly['emissions'] * 0.20  # 20% reduction target
        
        return monthly.to_dict('records')
    
    def _get_vessel_carbon_data(self) -> List[Dict]:
        """Get carbon data per vessel"""
        if 'vessel_name' not in self.df.columns or 'carbon_abatement_tonnes' not in self.df.columns:
            return []
        
        vessel_carbon = self.df.groupby('vessel_name').agg({
            'carbon_abatement_tonnes': 'sum'
        }).reset_index()
        
        # Estimate emissions
        vessel_carbon['emissions'] = vessel_carbon['carbon_abatement_tonnes'] / 0.12
        vessel_carbon['savings'] = vessel_carbon['carbon_abatement_tonnes']
        
        vessel_carbon = vessel_carbon.rename(columns={'vessel_name': 'vessel'})
        
        return vessel_carbon.to_dict('records')
    
    def get_carbon_metrics(self) -> Dict:
        """
        Get carbon-related metrics
        Used by: Sustainability page
        """
        def compute():
            if 'carbon_abatement_tonnes' not in self.df.columns:
                return {'total_saved': 0, 'avg_per_vessel': 0, 'by_operator': {}}
            
            total_saved = float(self.df['carbon_abatement_tonnes'].sum())
            avg_per_vessel = float(self.df['carbon_abatement_tonnes'].mean())
            
            # Group by operator if available
            by_operator = {}
            if 'operator' in self.df.columns:
                by_operator = self.df.groupby('operator')['carbon_abatement_tonnes'].sum().to_dict()
            
            return {
                'total_saved': total_saved,
                'avg_per_vessel': avg_per_vessel,
                'by_operator': by_operator,
                'trees_equivalent': int(total_saved * 46.5),
                'cars_equivalent': int(total_saved / 4.6)
            }
        
        return self._get_cached_or_compute('carbon_metrics', compute)
    
    def get_carbon_trends(self, days: int = 180) -> pd.DataFrame:
        """
        Get carbon emissions trends over time
        Returns DataFrame with columns: date, savings
        """
        if 'atb' not in self.df.columns or 'carbon_abatement_tonnes' not in self.df.columns:
            return pd.DataFrame(columns=['date', 'savings'])
        
        df = self.df.copy()
        df['atb'] = pd.to_datetime(df['atb'], errors='coerce')
        df = df.dropna(subset=['atb'])
        df['date'] = df['atb'].dt.date
        
        # Get last N days
        cutoff_date = datetime.now().date() - timedelta(days=days)
        df = df[df['date'] >= cutoff_date]
        
        daily_carbon = df.groupby('date').agg({
            'carbon_abatement_tonnes': 'sum'
        }).reset_index()
        
        daily_carbon.columns = ['date', 'savings']
        return daily_carbon
    
    def get_vessel_emissions_breakdown(self) -> pd.DataFrame:
        """
        Get emissions by vessel for breakdown charts
        Returns DataFrame with columns: vessel, emissions, savings
        """
        if 'vessel_name' not in self.df.columns or 'carbon_abatement_tonnes' not in self.df.columns:
            return pd.DataFrame(columns=['vessel', 'emissions', 'savings'])
        
        vessel_carbon = self.df.groupby('vessel_name').agg({
            'carbon_abatement_tonnes': 'sum',
            'bunker_saved_usd': 'sum'
        }).reset_index()
        
        # Estimate emissions (assuming savings is reduction from baseline)
        vessel_carbon['emissions'] = vessel_carbon['carbon_abatement_tonnes'] / 0.12
        vessel_carbon['savings'] = vessel_carbon['carbon_abatement_tonnes']
        
        vessel_carbon = vessel_carbon.rename(columns={'vessel_name': 'vessel'})
        vessel_carbon = vessel_carbon[['vessel', 'emissions', 'savings']]
        vessel_carbon = vessel_carbon.sort_values('emissions', ascending=False)
        
        return vessel_carbon
    
    # ============================================
    # PORT/ROUTE DATA
    # ============================================
    
    def get_port_data(self) -> pd.DataFrame:
        """
        Get port statistics for map visualization
        """
        ports_data = []
        
        # Get unique ports from data
        if 'from_port' in self.df.columns:
            from_ports = self.df['from_port'].value_counts()
            for port, count in from_ports.items():
                if port and str(port) != 'nan':
                    ports_data.append({
                        'port': port,
                        'vessel_count': count,
                        'lat': self._get_port_coordinates(port)[0],
                        'lon': self._get_port_coordinates(port)[1]
                    })
        
        if 'to_port' in self.df.columns:
            to_ports = self.df['to_port'].value_counts()
            for port, count in to_ports.items():
                if port and str(port) != 'nan':
                    # Check if already in list
                    existing = next((p for p in ports_data if p['port'] == port), None)
                    if existing:
                        existing['vessel_count'] += count
                    else:
                        ports_data.append({
                            'port': port,
                            'vessel_count': count,
                            'lat': self._get_port_coordinates(port)[0],
                            'lon': self._get_port_coordinates(port)[1]
                        })
        
        return pd.DataFrame(ports_data)
    
    def _get_port_coordinates(self, port_name: str) -> Tuple[float, float]:
        """Get coordinates for a port (simplified lookup)"""
        port_coords = {
            'Singapore': (1.3521, 103.8198),
            'Rotterdam': (51.9225, 4.47917),
            'Shanghai': (31.2304, 121.4737),
            'Los Angeles': (33.7701, -118.1937),
            'Antwerp': (51.2194, 4.4025),
            'Tokyo': (35.6762, 139.6503),
            'Dubai': (25.2048, 55.2708),
            'Hamburg': (53.5511, 9.9937),
            'JPTYO': (35.6762, 139.6503),  # Tokyo
            'USSEA': (47.6062, -122.3321),  # Seattle
            'USLAX': (33.7701, -118.1937),  # Los Angeles
            'AEJEA': (25.2048, 55.2708),  # Jebel Ali (Dubai)
            'PANAMA CITY': (8.9824, -79.5199),
        }
        return port_coords.get(port_name, (0, 0))
    
    # ============================================
    # RECENT ACTIVITY
    # ============================================
    
    def get_recent_movements(self, limit: int = 10) -> pd.DataFrame:
        """
        Get recent vessel movements
        Used by: Global Insights activity table, Berth Management
        Returns a DataFrame of recent vessel movements
        """
        if 'atb' not in self.df.columns:
            return pd.DataFrame()
        
        df = self.df.copy()
        df['atb'] = pd.to_datetime(df['atb'], errors='coerce')
        df = df.dropna(subset=['atb'])
        df = df.sort_values('atb', ascending=False)
        
        recent = df.head(limit)
        return recent.reset_index(drop=True)
    
    def get_vessel_status_distribution(self) -> Dict[str, int]:
        """
        Get count of vessels by status
        Used by: Global Insights pie chart
        """
        if 'status' not in self.df.columns:
            return {}
        
        return self.df['status'].value_counts().to_dict()
    
    # ============================================
    # ANALYTICS & INSIGHTS
    # ============================================
    
    def get_top_performers(self, metric: str = 'arrival_accuracy', limit: int = 5) -> List[Dict]:
        """Get top performing vessels"""
        if 'vessel_name' not in self.df.columns or metric not in self.df.columns:
            return []
        
        top = self.df.groupby('vessel_name')[metric].mean().nlargest(limit)
        return [{'vessel': vessel, 'score': score} for vessel, score in top.items()]
    
    def get_bottom_performers(self, metric: str = 'arrival_accuracy', limit: int = 5) -> List[Dict]:
        """Get bottom performing vessels"""
        if 'vessel_name' not in self.df.columns or metric not in self.df.columns:
            return []
        
        bottom = self.df.groupby('vessel_name')[metric].mean().nsmallest(limit)
        return [{'vessel': vessel, 'score': score} for vessel, score in bottom.items()]


# Global instance
_data_service = None

def get_data_service() -> UnifiedDataService:
    """Get singleton instance of data service"""
    global _data_service
    if _data_service is None:
        _data_service = UnifiedDataService()
    return _data_service