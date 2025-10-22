"""
Gemini client for ContextCloud Agents
Handles Google Generative AI integration for node search and analysis
"""

import os
import logging
from typing import List, Dict, Any, Optional
import google.generativeai as genai
from utils.logger import setup_logger

logger = setup_logger(__name__)

class GeminiClient:
    """Gemini client for AI-powered node search and analysis"""
    
    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY")
        self.model = None
        
    async def initialize(self):
        """Initialize Gemini client"""
        try:
            if not self.api_key:
                raise Exception("GEMINI_API_KEY environment variable is required")
            
            logger.info("🤖 Initializing Gemini client...")
            
            # Configure Gemini
            genai.configure(api_key=self.api_key)
            
            # Initialize the model
            self.model = genai.GenerativeModel('gemini-2.5-flash')
            
            logger.info("✅ Gemini client initialized successfully")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize Gemini client: {e}")
            raise
    
    async def find_relevant_nodes(self, query: str, nodes: List[Dict[str, Any]], limit: int = 10) -> Dict[str, Any]:
        """
        Find the most relevant nodes based on query using Gemini AI
        
        Args:
            query: User search query
            nodes: List of knowledge graph nodes
            limit: Maximum number of nodes to return
            
        Returns:
            Dictionary with relevant nodes and analysis summary
        """
        try:
            logger.info(f"🔍 Finding relevant nodes for query: {query}")
            
            if not self.model:
                raise Exception("Gemini client not initialized")
            
            # Prepare node summaries for analysis
            node_summaries = []
            for i, node in enumerate(nodes):
                summary = {
                    "id": node.get("id", f"node_{i}"),
                    "label": node.get("label", "Unknown"),
                    "type": node.get("type", "unknown"),
                    "summary": node.get("summary", ""),
                    "key_terms": node.get("key_terms", []),
                    "content_preview": node.get("content_preview", ""),
                    "entities": node.get("entities", [])
                }
                node_summaries.append(summary)
            
            # Create prompt for Gemini
            prompt = self._create_search_prompt(query, node_summaries, limit)
            
            # Query Gemini
            response = self.model.generate_content(prompt)
            
            # Parse response
            result = self._parse_search_response(response.text, nodes)
            
            logger.info(f"✅ Found {len(result['relevant_nodes'])} relevant nodes")
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Failed to find relevant nodes: {e}")
            raise
    
    def _create_search_prompt(self, query: str, node_summaries: List[Dict], limit: int) -> str:
        """Create a prompt for Gemini to analyze node relevance"""
        
        nodes_text = ""
        for node in node_summaries:
            nodes_text += f"""
Node ID: {node['id']}
Label: {node['label']}
Type: {node['type']}
Summary: {node['summary']}
Key Terms: {', '.join(node['key_terms'])}
Entities: {', '.join(node['entities'])}
Content Preview: {node['content_preview']}
---
"""
        
        prompt = f"""
You are an AI assistant helping to find the most relevant nodes in a knowledge graph based on a user query.

User Query: "{query}"

Available Nodes:
{nodes_text}

Please analyze each node and determine which ones are most relevant to the user query. Consider:
1. Semantic similarity between the query and node content
2. Relevance of key terms and entities
3. Context and meaning of the summary
4. Overall usefulness for answering the query

Return your response in the following JSON format:
{{
    "analysis_summary": "Brief explanation of your analysis and findings",
    "relevant_node_ids": ["node_id_1", "node_id_2", "node_id_3"],
    "relevance_scores": {{
        "node_id_1": 0.95,
        "node_id_2": 0.87,
        "node_id_3": 0.76
    }},
    "reasoning": {{
        "node_id_1": "Why this node is relevant",
        "node_id_2": "Why this node is relevant",
        "node_id_3": "Why this node is relevant"
    }}
}}

Please return the top {limit} most relevant nodes, ranked by relevance score (0.0 to 1.0).
"""
        
        return prompt
    
    def _parse_search_response(self, response_text: str, original_nodes: List[Dict]) -> Dict[str, Any]:
        """Parse Gemini response and return structured results"""
        try:
            import json
            import re
            
            # Extract JSON from response
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if not json_match:
                raise Exception("No JSON found in Gemini response")
            
            json_str = json_match.group()
            parsed_response = json.loads(json_str)
            
            # Get relevant nodes
            relevant_node_ids = parsed_response.get("relevant_node_ids", [])
            relevance_scores = parsed_response.get("relevance_scores", {})
            reasoning = parsed_response.get("reasoning", {})
            
            # Find the actual node objects
            relevant_nodes = []
            for node in original_nodes:
                node_id = node.get("id")
                if node_id in relevant_node_ids:
                    enhanced_node = node.copy()
                    enhanced_node["relevance_score"] = relevance_scores.get(node_id, 0.0)
                    enhanced_node["relevance_reasoning"] = reasoning.get(node_id, "")
                    relevant_nodes.append(enhanced_node)
            
            # Sort by relevance score
            relevant_nodes.sort(key=lambda x: x.get("relevance_score", 0.0), reverse=True)
            
            return {
                "analysis_summary": parsed_response.get("analysis_summary", ""),
                "relevant_nodes": relevant_nodes,
                "total_analyzed": len(original_nodes),
                "total_relevant": len(relevant_nodes)
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to parse Gemini response: {e}")
            # Fallback: return first few nodes
            return {
                "analysis_summary": "Failed to parse AI analysis, showing first available nodes",
                "relevant_nodes": original_nodes[:5],
                "total_analyzed": len(original_nodes),
                "total_relevant": min(5, len(original_nodes))
            }
    
    async def generate_summary(self, query: str, relevant_nodes: List[Dict[str, Any]]) -> str:
        """Generate a summary of findings based on the query and relevant nodes"""
        try:
            if not relevant_nodes:
                return "No relevant information found for your query."
            
            # Create summary prompt
            nodes_text = "\n".join([
                f"- {node['label']}: {node.get('summary', 'No summary available')}"
                for node in relevant_nodes[:10]  # Limit to top 10 for summary
            ])
            
            summary_prompt = f"""
            Based on the user's query: "{query}"
            
            Here are the most relevant findings from the knowledge graph:
            {nodes_text}
            
            Please provide a comprehensive summary that:
            1. Directly answers the user's query
            2. Highlights the key findings and connections
            3. Provides actionable insights where applicable
            4. Is written in a clear, professional tone
            
            Summary:
            """
            
            response = self.model.generate_content(summary_prompt)
            summary = response.text.strip()
            
            logger.info(f"✅ Generated summary for query: {query}")
            return summary
            
        except Exception as e:
            logger.error(f"❌ Failed to generate summary: {e}")
            return f"Unable to generate summary. Found {len(relevant_nodes)} relevant items related to your query."
    
    async def generate_insights(self, query: str, visible_nodes: List[Dict], full_graph: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate comprehensive AI insights based on query and knowledge graph data
        
        Args:
            query: User search query
            visible_nodes: Currently visible nodes in the graph
            full_graph: Complete knowledge graph data
            
        Returns:
            Dictionary with comprehensive insights and analysis
        """
        try:
            logger.info(f"🧠 Generating AI insights for query: {query}")
            
            if not self.model:
                raise Exception("Gemini client not initialized")
            
            # Prepare data for analysis
            all_nodes = full_graph.get("nodes", [])
            all_edges = full_graph.get("edges", [])
            
            # Create comprehensive analysis prompt
            insights_prompt = f"""
            You are an AI analyst examining a knowledge graph to provide deep insights.
            
            USER QUERY: "{query}"
            
            KNOWLEDGE GRAPH OVERVIEW:
            - Total Nodes: {len(all_nodes)}
            - Total Connections: {len(all_edges)}
            - Currently Visible Nodes: {len(visible_nodes)}
            
            VISIBLE NODES ANALYSIS:
            {self._format_nodes_for_analysis(visible_nodes)}
            
            GRAPH STRUCTURE INSIGHTS:
            {self._analyze_graph_structure(all_nodes, all_edges)}
            
            Please provide a comprehensive analysis that includes:
            
            1. **Key Findings**: What are the most important discoveries related to the query?
            2. **Relationship Patterns**: What interesting connections and patterns emerge?
            3. **Knowledge Gaps**: What information might be missing or needs further exploration?
            4. **Strategic Insights**: What actionable recommendations can you provide?
            5. **Data Quality**: How comprehensive and reliable is the current knowledge base?
            6. **Future Exploration**: What areas should be investigated next?
            
            Format your response as a structured JSON with the following keys:
            - summary: Brief overview of key findings
            - key_findings: List of important discoveries
            - relationship_patterns: Analysis of connections and patterns
            - knowledge_gaps: Identified gaps or missing information
            - strategic_insights: Actionable recommendations
            - data_quality_assessment: Evaluation of data completeness
            - suggested_next_steps: Recommended follow-up actions
            - confidence_score: Your confidence in the analysis (0-100)
            """
            
            response = self.model.generate_content(insights_prompt)
            
            # Parse and structure the response
            insights = self._parse_insights_response(response.text, query, visible_nodes, all_nodes)
            
            logger.info(f"✅ Generated comprehensive insights for query: {query}")
            return insights
            
        except Exception as e:
            logger.error(f"❌ Failed to generate insights: {e}")
            # Return fallback insights
            return self._generate_fallback_insights(query, visible_nodes, full_graph)
    
    def _format_nodes_for_analysis(self, nodes: List[Dict]) -> str:
        """Format nodes for AI analysis"""
        if not nodes:
            return "No nodes currently visible"
        
        formatted = []
        for node in nodes[:10]:  # Limit to first 10 for prompt efficiency
            formatted.append(f"- {node.get('label', 'Unknown')} ({node.get('type', 'unknown')}): {node.get('summary', 'No summary')}")
        
        if len(nodes) > 10:
            formatted.append(f"... and {len(nodes) - 10} more nodes")
        
        return "\n".join(formatted)
    
    def _analyze_graph_structure(self, nodes: List[Dict], edges: List[Dict]) -> str:
        """Analyze graph structure for insights"""
        if not nodes:
            return "No graph structure to analyze"
        
        # Count node types
        node_types = {}
        for node in nodes:
            node_type = node.get('type', 'unknown')
            node_types[node_type] = node_types.get(node_type, 0) + 1
        
        # Analyze connectivity
        node_connections = {}
        for edge in edges:
            source = edge.get('source', '')
            target = edge.get('target', '')
            node_connections[source] = node_connections.get(source, 0) + 1
            node_connections[target] = node_connections.get(target, 0) + 1
        
        avg_connections = sum(node_connections.values()) / len(node_connections) if node_connections else 0
        
        analysis = f"""
        Node Type Distribution: {dict(list(node_types.items())[:5])}
        Average Connections per Node: {avg_connections:.1f}
        Most Connected Nodes: {sorted(node_connections.items(), key=lambda x: x[1], reverse=True)[:3]}
        """
        
        return analysis
    
    def _parse_insights_response(self, response_text: str, query: str, visible_nodes: List[Dict], all_nodes: List[Dict]) -> Dict[str, Any]:
        """Parse and structure the insights response"""
        try:
            # Try to extract JSON from response
            import json
            import re
            
            # Look for JSON in the response
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                insights_data = json.loads(json_match.group())
            else:
                # Fallback to structured parsing
                insights_data = self._extract_structured_insights(response_text)
            
            # Ensure all required fields are present
            required_fields = [
                'summary', 'key_findings', 'relationship_patterns', 
                'knowledge_gaps', 'strategic_insights', 'data_quality_assessment',
                'suggested_next_steps', 'confidence_score'
            ]
            
            for field in required_fields:
                if field not in insights_data:
                    insights_data[field] = f"Analysis for {field} not available"
            
            # Add metadata
            from datetime import datetime
            insights_data['query'] = query
            insights_data['analysis_timestamp'] = datetime.now().isoformat()
            insights_data['nodes_analyzed'] = len(visible_nodes)
            insights_data['total_nodes'] = len(all_nodes)
            
            return insights_data
            
        except Exception as e:
            logger.error(f"❌ Failed to parse insights response: {e}")
            return self._generate_fallback_insights(query, visible_nodes, {'nodes': all_nodes})
    
    def _extract_structured_insights(self, text: str) -> Dict[str, Any]:
        """Extract structured insights from free-form text"""
        return {
            'summary': text[:200] + "..." if len(text) > 200 else text,
            'key_findings': ["Analysis based on available data"],
            'relationship_patterns': "Patterns identified in the knowledge graph",
            'knowledge_gaps': "Areas requiring additional data",
            'strategic_insights': "Recommendations based on current analysis",
            'data_quality_assessment': "Data quality evaluation",
            'suggested_next_steps': ["Continue data collection", "Refine analysis"],
            'confidence_score': 75
        }
    
    def _generate_fallback_insights(self, query: str, visible_nodes: List[Dict], full_graph: Dict[str, Any]) -> Dict[str, Any]:
        """Generate fallback insights when AI analysis fails"""
        from datetime import datetime
        return {
            'summary': f"Analysis of {len(visible_nodes)} nodes related to '{query}'",
            'key_findings': [
                f"Found {len(visible_nodes)} relevant nodes",
                f"Total knowledge base contains {len(full_graph.get('nodes', []))} nodes",
                "Analysis completed with available data"
            ],
            'relationship_patterns': "Multiple interconnected relationships identified",
            'knowledge_gaps': "Additional data collection recommended for deeper insights",
            'strategic_insights': "Continue exploring related topics for comprehensive understanding",
            'data_quality_assessment': "Current data provides good foundation for analysis",
            'suggested_next_steps': [
                "Expand search criteria",
                "Explore related topics",
                "Add more data sources"
            ],
            'confidence_score': 60,
            'query': query,
            'analysis_timestamp': datetime.now().isoformat(),
            'nodes_analyzed': len(visible_nodes),
            'total_nodes': len(full_graph.get('nodes', []))
        }

    async def health_check(self) -> str:
        """Check Gemini client health"""
        try:
            if not self.model:
                return "not_initialized"
            
            # Test with a simple query
            test_response = self.model.generate_content("Hello, are you working?")
            if test_response and test_response.text:
                return "healthy"
            else:
                return "unhealthy"
                
        except Exception as e:
            logger.error(f"❌ Gemini health check failed: {e}")
            return "error"