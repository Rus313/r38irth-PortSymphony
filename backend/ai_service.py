"""
AI Service Module
Multi-model Azure OpenAI integration
Backend Engineer: AI/ML Specialist
"""

from typing import List, Dict, Tuple
import numpy as np
import json
from datetime import datetime
import logging
import requests
import configkeys

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ============================================
# Simple request-based interface for Streamlit
# ============================================

def ask_ai(messages: List[Dict]) -> str:
    """
    Sends messages to Azure OpenAI via REST API using configkeys.
    Returns AI response text.
    """
    # ✅ ADD: Rate limiting check
    from security.rate_limiting import check_rate_limit
    check_rate_limit()
    
    # ✅ ADD: Input validation
    from security.validation import InputValidator
    for msg in messages:
        if 'content' in msg:
            # Check for SQL injection attempts
            if InputValidator.check_sql_injection(msg['content']):
                logger.error("SQL injection attempt in AI query")
                return "❌ Invalid input detected"
            
            # Sanitize HTML
            msg['content'] = InputValidator.sanitize_html(msg['content'])
    
    url = f"{configkeys.AZURE_OPENAI_ENDPOINT}openai/deployments/{configkeys.DEPLOYMENT_ID}/chat/completions?api-version={configkeys.AZURE_OPENAI_API_VERSION}"
    headers = {"Content-Type": "application/json", "api-key": configkeys.AZURE_OPENAI_API_KEY}
    payload = {"messages": messages, "temperature": 0.7}

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=30)  # ✅ ADD: timeout
        response.raise_for_status()
        data = response.json()
        return data["choices"][0]["message"]["content"]
    except requests.exceptions.Timeout:  # ✅ ADD: Better error handling
        logger.error("AI service timeout")
        return "❌ Request timeout. Please try again."
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 429:
            logger.warning("Rate limit exceeded on AI service")
            return "❌ Too many requests. Please wait a moment."
        logger.error(f"AI service error: {str(e)}")
        return f"❌ Error contacting AI service"
    except Exception as e:
        logger.error(f"ask_ai error: {str(e)}")
        return f"❌ Unexpected error occurred"

# ============================================
# Configuration class
# ============================================

class AzureOpenAIConfig:
    """Configuration for Azure OpenAI services"""
    
    def __init__(
        self,
        endpoint: str = configkeys.AZURE_OPENAI_ENDPOINT,
        api_key: str = configkeys.AZURE_OPENAI_API_KEY,
        api_version: str = configkeys.AZURE_OPENAI_API_VERSION
    ):
        self.endpoint = endpoint
        self.api_key = api_key
        self.api_version = api_version
        
        # Model deployment IDs
        self.models = {
            "chat": "gpt-4.1-mini",
            "analysis": "gpt-5-mini",
            "bulk": "gpt-4.1-nano",
            "embeddings": "text-embedding-3-small"
        }

# ============================================
# MultiModel AI Service
# ============================================

