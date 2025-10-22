"""
PlannerAgent - ContextCloud Agents
Orchestrates the workflow and decides which agents to call
"""

import logging
from typing import Dict, Any, List
from llama_index.core.agent import ReActAgent
from llama_index.core.tools import ToolMetadata
from utils.logger import AgentLogger

logger = AgentLogger("PlannerAgent")

class PlannerAgent:
    """Agent responsible for interpreting queries and planning workflows"""
    
    def __init__(self, weaviate_client, friendli_client, aws_tools):
        self.weaviate_client = weaviate_client
        self.friendli_client = friendli_client
        self.aws_tools = aws_tools
        self.agent = None
        
    async def initialize(self):
        """Initialize the PlannerAgent with tools"""
        try:
            logger.log_action("Initializing PlannerAgent with tools")
            
            # Define available tools for planning
            tools = [
                ToolMetadata(
                    name="analyze_query_intent",
                    description="Analyze user query to determine intent and required workflow"
                ),
                ToolMetadata(
                    name="plan_workflow",
                    description="Create a workflow plan based on query analysis"
                ),
                ToolMetadata(
                    name="coordinate_agents",
                    description="Coordinate with other agents to execute the workflow"
                )
            ]
            
            # Create ReAct agent
            self.agent = ReActAgent.from_tools(
                tools,
                verbose=True,
                system_prompt=self._get_system_prompt()
            )
            
            logger.log_action("PlannerAgent initialized successfully")
            
        except Exception as e:
            logger.log_error(f"Failed to initialize PlannerAgent: {e}")
            raise
    
    async def process_query(self, query: str) -> Dict[str, Any]:
        """Process user query and create workflow plan"""
        try:
            logger.log_action(f"Processing query: {query[:50]}...")
            
            # Analyze query intent
            intent_analysis = await self._analyze_query_intent(query)
            logger.log_tool_call("analyze_query_intent", {"query": query})
            
            # Create workflow plan
            workflow_plan = await self._create_workflow_plan(query, intent_analysis)
            logger.log_tool_call("plan_workflow", {"intent": intent_analysis})
            
            # Return planning results
            result = {
                "query": query,
                "intent_analysis": intent_analysis,
                "workflow_plan": workflow_plan,
                "next_agents": self._determine_next_agents(intent_analysis)
            }
            
            logger.log_result(f"Created workflow plan with {len(workflow_plan['steps'])} steps")
            return result
            
        except Exception as e:
            logger.log_error(f"Query processing failed: {e}")
            raise
    
    async def _analyze_query_intent(self, query: str) -> Dict[str, Any]:
        """Analyze user query to determine intent"""
        try:
            analysis_prompt = f"""
            Analyze the following user query and determine:
            1. The primary intent (search, analysis, summarization, compliance check, etc.)
            2. The type of information needed
            3. The complexity level (simple, moderate, complex)
            4. Whether document retrieval is needed
            5. Whether analysis or reasoning is required
            6. Whether summarization is needed
            
            Query: "{query}"
            
            Return a structured analysis in JSON format.
            """
            
            response = await self.friendli_client.query(analysis_prompt)
            
            # Try to parse structured response, fallback to simple analysis
            try:
                import json
                analysis = json.loads(response)
            except:
                analysis = {
                    "intent": "general_query",
                    "complexity": "moderate",
                    "needs_retrieval": True,
                    "needs_analysis": True,
                    "needs_summarization": True,
                    "raw_analysis": response
                }
            
            logger.log_action("Query intent analysis completed")
            return analysis
            
        except Exception as e:
            logger.log_error(f"Intent analysis failed: {e}")
            return {
                "intent": "general_query",
                "complexity": "moderate",
                "needs_retrieval": True,
                "needs_analysis": True,
                "needs_summarization": True,
                "error": str(e)
            }
    
    async def _create_workflow_plan(self, query: str, intent_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Create a workflow plan based on query analysis"""
        try:
            plan_prompt = f"""
            Create a detailed workflow plan for processing this query based on the intent analysis:
            
            Query: "{query}"
            Intent Analysis: {intent_analysis}
            
            Create a step-by-step plan that includes:
            1. Document retrieval strategy
            2. Analysis requirements
            3. Reasoning steps needed
            4. Output format requirements
            
            Return a structured workflow plan.
            """
            
            response = await self.friendli_client.query(plan_prompt)
            
            # Create workflow plan structure
            workflow_plan = {
                "steps": [
                    {
                        "step": 1,
                        "agent": "RetrieverAgent",
                        "action": "retrieve_relevant_documents",
                        "description": "Find documents relevant to the query"
                    },
                    {
                        "step": 2,
                        "agent": "AnalyzerAgent",
                        "action": "analyze_documents",
                        "description": "Analyze retrieved documents for insights"
                    },
                    {
                        "step": 3,
                        "agent": "ReporterAgent",
                        "action": "generate_summary",
                        "description": "Generate final summary and insights"
                    }
                ],
                "estimated_complexity": intent_analysis.get("complexity", "moderate"),
                "expected_output_type": "comprehensive_analysis"
            }
            
            logger.log_action("Workflow plan created")
            return workflow_plan
            
        except Exception as e:
            logger.log_error(f"Workflow planning failed: {e}")
            return {
                "steps": [],
                "error": str(e)
            }
    
    def _determine_next_agents(self, intent_analysis: Dict[str, Any]) -> List[str]:
        """Determine which agents should be called next"""
        next_agents = []
        
        if intent_analysis.get("needs_retrieval", True):
            next_agents.append("RetrieverAgent")
        
        if intent_analysis.get("needs_analysis", True):
            next_agents.append("AnalyzerAgent")
        
        if intent_analysis.get("needs_summarization", True):
            next_agents.append("ReporterAgent")
        
        # Always include ReporterAgent as final step
        if "ReporterAgent" not in next_agents:
            next_agents.append("ReporterAgent")
        
        return next_agents
    
    def _get_system_prompt(self) -> str:
        """Get system prompt for the PlannerAgent"""
        return """
        You are the PlannerAgent for ContextCloud, an enterprise knowledge management system.
        
        Your role is to:
        1. Analyze user queries to understand intent and requirements
        2. Create workflow plans for processing queries
        3. Coordinate with other agents (Retriever, Analyzer, Reporter)
        4. Ensure efficient and effective knowledge retrieval and analysis
        
        You have access to:
        - Weaviate vector database for document storage
        - Friendli AI for reasoning and analysis
        - AWS services for document processing
        
        Always provide clear, actionable plans that lead to comprehensive insights.
        """
