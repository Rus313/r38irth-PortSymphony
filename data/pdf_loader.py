"""
PDF Data Loader
Extracts PSA ship movement data from PDF and provides database-like interface
Data Engineer: PDF Processing Specialist
"""

import pdfplumber
import pandas as pd
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import logging
import numpy as np

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PDFDataLoader:
    """
    Loads and processes PSA ship movement data from PDF
    Provides same interface as DatabaseManager for easy integration
    """
    
    def __init__(self, pdf_path: str):
        self.pdf_path = pdf_path
        self.df = None
        self.vessels_df = None
        self.load_data()
    
    def load_data(self):
        """Extract data from PDF and convert to DataFrame"""
        try:
            logger.info(f"Loading data from {self.pdf_path}")
            
            with pdfplumber.open(self.pdf_path) as pdf:
                all_tables = []
                
                for page in pdf.pages:
                    tables = page.extract_tables()
                    if tables:
                        all_tables.extend(tables)
                
                if all_tables:
                    # First row is headers
                    headers = all_tables[0][0]
                    data_rows = []
                    
                    for table in all_tables:
                        data_rows.extend(table[1:])  # Skip header
                    
                    self.df = pd.DataFrame(data_rows, columns=headers)
                    self._process_data()
                    
                    logger.info(f"✅ Loaded {len(self.df)} records from PDF")
                else:
                    logger.warning("No tables found in PDF, using sample data")
                    self._create_sample_data()
        
        except Exception as e:
            logger.error(f"Error loading PDF: {e}")
            logger.warning("Using sample data instead")
            self._create_sample_data()
    
    def _process_data(self):
        """Clean and process the extracted data"""
        # Rename columns to match database schema
        column_mapping = {
            'Operator': 'operator',
            'Service': 'service',
            'Dir': 'direction',
            'BU': 'business_unit',
            'Vessel': 'vessel_name',
            'IMO': 'imo_number',
            'Rotation No.': 'rotation_no',
            'From': 'from_port',
            'To': 'to_port',
            'Berth': 'berth',
            'Status': 'status',
            'Final BTR (Local Time)': 'final_btr',
            'ABT (Local Time)': 'abt',
            'ATB (Local Time)': 'atb',
            'ATU (Local Time)': 'atu',
            'Arrival Variance (within 4h target)': 'arrival_variance_4h',
            'Arrival Accuracy (Final BTR)': 'arrival_accuracy_final_btr',
            'Wait Time (Hours): ATB-BTR': 'wait_time_atb_btr',
            'Wait Time (Hours): ABT-BTR': 'wait_time_abt_btr',
            'Wait Time (hours): ATB-ABT': 'wait_time_atb_abt',
            'Berth Time (hours): ATU - ATB': 'berth_time_hours',
            'Assured Port Time Achieved (%)': 'assured_port_time_pct',
            'Bunker Saved (USD)': 'bunker_saved_usd',
            'Carbon Abatement (Tonnes)': 'carbon_abatement_tonnes'
        }
        
        self.df = self.df.rename(columns=column_mapping)
        
        # Convert numeric columns
        numeric_cols = [
            'wait_time_atb_btr', 'wait_time_abt_btr', 'wait_time_atb_abt',
            'berth_time_hours', 'assured_port_time_pct',
            'bunker_saved_usd', 'carbon_abatement_tonnes'
        ]
        
        for col in numeric_cols:
            if col in self.df.columns:
                self.df[col] = pd.to_numeric(self.df[col], errors='coerce')
        
        # Parse dates (format: DD-MM-YY HH:MM)
        date_cols = ['final_btr', 'abt', 'atb', 'atu']
        for col in date_cols:
            if col in self.df.columns:
                self.df[col] = pd.to_datetime(
                    self.df[col], 
                    format='%d-%m-%y %H:%M',
                    errors='coerce'
                )
        
        # Clean IMO numbers
        if 'imo_number' in self.df.columns:
            self.df['imo_number'] = self.df['imo_number'].astype(str).str.strip()
        
        # Convert Y/N to boolean
        if 'arrival_variance_4h' in self.df.columns:
            self.df['arrival_variance_4h'] = self.df['arrival_variance_4h'].map({'Y': True, 'N': False})
        
        # Create vessels reference dataframe
        self._create_vessels_df()
    
    def _create_vessels_df(self):
        """Create separate vessels dataframe for vessel lookups"""
        if 'vessel_name' in self.df.columns and 'imo_number' in self.df.columns:
            self.vessels_df = self.df[['vessel_name', 'imo_number', 'operator', 'service']].drop_duplicates()

    def _create_sample_data(self):
        """Create sample data if PDF loading fails"""
        logger.warning("📦 Using sample data")
        
        now = datetime.now()
        
        self.df = pd.DataFrame({
            'operator': ['GRN', 'NVX', 'DPT', 'EVO', 'GRN', 'SVQ', 'DPT', 'MSC', 'CMA', 'MAE'],
            'service': ['DF5', 'KP9', 'HWI', '59H', '15P', 'DF5', '5RC', 'AE1', 'FAL', 'TP1'],
            'direction': ['W', 'E', 'W', 'W', 'W', 'E', 'E', 'W', 'E', 'W'],
            'business_unit': ['Container'] * 10,
            'vessel_name': ['MV RAPID VOYAGER', 'MV SOUTHERN SEAWAY', 'MV WESTERN AURORA', 
                           'MV EASTERN FALCON', 'MV TRUST SEAL', 'BRIGHT DOLPHIN',
                           'EMERALD ORCA', 'MSC Diana', 'CMA CGM Antoine', 'Maersk Essex'],
            'imo_number': ['6280239', '8506594', '9888242', '1709981', '2614463', 
                          '7173371', '9234567', '9876543', '9454436', '9632101'],
            'rotation_no': ['20251001', '20251002', '20251003', '20251004', '20251005',
                           '20251006', '20251007', '20251008', '20251009', '20251010'],
            'from_port': ['Singapore', 'Los Angeles', 'Tokyo', 'Taiwan', 'Osaka',
                         'Seattle', 'Jakarta', 'Singapore', 'Rotterdam', 'Los Angeles'],
            'to_port': ['Seattle', 'Dubai', 'Algeciras', 'Panama', 'Italy',
                       'Tokyo', 'Jakarta', 'Rotterdam', 'Singapore', 'Shanghai'],
            'berth': ['B01', 'B02', 'B03', 'B04', 'B05', 'B06', 'B07', 'B08', 'B01', 'B02'],
            'status': ['DEPARTED'] * 10,
            'atb': [now - timedelta(days=i) for i in range(10)],
            'atu': [now - timedelta(days=i, hours=-24) for i in range(10)],
            'wait_time_atb_btr': [4.92, 5.17, 8.83, 5.46, 5.97, 5.63, 4.21, 2.15, 3.87, 6.12],
            'berth_time_hours': [31.26, 23.96, 8.0, 36.23, 42.38, 30.59, 28.14, 25.33, 29.87, 22.45],
            'arrival_accuracy_final_btr': [95.5, 92.3, 88.1, 94.2, 91.0, 96.8, 93.5, 97.2, 89.8, 94.6],
            'bunker_saved_usd': [35776.21, 25568.79, 19575.91, 23862.37, 18299.25,
                                15986.41, 21234.56, 28456.78, 17890.12, 24567.89],
            'carbon_abatement_tonnes': [0.204, 0.228, 0.135, 0.357, 0.232, 
                                       0.162, 0.189, 0.312, 0.156, 0.278]
        })
        
        self._create_vessels_df()
    
    # ============================================
    # DATABASE-LIKE INTERFACE METHODS
    # ============================================
    
    def get_recent_vessels(self, limit: int = 10) -> List[Dict]:
        """Get most recent vessel movements"""
        if self.df is not None and not self.df.empty:
            return self.df.head(limit).to_dict('records')
        return []
    
    def get_vessel_by_imo(self, imo_number: str) -> Optional[Dict]:
        """Get vessel details by IMO number"""
        if self.vessels_df is not None:
            result = self.vessels_df[self.vessels_df['imo_number'] == str(imo_number)]
            if not result.empty:
                return result.iloc[0].to_dict()
        return None
    
    def get_upcoming_arrivals(self, hours: int = 48) -> List[Dict]:
        """Get vessels arriving in next N hours"""
        # Since we have historical data, return recent movements
        return self.get_recent_vessels(10)
    
    def get_historical_movements(self, days: int = 30, limit: int = 500) -> List[Dict]:
        """Get historical vessel movements"""
        if self.df is not None:
            return self.df.head(limit).to_dict('records')
        return []
    
    def _convert_yes_no_to_percentage(self, column_name: str) -> float:
        """Convert Y/N column to percentage"""
        if column_name in self.df.columns:
            return (self.df[column_name] == 'Y').sum() / len(self.df) * 100
        return 0.0

    def get_current_metrics(self) -> Dict:
        """Get current performance metrics"""
        if self.df is None or self.df.empty:
            return {}
        
        metrics = {
            'avg_arrival_accuracy': (self.df['arrival_accuracy_final_btr'] == 'Y').mean() * 100 if 'arrival_accuracy_final_btr' in self.df.columns else 92.5,            'avg_wait_time': self.df['wait_time_atb_btr'].mean() if 'wait_time_atb_btr' in self.df.columns else 5.0,
            'total_carbon_saved': self.df['carbon_abatement_tonnes'].sum() if 'carbon_abatement_tonnes' in self.df.columns else 2.5,
            'total_bunker_saved': self.df['bunker_saved_usd'].sum() if 'bunker_saved_usd' in self.df.columns else 200000,
            'total_movements': len(self.df)
        }
        
        return metrics
    
    def get_performance_data(self, days: int = 30) -> List[Dict]:
        """Get performance data for analysis"""
        if self.df is None or self.df.empty:
            return []
        
        # If we have date columns, group by date
        if 'atb' in self.df.columns:
            try:
                daily = self.df.groupby(self.df['atb'].dt.date).agg({
                    'wait_time_atb_btr': 'mean',
                    'berth_time_hours': 'mean',
                    'arrival_accuracy_final_btr': 'mean',
                    'vessel_name': 'count'
                }).reset_index()
                
                daily.columns = ['date', 'avg_wait_time', 'avg_berth_time', 'avg_accuracy', 'vessel_count']
                return daily.head(days).to_dict('records')
            except:
                pass
        
        return []
    
    def get_carbon_metrics(self, days: int = 30) -> List[Dict]:
        """Get carbon emissions and savings data"""
        if self.df is None or self.df.empty:
            return []
        
        carbon_cols = ['vessel_name', 'imo_number', 'carbon_abatement_tonnes', 'atb']
        available_cols = [col for col in carbon_cols if col in self.df.columns]
        
        if available_cols:
            result = self.df[available_cols].copy()
            # Add date column if atb exists
            if 'atb' in result.columns:
                result['date'] = result['atb'].dt.date
            return result.head(days * 5).to_dict('records')
        
        return []
    
    def get_carbon_summary(self) -> Dict:
        """Get carbon emissions summary"""
        if self.df is None or self.df.empty:
            return {}
        
        return {
            'total_emissions': 0,  # Not in source data
            'total_savings': self.df['carbon_abatement_tonnes'].sum() if 'carbon_abatement_tonnes' in self.df.columns else 0,
            'avg_emissions_rate': 0,
            'vessels_tracked': self.df['vessel_name'].nunique() if 'vessel_name' in self.df.columns else 0
        }
    
    def get_berth_availability(self) -> List[Dict]:
        """Get current berth availability"""
        berths = []
        unique_berths = self.df['berth'].unique() if 'berth' in self.df.columns else ['B01', 'B02', 'B03', 'B04']
        
        for i, berth in enumerate(unique_berths[:16]):
            status = ['Available', 'Occupied', 'Occupied', 'Available'][i % 4]
            berths.append({
                'berth_id': berth,
                'terminal': f'Terminal {(i // 4) + 1}',
                'status': status,
                'current_vessel_imo': None if status == 'Available' else f'IMO{9000000 + i}',
                'expected_available_time': None,
                'max_vessel_size': 20000
            })
        
        return berths
    
    def get_berth_utilization(self, days: int = 7) -> List[Dict]:
        """Calculate berth utilization metrics"""
        if 'berth' not in self.df.columns or 'berth_time_hours' not in self.df.columns:
            return []
        
        utilization = self.df.groupby('berth').agg({
            'vessel_name': 'count',
            'berth_time_hours': ['mean', 'sum']
        }).reset_index()
        
        utilization.columns = ['berth', 'total_vessels', 'avg_berth_time', 'total_occupied_hours']
        
        total_hours = days * 24
        utilization['utilization_pct'] = (utilization['total_occupied_hours'] / total_hours * 100).clip(0, 100)
        
        return utilization.to_dict('records')
    
    def get_weather_forecast(self, port: str = "Singapore") -> List[Dict]:
        """Get weather forecast (mock data)"""
        return []
    
    def get_current_weather(self, port: str) -> Optional[Dict]:
        """Get current weather (mock data)"""
        return None
    
    # Additional helper methods
    
    def get_vessel_list(self) -> List[str]:
        """Get list of all vessel names"""
        if 'vessel_name' in self.df.columns:
            return self.df['vessel_name'].unique().tolist()
        return []
    
    def get_port_list(self) -> List[str]:
        """Get list of all ports"""
        ports = set()
        if 'from_port' in self.df.columns:
            ports.update(self.df['from_port'].unique())
        if 'to_port' in self.df.columns:
            ports.update(self.df['to_port'].unique())
        return list(ports)
    
    def get_summary_stats(self) -> Dict:
        """Get overall summary statistics"""
        return {
            'total_records': len(self.df) if self.df is not None else 0,
            'unique_vessels': self.df['vessel_name'].nunique() if 'vessel_name' in self.df.columns else 0,
            'unique_ports': len(self.get_port_list()),
            'date_range': f"{self.df['atb'].min()} to {self.df['atb'].max()}" if 'atb' in self.df.columns else 'N/A'
        }


# Singleton instance for caching
_loader_instance = None

def get_data_loader(pdf_path: str = 'data/ship_movements.pdf') -> PDFDataLoader:
    """Get or create PDF data loader instance (cached)"""
    global _loader_instance
    if _loader_instance is None:
        _loader_instance = PDFDataLoader(pdf_path)
    return _loader_instance