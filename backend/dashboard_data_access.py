import pandas as pd
from typing import Dict, List, Any
from datetime import datetime, timedelta
import logging
from data.pdf_loader import PDFDataLoader

logger = logging.getLogger(__name__)

class DashboardDataAccess:
    def __init__(self, db_manager=None):
        """
        If db_manager is None, fallback to dashboard's _create_sample_data().
        """
        if db_manager is None:
            self.db = PDFDataLoader()  # uses _create_sample_data internally
        else:
            self.db = db_manager

    # --------------------------
    # Helper to fetch sample data
    # --------------------------
    def _fetch_recent_vessels(self, limit=100) -> List[Dict[str, Any]]:
        """Return recent vessels, using _create_sample_data() fallback if necessary"""
        if hasattr(self.db, "_create_sample_data"):
            return self.db._create_sample_data()[:limit]
        elif hasattr(self.db, "get_recent_vessels"):
            return self.db.get_recent_vessels(limit=limit)
        else:
            return []

    def _fetch_current_metrics(self) -> Dict[str, Any]:
        """Return current metrics, using sample data fallback if needed"""
        if hasattr(self.db, "_create_sample_data"):
            vessels = self.db._create_sample_data()
            return {
                "avg_arrival_accuracy": 90.0,
                "avg_wait_time": sum(v.get("wait_time_atb_btr",0) for v in vessels)/len(vessels) if vessels else 0,
                "total_carbon_saved": sum(v.get("carbon_abatement_tonnes",0) for v in vessels),
                "total_movements": len(vessels)
            }
        elif hasattr(self.db, "get_current_metrics"):
            return self.db.get_current_metrics()
        else:
            return {}

    def _fetch_berth_status(self) -> List[Dict[str, Any]]:
        """Return berth status, fallback to sample data if needed"""
        if hasattr(self.db, "_create_sample_data"):
            vessels = self.db._create_sample_data()
            berths = list({v.get("berth"): "Occupied" for v in vessels if v.get("berth")} )
            return [{"berth_id": b, "status": "Occupied"} for b in berths]
        elif hasattr(self.db, "get_berth_availability"):
            return self.db.get_berth_availability()
        else:
            return []

    # --------------------------
    # Methods for AI dashboard
    # --------------------------
    def get_current_state(self) -> Dict[str, Any]:
        try:
            recent_vessels = self._fetch_recent_vessels(limit=100)
            performance_metrics = self._fetch_current_metrics()
            berth_status = self._fetch_berth_status()

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
                            "arrival_time": str(v.get('atb', ''))
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

    # --------------------------
    # Filtering & analysis
    # --------------------------
    def filter_data(self, filters: Dict[str, Any]) -> Dict[str, Any]:
        try:
            all_vessels = self._fetch_recent_vessels(limit=1000)
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

            summary = {
                "count": len(df),
                "avg_wait_time": float(df['wait_time_atb_btr'].mean()) if 'wait_time_atb_btr' in df.columns and not df.empty else 0,
                "max_wait_time": float(df['wait_time_atb_btr'].max()) if 'wait_time_atb_btr' in df.columns and not df.empty else 0,
                "total_carbon_saved": float(df['carbon_abatement_tonnes'].sum()) if 'carbon_abatement_tonnes' in df.columns and not df.empty else 0,
                "delayed_count": len(df[df['wait_time_atb_btr'] > 4]) if 'wait_time_atb_btr' in df.columns else 0
            }

            records = df.head(50).to_dict('records')
            for record in records:
                for key, value in record.items():
                    if pd.isna(value):
                        record[key] = None
                    elif isinstance(value, (pd.Timestamp, datetime)):
                        record[key] = str(value)

            return {
                "count": len(df),
                "data": records,
                "summary": summary,
                "filters_applied": filters
            }
        except Exception as e:
            logger.error(f"Error filtering data: {e}")
            return {"error": str(e), "count": 0, "data": []}

    # --------------------------
    # Utility helpers
    # --------------------------
    def _group_by_status(self, vessels: List[Dict]) -> Dict[str, int]:
        status_counts = {}
        for vessel in vessels:
            status = vessel.get('status', 'Unknown')
            status_counts[status] = status_counts.get(status, 0) + 1
        return status_counts

    def _group_by_berth(self, vessels: List[Dict]) -> Dict[str, List[str]]:
        berth_vessels = {}
        for vessel in vessels:
            berth = vessel.get('berth', 'Unknown')
            berth_vessels.setdefault(berth, []).append(vessel.get('vessel_name'))
        return berth_vessels

    def _calculate_utilization(self, berth_status: List[Dict]) -> float:
        if not berth_status:
            return 0.0
        occupied = len([b for b in berth_status if b['status'] == 'Occupied'])
        return (occupied / len(berth_status)) * 100