class MultiModelAIService:
    """
    Intelligent AI service that routes queries to appropriate models
    """
    
    def __init__(self, config: AzureOpenAIConfig = None):
        self.config = config or AzureOpenAIConfig()
        
        # Full system prompts
        self.system_prompts = {
            "chat": """You are a maritime operations assistant for PSA International.
You help users understand vessel performance, berth utilization, and sustainability metrics.
Provide concise, actionable responses. Use data from the context when available.
If you need more detailed analysis, recommend using the analysis feature.""",
            
            "bunching": """You are a vessel bunching detection expert.
Analyze vessel arrival patterns to identify clusters arriving within 4-hour windows.
Calculate potential carbon and cost savings from schedule optimization.
Provide specific, actionable recommendations with quantified impact.""",
            
            "weather": """You are a marine weather impact analyst.
Analyze weather conditions and predict impacts on vessel schedules.
Identify high-risk scenarios and recommend mitigation strategies.
Quantify delay risks and suggest alternative schedules.""",
            
            "carbon": """You are a maritime sustainability optimization expert.
Analyze vessel operations for carbon reduction opportunities.
Calculate emissions, identify inefficiencies, suggest optimizations.
Estimate cost savings from reduced bunker consumption.""",
            
            "performance": """You are a vessel performance analyst.
Analyze arrival accuracy, wait times, and berth utilization metrics.
Identify top and bottom performers with specific examples.
Provide actionable recommendations for improvement."""
        }

    # ============================================
    # Fast Chat
    # ============================================
    def chat(self, user_message: str, conversation_history: List[Dict] = None, context: Dict = None) -> str:
        """
        Fast conversational responses
        """
        try:
            messages = [{"role": "system", "content": self.system_prompts["chat"]}]
            
            if context:
                context_str = self._format_context(context)
                messages.append({"role": "system", "content": f"Additional context:\n{context_str}"})
            
            if conversation_history:
                messages.extend(conversation_history[-10:])
            
            messages.append({"role": "user", "content": user_message})
            
            return ask_ai(messages)
            
        except Exception as e:
            logger.error(f"Chat error: {str(e)}")
            return f"I encountered an error: {str(e)}. Please try again."
    
    # ============================================
    # Deep Analysis
    # ============================================
    def analyze(self, data_summary: str, analysis_type: str = "performance") -> Dict:
        try:
            system_prompt = self.system_prompts.get(analysis_type, self.system_prompts["performance"])
            
            analysis_prompt = f"""Analyze the following maritime operations data:

{data_summary}

Provide:
1. Key Findings (3-5 bullet points)
2. Specific Issues Detected
3. Quantified Impact Assessment
4. Actionable Recommendations (prioritized)
5. Expected Outcomes

Format your response as structured JSON."""
            
            response_text = ask_ai([
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": analysis_prompt}
            ])
            
            result = json.loads(response_text)
            
            return {
                "analysis_type": analysis_type,
                "timestamp": datetime.now().isoformat(),
                "insights": result,
                "model_used": self.config.models["analysis"]
            }
        except Exception as e:
            logger.error(f"Analysis error: {str(e)}")
            return {"error": str(e), "analysis_type": analysis_type}

    # ============================================
    # Bulk Processing
    # ============================================
    def process_bulk_data(self, large_dataset: str, processing_type: str = "summary") -> Dict:
        try:
            prompt = f"""Analyze this large historical maritime dataset:

{large_dataset}

Provide comprehensive analysis including:
1. Summary Statistics
2. Trend Analysis (patterns over time)
3. Anomaly Detection
4. Key Insights and Correlations
5. Recommendations

Be thorough - this is historical data for strategic planning."""

            response_text = ask_ai([
                {"role": "system", "content": "You are a data analysis expert specialized in maritime logistics."},
                {"role": "user", "content": prompt}
            ])
            
            return {
                "summary": response_text,
                "records_processed": large_dataset.count('\n'),
                "model_used": self.config.models["bulk"],
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Bulk processing error: {str(e)}")
            return {"error": str(e)}

    # ============================================
    # Semantic Search (Embeddings)
    # ============================================
    def create_embeddings(self, texts: List[str]) -> np.ndarray:
        try:
            response = ask_ai([
                {"role": "system", "content": "Create embeddings for semantic search."},
                {"role": "user", "content": json.dumps(texts)}
            ])
            embeddings = json.loads(response)  # Ensure you return actual vectors
            return np.array(embeddings)
        except Exception as e:
            logger.error(f"Embedding error: {str(e)}")
            return np.array([])

    def semantic_search(self, query: str, document_embeddings: np.ndarray, documents: List[str], top_k: int = 5) -> List[Dict]:
        try:
            query_embedding = self.create_embeddings([query])[0]
            similarities = np.dot(document_embeddings, query_embedding) / (np.linalg.norm(document_embeddings, axis=1) * np.linalg.norm(query_embedding))
            top_indices = np.argsort(similarities)[::-1][:top_k]
            results = [
                {
                    "rank": rank + 1,
                    "document": documents[i],
                    "similarity": float(similarities[i]),
                    "relevance": "High" if similarities[i] > 0.8 else "Medium" if similarities[i] > 0.6 else "Low"
                }
                for rank, i in enumerate(top_indices)
            ]
            return results
        except Exception as e:
            logger.error(f"Semantic search error: {str(e)}")
            return []

    # ============================================
    # Helper Methods
    # ============================================
    def _format_context(self, context: Dict) -> str:
        formatted = []
        for key, value in context.items():
            if isinstance(value, (list, dict)):
                formatted.append(f"{key}: {json.dumps(value, indent=2)}")
            else:
                formatted.append(f"{key}: {value}")
        return "\n".join(formatted)

    def classify_intent(self, query: str) -> Tuple[str, str]:
        query_lower = query.lower()
        analysis_keywords = {
            'bunching': ['bunch', 'cluster', 'multiple vessels', 'congestion'],
            'weather': ['weather', 'wind', 'storm', 'forecast', 'delay'],
            'carbon': ['carbon', 'emission', 'sustainability', 'green', 'optimize'],
            'performance': ['performance', 'accuracy', 'efficiency', 'metrics']
        }
        for analysis_type, keywords in analysis_keywords.items():
            if any(kw in query_lower for kw in keywords):
                if any(word in query_lower for word in ['analyze', 'predict', 'detect', 'recommend']):
                    return ('analysis', analysis_type)
        if any(word in query_lower for word in ['history', 'historical', 'trend', 'all vessels', 'past']):
            return ('bulk', 'historical')
        return ('chat', 'general')
