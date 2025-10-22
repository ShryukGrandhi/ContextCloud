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
from tools.aws_tools import AWSTools
from utils.logger import setup_logger

# Load environment variables
load_dotenv()

# Setup logging
logger = setup_logger(__name__)

# Global clients
weaviate_client = None
friendli_client = None
aws_tools = None
agent_orchestrator = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize and cleanup resources"""
    global weaviate_client, friendli_client, aws_tools, agent_orchestrator
    
    logger.info("🚀 Starting ContextCloud Agents...")
    
    try:
        # Initialize clients
        weaviate_client = WeaviateClient()
        await weaviate_client.initialize()
        
        friendli_client = FriendliClient()
        
        aws_tools = AWSTools()
        await aws_tools.initialize()
        
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
        aws_status = await aws_tools.health_check() if aws_tools else "not_initialized"
        
        return {
            "status": "healthy",
            "services": {
                "weaviate": weaviate_status,
                "friendli": friendli_status,
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
        
        return {
            "message": "Knowledge graph retrieved",
            "graph": graph_data,
            "node_count": len(graph_data.get("nodes", [])),
            "edge_count": len(graph_data.get("edges", []))
        }
        
    except Exception as e:
        logger.error(f"❌ Graph retrieval failed: {e}")
        raise HTTPException(status_code=500, detail=f"Graph retrieval failed: {str(e)}")

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
