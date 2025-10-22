"""
Agent Orchestrator - ContextCloud Agents
Coordinates the multi-agent workflow using LlamaIndex
"""

import logging
from typing import Dict, Any, List, Optional
from utils.logger import AgentLogger, setup_logger

from .planner import PlannerAgent
from .retriever import RetrieverAgent
from .analyzer import AnalyzerAgent
from .reporter import ReporterAgent

logger = setup_logger(__name__)

class AgentOrchestrator:
    """Orchestrates the multi-agent workflow for ContextCloud"""
    
    def __init__(self, weaviate_client, friendli_client, aws_tools):
        self.weaviate_client = weaviate_client
        self.friendli_client = friendli_client
        self.aws_tools = aws_tools
        
        # Initialize agents
        self.planner_agent = None
        self.retriever_agent = None
        self.analyzer_agent = None
        self.reporter_agent = None
        
        # Agent status tracking
        self.agent_status = {
            "PlannerAgent": "not_initialized",
            "RetrieverAgent": "not_initialized",
            "AnalyzerAgent": "not_initialized",
            "ReporterAgent": "not_initialized"
        }
        
        self.agent_logger = AgentLogger("Orchestrator")
    
    async def initialize(self):
        """Initialize all agents"""
        try:
            self.agent_logger.log_action("Initializing all agents")
            
            # Initialize PlannerAgent
            self.planner_agent = PlannerAgent(
                self.weaviate_client,
                self.friendli_client,
                self.aws_tools
            )
            await self.planner_agent.initialize()
            self.agent_status["PlannerAgent"] = "ready"
            self.agent_logger.log_action("PlannerAgent initialized")
            
            # Initialize RetrieverAgent
            self.retriever_agent = RetrieverAgent(
                self.weaviate_client,
                self.friendli_client,
                self.aws_tools
            )
            await self.retriever_agent.initialize()
            self.agent_status["RetrieverAgent"] = "ready"
            self.agent_logger.log_action("RetrieverAgent initialized")
            
            # Initialize AnalyzerAgent
            self.analyzer_agent = AnalyzerAgent(
                self.weaviate_client,
                self.friendli_client,
                self.aws_tools
            )
            await self.analyzer_agent.initialize()
            self.agent_status["AnalyzerAgent"] = "ready"
            self.agent_logger.log_action("AnalyzerAgent initialized")
            
            # Initialize ReporterAgent
            self.reporter_agent = ReporterAgent(
                self.weaviate_client,
                self.friendli_client,
                self.aws_tools
            )
            await self.reporter_agent.initialize()
            self.agent_status["ReporterAgent"] = "ready"
            self.agent_logger.log_action("ReporterAgent initialized")
            
            self.agent_logger.log_result("All agents initialized successfully")
            
        except Exception as e:
            self.agent_logger.log_error(f"Agent initialization failed: {e}")
            raise
    
    async def process_query(self, query: str) -> Dict[str, Any]:
        """Process a user query through the complete agent workflow"""
        try:
            self.agent_logger.log_action(f"Starting multi-agent workflow for query: {query[:50]}...")
            
            # Step 1: Planning
            self.agent_logger.log_action("Step 1: Planning workflow")
            planning_results = await self.planner_agent.process_query(query)
            self.agent_status["PlannerAgent"] = "completed"
            
            # Step 2: Document Retrieval
            self.agent_logger.log_action("Step 2: Retrieving documents")
            retrieval_results = await self.retriever_agent.retrieve_documents(
                query, 
                limit=10
            )
            self.agent_status["RetrieverAgent"] = "completed"
            
            # Step 3: Document Analysis
            self.agent_logger.log_action("Step 3: Analyzing documents")
            analysis_results = await self.analyzer_agent.analyze_documents(
                retrieval_results.get("documents", []),
                query
            )
            self.agent_status["AnalyzerAgent"] = "completed"
            
            # Step 4: Report Generation
            self.agent_logger.log_action("Step 4: Generating final report")
            final_report = await self.reporter_agent.generate_report(
                {
                    "retrieval_results": retrieval_results,
                    "analysis_results": analysis_results,
                    "planning_results": planning_results
                },
                query
            )
            self.agent_status["ReporterAgent"] = "completed"
            
            # Combine all results
            result = {
                "query": query,
                "workflow_status": "completed",
                "planning_results": planning_results,
                "retrieval_results": retrieval_results,
                "analysis_results": analysis_results,
                "final_report": final_report,
                "agent_status": self.agent_status.copy(),
                "workflow_metadata": {
                    "total_agents": 4,
                    "agents_completed": 4,
                    "workflow_duration": "estimated_30_seconds",
                    "confidence_score": final_report.get("report_metadata", {}).get("confidence_score", 0.8)
                }
            }
            
            self.agent_logger.log_result("Multi-agent workflow completed successfully")
            return result
            
        except Exception as e:
            self.agent_logger.log_error(f"Multi-agent workflow failed: {e}")
            # Update agent status to reflect failure
            for agent_name in self.agent_status:
                if self.agent_status[agent_name] == "ready":
                    self.agent_status[agent_name] = "failed"
            
            raise
    
    async def get_status(self) -> Dict[str, Any]:
        """Get current status of all agents"""
        try:
            return {
                "agents": self.agent_status.copy(),
                "orchestrator_status": "ready" if all(
                    status == "ready" for status in self.agent_status.values()
                ) else "initializing",
                "total_agents": len(self.agent_status),
                "ready_agents": sum(1 for status in self.agent_status.values() if status == "ready"),
                "completed_agents": sum(1 for status in self.agent_status.values() if status == "completed"),
                "failed_agents": sum(1 for status in self.agent_status.values() if status == "failed")
            }
            
        except Exception as e:
            self.agent_logger.log_error(f"Status retrieval failed: {e}")
            return {
                "agents": self.agent_status.copy(),
                "orchestrator_status": "error",
                "error": str(e)
            }
    
    async def reset_agents(self):
        """Reset all agents to ready state"""
        try:
            self.agent_logger.log_action("Resetting all agents to ready state")
            
            for agent_name in self.agent_status:
                if self.agent_status[agent_name] in ["completed", "failed"]:
                    self.agent_status[agent_name] = "ready"
            
            self.agent_logger.log_result("All agents reset to ready state")
            
        except Exception as e:
            self.agent_logger.log_error(f"Agent reset failed: {e}")
            raise
    
    async def get_agent_logs(self) -> List[Dict[str, Any]]:
        """Get logs from all agents"""
        try:
            logs = []
            
            # Add orchestrator logs
            logs.append({
                "agent": "Orchestrator",
                "timestamp": "2024-01-01T00:00:00Z",
                "message": "Multi-agent workflow orchestration",
                "status": "active"
            })
            
            # Add individual agent logs (simplified for demo)
            for agent_name, status in self.agent_status.items():
                logs.append({
                    "agent": agent_name,
                    "timestamp": "2024-01-01T00:00:00Z",
                    "message": f"Agent status: {status}",
                    "status": status
                })
            
            return logs
            
        except Exception as e:
            self.agent_logger.log_error(f"Log retrieval failed: {e}")
            return []
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform health check on all agents"""
        try:
            health_status = {
                "orchestrator": "healthy",
                "agents": {},
                "services": {}
            }
            
            # Check agent health
            for agent_name, status in self.agent_status.items():
                if status == "ready":
                    health_status["agents"][agent_name] = "healthy"
                elif status == "completed":
                    health_status["agents"][agent_name] = "healthy"
                else:
                    health_status["agents"][agent_name] = "unhealthy"
            
            # Check service health
            try:
                weaviate_health = await self.weaviate_client.health_check()
                health_status["services"]["weaviate"] = weaviate_health
            except Exception:
                health_status["services"]["weaviate"] = "error"
            
            try:
                friendli_health = await self.friendli_client.health_check()
                health_status["services"]["friendli"] = friendli_health
            except Exception:
                health_status["services"]["friendli"] = "error"
            
            try:
                aws_health = await self.aws_tools.health_check()
                health_status["services"]["aws"] = aws_health
            except Exception:
                health_status["services"]["aws"] = "error"
            
            return health_status
            
        except Exception as e:
            self.agent_logger.log_error(f"Health check failed: {e}")
            return {
                "orchestrator": "error",
                "agents": {},
                "services": {},
                "error": str(e)
            }
