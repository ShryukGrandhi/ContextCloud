"""
Friendli AI client for ContextCloud Agents
Handles AI inference and reasoning tasks
"""

import os
import json
import logging
from typing import Dict, Any, Optional
from friendli import FriendliClient
from utils.logger import setup_logger

logger = setup_logger(__name__)

class FriendliClientWrapper:
    """Wrapper for Friendli AI client with enhanced functionality"""
    
    def __init__(self):
        self.client: Optional[FriendliClient] = None
        self.api_key = os.getenv("FRIENDLI_API_KEY")
        self.model_name = os.getenv("FRIENDLI_MODEL_NAME", "llama-2-70b-chat")
        
    async def initialize(self):
        """Initialize Friendli client"""
        try:
            if not self.api_key:
                raise Exception("FRIENDLI_API_KEY not found in environment variables")
            
            logger.info(f"🧠 Initializing Friendli AI client with model: {self.model_name}")
            
            self.client = FriendliClient(
                api_key=self.api_key
            )
            
            logger.info("✅ Friendli AI client initialized successfully")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize Friendli client: {e}")
            raise
    
    async def query(self, prompt: str, context: Optional[str] = None) -> str:
        """Send a query to Friendli AI for reasoning"""
        try:
            if not self.client:
                await self.initialize()
            
            # Prepare the full prompt with context if provided
            full_prompt = self._prepare_prompt(prompt, context)
            
            logger.info(f"🧠 Querying Friendli AI: {prompt[:50]}...")
            
            # Generate response using Friendli
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {
                        "role": "system",
                        "content": "You are ContextCloud, an AI assistant specialized in enterprise knowledge management and compliance intelligence. Provide clear, accurate, and actionable insights based on the provided context."
                    },
                    {
                        "role": "user",
                        "content": full_prompt
                    }
                ],
                max_tokens=1000,
                temperature=0.7
            )
            
            result = response.choices[0].message.content
            logger.info(f"✅ Friendli AI response generated ({len(result)} chars)")
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Friendli AI query failed: {e}")
            raise
    
    async def analyze_documents(self, documents: list, query: str) -> str:
        """Analyze multiple documents and provide insights"""
        try:
            logger.info(f"📊 Analyzing {len(documents)} documents for query: {query[:50]}...")
            
            # Prepare context from documents
            context = self._prepare_document_context(documents)
            
            analysis_prompt = f"""
            Based on the following documents, analyze and provide insights for the query: "{query}"
            
            Documents:
            {context}
            
            Please provide:
            1. Key findings relevant to the query
            2. Important patterns or trends
            3. Compliance considerations (if applicable)
            4. Actionable recommendations
            
            Format your response in a clear, structured manner.
            """
            
            response = await self.query(analysis_prompt)
            logger.info("✅ Document analysis completed")
            
            return response
            
        except Exception as e:
            logger.error(f"❌ Document analysis failed: {e}")
            raise
    
    async def summarize_content(self, content: str, max_length: int = 500) -> str:
        """Summarize content using Friendli AI"""
        try:
            logger.info(f"📝 Summarizing content ({len(content)} chars)")
            
            summary_prompt = f"""
            Please provide a concise summary of the following content in approximately {max_length} characters:
            
            {content}
            
            Focus on the key points, main findings, and important details.
            """
            
            response = await self.query(summary_prompt)
            logger.info("✅ Content summarization completed")
            
            return response
            
        except Exception as e:
            logger.error(f"❌ Content summarization failed: {e}")
            raise
    
    async def extract_insights(self, text: str) -> Dict[str, Any]:
        """Extract structured insights from text"""
        try:
            logger.info(f"🔍 Extracting insights from text ({len(text)} chars)")
            
            insights_prompt = f"""
            Analyze the following text and extract structured insights in JSON format:
            
            {text}
            
            Please provide a JSON response with the following structure:
            {{
                "key_topics": ["topic1", "topic2", "topic3"],
                "important_entities": ["entity1", "entity2", "entity3"],
                "sentiment": "positive/negative/neutral",
                "compliance_mentions": ["compliance1", "compliance2"],
                "action_items": ["action1", "action2"],
                "summary": "brief summary of the content"
            }}
            
            Return only the JSON object, no additional text.
            """
            
            response = await self.query(insights_prompt)
            
            # Try to parse JSON response
            try:
                insights = json.loads(response)
                logger.info("✅ Insights extraction completed")
                return insights
            except json.JSONDecodeError:
                logger.warning("⚠️ Could not parse JSON response, returning raw text")
                return {"raw_response": response}
            
        except Exception as e:
            logger.error(f"❌ Insights extraction failed: {e}")
            raise
    
    def _prepare_prompt(self, prompt: str, context: Optional[str] = None) -> str:
        """Prepare prompt with optional context"""
        if context:
            return f"""
            Context:
            {context}
            
            Query:
            {prompt}
            """
        return prompt
    
    def _prepare_document_context(self, documents: list) -> str:
        """Prepare context from multiple documents"""
        context_parts = []
        
        for i, doc in enumerate(documents, 1):
            context_parts.append(f"""
            Document {i}: {doc.get('filename', 'Unknown')}
            Type: {doc.get('document_type', 'Unknown')}
            Content: {doc.get('content', '')[:1000]}...
            Entities: {', '.join(doc.get('entities', []))}
            """)
        
        return "\n".join(context_parts)
    
    async def health_check(self) -> str:
        """Check Friendli AI health"""
        try:
            if not self.client:
                return "not_initialized"
            
            # Try a simple query to test the connection
            test_response = await self.query("Hello, this is a health check.")
            
            if test_response:
                return "healthy"
            else:
                return "unhealthy"
                
        except Exception as e:
            logger.error(f"❌ Friendli health check failed: {e}")
            return "error"

# Alias for easier import
FriendliClient = FriendliClientWrapper
