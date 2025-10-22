"""
ContextCloud Agents - Main FastAPI Application
AWS AI Agents Hack Day Entry

Multi-agent system using LlamaIndex, Weaviate, and Friendli AI
"""

import os
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
import uvicorn

from agents.orchestrator import AgentOrchestrator
from services.weaviate_client import WeaviateClient
from services.friendli_client import FriendliClient
from services.gemini_client import GeminiClient
from tools.aws_tools import AWSTools
from utils.logger import setup_logger

# Load environment variables
load_dotenv()

# Setup logging
logger = setup_logger(__name__)

# Global clients
weaviate_client = None
friendli_client = None
gemini_client = None
aws_tools = None
agent_orchestrator = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize and cleanup resources"""
    global weaviate_client, friendli_client, gemini_client, aws_tools, agent_orchestrator
    
    logger.info("🚀 Starting ContextCloud Agents...")
    
    try:
        # Initialize clients
        weaviate_client = WeaviateClient()
        await weaviate_client.initialize()
        
        friendli_client = FriendliClient()
        
        gemini_client = GeminiClient()
        await gemini_client.initialize()
        
        # aws_tools = AWSTools()
        # await aws_tools.initialize()
        aws_tools = None  # Temporarily disabled for testing
        
        # Initialize agent orchestrator
        agent_orchestrator = AgentOrchestrator(
            weaviate_client=weaviate_client,
            friendli_client=friendli_client,
            aws_tools=aws_tools
        )
        
        logger.info("✅ All services initialized successfully")
        
    except Exception as e:
        logger.error(f"❌ Failed to initialize services: {e}")
        raise
    
    yield
    
    # Cleanup
    logger.info("🔄 Shutting down ContextCloud Agents...")

# Create FastAPI app
app = FastAPI(
    title="ContextCloud Agents",
    description="Multi-agent enterprise knowledge platform for AWS AI Agents Hack Day",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "message": "ContextCloud Agents API",
        "status": "healthy",
        "version": "1.0.0",
        "agents": ["PlannerAgent", "RetrieverAgent", "AnalyzerAgent", "ReporterAgent"]
    }

@app.get("/health")
async def health_check():
    """Detailed health check"""
    try:
        weaviate_status = await weaviate_client.health_check() if weaviate_client else "not_initialized"
        friendli_status = await friendli_client.health_check() if friendli_client else "not_initialized"
        gemini_status = await gemini_client.health_check() if gemini_client else "not_initialized"
        aws_status = await aws_tools.health_check() if aws_tools else "not_initialized"
        
        return {
            "status": "healthy",
            "services": {
                "weaviate": weaviate_status,
                "friendli": friendli_status,
                "gemini": gemini_status,
                "aws": aws_status
            },
            "agents_ready": agent_orchestrator is not None
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return JSONResponse(
            status_code=503,
            content={"status": "unhealthy", "error": str(e)}
        )

@app.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
    document_type: str = Form("general"),
    metadata: str = Form("{}")
):
    """Upload and process documents for the knowledge base"""
    try:
        logger.info(f"📄 Processing upload: {file.filename}")
        
        # Validate file
        if not file.filename:
            raise HTTPException(status_code=400, detail="No file provided")
        
        # Process with AWS Textract
        extracted_text = await aws_tools.extract_text_from_document(file)
        
        # Store in S3
        s3_uri = await aws_tools.store_document_in_s3(file, extracted_text)
        
        # Extract entities with AWS Comprehend
        entities = await aws_tools.extract_entities(extracted_text)
        
        # Store in Weaviate
        doc_id = await weaviate_client.store_document(
            content=extracted_text,
            metadata={
                "filename": file.filename,
                "document_type": document_type,
                "s3_uri": s3_uri,
                "entities": entities,
                "upload_metadata": metadata
            }
        )
        
        logger.info(f"✅ Document processed and stored: {doc_id}")
        
        return {
            "message": "Document uploaded and processed successfully",
            "document_id": doc_id,
            "s3_uri": s3_uri,
            "entities_found": len(entities),
            "filename": file.filename
        }
        
    except Exception as e:
        logger.error(f"❌ Upload failed: {e}")
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

@app.post("/agents/run")
async def run_agents(query: dict):
    """Trigger the multi-agent orchestration workflow"""
    try:
        user_query = query.get("query", "")
        if not user_query:
            raise HTTPException(status_code=400, detail="Query is required")
        
        logger.info(f"🤖 Running agents for query: {user_query}")
        
        # Run the full agent orchestration
        result = await agent_orchestrator.process_query(user_query)
        
        return {
            "message": "Agents completed successfully",
            "query": user_query,
            "result": result,
            "agents_executed": ["PlannerAgent", "RetrieverAgent", "AnalyzerAgent", "ReporterAgent"]
        }
        
    except Exception as e:
        logger.error(f"❌ Agent execution failed: {e}")
        raise HTTPException(status_code=500, detail=f"Agent execution failed: {str(e)}")

@app.post("/ask")
async def ask_friendli(query: dict):
    """Direct query to Friendli AI for reasoning"""
    try:
        user_query = query.get("query", "")
        if not user_query:
            raise HTTPException(status_code=400, detail="Query is required")
        
        logger.info(f"🧠 Querying Friendli AI: {user_query}")
        
        # Query Friendli AI directly
        response = await friendli_client.query(user_query)
        
        return {
            "message": "Friendli AI response generated",
            "query": user_query,
            "response": response
        }
        
    except Exception as e:
        logger.error(f"❌ Friendli query failed: {e}")
        raise HTTPException(status_code=500, detail=f"Friendli query failed: {str(e)}")

@app.get("/graph")
async def get_knowledge_graph():
    """Retrieve the knowledge graph for frontend visualization"""
    try:
        logger.info("📊 Retrieving knowledge graph")
        
        # Get graph data from Weaviate
        graph_data = await weaviate_client.get_knowledge_graph()
        
        # Transform nodes to match frontend expectations
        transformed_nodes = []
        for node in graph_data.get("nodes", []):
            transformed_node = {
                "id": node.get("id"),
                "name": node.get("label", node.get("name", "Unknown")),  # Use label as name
                "type": node.get("type", "unknown"),
                "size": 15 if node.get("type") == "department" else 12 if node.get("type") == "entity" else 10,
                "color": node.get("color", "#888888"),
                "summary": node.get("summary", ""),
                "key_terms": node.get("key_terms", []),
                "content_preview": node.get("content_preview", "")
            }
            transformed_nodes.append(transformed_node)
        
        # Transform edges to match frontend expectations (source/target instead of source/target)
        transformed_edges = []
        for edge in graph_data.get("edges", []):
            transformed_edge = {
                "source": edge.get("source"),
                "target": edge.get("target"),
                "type": edge.get("label", "related"),
                "strength": 0.7  # Default strength
            }
            transformed_edges.append(transformed_edge)
        
        transformed_graph = {
            "nodes": transformed_nodes,
            "links": transformed_edges  # Frontend expects "links" not "edges"
        }
        
        return {
            "message": "Knowledge graph retrieved",
            "graph": transformed_graph,
            "node_count": len(transformed_nodes),
            "edge_count": len(transformed_edges)
        }
        
    except Exception as e:
        logger.error(f"❌ Graph retrieval failed: {e}")
        raise HTTPException(status_code=500, detail=f"Graph retrieval failed: {str(e)}")

@app.post("/search/gemini")
async def search_with_gemini(query: dict):
    """Search knowledge graph using Gemini AI"""
    try:
        if not gemini_client:
            raise HTTPException(status_code=503, detail="Gemini client not initialized")
        
        if not weaviate_client:
            raise HTTPException(status_code=503, detail="Weaviate client not initialized")
        
        user_query = query.get("query", "").strip()
        if not user_query:
            raise HTTPException(status_code=400, detail="Query is required")
        
        logger.info(f"🔍 Gemini search query: {user_query}")
        
        # Get the knowledge graph
        graph_data = await weaviate_client.get_knowledge_graph()
        
        # Use Gemini to find relevant nodes
        search_result = await gemini_client.find_relevant_nodes(user_query, graph_data["nodes"])
        relevant_nodes = search_result.get("relevant_nodes", [])
        
        # Generate summary
        summary = await gemini_client.generate_summary(user_query, relevant_nodes)
        
        return {
            "message": "Gemini search completed",
            "query": user_query,
            "relevant_nodes": relevant_nodes,
            "summary": summary,
            "analysis_summary": search_result.get("analysis_summary", ""),
            "total_nodes_searched": len(graph_data["nodes"]),
            "relevant_nodes_found": len(relevant_nodes)
        }
        
    except Exception as e:
        logger.error(f"❌ Gemini search failed: {e}")
        raise HTTPException(status_code=500, detail=f"Gemini search failed: {str(e)}")

@app.post("/insights/generate")
async def generate_ai_insights(request: dict):
    """Generate AI insights based on current query and knowledge graph data"""
    try:
        if not gemini_client:
            raise HTTPException(status_code=503, detail="Gemini client not initialized")
        
        if not weaviate_client:
            raise HTTPException(status_code=503, detail="Weaviate client not initialized")
        
        user_query = request.get("query", "").strip()
        visible_nodes = request.get("visible_nodes", [])
        
        logger.info(f"🧠 Generating AI insights for query: {user_query}")
        
        # Get the full knowledge graph
        graph_data = await weaviate_client.get_knowledge_graph()
        
        # Generate comprehensive insights using Gemini
        insights = await gemini_client.generate_insights(
            query=user_query,
            visible_nodes=visible_nodes,
            full_graph=graph_data
        )
        
        return {
            "message": "AI insights generated successfully",
            "query": user_query,
            "insights": insights,
            "analysis_scope": {
                "visible_nodes": len(visible_nodes),
                "total_nodes": len(graph_data.get("nodes", [])),
                "total_edges": len(graph_data.get("edges", []))
            }
        }
        
    except Exception as e:
        logger.error(f"❌ AI insights generation failed: {e}")
        raise HTTPException(status_code=500, detail=f"AI insights generation failed: {str(e)}")

@app.get("/agents/status")
async def get_agent_status():
    """Get current status of all agents"""
    try:
        if not agent_orchestrator:
            raise HTTPException(status_code=503, detail="Agent orchestrator not initialized")
        
        status = await agent_orchestrator.get_status()
        
        return {
            "message": "Agent status retrieved",
            "agents": status
        }
        
    except Exception as e:
        logger.error(f"❌ Status retrieval failed: {e}")
        raise HTTPException(status_code=500, detail=f"Status retrieval failed: {str(e)}")

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
