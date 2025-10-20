"""
Centralized Demo Dataset
Single source of fake data used by both dashboard AND AI chatbot
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta

class DemoDataset:
    """
    All fake data in one place
    Used by both visualizations and AI chatbot for consistency
    """
    
    def __init__(self):
        # Set random seed for reproducibility
        np.random.seed(42)
        
        # Generate all datasets
        self.vessels = self._generate_vessels()
        self.movements = self._generate_movements()
        self.berths = self._generate_berths()
        self.performance = self._generate_performance()
        self.carbon = self._generate_carbon()
        self.ports = self._generate_ports()
        
    def _generate_vessels(self) -> pd.DataFrame:
        """Generate vessel master data"""
        return pd.DataFrame({
            'vessel_name': [
                'MSC Diana', 'Ever Given', 'CMA CGM Antoine', 'Maersk Essex',
                'COSCO Shipping', 'Hapag-Lloyd Berlin', 'ONE Innovation', 
                'Yang Ming Excellence', 'MSC Mediterranean', 'CMA CGM Paris',
                'Maersk Tokyo', 'ONE Harmony', 'MSK Melbourne'
            ],
            'imo_number': [
                '9876543', '9811000', '9454436', '9632101', '9793241',
                '9234567', '9345678', '9456789', '9567890', '9678901',
                '9789012', '9890123', '9901234'
            ],
            'operator': [
                'MSC', 'Evergreen', 'CMA CGM', 'Maersk', 'COSCO',
                'Hapag-Lloyd', 'ONE', 'Yang Ming', 'MSC', 'CMA CGM',
                'Maersk', 'ONE', 'Maersk'
            ],
            'service': [
                'Asia-Europe', 'Far East-Europe', 'Asia-Med', 'Trans-Pacific', 'Asia-US',
                'Europe-Asia', 'Trans-Pacific', 'Asia-Europe', 'Med-Asia', 'Europe-Asia',
                'Trans-Pacific', 'Asia-Europe', 'Trans-Pacific'
            ],
            'status': [
                'At Berth', 'In Transit', 'Waiting', 'Departed', 'In Transit',
                'At Berth', 'At Berth', 'Waiting', 'In Transit', 'Waiting',
                'In Transit', 'Waiting', 'At Berth'
            ]
        })
    
    def _generate_movements(self) -> pd.DataFrame:
        """Generate ship movements with consistent values"""
        dates = pd.date_range(end=datetime.now(), periods=30, freq='D')
        
        data = []
        for i, date in enumerate(dates):
            for j in range(3):  # 3 movements per day
                vessel_idx = (i * 3 + j) % len(self.vessels)
                data.append({
                    'date': date,
                    'vessel_name': self.vessels.iloc[vessel_idx]['vessel_name'],
                    'imo_number': self.vessels.iloc[vessel_idx]['imo_number'],
                    'operator': self.vessels.iloc[vessel_idx]['operator'],
                    'service': self.vessels.iloc[vessel_idx]['service'],
                    'from_port': np.random.choice(['Singapore', 'Rotterdam', 'Shanghai', 'Los Angeles', 'Antwerp']),
                    'to_port': np.random.choice(['Singapore', 'Rotterdam', 'Shanghai', 'Los Angeles', 'Antwerp']),
                    'berth': f'B{np.random.randint(1, 17):02d}',
                    'atb': date + timedelta(hours=np.random.randint(0, 23)),
                    'atu': date + timedelta(hours=np.random.randint(24, 48)),
                    'wait_time_atb_btr': round(np.random.uniform(0.5, 6.0), 2),
                    'berth_time_hours': round(np.random.uniform(18, 36), 2),
                    'arrival_accuracy_final_btr': round(np.random.uniform(85, 100), 1),
                    'carbon_abatement_tonnes': round(np.random.uniform(8, 50), 2),
                    'bunker_saved_usd': round(np.random.uniform(10000, 25000), 2),
                    'status': 'DEPARTED'
                })
        
        return pd.DataFrame(data)
    
    def _generate_berths(self) -> pd.DataFrame:
        """Generate berth availability data"""
        berths = []
        terminals = ['Terminal 1', 'Terminal 2', 'Terminal 3', 'Terminal 4']
        
        # Specific berths with specific statuses for consistency
        berth_configs = [
            {'id': 1, 'status': 'Available', 'vessel_idx': None},
            {'id': 2, 'status': 'Occupied', 'vessel_idx': 0},  # MSC Diana
            {'id': 3, 'status': 'Occupied', 'vessel_idx': 1},  # Ever Given
            {'id': 4, 'status': 'Available', 'vessel_idx': None},
            {'id': 5, 'status': 'Occupied', 'vessel_idx': 2},  # CMA CGM Antoine
            {'id': 6, 'status': 'Maintenance', 'vessel_idx': None},
            {'id': 7, 'status': 'Available', 'vessel_idx': None},
            {'id': 8, 'status': 'Occupied', 'vessel_idx': 3},  # Maersk Essex
            {'id': 9, 'status': 'Occupied', 'vessel_idx': 4},  # COSCO Shipping
            {'id': 10, 'status': 'Occupied', 'vessel_idx': 5},  # Hapag-Lloyd
            {'id': 11, 'status': 'Available', 'vessel_idx': None},
            {'id': 12, 'status': 'Occupied', 'vessel_idx': 6},  # ONE Innovation
            {'id': 13, 'status': 'Occupied', 'vessel_idx': 7},  # Yang Ming
            {'id': 14, 'status': 'Available', 'vessel_idx': None},
            {'id': 15, 'status': 'Occupied', 'vessel_idx': 8},  # MSK Melbourne
            {'id': 16, 'status': 'Available', 'vessel_idx': None},
        ]
        
        for config in berth_configs:
            i = config['id']
            berths.append({
                'berth_id': f'B{i:02d}',
                'terminal': terminals[(i-1) // 4],
                'status': config['status'],
                'current_vessel_imo': self.vessels.iloc[config['vessel_idx']]['imo_number'] if config['vessel_idx'] is not None else None,
                'max_vessel_size': [15000, 18000, 20000, 22000][(i-1) % 4],
                'max_draft': [14.0, 15.5, 16.0, 17.0][(i-1) % 4]
            })
        
        return pd.DataFrame(berths)
    
    def _generate_performance(self) -> pd.DataFrame:
        """Generate performance metrics over time"""
        dates = pd.date_range(end=datetime.now(), periods=60, freq='D')
        
        # Create trending data (improving over time)
        base_accuracy = 85
        base_wait = 3.5
        base_util = 75
        
        return pd.DataFrame({
            'date': dates,
            'avg_arrival_accuracy': np.linspace(base_accuracy, 92, 60) + np.random.normal(0, 2, 60),
            'avg_wait_time': np.linspace(base_wait, 2.1, 60) + np.random.normal(0, 0.3, 60),
            'berth_utilization': np.linspace(base_util, 82, 60) + np.random.normal(0, 3, 60),
            'vessels_count': np.random.randint(40, 50, 60),
            'on_time_performance': np.linspace(80, 90, 60) + np.random.normal(0, 2, 60)
        })
    
    def _generate_carbon(self) -> pd.DataFrame:
        """Generate carbon metrics"""
        dates = pd.date_range(end=datetime.now(), periods=180, freq='D')
        
        # Emissions decreasing over time
        baseline_emissions = 1000
        reduction = np.linspace(0, 250, 180)
        
        return pd.DataFrame({
            'date': dates,
            'total_emissions': (baseline_emissions - reduction) + np.random.normal(0, 30, 180),
            'carbon_saved': reduction + np.random.normal(0, 15, 180),
            'baseline': baseline_emissions,
            'target': 750
        })
    
    def _generate_ports(self) -> pd.DataFrame:
        """Generate port location data"""
        return pd.DataFrame({
            'port_name': ['Singapore', 'Rotterdam', 'Shanghai', 'Los Angeles', 'Antwerp'],
            'latitude': [1.3521, 51.9225, 31.2304, 33.7701, 51.2194],
            'longitude': [103.8198, 4.47917, 121.4737, -118.1937, 4.4025],
            'country': ['Singapore', 'Netherlands', 'China', 'USA', 'Belgium'],
            'vessel_count': [45, 32, 38, 28, 25]
        })
    
    # ============================================
    # API-like methods (same as DatabaseManager)
    # ============================================
    
    def get_current_metrics(self) -> dict:
        """Get current KPI metrics"""
        latest_perf = self.performance.iloc[-1]
        total_carbon = self.carbon['carbon_saved'].tail(30).sum()
        total_bunker = self.movements.tail(30)['bunker_saved_usd'].sum()
        
        return {
            'avg_arrival_accuracy': float(latest_perf['avg_arrival_accuracy']),
            'avg_wait_time': float(latest_perf['avg_wait_time']),
            'berth_utilization': float(latest_perf['berth_utilization']),
            'total_carbon_saved': float(total_carbon),
            'total_bunker_saved': float(total_bunker),
            'total_movements': len(self.movements)
        }
    
    def get_recent_vessels(self, limit: int = 10) -> list:
        """Get recent vessel movements"""
        return self.movements.tail(limit).to_dict('records')
    
    def get_berth_availability(self) -> list:
        """Get berth status"""
        return self.berths.to_dict('records')
    
    def get_performance_data(self, days: int = 30) -> list:
        """Get performance trend data"""
        return self.performance.tail(days).to_dict('records')
    
    def get_carbon_metrics(self, days: int = 30) -> list:
        """Get carbon data"""
        carbon_data = self.carbon.tail(days).copy()
        
        # Add vessel association
        result = []
        for i, row in carbon_data.iterrows():
            vessel_idx = i % len(self.vessels)
            result.append({
                'date': row['date'],
                'vessel_name': self.vessels.iloc[vessel_idx]['vessel_name'],
                'imo_number': self.vessels.iloc[vessel_idx]['imo_number'],
                'total_emissions': row['total_emissions'],
                'carbon_saved': row['carbon_saved']
            })
        
        return result
    
    def get_carbon_summary(self) -> dict:
        """Get carbon summary"""
        total_saved = self.carbon['carbon_saved'].sum()
        
        return {
            'total_emissions': 0,
            'total_savings': float(total_saved),
            'avg_emissions_rate': 0,
            'vessels_tracked': len(self.vessels)
        }
    
    def get_berth_utilization(self, days: int = 7) -> list:
        """Calculate berth utilization"""
        berth_stats = []
        
        for berth_id in self.berths['berth_id'].unique():
            berth_movements = self.movements[self.movements['berth'] == berth_id].tail(days * 3)
            
            total_hours = berth_movements['berth_time_hours'].sum() if not berth_movements.empty else 0
            avg_time = berth_movements['berth_time_hours'].mean() if not berth_movements.empty else 0
            
            berth_stats.append({
                'berth': berth_id,
                'total_vessels': len(berth_movements),
                'avg_berth_time': float(avg_time),
                'total_occupied_hours': float(total_hours),
                'utilization_pct': float(min(total_hours / (days * 24) * 100, 100))
            })
        
        return berth_stats
    
    def get_vessel_list(self) -> list:
        """Get list of all vessel names"""
        return self.vessels['vessel_name'].tolist()
    
    def get_port_list(self) -> list:
        """Get list of all ports"""
        ports = set()
        ports.update(self.movements['from_port'].unique())
        ports.update(self.movements['to_port'].unique())
        return list(ports)
    
    def get_summary_stats(self) -> dict:
        """Get overall summary statistics"""
        return {
            'total_records': len(self.movements),
            'unique_vessels': len(self.vessels),
            'unique_ports': len(self.get_port_list()),
            'date_range': f"{self.movements['date'].min().strftime('%Y-%m-%d')} to {self.movements['date'].max().strftime('%Y-%m-%d')}"
        }
    
    def get_upcoming_arrivals(self, hours: int = 48) -> list:
        """Get upcoming vessel arrivals (simulated)"""
        # For demo, return some waiting vessels
        waiting_vessels = self.vessels[self.vessels['status'] == 'Waiting']
        
        result = []
        for i, vessel in waiting_vessels.iterrows():
            eta = datetime.now() + timedelta(hours=np.random.randint(2, hours))
            result.append({
                'vessel_name': vessel['vessel_name'],
                'imo_number': vessel['imo_number'],
                'operator': vessel['operator'],
                'from_port': np.random.choice(['Singapore', 'Rotterdam', 'Shanghai']),
                'to_port': 'Singapore',
                'berth': f'B{np.random.randint(1, 17):02d}',
                'eta': eta.strftime('%Y-%m-%d %H:%M'),
                'status': 'In Transit'
            })
        
        return result
    
    def get_historical_movements(self, days: int = 30, limit: int = 500) -> list:
        """Get historical vessel movements"""
        return self.movements.tail(min(limit, len(self.movements))).to_dict('records')
    
    def get_weather_forecast(self, port: str = "Singapore") -> list:
        """Get weather forecast (mock data)"""
        return []
    
    def get_current_weather(self, port: str) -> dict:
        """Get current weather (mock data)"""
        return None


# ============================================
# Global instance
# ============================================

_demo_dataset = None

def get_demo_dataset():
    """Get or create demo dataset instance"""
    global _demo_dataset
    if _demo_dataset is None:
        _demo_dataset = DemoDataset()
    return _demo_dataset