"""
AI Service Module
Multi-model Azure OpenAI integration
Backend Engineer: AI/ML Specialist
"""

from openai import AzureOpenAI
from typing import List, Dict, Optional, Tuple
import numpy as np
import json
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AzureOpenAIConfig:
    """Configuration for Azure OpenAI services"""
    
    def __init__(
        self,
        endpoint: str,
        api_key: str,
        api_version: str = "2025-01-01-preview"
    ):
        self.endpoint = endpoint
        self.api_key = api_key
        self.api_version = api_version
        
        # Model deployment IDs from hackathon
        self.models = {
            "chat": "gpt-4.1-mini",           # Fast conversational
            "analysis": "gpt-5-mini",          # Deep insights
            "bulk": "openai",                  # Large data (gpt-4.1-nano)
            "embeddings": "text-embedding-3-small"
        }


class MultiModelAIService:
    """
    Intelligent AI service that routes queries to appropriate models
    """
    
    def __init__(self, config: AzureOpenAIConfig):
        self.config = config
        self.client = AzureOpenAI(
            azure_endpoint=config.endpoint,
            api_key=config.api_key,
            api_version=config.api_version
        )
        
        # System prompts for different contexts
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
    # USE CASE 1: Fast Chat (gpt-4.1-mini)
    # ============================================
    
    def chat(
        self,
        user_message: str,
        conversation_history: List[Dict] = None,
        context: Dict = None
    ) -> str:
        """
        Fast conversational responses for user questions.
        Best for: Quick queries, clarifications, simple data lookups
        
        Args:
            user_message: User's question
            conversation_history: Previous messages
            context: Additional context from database
            
        Returns:
            AI response string
        """
        try:
            messages = [{"role": "system", "content": self.system_prompts["chat"]}]
            
            # Add context if provided
            if context:
                context_str = self._format_context(context)
                messages.append({
                    "role": "system",
                    "content": f"Additional context:\n{context_str}"
                })
            
            # Add conversation history
            if conversation_history:
                messages.extend(conversation_history[-10:])  # Last 10 messages
            
            # Add current message
            messages.append({"role": "user", "content": user_message})
            
            logger.info(f"Chat request with {len(messages)} messages")
            
            response = self.client.chat.completions.create(
                model=self.config.models["chat"],
                messages=messages,
                temperature=0.7,
                max_tokens=500,
                top_p=0.9
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"Chat error: {str(e)}")
            return f"I encountered an error: {str(e)}. Please try again."
    
    # ============================================
    # USE CASE 2: Deep Analysis (gpt-5-mini)
    # ============================================
    
    def analyze(
        self,
        data_summary: str,
        analysis_type: str = "performance"
    ) -> Dict:
        """
        Deep analysis for predictions and strategic insights.
        Best for: Bunching detection, weather impact, carbon optimization
        
        Args:
            data_summary: Formatted data to analyze
            analysis_type: Type of analysis (bunching/weather/carbon/performance)
            
        Returns:
            Dictionary with insights and recommendations
        """
        try:
            system_prompt = self.system_prompts.get(
                analysis_type,
                self.system_prompts["performance"]
            )
            
            analysis_prompt = f"""Analyze the following maritime operations data:

{data_summary}

Provide:
1. Key Findings (3-5 bullet points)
2. Specific Issues Detected
3. Quantified Impact Assessment
4. Actionable Recommendations (prioritized)
5. Expected Outcomes

Format your response as structured JSON."""

            logger.info(f"Analysis request: {analysis_type}")
            
            response = self.client.chat.completions.create(
                model=self.config.models["analysis"],
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": analysis_prompt}
                ],
                temperature=0.3,  # Lower for analytical accuracy
                max_tokens=1500,
                response_format={"type": "json_object"}
            )
            
            result = json.loads(response.choices[0].message.content)
            
            return {
                "analysis_type": analysis_type,
                "timestamp": datetime.now().isoformat(),
                "insights": result,
                "model_used": self.config.models["analysis"]
            }
            
        except Exception as e:
            logger.error(f"Analysis error: {str(e)}")
            return {
                "error": str(e),
                "analysis_type": analysis_type
            }
    
    # ============================================
    # USE CASE 3: Bulk Processing (gpt-4.1-nano)
    # ============================================
    
    def process_bulk_data(
        self,
        large_dataset: str,
        processing_type: str = "summary"
    ) -> Dict:
        """
        Process large volumes of historical data.
        Best for: Historical analysis, pattern detection, trend analysis
        
        Args:
            large_dataset: Large text dataset (up to 1M tokens)
            processing_type: Type of processing needed
            
        Returns:
            Processed insights
        """
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

            logger.info(f"Bulk processing: {len(large_dataset)} characters")
            
            response = self.client.chat.completions.create(
                model=self.config.models["bulk"],
                messages=[
                    {"role": "system", "content": "You are a data analysis expert specialized in maritime logistics."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.2,
                max_tokens=4000  # Utilize high token capacity
            )
            
            return {
                "summary": response.choices[0].message.content,
                "records_processed": large_dataset.count('\n'),
                "model_used": self.config.models["bulk"],
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Bulk processing error: {str(e)}")
            return {"error": str(e)}
    
    # ============================================
    # USE CASE 4: Semantic Search (Embeddings)
    # ============================================
    
    def create_embeddings(self, texts: List[str]) -> np.ndarray:
        """
        Create vector embeddings for semantic search.
        
        Args:
            texts: List of text strings to embed
            
        Returns:
            NumPy array of embeddings
        """
        try:
            logger.info(f"Creating embeddings for {len(texts)} texts")
            
            response = self.client.embeddings.create(
                model=self.config.models["embeddings"],
                input=texts
            )
            
            embeddings = [item.embedding for item in response.data]
            return np.array(embeddings)
            
        except Exception as e:
            logger.error(f"Embedding error: {str(e)}")
            return np.array([])
    
    def semantic_search(
        self,
        query: str,
        document_embeddings: np.ndarray,
        documents: List[str],
        top_k: int = 5
    ) -> List[Dict]:
        """
        Find most relevant documents using cosine similarity.
        
        Args:
            query: Search query
            document_embeddings: Pre-computed document embeddings
            documents: Original documents
            top_k: Number of results to return
            
        Returns:
            List of top-k results with similarity scores
        """
        try:
            # Get query embedding
            query_embedding = self.create_embeddings([query])[0]
            
            # Calculate cosine similarity
            similarities = np.dot(document_embeddings, query_embedding) / (
                np.linalg.norm(document_embeddings, axis=1) * 
                np.linalg.norm(query_embedding)
            )
            
            # Get top-k indices
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
            
            logger.info(f"Semantic search returned {len(results)} results")
            return results
            
        except Exception as e:
            logger.error(f"Semantic search error: {str(e)}")
            return []
    
    # ============================================
    # Helper Methods
    # ============================================
    
    def _format_context(self, context: Dict) -> str:
        """Format context dictionary into readable string"""
        formatted = []
        for key, value in context.items():
            if isinstance(value, (list, dict)):
                formatted.append(f"{key}: {json.dumps(value, indent=2)}")
            else:
                formatted.append(f"{key}: {value}")
        return "\n".join(formatted)
    
    def classify_intent(self, query: str) -> Tuple[str, str]:
        """
        Classify user query to route to appropriate handler.
        
        Returns:
            Tuple of (intent_type, analysis_type)
        """
        query_lower = query.lower()
        
        # Analysis keywords
        analysis_keywords = {
            'bunching': ['bunch', 'cluster', 'multiple vessels', 'congestion'],
            'weather': ['weather', 'wind', 'storm', 'forecast', 'delay'],
            'carbon': ['carbon', 'emission', 'sustainability', 'green', 'optimize'],
            'performance': ['performance', 'accuracy', 'efficiency', 'metrics']
        }
        
        # Check for analysis needs
        for analysis_type, keywords in analysis_keywords.items():
            if any(kw in query_lower for kw in keywords):
                if any(word in query_lower for word in ['analyze', 'predict', 'detect', 'recommend']):
                    return ('analysis', analysis_type)
        
        # Check for bulk processing
        if any(word in query_lower for word in ['history', 'historical', 'trend', 'all vessels', 'past']):
            return ('bulk', 'historical')
        
        # Default to chat
        return ('chat', 'general')
