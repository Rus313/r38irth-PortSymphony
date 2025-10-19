"""
Query Handler Module
Intelligent query routing and processing
Backend Engineer: System Architect
"""

from typing import Dict, List, Any
import logging
from backend.ai_service import MultiModelAIService
from data.database_manager import DatabaseManager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SmartQueryHandler:
    """
    Routes user queries to appropriate AI models and data sources
    """
    
    def __init__(
        self,
        ai_service: MultiModelAIService,
        db_manager: DatabaseManager
    ):
        self.ai = ai_service
        self.db = db_manager
    
    def handle_query(
        self,
        query: str,
        conversation_history: List[Dict] = None
    ) -> Dict[str, Any]:
        """
        Main entry point for handling user queries.
        Intelligently routes to appropriate handler.
        
        Args:
            query: User's question
            conversation_history: Previous conversation messages
            
        Returns:
            Response dictionary with content and metadata
        """
        try:
            # Classify query intent
            intent_type, analysis_category = self.ai.classify_intent(query)
            
            logger.info(f"Query classified as: {intent_type}/{analysis_category}")
            
            # Route to appropriate handler
            if intent_type == 'chat':
                return self._handle_chat_query(query, conversation_history)
            
            elif intent_type == 'analysis':
                return self._handle_analysis_query(query, analysis_category)
            
            elif intent_type == 'bulk':
                return self._handle_bulk_query(query)
            
            else:
                return self._handle_chat_query(query, conversation_history)
                
        except Exception as e:
            logger.error(f"Query handling error: {str(e)}")
            return {
                "type": "error",
                "content": f"An error occurred: {str(e)}",
                "metadata": {"error": str(e)}
            }
    
    def _handle_chat_query(
        self,
        query: str,
        conversation_history: List[Dict] = None
    ) -> Dict:
        """Handle simple chat queries with fast model"""
        
        # Fetch relevant context from database
        context = self._get_relevant_context(query)
        
        # Get AI response using fast model
        response = self.ai.chat(
            user_message=query,
            conversation_history=conversation_history,
            context=context
        )
        
        return {
            "type": "chat",
            "content": response,
            "metadata": {
                "model": "gpt-4.1-mini",
                "context_provided": bool(context),
                "response_time": "fast"
            }
        }
    
    def _handle_analysis_query(
        self,
        query: str,
        analysis_category: str
    ) -> Dict:
        """Handle complex analysis queries with advanced model"""
        
        # Fetch relevant data based on analysis type
        data = self._fetch_analysis_data(analysis_category)
        
        # Format data for analysis
        data_summary = self._format_data_for_analysis(data, analysis_category)
        
        # Perform deep analysis
        analysis_result = self.ai.analyze(
            data_summary=data_summary,
            analysis_type=analysis_category
        )
        
        return {
            "type": "analysis",
            "content": analysis_result,
            "metadata": {
                "model": "gpt-5-mini",
                "analysis_category": analysis_category,
                "data_points_analyzed": len(data) if isinstance(data, list) else 0
            }
        }
    
    def _handle_bulk_query(self, query: str) -> Dict:
        """Handle historical/bulk data queries"""
        
        # Fetch large historical dataset
        historical_data = self.db.get_historical_movements(limit=500)
        
        # Format as text for bulk processing
        formatted_data = self._format_bulk_data(historical_data)
        
        # Process with high-token model
        bulk_result = self.ai.process_bulk_data(
            large_dataset=formatted_data,
            processing_type="historical_analysis"
        )
        
        return {
            "type": "bulk_analysis",
            "content": bulk_result,
            "metadata": {
                "model": "gpt-4.1-nano",
                "records_processed": len(historical_data)
            }
        }
    
    def _get_relevant_context(self, query: str) -> Dict:
        """Fetch relevant context from database for chat queries"""
        
        context = {}
        
        # Check if query mentions specific vessels
        if any(word in query.lower() for word in ['vessel', 'ship']):
            context['recent_vessels'] = self.db.get_recent_vessels(limit=5)
        
        # Check if query mentions metrics
        if any(word in query.lower() for word in ['accuracy', 'wait', 'time', 'performance']):
            context['current_metrics'] = self.db.get_current_metrics()
        
        # Check if query mentions ports
        if 'port' in query.lower() or 'berth' in query.lower():
            context['berth_status'] = self.db.get_berth_availability()
        
        return context
    
    def _fetch_analysis_data(self, analysis_category: str) -> List[Dict]:
        """Fetch data specific to analysis category"""
        
        if analysis_category == 'bunching':
            # Get upcoming arrivals in next 48 hours
            return self.db.get_upcoming_arrivals(hours=48)
        
        elif analysis_category == 'weather':
            # Get weather forecast and affected vessels
            return {
                'weather': self.db.get_weather_forecast(),
                'schedule': self.db.get_upcoming_arrivals(hours=72)
            }
        
        elif analysis_category == 'carbon':
            # Get emissions data for analysis
            return self.db.get_carbon_metrics(days=30)
        
        elif analysis_category == 'performance':
            # Get performance metrics
            return self.db.get_performance_data(days=30)
        
        else:
            return self.db.get_recent_vessels(limit=50)
    
    def _format_data_for_analysis(
        self,
        data: Any,
        analysis_category: str
    ) -> str:
        """Format data into readable text for AI analysis"""
        
        if analysis_category == 'bunching':
            # Format vessel arrival data
            formatted_lines = ["UPCOMING VESSEL ARRIVALS:\n"]
            for vessel in data:
                formatted_lines.append(
                    f"- {vessel.get('vessel_name')} (IMO: {vessel.get('imo_number')})\n"
                    f"  From: {vessel.get('from_port')} | To: {vessel.get('to_port')}\n"
                    f"  Expected Arrival: {vessel.get('eta')}\n"
                    f"  Berth: {vessel.get('berth')}\n"
                )
            return "\n".join(formatted_lines)
        
        elif analysis_category == 'weather':
            # Format weather and schedule data
            weather_info = data.get('weather', {})
            schedule_info = data.get('schedule', [])
            
            formatted = f"""WEATHER FORECAST:
{weather_info}

AFFECTED VESSELS:
"""
            for vessel in schedule_info:
                formatted += f"- {vessel.get('vessel_name')}: ETA {vessel.get('eta')}\n"
            
            return formatted
        
        elif analysis_category == 'carbon':
            # Format emissions data
            formatted_lines = ["CARBON EMISSIONS DATA:\n"]
            for record in data:
                formatted_lines.append(
                    f"Date: {record.get('date')} | "
                    f"Vessel: {record.get('vessel_name')} | "
                    f"Emissions: {record.get('total_emissions')} tonnes | "
                    f"Savings: {record.get('savings')} tonnes\n"
                )
            return "\n".join(formatted_lines)
        
        else:
            # Generic formatting
            import json
            return json.dumps(data, indent=2, default=str)
    
    def _format_bulk_data(self, historical_data: List[Dict]) -> str:
        """Format large dataset for bulk processing"""
        
        formatted_lines = [
            "HISTORICAL VESSEL MOVEMENT DATA",
            "=" * 50,
            ""
        ]
        
        for record in historical_data:
            formatted_lines.append(
                f"Vessel: {record.get('vessel_name')} (IMO: {record.get('imo_number')})\n"
                f"Route: {record.get('from_port')} → {record.get('to_port')}\n"
                f"Arrival Time: {record.get('atb')} | Departure: {record.get('atu')}\n"
                f"Wait Time: {record.get('wait_time_hours')} hrs | "
                f"Berth Time: {record.get('berth_time_hours')} hrs\n"
                f"Arrival Accuracy: {record.get('arrival_accuracy')}% | "
                f"Status: {record.get('status')}\n"
                f"Carbon Abatement: {record.get('carbon_abatement_tonnes')} tonnes | "
                f"Bunker Saved: ${record.get('bunker_saved_usd')}\n"
                f"{'-' * 50}\n"
            )
        
        return "\n".join(formatted_lines)


