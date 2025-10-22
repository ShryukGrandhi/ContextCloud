"""
ContextCloud Agents - Demo Backend
Simplified version for local demo
"""

import json
import logging
from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from datetime import datetime
import asyncio

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="ContextCloud Agents - Demo",
    description="Multi-agent enterprise knowledge platform demo",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "message": "ContextCloud Agents API - Demo Mode",
        "status": "healthy",
        "version": "1.0.0",
        "agents": ["PlannerAgent", "RetrieverAgent", "AnalyzerAgent", "ReporterAgent"],
        "mode": "demo"
    }

@app.get("/health")
async def health_check():
    """Detailed health check"""
    return {
        "status": "healthy",
        "services": {
            "weaviate": "demo_mode",
            "friendli": "demo_mode", 
            "aws": "demo_mode"
        },
        "agents_ready": True,
        "mode": "demo"
    }

@app.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
    document_type: str = Form("general"),
    metadata: str = Form("{}")
):
    """Upload and process documents for the knowledge base"""
    try:
        logger.info(f"📄 Processing upload: {file.filename}")
        
        # Simulate document processing
        await asyncio.sleep(1)  # Simulate processing time
        
        # Generate demo response
        doc_id = f"demo_doc_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        logger.info(f"✅ Document processed: {doc_id}")
        
        return {
            "message": "Document uploaded and processed successfully (Demo Mode)",
            "document_id": doc_id,
            "s3_uri": f"s3://demo-bucket/{doc_id}",
            "entities_found": 5,
            "filename": file.filename,
            "mode": "demo"
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
        
        # Simulate agent workflow
        await asyncio.sleep(2)  # Simulate processing time
        
        # Generate demo result
        result = {
            "query": user_query,
            "workflow_status": "completed",
            "agents_executed": ["PlannerAgent", "RetrieverAgent", "AnalyzerAgent", "ReporterAgent"],
            "planning_results": {
                "query": user_query,
                "intent_analysis": {
                    "intent": "general_query",
                    "complexity": "moderate",
                    "needs_retrieval": True,
                    "needs_analysis": True,
                    "needs_summarization": True
                },
                "workflow_plan": {
                    "steps": [
                        {"step": 1, "agent": "RetrieverAgent", "action": "retrieve_relevant_documents"},
                        {"step": 2, "agent": "AnalyzerAgent", "action": "analyze_documents"},
                        {"step": 3, "agent": "ReporterAgent", "action": "generate_summary"}
                    ]
                }
            },
            "retrieval_results": {
                "query": user_query,
                "documents_found": 3,
                "documents_returned": 3,
                "documents": [
                    {
                        "filename": "Policy Manual 2024.pdf",
                        "document_type": "policy",
                        "content": f"Relevant policy information for: {user_query}",
                        "entities": ["GDPR", "Compliance", "Data Protection"],
                        "certainty": 0.85
                    },
                    {
                        "filename": "Compliance Guide.pdf", 
                        "document_type": "guide",
                        "content": f"Compliance guidelines related to: {user_query}",
                        "entities": ["Regulation", "Standards", "Requirements"],
                        "certainty": 0.78
                    },
                    {
                        "filename": "Data Privacy Report.pdf",
                        "document_type": "report", 
                        "content": f"Data privacy considerations for: {user_query}",
                        "entities": ["Privacy", "Security", "Protection"],
                        "certainty": 0.72
                    }
                ]
            },
            "analysis_results": {
                "query": user_query,
                "documents_analyzed": 3,
                "analysis_results": {
                    "analysis_text": f"Comprehensive analysis of {user_query} reveals important patterns in enterprise documents. Key findings include compliance requirements, data protection measures, and policy implications.",
                    "documents_processed": 3,
                    "analysis_type": "comprehensive_document_analysis"
                },
                "entity_analysis": {
                    "total_entities": 9,
                    "unique_entities": 7,
                    "top_entities": [("GDPR", 2), ("Compliance", 2), ("Data Protection", 1)],
                    "entity_extraction_method": "demo_mode"
                },
                "reasoning_results": {
                    "reasoning_text": f"Based on the analysis of retrieved documents, the query '{user_query}' relates to enterprise compliance and data protection requirements. The documents provide comprehensive coverage of relevant policies and guidelines.",
                    "reasoning_type": "deep_analysis",
                    "confidence_level": "high"
                }
            },
            "final_report": {
                "query": user_query,
                "summary": f"Executive Summary: Analysis of '{user_query}' reveals comprehensive enterprise knowledge covering compliance requirements, data protection measures, and policy implications.",
                "structured_report": {
                    "executive_summary": {
                        "query": user_query,
                        "documents_analyzed": 3,
                        "key_findings": ["Compliance requirements identified", "Data protection measures documented", "Policy implications analyzed"],
                        "confidence_level": "high"
                    },
                    "insights_and_recommendations": {
                        "primary_insights": [
                            "Comprehensive compliance framework identified",
                            "Data protection measures are well-documented", 
                            "Policy implications require attention"
                        ],
                        "actionable_recommendations": [
                            "Review compliance requirements regularly",
                            "Implement data protection measures",
                            "Update policies based on findings"
                        ]
                    }
                },
                "formatted_output": {
                    "summary": f"Analysis completed for query: {user_query}",
                    "insights": {
                        "primary_insights": ["Comprehensive compliance framework identified"],
                        "actionable_recommendations": ["Review compliance requirements regularly"]
                    },
                    "visualization_data": {
                        "nodes": [
                            {"id": "query", "label": user_query, "type": "query", "size": 20},
                            {"id": "insight1", "label": "Compliance Framework", "type": "insight", "size": 15},
                            {"id": "insight2", "label": "Data Protection", "type": "insight", "size": 15}
                        ],
                        "edges": [
                            {"source": "query", "target": "insight1", "label": "generates"},
                            {"source": "query", "target": "insight2", "label": "generates"}
                        ]
                    }
                }
            },
            "agent_status": {
                "PlannerAgent": "completed",
                "RetrieverAgent": "completed", 
                "AnalyzerAgent": "completed",
                "ReporterAgent": "completed"
            },
            "mode": "demo"
        }
        
        return {
            "message": "Agents completed successfully (Demo Mode)",
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
        
        logger.info(f"🧠 Querying Friendli AI (Demo Mode): {user_query}")
        
        # Simulate Friendli AI response
        await asyncio.sleep(1)
        
        response = f"""Demo Response for: "{user_query}"

Based on the enterprise knowledge base, here are the key insights:

**Analysis Results:**
- Query intent: {user_query.lower()}
- Relevant documents: 3 policy documents identified
- Key entities: GDPR, Compliance, Data Protection
- Confidence level: High

**Recommendations:**
1. Review current compliance policies
2. Update data protection measures
3. Conduct regular compliance audits

**Next Steps:**
- Implement recommended changes
- Schedule follow-up review
- Monitor compliance metrics

This is a demo response from the ContextCloud Agents system."""
        
        return {
            "message": "Friendli AI response generated (Demo Mode)",
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
        logger.info("📊 Retrieving knowledge graph (Demo Mode)")
        
        # Generate demo graph data
        graph_data = {
            "nodes": [
                {"id": "query", "name": "Enterprise Knowledge", "type": "query", "size": 20, "color": "#00d4ff"},
                {"id": "doc1", "name": "Policy Manual 2024", "type": "document", "size": 15, "color": "#00ff88"},
                {"id": "doc2", "name": "Compliance Guide", "type": "document", "size": 15, "color": "#00ff88"},
                {"id": "doc3", "name": "Data Privacy Report", "type": "document", "size": 15, "color": "#00ff88"},
                {"id": "entity1", "name": "GDPR", "type": "entity", "size": 10, "color": "#b347d9"},
                {"id": "entity2", "name": "Data Protection", "type": "entity", "size": 10, "color": "#b347d9"},
                {"id": "entity3", "name": "Compliance", "type": "entity", "size": 10, "color": "#b347d9"},
                {"id": "insight1", "name": "Privacy Requirements", "type": "insight", "size": 12, "color": "#ff6b9d"},
                {"id": "insight2", "name": "Risk Assessment", "type": "insight", "size": 12, "color": "#ff6b9d"}
            ],
            "edges": [
                {"source": "query", "target": "doc1", "type": "retrieves", "strength": 0.8},
                {"source": "query", "target": "doc2", "type": "retrieves", "strength": 0.7},
                {"source": "query", "target": "doc3", "type": "retrieves", "strength": 0.6},
                {"source": "doc1", "target": "entity1", "type": "contains", "strength": 0.9},
                {"source": "doc2", "target": "entity2", "type": "contains", "strength": 0.8},
                {"source": "doc3", "target": "entity3", "type": "contains", "strength": 0.7},
                {"source": "entity1", "target": "insight1", "type": "generates", "strength": 0.6},
                {"source": "entity2", "target": "insight2", "type": "generates", "strength": 0.5}
            ]
        }
        
        return {
            "message": "Knowledge graph retrieved (Demo Mode)",
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
        status = {
            "PlannerAgent": "ready",
            "RetrieverAgent": "ready", 
            "AnalyzerAgent": "ready",
            "ReporterAgent": "ready"
        }
        
        return {
            "message": "Agent status retrieved (Demo Mode)",
            "agents": status
        }
        
    except Exception as e:
        logger.error(f"❌ Status retrieval failed: {e}")
        raise HTTPException(status_code=500, detail=f"Status retrieval failed: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "demo_main:app",
        host="0.0.0.0",
        port=8002,
        reload=True,
        log_level="info"
    )
