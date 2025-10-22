"""
AnalyzerAgent - ContextCloud Agents
Handles document analysis and reasoning using Friendli AI and AWS Comprehend
"""

import logging
from typing import Dict, Any, List
from llama_index.core.agent import ReActAgent
from llama_index.core.tools import ToolMetadata
from utils.logger import AgentLogger

logger = AgentLogger("AnalyzerAgent")

class AnalyzerAgent:
    """Agent responsible for analyzing documents and performing reasoning tasks"""
    
    def __init__(self, weaviate_client, friendli_client, aws_tools):
        self.weaviate_client = weaviate_client
        self.friendli_client = friendli_client
        self.aws_tools = aws_tools
        self.agent = None
        
    async def initialize(self):
        """Initialize the AnalyzerAgent with tools"""
        try:
            logger.log_action("Initializing AnalyzerAgent with tools")
            
            # Define available tools for analysis
            tools = [
                ToolMetadata(
                    name="analyze_documents",
                    description="Analyze retrieved documents for insights and patterns"
                ),
                ToolMetadata(
                    name="extract_entities",
                    description="Extract entities from documents using AWS Comprehend"
                ),
                ToolMetadata(
                    name="perform_reasoning",
                    description="Perform reasoning and analysis using Friendli AI"
                ),
                ToolMetadata(
                    name="detect_patterns",
                    description="Detect patterns and trends in the documents"
                )
            ]
            
            # Create ReAct agent
            self.agent = ReActAgent.from_tools(
                tools,
                verbose=True,
                system_prompt=self._get_system_prompt()
            )
            
            logger.log_action("AnalyzerAgent initialized successfully")
            
        except Exception as e:
            logger.log_error(f"Failed to initialize AnalyzerAgent: {e}")
            raise
    
    async def analyze_documents(self, documents: List[Dict[str, Any]], query: str) -> Dict[str, Any]:
        """Analyze retrieved documents for insights"""
        try:
            logger.log_action(f"Analyzing {len(documents)} documents for query: {query[:50]}...")
            
            # Perform document analysis
            logger.log_tool_call("analyze_documents", {"doc_count": len(documents), "query": query})
            analysis_results = await self._perform_document_analysis(documents, query)
            
            # Extract entities from documents
            logger.log_tool_call("extract_entities", {"doc_count": len(documents)})
            entity_analysis = await self._extract_entities_from_documents(documents)
            
            # Perform reasoning and pattern detection
            logger.log_tool_call("perform_reasoning", {"query": query})
            reasoning_results = await self._perform_reasoning_analysis(documents, query)
            
            logger.log_tool_call("detect_patterns", {"doc_count": len(documents)})
            pattern_results = await self._detect_patterns(documents)
            
            # Combine all analysis results
            result = {
                "query": query,
                "documents_analyzed": len(documents),
                "analysis_results": analysis_results,
                "entity_analysis": entity_analysis,
                "reasoning_results": reasoning_results,
                "pattern_results": pattern_results,
                "analysis_metadata": {
                    "analysis_method": "multi_modal",
                    "tools_used": ["Friendli AI", "AWS Comprehend", "Pattern Detection"],
                    "confidence_score": self._calculate_confidence_score(analysis_results)
                }
            }
            
            logger.log_result(f"Analysis completed with confidence score: {result['analysis_metadata']['confidence_score']}")
            return result
            
        except Exception as e:
            logger.log_error(f"Document analysis failed: {e}")
            raise
    
    async def _perform_document_analysis(self, documents: List[Dict[str, Any]], query: str) -> Dict[str, Any]:
        """Perform comprehensive document analysis"""
        try:
            logger.log_action("Performing document analysis with Friendli AI")
            
            # Prepare document content for analysis
            doc_content = []
            for i, doc in enumerate(documents[:5]):  # Analyze top 5 documents
                doc_content.append(f"""
                Document {i+1}: {doc.get('filename', 'Unknown')}
                Type: {doc.get('document_type', 'Unknown')}
                Content: {doc.get('content', '')[:1500]}...
                """)
            
            analysis_prompt = f"""
            Analyze the following documents in relation to this query and provide comprehensive insights:
            
            Query: "{query}"
            
            Documents:
            {chr(10).join(doc_content)}
            
            Please provide:
            1. Key findings relevant to the query
            2. Important patterns or trends identified
            3. Compliance considerations (if applicable)
            4. Risk factors or concerns
            5. Actionable recommendations
            6. Confidence level in the analysis
            
            Format your response in a clear, structured manner suitable for enterprise decision-making.
            """
            
            analysis = await self.friendli_client.query(analysis_prompt)
            
            return {
                "analysis_text": analysis,
                "documents_processed": len(documents),
                "analysis_type": "comprehensive_document_analysis"
            }
            
        except Exception as e:
            logger.log_error(f"Document analysis failed: {e}")
            return {"error": str(e), "analysis_text": "Analysis failed"}
    
    async def _extract_entities_from_documents(self, documents: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Extract entities from documents using AWS Comprehend"""
        try:
            logger.log_action("Extracting entities using AWS Comprehend")
            
            all_entities = []
            entity_frequencies = {}
            document_entities = {}
            
            for i, doc in enumerate(documents):
                content = doc.get("content", "")
                if content:
                    # Extract entities using AWS Comprehend
                    entities = await self.aws_tools.extract_entities(content)
                    
                    # Store entities for this document
                    document_entities[f"doc_{i}"] = entities
                    
                    # Aggregate all entities
                    all_entities.extend(entities)
                    
                    # Count entity frequencies
                    for entity in entities:
                        entity_frequencies[entity] = entity_frequencies.get(entity, 0) + 1
            
            # Get top entities
            top_entities = sorted(
                entity_frequencies.items(),
                key=lambda x: x[1],
                reverse=True
            )[:10]
            
            return {
                "total_entities": len(all_entities),
                "unique_entities": len(set(all_entities)),
                "top_entities": top_entities,
                "document_entities": document_entities,
                "entity_extraction_method": "aws_comprehend"
            }
            
        except Exception as e:
            logger.log_error(f"Entity extraction failed: {e}")
            return {"error": str(e), "total_entities": 0}
    
    async def _perform_reasoning_analysis(self, documents: List[Dict[str, Any]], query: str) -> Dict[str, Any]:
        """Perform reasoning analysis using Friendli AI"""
        try:
            logger.log_action("Performing reasoning analysis with Friendli AI")
            
            # Prepare reasoning prompt
            reasoning_prompt = f"""
            Perform deep reasoning analysis on the following documents to answer this query:
            
            Query: "{query}"
            
            Documents Summary:
            {self._prepare_document_summary(documents)}
            
            Please provide:
            1. Logical reasoning chain
            2. Evidence-based conclusions
            3. Potential implications
            4. Reasoning confidence level
            5. Alternative interpretations (if any)
            
            Focus on enterprise-relevant insights and compliance considerations.
            """
            
            reasoning = await self.friendli_client.query(reasoning_prompt)
            
            return {
                "reasoning_text": reasoning,
                "reasoning_type": "deep_analysis",
                "confidence_level": "high"
            }
            
        except Exception as e:
            logger.log_error(f"Reasoning analysis failed: {e}")
            return {"error": str(e), "reasoning_text": "Reasoning analysis failed"}
    
    async def _detect_patterns(self, documents: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Detect patterns and trends in documents"""
        try:
            logger.log_action("Detecting patterns and trends")
            
            # Analyze document types
            doc_types = {}
            for doc in documents:
                doc_type = doc.get("document_type", "unknown")
                doc_types[doc_type] = doc_types.get(doc_type, 0) + 1
            
            # Analyze entity patterns
            all_entities = []
            for doc in documents:
                all_entities.extend(doc.get("entities", []))
            
            entity_patterns = {}
            for entity in all_entities:
                entity_patterns[entity] = entity_patterns.get(entity, 0) + 1
            
            # Get top patterns
            top_entity_patterns = sorted(
                entity_patterns.items(),
                key=lambda x: x[1],
                reverse=True
            )[:10]
            
            return {
                "document_type_distribution": doc_types,
                "entity_patterns": top_entity_patterns,
                "pattern_analysis_method": "frequency_analysis",
                "total_patterns_identified": len(entity_patterns)
            }
            
        except Exception as e:
            logger.log_error(f"Pattern detection failed: {e}")
            return {"error": str(e), "total_patterns_identified": 0}
    
    def _prepare_document_summary(self, documents: List[Dict[str, Any]]) -> str:
        """Prepare a summary of documents for analysis"""
        summary_parts = []
        
        for i, doc in enumerate(documents[:3]):  # Top 3 documents
            summary_parts.append(f"""
            Document {i+1}: {doc.get('filename', 'Unknown')}
            Type: {doc.get('document_type', 'Unknown')}
            Key Entities: {', '.join(doc.get('entities', [])[:5])}
            Content Summary: {doc.get('content', '')[:300]}...
            """)
        
        return "\n".join(summary_parts)
    
    def _calculate_confidence_score(self, analysis_results: Dict[str, Any]) -> float:
        """Calculate confidence score for analysis results"""
        try:
            # Simple confidence calculation based on analysis completeness
            score = 0.5  # Base score
            
            if analysis_results.get("analysis_text"):
                score += 0.3
            
            if len(analysis_results.get("analysis_text", "")) > 200:
                score += 0.2
            
            return min(score, 1.0)
            
        except Exception:
            return 0.5
    
    def _get_system_prompt(self) -> str:
        """Get system prompt for the AnalyzerAgent"""
        return """
        You are the AnalyzerAgent for ContextCloud, an enterprise knowledge management system.
        
        Your role is to:
        1. Analyze retrieved documents for insights and patterns
        2. Extract entities and relationships using AWS Comprehend
        3. Perform reasoning and analysis using Friendli AI
        4. Detect patterns and trends in enterprise documents
        
        You have access to:
        - Friendli AI for advanced reasoning and analysis
        - AWS Comprehend for entity extraction and NLP
        - Document metadata and content for pattern detection
        
        Always provide thorough, evidence-based analysis suitable for enterprise decision-making.
        """