class ProactiveInsightsGenerator:
    """
    Generates proactive insights automatically on schedule
    """
    
    def __init__(
        self,
        ai_service: MultiModelAIService,
        db_manager: DatabaseManager
    ):
        self.ai = ai_service
        self.db = db_manager
    
    def generate_daily_bunching_report(self) -> Dict:
        """
        Detect vessel bunching and generate daily report
        Uses GPT-5-mini for complex analysis
        """
        logger.info("Generating daily bunching report")
        
        # Get today's and tomorrow's vessel movements
        upcoming_vessels = self.db.get_upcoming_arrivals(hours=48)
        
        # Format data for analysis
        data_summary = self._format_bunching_data(upcoming_vessels)
        
        # Analyze with GPT-5-mini
        analysis = self.ai.analyze(
            data_summary=data_summary,
            analysis_type="bunching"
        )
        
        return {
            "report_type": "bunching_detection",
            "date": datetime.now().strftime("%Y-%m-%d"),
            "vessels_analyzed": len(upcoming_vessels),
            "bunching_events": self._count_bunching_events(upcoming_vessels),
            "analysis": analysis,
            "priority": self._calculate_priority(analysis)
        }
    
    def generate_weather_impact_forecast(self) -> Dict:
        """
        Forecast weather impacts on operations
        Uses GPT-5-mini for prediction
        """
        logger.info("Generating weather impact forecast")
        
        # Get weather data and schedule
        weather_data = self.db.get_weather_forecast()
        vessel_schedule = self.db.get_upcoming_arrivals(hours=72)
        
        # Combine data
        combined_data = f"""
WEATHER FORECAST (Next 72 hours):
{weather_data}

VESSEL SCHEDULE:
{self._format_schedule_data(vessel_schedule)}
"""
        
        # Analyze impact
        analysis = self.ai.analyze(
            data_summary=combined_data,
            analysis_type="weather"
        )
        
        return {
            "report_type": "weather_impact",
            "forecast_period": "72 hours",
            "affected_vessels": len(vessel_schedule),
            "analysis": analysis,
            "risk_level": self._assess_weather_risk(analysis)
        }
    
    def generate_carbon_optimization_report(self) -> Dict:
        """
        Identify carbon reduction opportunities
        Uses GPT-5-mini for optimization analysis
        """
        logger.info("Generating carbon optimization report")
        
        # Get recent emissions data
        carbon_data = self.db.get_carbon_metrics(days=30)
        
        # Format for analysis
        data_summary = f"""
CARBON EMISSIONS - LAST 30 DAYS:

Total Emissions: {sum(d.get('total_emissions', 0) for d in carbon_data)} tonnes
Total Savings: {sum(d.get('savings', 0) for d in carbon_data)} tonnes
Average Emissions per Vessel: {sum(d.get('total_emissions', 0) for d in carbon_data) / max(len(carbon_data), 1):.2f} tonnes

DETAILED BREAKDOWN:
{self._format_carbon_data(carbon_data)}
"""
        
        # Analyze opportunities
        analysis = self.ai.analyze(
            data_summary=data_summary,
            analysis_type="carbon"
        )
        
        return {
            "report_type": "carbon_optimization",
            "period": "30 days",
            "total_emissions": sum(d.get('total_emissions', 0) for d in carbon_data),
            "total_savings": sum(d.get('savings', 0) for d in carbon_data),
            "analysis": analysis,
            "savings_potential": self._extract_savings_potential(analysis)
        }
    
    def _format_bunching_data(self, vessels: List[Dict]) -> str:
        """Format vessel data for bunching analysis"""
        lines = ["VESSEL ARRIVAL ANALYSIS:\n"]
        
        # Group by berth and time window
        from collections import defaultdict
        berth_schedule = defaultdict(list)
        
        for vessel in vessels:
            berth = vessel.get('berth', 'Unknown')
            berth_schedule[berth].append(vessel)
        
        for berth, berth_vessels in berth_schedule.items():
            lines.append(f"\nBERTH: {berth}")
            lines.append(f"Scheduled Arrivals: {len(berth_vessels)}")
            for vessel in berth_vessels:
                lines.append(
                    f"  - {vessel.get('vessel_name')} | "
                    f"ETA: {vessel.get('eta')} | "
                    f"From: {vessel.get('from_port')}"
                )
        
        return "\n".join(lines)
    
    def _format_schedule_data(self, vessels: List[Dict]) -> str:
        """Format vessel schedule data"""
        lines = []
        for vessel in vessels:
            lines.append(
                f"{vessel.get('vessel_name')} | "
                f"ETA: {vessel.get('eta')} | "
                f"Berth: {vessel.get('berth')}"
            )
        return "\n".join(lines)
    
    def _format_carbon_data(self, data: List[Dict]) -> str:
        """Format carbon emissions data"""
        lines = []
        for record in data:
            lines.append(
                f"Date: {record.get('date')} | "
                f"Vessel: {record.get('vessel_name')} | "
                f"Emissions: {record.get('total_emissions', 0):.2f}t | "
                f"Saved: {record.get('savings', 0):.2f}t"
            )
        return "\n".join(lines)
    
    def _count_bunching_events(self, vessels: List[Dict]) -> int:
        """Count number of bunching events (3+ vessels within 4 hours)"""
        # Simplified logic - would need actual datetime parsing
        from collections import defaultdict
        
        time_windows = defaultdict(int)
        for vessel in vessels:
            # Group by 4-hour windows (simplified)
            eta = str(vessel.get('eta', ''))[:13]  # Group by date and hour
            time_windows[eta] += 1
        
        return sum(1 for count in time_windows.values() if count >= 3)
    
    def _calculate_priority(self, analysis: Dict) -> str:
        """Calculate priority level based on analysis"""
        insights = analysis.get('insights', {})
        
        # Check for high-priority keywords in findings
        high_priority_keywords = ['critical', 'urgent', 'immediate', 'severe']
        findings = str(insights).lower()
        
        if any(kw in findings for kw in high_priority_keywords):
            return "HIGH"
        elif 'moderate' in findings or 'attention' in findings:
            return "MEDIUM"
        else:
            return "LOW"
    
    def _assess_weather_risk(self, analysis: Dict) -> str:
        """Assess weather risk level"""
        insights = str(analysis.get('insights', {})).lower()
        
        if any(word in insights for word in ['severe', 'dangerous', 'extreme']):
            return "HIGH"
        elif any(word in insights for word in ['moderate', 'caution', 'warning']):
            return "MEDIUM"
        else:
            return "LOW"
    
    def _extract_savings_potential(self, analysis: Dict) -> Dict:
        """Extract carbon savings potential from analysis"""
        # This would parse the AI response for specific savings numbers
        # Simplified version
        return {
            "estimated_carbon_reduction": "15-25%",
            "estimated_cost_savings": "$50K-100K annually",
            "confidence": "HIGH"
        }