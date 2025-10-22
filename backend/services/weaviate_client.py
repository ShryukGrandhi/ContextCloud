"""
Weaviate client for ContextCloud Agents
Handles vector storage and retrieval for the knowledge base
"""

import os
import json
import logging
from typing import List, Dict, Any, Optional
import weaviate
from weaviate import Client
from utils.logger import setup_logger

logger = setup_logger(__name__)

class WeaviateClient:
    """Weaviate client for vector storage and retrieval"""
    
    def __init__(self):
        self.client: Optional[Client] = None
        self.url = os.getenv("WEAVIATE_URL", "http://localhost:8080")
        self.api_key = os.getenv("WEAVIATE_API_KEY")
        
    async def initialize(self):
        """Initialize Weaviate client and create schema"""
        try:
            logger.info(f"🔗 Connecting to Weaviate at {self.url}")
            
            # Initialize client
            if self.api_key:
                self.client = weaviate.Client(
                    url=self.url,
                    auth_client_secret=weaviate.AuthApiKey(api_key=self.api_key)
                )
            else:
                self.client = weaviate.Client(url=self.url)
            
            # Test connection
            if not self.client.is_ready():
                raise Exception("Weaviate client is not ready")
            
            # Create schema if it doesn't exist
            await self._create_schema()
            
            logger.info("✅ Weaviate client initialized successfully")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize Weaviate client: {e}")
            raise
    
    async def _create_schema(self):
        """Create the document schema in Weaviate"""
        try:
            schema = {
                "class": "Document",
                "description": "Enterprise documents for ContextCloud Agents",
                "vectorizer": "text2vec-transformers",
                "properties": [
                    {
                        "name": "content",
                        "dataType": ["text"],
                        "description": "Document content"
                    },
                    {
                        "name": "filename",
                        "dataType": ["string"],
                        "description": "Original filename"
                    },
                    {
                        "name": "document_type",
                        "dataType": ["string"],
                        "description": "Type of document (policy, manual, report, etc.)"
                    },
                    {
                        "name": "s3_uri",
                        "dataType": ["string"],
                        "description": "S3 storage URI"
                    },
                    {
                        "name": "entities",
                        "dataType": ["text[]"],
                        "description": "Extracted entities"
                    },
                    {
                        "name": "upload_metadata",
                        "dataType": ["object"],
                        "description": "Additional metadata"
                    },
                    {
                        "name": "created_at",
                        "dataType": ["date"],
                        "description": "Document creation timestamp"
                    }
                ]
            }
            
            # Check if schema exists
            if self.client.schema.exists("Document"):
                logger.info("📋 Document schema already exists")
            else:
                self.client.schema.create_class(schema)
                logger.info("📋 Created Document schema")
                
        except Exception as e:
            logger.error(f"❌ Failed to create schema: {e}")
            raise
    
    async def store_document(self, content: str, metadata: Dict[str, Any]) -> str:
        """Store a document in Weaviate"""
        try:
            logger.info(f"💾 Storing document: {metadata.get('filename', 'unnamed')}")
            
            doc_object = {
                "content": content,
                "filename": metadata.get("filename", ""),
                "document_type": metadata.get("document_type", "general"),
                "s3_uri": metadata.get("s3_uri", ""),
                "entities": metadata.get("entities", []),
                "upload_metadata": metadata.get("upload_metadata", {}),
                "created_at": metadata.get("created_at", "2024-01-01T00:00:00Z")
            }
            
            result = self.client.data_object.create(
                data_object=doc_object,
                class_name="Document"
            )
            
            doc_id = result["id"]
            logger.info(f"✅ Document stored with ID: {doc_id}")
            
            return doc_id
            
        except Exception as e:
            logger.error(f"❌ Failed to store document: {e}")
            raise
    
    async def query_documents(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Query documents using vector similarity"""
        try:
            logger.info(f"🔍 Querying documents: {query[:50]}...")
            
            query_result = (
                self.client.query
                .get("Document", ["content", "filename", "document_type", "entities", "s3_uri"])
                .with_near_text({"concepts": [query]})
                .with_limit(limit)
                .with_additional(["certainty", "distance"])
                .do()
            )
            
            documents = []
            if "data" in query_result and "Get" in query_result["data"]:
                for doc in query_result["data"]["Get"]["Document"]:
                    documents.append({
                        "content": doc.get("content", ""),
                        "filename": doc.get("filename", ""),
                        "document_type": doc.get("document_type", ""),
                        "entities": doc.get("entities", []),
                        "s3_uri": doc.get("s3_uri", ""),
                        "certainty": doc.get("_additional", {}).get("certainty", 0),
                        "distance": doc.get("_additional", {}).get("distance", 0)
                    })
            
            logger.info(f"✅ Found {len(documents)} relevant documents")
            return documents
            
        except Exception as e:
            logger.error(f"❌ Failed to query documents: {e}")
            raise
    
    async def get_knowledge_graph(self) -> Dict[str, Any]:
        """Get knowledge graph data for visualization"""
        try:
            logger.info("📊 Building knowledge graph")
            
            # Get all documents
            query_result = (
                self.client.query
                .get("Document", ["content", "filename", "document_type", "entities"])
                .with_limit(100)
                .do()
            )
            
            nodes = []
            edges = []
            
            if "data" in query_result and "Get" in query_result["data"]:
                for i, doc in enumerate(query_result["data"]["Get"]["Document"]):
                    # Create document node
                    node = {
                        "id": f"doc_{i}",
                        "label": doc.get("filename", f"Document {i}"),
                        "type": doc.get("document_type", "general"),
                        "entities": doc.get("entities", []),
                        "content_preview": doc.get("content", "")[:100] + "..."
                    }
                    nodes.append(node)
                    
                    # Create entity nodes and edges
                    entities = doc.get("entities", [])
                    for entity in entities:
                        entity_node = {
                            "id": f"entity_{entity}",
                            "label": entity,
                            "type": "entity"
                        }
                        
                        if entity_node not in nodes:
                            nodes.append(entity_node)
                        
                        # Create edge between document and entity
                        edge = {
                            "source": f"doc_{i}",
                            "target": f"entity_{entity}",
                            "label": "contains"
                        }
                        edges.append(edge)
            
            logger.info(f"✅ Generated graph with {len(nodes)} nodes and {len(edges)} edges")
            
            return {
                "nodes": nodes,
                "edges": edges
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to generate knowledge graph: {e}")
            raise
    
    async def health_check(self) -> str:
        """Check Weaviate health"""
        try:
            if not self.client:
                return "not_initialized"
            
            if self.client.is_ready():
                return "healthy"
            else:
                return "unhealthy"
                
        except Exception as e:
            logger.error(f"❌ Weaviate health check failed: {e}")
            return "error"
