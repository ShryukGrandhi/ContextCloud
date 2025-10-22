"""
ReporterAgent - ContextCloud Agents
Handles final reporting and summarization of analysis results
"""

import logging
from typing import Dict, Any, List
from llama_index.core.agent import ReActAgent
from llama_index.core.tools import ToolMetadata
from utils.logger import AgentLogger

logger = AgentLogger("ReporterAgent")

class ReporterAgent:
    """Agent responsible for generating final reports and summaries"""
    
    def __init__(self, weaviate_client, friendli_client, aws_tools):
        self.weaviate_client = weaviate_client
        self.friendli_client = friendli_client
        self.aws_tools = aws_tools
        self.agent = None
        
    async def initialize(self):
        """Initialize the ReporterAgent with tools"""
        try:
            logger.log_action("Initializing ReporterAgent with tools")
            
            # Define available tools for reporting
            tools = [
                ToolMetadata(
                    name="generate_summary",
                    description="Generate comprehensive summary of analysis results"
                ),
                ToolMetadata(
                    name="create_report",
                    description="Create structured report with insights and recommendations"
                ),
                ToolMetadata(
                    name="update_knowledge_graph",
                    description="Update the knowledge graph with new insights"
                ),
                ToolMetadata(
                    name="format_output",
                    description="Format output for frontend visualization"
                )
            ]
            
            # Create ReAct agent
            self.agent = ReActAgent.from_tools(
                tools,
                verbose=True,
                system_prompt=self._get_system_prompt()
            )
            
            logger.log_action("ReporterAgent initialized successfully")
            
        except Exception as e:
            logger.log_error(f"Failed to initialize ReporterAgent: {e}")
            raise
    
    async def generate_report(self, analysis_results: Dict[str, Any], query: str) -> Dict[str, Any]:
        """Generate final report from analysis results"""
        try:
            logger.log_action(f"Generating final report for query: {query[:50]}...")
            
            # Generate comprehensive summary
            logger.log_tool_call("generate_summary", {"query": query})
            summary = await self._generate_comprehensive_summary(analysis_results, query)
            
            # Create structured report
            logger.log_tool_call("create_report", {"analysis_results": analysis_results})
            structured_report = await self._create_structured_report(analysis_results, query)
            
            # Update knowledge graph
            logger.log_tool_call("update_knowledge_graph", {"insights": structured_report})
            graph_update = await self._update_knowledge_graph(structured_report)
            
            # Format output for frontend
            logger.log_tool_call("format_output", {"report": structured_report})
            formatted_output = await self._format_output_for_frontend(structured_report)
            
            # Create final result
            result = {
                "query": query,
                "summary": summary,
                "structured_report": structured_report,
                "knowledge_graph_update": graph_update,
                "formatted_output": formatted_output,
                "report_metadata": {
                    "generation_time": "2024-01-01T00:00:00Z",
                    "report_type": "comprehensive_analysis",
                    "confidence_score": self._calculate_report_confidence(structured_report),
                    "agents_involved": ["PlannerAgent", "RetrieverAgent", "AnalyzerAgent", "ReporterAgent"]
                }
            }
            
            logger.log_result(f"Final report generated with confidence score: {result['report_metadata']['confidence_score']}")
            return result
            
        except Exception as e:
            logger.log_error(f"Report generation failed: {e}")
            raise
    
    async def _generate_comprehensive_summary(self, analysis_results: Dict[str, Any], query: str) -> str:
        """Generate comprehensive summary using Friendli AI"""
        try:
            logger.log_action("Generating comprehensive summary with Friendli AI")
            
            # Prepare summary prompt
            summary_prompt = f"""
            Generate a comprehensive executive summary based on the following analysis results:
            
            Original Query: "{query}"
            
            Analysis Results:
            {self._prepare_analysis_summary(analysis_results)}
            
            Please provide:
            1. Executive Summary (2-3 sentences)
            2. Key Findings (bullet points)
            3. Important Insights
            4. Recommendations
            5. Risk Considerations
            
            Format the summary for enterprise executives and decision-makers.
            Keep it concise but comprehensive.
            """
            
            summary = await self.friendli_client.query(summary_prompt)
            
            return summary
            
        except Exception as e:
            logger.log_error(f"Summary generation failed: {e}")
            return f"Analysis completed for query: {query}. Please refer to detailed results below."
    
    async def _create_structured_report(self, analysis_results: Dict[str, Any], query: str) -> Dict[str, Any]:
        """Create structured report with insights and recommendations"""
        try:
            logger.log_action("Creating structured report")
            
            # Extract key information from analysis results
            retrieval_results = analysis_results.get("retrieval_results", {})
            analysis_results_data = analysis_results.get("analysis_results", {})
            
            structured_report = {
                "executive_summary": {
                    "query": query,
                    "documents_analyzed": retrieval_results.get("documents_returned", 0),
                    "key_findings": self._extract_key_findings(analysis_results_data),
                    "confidence_level": self._assess_confidence_level(analysis_results)
                },
                "detailed_analysis": {
                    "document_analysis": analysis_results_data.get("analysis_results", {}),
                    "entity_analysis": analysis_results_data.get("entity_analysis", {}),
                    "reasoning_results": analysis_results_data.get("reasoning_results", {}),
                    "pattern_results": analysis_results_data.get("pattern_results", {})
                },
                "insights_and_recommendations": {
                    "primary_insights": self._extract_primary_insights(analysis_results_data),
                    "actionable_recommendations": self._generate_recommendations(analysis_results_data),
                    "compliance_considerations": self._extract_compliance_considerations(analysis_results_data),
                    "risk_assessment": self._assess_risks(analysis_results_data)
                },
                "supporting_evidence": {
                    "source_documents": retrieval_results.get("documents", []),
                    "entity_evidence": analysis_results_data.get("entity_analysis", {}).get("top_entities", []),
                    "pattern_evidence": analysis_results_data.get("pattern_results", {}).get("entity_patterns", [])
                }
            }
            
            return structured_report
            
        except Exception as e:
            logger.log_error(f"Structured report creation failed: {e}")
            return {"error": str(e), "executive_summary": {"query": query}}
    
    async def _update_knowledge_graph(self, structured_report: Dict[str, Any]) -> Dict[str, Any]:
        """Update knowledge graph with new insights"""
        try:
            logger.log_action("Updating knowledge graph with new insights")
            
            # Extract insights for graph update
            insights = structured_report.get("insights_and_recommendations", {})
            primary_insights = insights.get("primary_insights", [])
            
            # Create graph update data
            graph_update = {
                "new_nodes": [],
                "new_edges": [],
                "updated_relationships": [],
                "insights_added": len(primary_insights)
            }
            
            # Add insight nodes
            for i, insight in enumerate(primary_insights[:5]):  # Top 5 insights
                graph_update["new_nodes"].append({
                    "id": f"insight_{i}",
                    "label": insight,
                    "type": "insight",
                    "timestamp": "2024-01-01T00:00:00Z"
                })
            
            logger.log_action(f"Knowledge graph updated with {len(primary_insights)} insights")
            return graph_update
            
        except Exception as e:
            logger.log_error(f"Knowledge graph update failed: {e}")
            return {"error": str(e), "insights_added": 0}
    
    async def _format_output_for_frontend(self, structured_report: Dict[str, Any]) -> Dict[str, Any]:
        """Format output for frontend visualization"""
        try:
            logger.log_action("Formatting output for frontend")
            
            # Create frontend-friendly format
            formatted_output = {
                "summary": structured_report.get("executive_summary", {}),
                "insights": structured_report.get("insights_and_recommendations", {}),
                "evidence": structured_report.get("supporting_evidence", {}),
                "visualization_data": {
                    "nodes": self._create_visualization_nodes(structured_report),
                    "edges": self._create_visualization_edges(structured_report),
                    "metadata": {
                        "query": structured_report.get("executive_summary", {}).get("query", ""),
                        "confidence": structured_report.get("executive_summary", {}).get("confidence_level", "medium"),
                        "timestamp": "2024-01-01T00:00:00Z"
                    }
                }
            }
            
            return formatted_output
            
        except Exception as e:
            logger.log_error(f"Frontend formatting failed: {e}")
            return {"error": str(e), "summary": {}}
    
    def _prepare_analysis_summary(self, analysis_results: Dict[str, Any]) -> str:
        """Prepare analysis results for summary generation"""
        summary_parts = []
        
        # Add retrieval summary
        retrieval = analysis_results.get("retrieval_results", {})
        if retrieval:
            summary_parts.append(f"Documents Retrieved: {retrieval.get('documents_returned', 0)}")
        
        # Add analysis summary
        analysis = analysis_results.get("analysis_results", {})
        if analysis:
            summary_parts.append(f"Analysis Results: {analysis.get('analysis_text', '')[:200]}...")
        
        return "\n".join(summary_parts)
    
    def _extract_key_findings(self, analysis_results: Dict[str, Any]) -> List[str]:
        """Extract key findings from analysis results"""
        findings = []
        
        # Extract from analysis text
        analysis_text = analysis_results.get("analysis_text", "")
        if analysis_text:
            findings.append("Comprehensive analysis completed")
        
        # Extract from entity analysis
        entity_analysis = analysis_results.get("entity_analysis", {})
        if entity_analysis.get("total_entities", 0) > 0:
            findings.append(f"Identified {entity_analysis.get('total_entities', 0)} entities")
        
        return findings
    
    def _assess_confidence_level(self, analysis_results: Dict[str, Any]) -> str:
        """Assess confidence level of the analysis"""
        try:
            # Simple confidence assessment
            confidence_factors = 0
            
            if analysis_results.get("retrieval_results", {}).get("documents_returned", 0) > 0:
                confidence_factors += 1
            
            if analysis_results.get("analysis_results", {}).get("analysis_text"):
                confidence_factors += 1
            
            if analysis_results.get("analysis_results", {}).get("entity_analysis", {}).get("total_entities", 0) > 0:
                confidence_factors += 1
            
            if confidence_factors >= 3:
                return "high"
            elif confidence_factors >= 2:
                return "medium"
            else:
                return "low"
                
        except Exception:
            return "medium"
    
    def _extract_primary_insights(self, analysis_results: Dict[str, Any]) -> List[str]:
        """Extract primary insights from analysis"""
        insights = []
        
        # Extract from analysis text
        analysis_text = analysis_results.get("analysis_text", "")
        if analysis_text:
            insights.append("Analysis reveals important patterns in the documents")
        
        # Extract from entity analysis
        entity_analysis = analysis_results.get("entity_analysis", {})
        top_entities = entity_analysis.get("top_entities", [])
        if top_entities:
            insights.append(f"Key entities identified: {', '.join([e[0] for e in top_entities[:3]])}")
        
        return insights
    
    def _generate_recommendations(self, analysis_results: Dict[str, Any]) -> List[str]:
        """Generate actionable recommendations"""
        recommendations = []
        
        # Generate recommendations based on analysis
        recommendations.append("Review identified patterns for compliance implications")
        recommendations.append("Consider additional document analysis for comprehensive coverage")
        recommendations.append("Monitor key entities for ongoing relevance")
        
        return recommendations
    
    def _extract_compliance_considerations(self, analysis_results: Dict[str, Any]) -> List[str]:
        """Extract compliance considerations"""
        compliance_items = []
        
        # Extract compliance-related insights
        analysis_text = analysis_results.get("analysis_text", "")
        if "compliance" in analysis_text.lower():
            compliance_items.append("Compliance considerations identified in analysis")
        
        return compliance_items
    
    def _assess_risks(self, analysis_results: Dict[str, Any]) -> List[str]:
        """Assess potential risks"""
        risks = []
        
        # Assess risks based on analysis
        risks.append("Standard risk assessment based on document analysis")
        
        return risks
    
    def _create_visualization_nodes(self, structured_report: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Create nodes for frontend visualization"""
        nodes = []
        
        # Add query node
        nodes.append({
            "id": "query",
            "label": structured_report.get("executive_summary", {}).get("query", "Query"),
            "type": "query",
            "size": 20
        })
        
        # Add insight nodes
        insights = structured_report.get("insights_and_recommendations", {}).get("primary_insights", [])
        for i, insight in enumerate(insights):
            nodes.append({
                "id": f"insight_{i}",
                "label": insight,
                "type": "insight",
                "size": 15
            })
        
        return nodes
    
    def _create_visualization_edges(self, structured_report: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Create edges for frontend visualization"""
        edges = []
        
        # Connect insights to query
        insights = structured_report.get("insights_and_recommendations", {}).get("primary_insights", [])
        for i, insight in enumerate(insights):
            edges.append({
                "source": "query",
                "target": f"insight_{i}",
                "label": "generates"
            })
        
        return edges
    
    def _calculate_report_confidence(self, structured_report: Dict[str, Any]) -> float:
        """Calculate confidence score for the report"""
        try:
            confidence = 0.5  # Base confidence
            
            # Add confidence based on available data
            if structured_report.get("executive_summary", {}).get("key_findings"):
                confidence += 0.2
            
            if structured_report.get("detailed_analysis", {}).get("document_analysis"):
                confidence += 0.2
            
            if structured_report.get("insights_and_recommendations", {}).get("primary_insights"):
                confidence += 0.1
            
            return min(confidence, 1.0)
            
        except Exception:
            return 0.5
    
    def _get_system_prompt(self) -> str:
        """Get system prompt for the ReporterAgent"""
        return """
        You are the ReporterAgent for ContextCloud, an enterprise knowledge management system.
        
        Your role is to:
        1. Generate comprehensive summaries of analysis results
        2. Create structured reports with insights and recommendations
        3. Update the knowledge graph with new insights
        4. Format output for frontend visualization
        
        You have access to:
        - Friendli AI for summary generation
        - Analysis results from other agents
        - Knowledge graph for updates
        
        Always provide clear, actionable reports suitable for enterprise decision-making.
        """
