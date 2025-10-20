"""
REAL AI Agent with Azure OpenAI Function Calling
Interprets dashboard data in real-time with domain expertise
"""

import json
from typing import Dict, List, Any
import logging
import requests
import configkeys
from backend.psa_knowledge_base import (
    interpret_wait_time, 
    interpret_arrival_accuracy,
    interpret_berth_utilization,
    get_recommendations_for_wait_time,
    get_recommendations_for_accuracy,
    get_recommendations_for_utilization,
    get_berth_specific_insights,
    get_carbon_insights,
    OPERATIONAL_INSIGHTS,
    PERFORMANCE_THRESHOLDS,
    build_stakeholder_context
)

logger = logging.getLogger(__name__)

class DashboardAgent:
    """
    AI Agent that interprets dashboard data using Azure OpenAI with function calling
    Includes domain expertise, few-shot learning, and validation
    """
    
    def __init__(self, data_access):
        self.data = data_access
        
        # Azure OpenAI configuration
        self.endpoint = configkeys.AZURE_OPENAI_ENDPOINT
        self.api_key = configkeys.AZURE_OPENAI_API_KEY
        self.api_version = configkeys.AZURE_OPENAI_API_VERSION
        self.deployment = configkeys.DEPLOYMENT_ID
        
        # ✅ OPTION 1: Enhanced System Prompt with Domain Knowledge
        self.system_prompt = """You are an expert maritime operations analyst for PSA International with 20+ years of experience in port operations, vessel management, and logistics optimization.

DOMAIN EXPERTISE:
You understand:
- Maritime operations and port logistics
- Vessel scheduling and berth allocation
- Performance metrics and KPIs
- Carbon emissions and sustainability
- Operational efficiency optimization

PERFORMANCE THRESHOLDS (Industry Standards):
Wait Time:
  • Excellent: 0-2 hours ✅
  • Acceptable: 2-4 hours ✅
  • Concerning: 4-6 hours ⚠️
  • Critical: >6 hours 🚨 (Immediate action required)

Arrival Accuracy:
  • Excellent: >95% ✅
  • Good: 90-95% ✅
  • Needs Improvement: 85-90% ⚠️
  • Poor: <85% 🔴 (Root cause analysis needed)

Berth Utilization:
  • Optimal: 75-85% ✅ (Sweet spot)
  • Underutilized: <75% 📉 (Opportunity for more throughput)
  • Congested: >85% ⚠️ (Risk of delays)
  • Critical: >90% 🚨 (Congestion expected)

OPERATIONAL CONTEXT:
- Port operates 24/7 with peak hours: 08:00-12:00, 14:00-18:00
- Target turnaround time: 18-20 hours
- Average berth time: 24 hours
- Carbon reduction target: 15-20% annually
- Port capacity: 24 berths across 4 terminals
- Typical vessel size: 15,000-22,000 TEU

STAKEHOLDER AWARENESS:
Adapt your communication based on who you're talking to:
- Top Management: Focus on KPIs, ROI, strategic impact, percentages, trends
- Middle Management: Focus on operational efficiency, resource allocation, bottlenecks
- Frontline Operations: Focus on immediate actions, specific vessels, berth assignments

CRITICAL INSTRUCTIONS:
You have REAL-TIME access to dashboard data through these functions:
1. get_dashboard_state() - See ALL current data (vessels, berths, KPIs, performance)
   → ALWAYS call this FIRST to understand the situation

2. filter_data() - Filter by specific criteria (berth, time window, vessel, status)
   → Use when user asks about specific berths, time periods, or vessels

3. analyze_delays() - Deep analysis of delay patterns and root causes
   → Use for delay-related questions or when wait times are concerning

4. get_recommendations() - Get optimization suggestions
   → Use when asked "what should I do" or for improvement suggestions

RESPONSE PROTOCOL:
1. Call appropriate function(s) to get REAL data
2. Interpret the data using domain knowledge
3. Provide SPECIFIC answer with:
   - Exact numbers (vessel names, berth IDs, wait times, percentages)
   - Status assessment (excellent/concerning/critical with icons)
   - Root cause if issues found
   - Actionable recommendations with expected impact
4. Use appropriate tone for stakeholder
5. Be concise but thorough - no fluff

RESPONSE FORMAT:
✅ Start with direct answer to the question
📊 Provide supporting data (specific vessels, numbers, trends)
🔍 Identify patterns or concerns if any
💡 End with actionable recommendations

Remember: You're not just reporting data - you're providing expert analysis and actionable insights!"""
        
        # Define tools (function calling)
        self.tools = [
            {
                "type": "function",
                "function": {
                    "name": "get_dashboard_state",
                    "description": "Get complete current dashboard state including all vessels, berths, KPIs, and performance metrics. Use this FIRST to understand the current situation.",
                    "parameters": {
                        "type": "object",
                        "properties": {},
                        "required": []
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "filter_data",
                    "description": "Filter dashboard data by specific criteria like berth, time window, vessel name, or status. Returns matching vessels with summary statistics.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "berth": {
                                "type": "string",
                                "description": "Berth ID to filter by (e.g., 'B02', 'B05'). Leave empty for all berths."
                            },
                            "time_window_hours": {
                                "type": "integer",
                                "description": "Number of hours to look back from now (e.g., 3 for last 3 hours, 24 for last day)"
                            },
                            "vessel_name": {
                                "type": "string",
                                "description": "Vessel name or partial name to search for"
                            },
                            "status": {
                                "type": "string",
                                "enum": ["At Berth", "Waiting", "In Transit", "Departed", "Delayed", "DEPARTED"],
                                "description": "Vessel status to filter by"
                            }
                        },
                        "required": []
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "analyze_delays",
                    "description": "Perform deep analysis of delay patterns, identify worst-performing berths/vessels, and determine root causes. Use this for delay-related questions.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "berth": {
                                "type": "string",
                                "description": "Specific berth to analyze (optional). Leave empty for all berths."
                            },
                            "time_period": {
                                "type": "string",
                                "description": "Time period to analyze (e.g., '3h', '24h', '7d'). Default: '24h'",
                                "default": "24h"
                            }
                        },
                        "required": []
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_recommendations",
                    "description": "Get AI-powered optimization recommendations based on current dashboard data. Provides specific, actionable suggestions.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "focus_area": {
                                "type": "string",
                                "enum": ["efficiency", "delays", "carbon", "utilization"],
                                "description": "What area to focus recommendations on: efficiency (overall), delays (reduce wait times), carbon (emissions reduction), utilization (berth usage)"
                            }
                        },
                        "required": ["focus_area"]
                    }
                }
            }
        ]
        
        # ✅ OPTION 2: Few-Shot Examples
        self.few_shot_examples = [
            {
                "role": "user",
                "content": "Are there any delays right now?"
            },
            {
                "role": "assistant",
                "content": """I'll check the current dashboard state for you.

[Calling: get_dashboard_state()]

Based on current data, I can see we have 2 vessels with significant delays:

**Critical Delays:**
1. **MSC Diana** at Berth B02:
   - Wait time: 5.8 hours 🚨 CRITICAL
   - Status: This exceeds our 2-hour target significantly
   - Root cause: Port congestion

2. **Ever Given** at Berth B05:
   - Wait time: 3.2 hours ⚠️ CONCERNING
   - Status: Above target but not critical yet

**Overall Status:**
- Average wait time across all berths: 2.4 hours (slightly above 2-hour target)
- Total vessels waiting: 4
- Terminal 1 utilization: 87% (risk of congestion)

**Immediate Actions Needed:**
1. 🚨 Priority: Expedite operations at B02 to free up capacity for MSC Diana
2. ⚠️ Monitor: Ever Given at B05 - prevent escalation to critical
3. 💡 Consider: Reassigning incoming vessels to Terminal 3 (lower utilization)

**Expected Impact:** Implementing these actions should reduce average wait time to <2 hours within 2-3 hours."""
            },
            {
                "role": "user",
                "content": "Show me berth B02 for the last 3 hours"
            },
            {
                "role": "assistant",
                "content": """I'll filter the data for Berth B02 over the last 3 hours.

[Calling: filter_data(berth="B02", time_window_hours=3)]

**Berth B02 Analysis (Last 3 Hours):**

**Current Status:** 🔴 Occupied
**Vessel:** MSC Diana (IMO: 9876543)
- Arrived: 14:23 (2.8 hours ago)
- Wait time before berthing: 1.2 hours ✅ (within target)
- Expected departure: 18:00 (1.5 hours from now)
- Operations progress: 65% complete

**Performance Metrics:**
- Arrival accuracy: 94.2% ✅ GOOD (target: >90%)
- Berth time so far: 2.8 hours (on track for 18-20 hour turnaround)
- No operational issues detected

**Berth Characteristics:**
- Terminal: Terminal 1
- Capacity: Large (max 20,000 TEU vessels)
- Equipment: 4 gantry cranes
- Current utilization: Normal

**Upcoming Schedule:**
- Next vessel: CMA CGM Antoine
- Scheduled arrival: 19:30 (30 minutes after expected B02 availability)
- Buffer: Adequate ✅

**Assessment:** Operations at B02 are running smoothly with no concerns. Vessel turnaround on schedule."""
            }
        ]
    
    # ========================================
    # CRITICAL: All methods below MUST be indented inside the class!
    # ========================================
    
    def process_query(self, user_query: str, conversation_history: List[Dict] = None, stakeholder_role: str = "middle_management") -> Dict[str, Any]:
        """
        Process user query with Azure OpenAI function calling
        
        Args:
            user_query: User's question
            conversation_history: Previous conversation messages
            stakeholder_role: User's role for tailored responses
            
        Returns:
            Dictionary with response and metadata
        """
        
        # Build messages with system prompt
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "system", "content": build_stakeholder_context(stakeholder_role)}
        ]
        
        # Add few-shot examples
        messages.extend(self.few_shot_examples)
        
        # Add conversation history
        if conversation_history:
            messages.extend(conversation_history[-5:])  # Last 5 messages for context
        
        # Add current user query
        messages.append({"role": "user", "content": user_query})
        
        try:
            response_data = self._call_azure_with_tools(messages)
            
            # ✅ OPTION 3: Post-process validation
            response_data = self._validate_and_enhance_response(response_data)
            
            return response_data
        except Exception as e:
            logger.error(f"Error processing query: {e}")
            return {
                "response": f"I encountered an error analyzing the dashboard: {str(e)}. Please try rephrasing your question.",
                "function_calls_made": 0,
                "data_accessed": False,
                "error": str(e)
            }
    
    def _call_azure_with_tools(self, messages: List[Dict]) -> Dict[str, Any]:
        """
        Call Azure OpenAI with function calling capability
        """
        
        url = f"{self.endpoint}openai/deployments/{self.deployment}/chat/completions?api-version={self.api_version}"
        
        headers = {
            "Content-Type": "application/json",
            "api-key": self.api_key
        }
        
        max_iterations = 5
        iteration = 0
        function_calls_made = []
        last_function_result = None
        
        while iteration < max_iterations:
            try:
                payload = {
                    "messages": messages,
                    "tools": self.tools,
                    "tool_choice": "auto",
                    "temperature": 0.7,
                    "max_tokens": 2000
                }
                
                response = requests.post(url, headers=headers, json=payload, timeout=60)
                response.raise_for_status()
                result = response.json()
                
                message = result["choices"][0]["message"]
                
                # Check if AI wants to call functions
                if message.get("tool_calls"):
                    messages.append(message)
                    
                    for tool_call in message["tool_calls"]:
                        function_name = tool_call["function"]["name"]
                        function_args = json.loads(tool_call["function"]["arguments"])
                        
                        logger.info(f"🤖 AI calling: {function_name}({function_args})")
                        
                        # Execute function with domain knowledge enhancement
                        function_result = self._execute_function_with_insights(function_name, function_args)
                        last_function_result = function_result
                        
                        function_calls_made.append({
                            "function": function_name,
                            "arguments": function_args
                        })
                        
                        # Add result to conversation
                        messages.append({
                            "role": "tool",
                            "tool_call_id": tool_call["id"],
                            "name": function_name,
                            "content": json.dumps(function_result)
                        })
                    
                    iteration += 1
                    continue
                
                else:
                    # AI has final answer
                    return {
                        "response": message["content"],
                        "function_calls_made": len(function_calls_made),
                        "functions_called": function_calls_made,
                        "data_accessed": len(function_calls_made) > 0,
                        "raw_data": last_function_result
                    }
            
            except Exception as e:
                logger.error(f"Error in Azure OpenAI call (iteration {iteration}): {e}")
                raise
        
        # Max iterations reached
        return {
            "response": "I've analyzed multiple aspects of the dashboard data. Could you ask a more specific question to help me focus on what matters most to you?",
            "function_calls_made": len(function_calls_made),
            "functions_called": function_calls_made,
            "data_accessed": True,
            "warning": "Max iterations reached"
        }
    
    def _execute_function_with_insights(self, function_name: str, arguments: Dict) -> Any:
        """
        Execute function and enhance with domain knowledge (Option 4)
        """
        
        logger.info(f"⚙️ Executing: {function_name}")
        
        try:
            if function_name == "get_dashboard_state":
                result = self.data.get_current_state()
                
                # ✅ Enhance with interpretations
                if result.get('performance'):
                    perf = result['performance']
                    
                    # Add wait time interpretation
                    if perf.get('avg_wait_time'):
                        result['performance']['wait_time_interpretation'] = interpret_wait_time(perf['avg_wait_time'])
                    
                    # Add arrival accuracy interpretation
                    if perf.get('avg_arrival_accuracy'):
                        result['performance']['accuracy_interpretation'] = interpret_arrival_accuracy(perf['avg_arrival_accuracy'])
                
                # Add berth utilization interpretation
                if result.get('berths', {}).get('total_utilization'):
                    util = result['berths']['total_utilization']
                    result['berths']['utilization_interpretation'] = interpret_berth_utilization(util)
                
                logger.info(f"✅ Dashboard state: {result.get('vessels', {}).get('total_count', 0)} vessels")
                return result
            
            elif function_name == "filter_data":
                result = self.data.filter_data(arguments)
                
                # ✅ Enhance with interpretations and recommendations
                if result.get('summary'):
                    summary = result['summary']
                    
                    # Interpret wait time
                    if summary.get('avg_wait_time'):
                        wait_time = summary['avg_wait_time']
                        result['interpretation'] = interpret_wait_time(wait_time)
                        
                        # Add specific recommendations
                        if result['interpretation']['action_needed']:
                            result['recommendations'] = get_recommendations_for_wait_time(
                                wait_time,
                                arguments.get('berth'),
                                summary.get('count', 0)
                            )
                    
                    # Add berth-specific insights if berth specified
                    if arguments.get('berth'):
                        berth_insights = get_berth_specific_insights(arguments['berth'])
                        if 'error' not in berth_insights:
                            result['berth_insights'] = berth_insights
                
                logger.info(f"✅ Filtered: {result.get('count', 0)} records")
                return result
            
            elif function_name == "analyze_delays":
                result = self.data.analyze_delays(
                    berth=arguments.get('berth'),
                    time_period=arguments.get('time_period', '24h')
                )
                
                # ✅ Enhance with interpretations
                if result.get('avg_delay_time'):
                    result['delay_interpretation'] = interpret_wait_time(result['avg_delay_time'])
                
                if result.get('total_delays') and result['total_delays'] > 0:
                    result['recommendations'] = get_recommendations_for_wait_time(
                        result.get('avg_delay_time', 0),
                        arguments.get('berth'),
                        result['total_delays']
                    )
                
                logger.info(f"✅ Delays: {result.get('total_delays', 0)} found")
                return result
            
            elif function_name == "get_recommendations":
                focus = arguments.get('focus_area')
                result = self.data.get_recommendations(focus)
                
                # ✅ Enhance with specific recommendations from knowledge base
                state = self.data.get_current_state()
                
                additional_recs = []
                if focus == "delays" and state.get('performance', {}).get('avg_wait_time'):
                    wait_time = state['performance']['avg_wait_time']
                    additional_recs.extend(get_recommendations_for_wait_time(wait_time))
                
                elif focus == "efficiency" and state.get('performance', {}).get('avg_arrival_accuracy'):
                    accuracy = state['performance']['avg_arrival_accuracy']
                    additional_recs.extend(get_recommendations_for_accuracy(accuracy))
                
                elif focus == "utilization" and state.get('berths', {}).get('total_utilization'):
                    util = state['berths']['total_utilization']
                    additional_recs.extend(get_recommendations_for_utilization(util))
                
                # Combine with data-driven recommendations
                if isinstance(result, list):
                    result.extend(additional_recs)
                else:
                    result = additional_recs
                
                # Remove duplicates
                result = list(dict.fromkeys(result))
                
                logger.info(f"✅ Recommendations: {len(result)}")
                return {"recommendations": result}
            
            else:
                return {"error": f"Unknown function: {function_name}"}
        
        except Exception as e:
            logger.error(f"❌ Error in {function_name}: {e}")
            return {"error": str(e)}
    
    def _validate_and_enhance_response(self, response_data: Dict) -> Dict:
        """
        ✅ OPTION 3: Validate and enhance AI response with domain knowledge
        """
        
        response_text = response_data.get('response', '')
        raw_data = response_data.get('raw_data', {})
        
        # Check if response mentions metrics without proper context
        enhancements = []
        
        # 1. Wait time validation
        if "wait" in response_text.lower() or "delay" in response_text.lower():
            if raw_data and isinstance(raw_data, dict):
                # Check for wait time in various places
                wait_time = None
                
                if raw_data.get('summary', {}).get('avg_wait_time'):
                    wait_time = raw_data['summary']['avg_wait_time']
                elif raw_data.get('performance', {}).get('avg_wait_time'):
                    wait_time = raw_data['performance']['avg_wait_time']
                elif raw_data.get('avg_delay_time'):
                    wait_time = raw_data['avg_delay_time']
                
                if wait_time:
                    interpretation = interpret_wait_time(wait_time)
                    
                    # Add context if AI didn't provide proper interpretation
                    if wait_time > 4 and interpretation['severity'] in ['concerning', 'critical']:
                        if 'critical' not in response_text.lower() and 'concerning' not in response_text.lower():
                            enhancements.append(
                                f"\n\n⚠️ **Important Context:** {interpretation['message']}"
                            )
        
        # 2. Accuracy validation
        if "accuracy" in response_text.lower():
            if raw_data and isinstance(raw_data, dict):
                accuracy = raw_data.get('performance', {}).get('avg_arrival_accuracy')
                
                if accuracy and accuracy < 90:
                    if 'below target' not in response_text.lower():
                        enhancements.append(
                            f"\n\n📊 **Performance Note:** Current arrival accuracy ({accuracy:.1f}%) is below the 90% target threshold."
                        )
        
        # 3. Utilization validation
        if "utilization" in response_text.lower() or "capacity" in response_text.lower():
            if raw_data and isinstance(raw_data, dict):
                util = raw_data.get('berths', {}).get('total_utilization')
                
                if util:
                    if util > 85 and 'congestion' not in response_text.lower():
                        enhancements.append(
                            f"\n\n⚠️ **Capacity Alert:** Berth utilization at {util:.1f}% - approaching capacity limits (target: 75-85%)."
                        )
                    elif util < 70 and 'underutilized' not in response_text.lower():
                        enhancements.append(
                            f"\n\n📉 **Opportunity:** Berth utilization at {util:.1f}% suggests capacity for {((80-util)/4):.0f} more vessels/day."
                        )
        
        # 4. Add carbon context if mentioned
        if "carbon" in response_text.lower() or "emission" in response_text.lower():
            if raw_data and isinstance(raw_data, dict):
                carbon_saved = raw_data.get('performance', {}).get('total_carbon_saved')
                
                if carbon_saved and carbon_saved > 0:
                    carbon_insights = get_carbon_insights(carbon_saved, 30)
                    if 'equivalent' not in response_text.lower():
                        enhancements.append(
                            f"\n\n🌱 **Sustainability Impact:** {carbon_saved:.0f} tonnes CO₂ saved = {carbon_insights['equivalents']['trees_planted']} or {carbon_insights['equivalents']['cars_off_road']}."
                        )
        
        # Apply enhancements
        if enhancements:
            response_data['response'] = response_text + ''.join(enhancements)
        
        return response_data