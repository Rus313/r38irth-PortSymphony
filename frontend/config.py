"""
Frontend Configuration
Centralized configuration for UI/UX settings
"""

from dataclasses import dataclass
from typing import Dict, List

@dataclass
class PageConfig:
    """Page-level configuration"""
    PAGE_TITLE: str = "PSA Global Insights Dashboard"
    PAGE_ICON: str = "🚢"
    LAYOUT: str = "wide"
    SIDEBAR_STATE: str = "expanded"

@dataclass
class Colors:
    """Color scheme for consistent UI"""
    PRIMARY: str = "#0066CC"
    SECONDARY: str = "#00B4D8"
    SUCCESS: str = "#06D6A0"
    WARNING: str = "#FFD60A"
    DANGER: str = "#EF476F"
    INFO: str = "#00B4D8"
    
    # Chart colors
    CHART_COLORS: List[str] = None
    
    def __post_init__(self):
        self.CHART_COLORS = [
            self.PRIMARY,
            self.SECONDARY,
            self.SUCCESS,
            "#8338EC",
            "#FF006E",
            "#FB5607"
        ]

@dataclass
class DepartmentConfig:
    """Department-specific view configurations"""
    DEPARTMENTS: Dict[str, Dict] = None
    
    def __post_init__(self):
        self.DEPARTMENTS = {
            'Operations': {
                'icon': '⚙️',
                'color': Colors.PRIMARY,
                'modules': ['Vessel Performance', 'Berth Management', 'Real-time Tracking'],
                'metrics': ['arrival_accuracy', 'wait_time', 'berth_utilization']
            },
            'Sustainability': {
                'icon': '🌱',
                'color': Colors.SUCCESS,
                'modules': ['Carbon Analytics', 'Emissions Tracking', 'Optimization'],
                'metrics': ['carbon_abatement', 'bunker_saved', 'emissions_per_hour']
            },
            'Planning': {
                'icon': '📊',
                'color': Colors.INFO,
                'modules': ['Forecasting', 'Schedule Optimization', 'Resource Allocation'],
                'metrics': ['predicted_arrivals', 'berth_availability', 'capacity_utilization']
            },
            'Management': {
                'icon': '👔',
                'color': Colors.WARNING,
                'modules': ['Global Insights', 'Performance Reports', 'Strategic Analytics'],
                'metrics': ['overall_performance', 'cost_savings', 'roi']
            }
        }

@dataclass
class MetricConfig:
    """Metric display configurations"""
    METRICS: Dict[str, Dict] = None
    
    def __post_init__(self):
        self.METRICS = {
            'arrival_accuracy': {
                'label': 'Arrival Accuracy',
                'unit': '%',
                'format': '.1f',
                'icon': '🎯',
                'good_threshold': 90,
                'help_text': 'Percentage of vessels arriving within 4-hour window'
            },
            'wait_time': {
                'label': 'Avg Wait Time',
                'unit': 'hrs',
                'format': '.2f',
                'icon': '⏱️',
                'good_threshold': 2,
                'inverse': True,  # Lower is better
                'help_text': 'Average time vessels wait before berthing'
            },
            'berth_utilization': {
                'label': 'Berth Utilization',
                'unit': '%',
                'format': '.1f',
                'icon': '⚓',
                'good_threshold': 80,
                'help_text': 'Percentage of time berths are occupied'
            },
            'carbon_abatement': {
                'label': 'Carbon Abatement',
                'unit': 'tonnes',
                'format': '.2f',
                'icon': '🌱',
                'good_threshold': 100,
                'help_text': 'Total carbon emissions saved through optimization'
            },
            'bunker_saved': {
                'label': 'Bunker Savings',
                'unit': 'USD',
                'format': ',.0f',
                'icon': '💰',
                'prefix': '$',
                'good_threshold': 10000,
                'help_text': 'Cost savings from reduced bunker consumption'
            }
        }

@dataclass
class ChartConfig:
    """Chart styling and configuration"""
    DEFAULT_HEIGHT: int = 400
    DEFAULT_THEME: str = 'plotly_dark'
    
    LAYOUT_CONFIG: Dict = None
    
    def __post_init__(self):
        self.LAYOUT_CONFIG = {
            'paper_bgcolor': 'rgba(0,0,0,0)',
            'plot_bgcolor': 'rgba(0,0,0,0)',
            'font': {
                'color': '#FFFFFF',
                'family': 'Inter, sans-serif'
            },
            'margin': {'t': 60, 'b': 60, 'l': 60, 'r': 60},
            'hovermode': 'closest',
            'hoverlabel': {
                'bgcolor': '#2D2D2D',
                'font_size': 12,
                'font_family': 'Inter, sans-serif'
            }
        }

# Initialize configurations
colors = Colors()
departments = DepartmentConfig()
metrics = MetricConfig()
charts = ChartConfig()
