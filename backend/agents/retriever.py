"""
RetrieverAgent - ContextCloud Agents
Handles document retrieval from Weaviate vector database
"""

import logging
from typing import Dict, Any, List
from llama_index.core.agent import ReActAgent
from llama_index.core.tools import ToolMetadata
from utils.logger import AgentLogger

logger = AgentLogger("RetrieverAgent")

class RetrieverAgent:
    """Agent responsible for retrieving relevant documents from the knowledge base"""
    
    def __init__(self, weaviate_client, friendli_client, aws_tools):
        self.weaviate_client = weaviate_client
        self.friendli_client = friendli_client
        self.aws_tools = aws_tools
        self.agent = None
        
    async def initialize(self):
        """Initialize the RetrieverAgent with tools"""
        try:
            logger.log_action("Initializing RetrieverAgent with tools")
            
            # Define available tools for retrieval
            tools = [
                ToolMetadata(
                    name="query_documents",
                    description="Query documents from Weaviate vector database"
                ),
                ToolMetadata(
                    name="filter_by_entities",
                    description="Filter documents by extracted entities"
                ),
                ToolMetadata(
                    name="rank_by_relevance",
                    description="Rank retrieved documents by relevance score"
                )
            ]
            
            # Create ReAct agent
            self.agent = ReActAgent.from_tools(
                tools,
                verbose=True,
                system_prompt=self._get_system_prompt()
            )
            
            logger.log_action("RetrieverAgent initialized successfully")
            
        except Exception as e:
            logger.log_error(f"Failed to initialize RetrieverAgent: {e}")
            raise
    
    async def retrieve_documents(self, query: str, limit: int = 10) -> Dict[str, Any]:
        """Retrieve relevant documents for a query"""
        try:
            logger.log_action(f"Retrieving documents for query: {query[:50]}...")
            
            # Query documents from Weaviate
            logger.log_tool_call("query_documents", {"query": query, "limit": limit})
            documents = await self.weaviate_client.query_documents(query, limit)
            
            # Filter and rank documents
            filtered_docs = await self._filter_documents(documents, query)
            ranked_docs = await self._rank_documents(filtered_docs, query)
            
            # Generate retrieval summary
            summary = await self._generate_retrieval_summary(query, ranked_docs)
            
            result = {
                "query": query,
                "documents_found": len(documents),
                "documents_returned": len(ranked_docs),
                "documents": ranked_docs,
                "retrieval_summary": summary,
                "retrieval_metadata": {
                    "search_strategy": "vector_similarity",
                    "ranking_method": "relevance_score",
                    "filtering_applied": True
                }
            }
            
            logger.log_result(f"Retrieved {len(ranked_docs)} relevant documents")
            return result
            
        except Exception as e:
            logger.log_error(f"Document retrieval failed: {e}")
            raise
    
    async def _filter_documents(self, documents: List[Dict[str, Any]], query: str) -> List[Dict[str, Any]]:
        """Filter documents based on relevance and quality"""
        try:
            logger.log_action("Filtering documents by relevance")
            
            filtered_docs = []
            for doc in documents:
                # Check if document has sufficient content
                if len(doc.get("content", "")) < 100:
                    continue
                
                # Check certainty score if available
                certainty = doc.get("certainty", 0)
                if certainty < 0.3:  # Low confidence threshold
                    continue
                
                # Check if document type is relevant
                doc_type = doc.get("document_type", "").lower()
                if doc_type in ["irrelevant", "test", "duplicate"]:
                    continue
                
                filtered_docs.append(doc)
            
            logger.log_action(f"Filtered to {len(filtered_docs)} high-quality documents")
            return filtered_docs
            
        except Exception as e:
            logger.log_error(f"Document filtering failed: {e}")
            return documents  # Return original documents on error
    
    async def _rank_documents(self, documents: List[Dict[str, Any]], query: str) -> List[Dict[str, Any]]:
        """Rank documents by relevance to the query"""
        try:
            logger.log_action("Ranking documents by relevance")
            
            # Simple ranking based on certainty score and content length
            ranked_docs = sorted(
                documents,
                key=lambda x: (
                    x.get("certainty", 0) * 0.7 +  # 70% weight on certainty
                    min(len(x.get("content", "")) / 10000, 1) * 0.3  # 30% weight on content length
                ),
                reverse=True
            )
            
            logger.log_action(f"Ranked {len(ranked_docs)} documents")
            return ranked_docs
            
        except Exception as e:
            logger.log_error(f"Document ranking failed: {e}")
            return documents  # Return original documents on error
    
    async def _generate_retrieval_summary(self, query: str, documents: List[Dict[str, Any]]) -> str:
        """Generate a summary of the retrieval results"""
        try:
            logger.log_action("Generating retrieval summary")
            
            if not documents:
                return "No relevant documents found for the query."
            
            # Prepare document summaries for analysis
            doc_summaries = []
            for i, doc in enumerate(documents[:5]):  # Top 5 documents
                doc_summaries.append(f"""
                Document {i+1}: {doc.get('filename', 'Unknown')}
                Type: {doc.get('document_type', 'Unknown')}
                Entities: {', '.join(doc.get('entities', [])[:5])}
                Content Preview: {doc.get('content', '')[:200]}...
                """)
            
            summary_prompt = f"""
            Summarize the document retrieval results for this query:
            
            Query: "{query}"
            
            Retrieved Documents:
            {chr(10).join(doc_summaries)}
            
            Provide a concise summary of:
            1. What types of documents were found
            2. Key entities and topics covered
            3. Overall relevance to the query
            
            Keep the summary under 200 words.
            """
            
            summary = await self.friendli_client.query(summary_prompt)
            logger.log_action("Retrieval summary generated")
            
            return summary
            
        except Exception as e:
            logger.log_error(f"Summary generation failed: {e}")
            return f"Retrieved {len(documents)} documents for query: {query[:50]}..."
    
    def _get_system_prompt(self) -> str:
        """Get system prompt for the RetrieverAgent"""
        return """
        You are the RetrieverAgent for ContextCloud, an enterprise knowledge management system.
        
        Your role is to:
        1. Query the Weaviate vector database for relevant documents
        2. Filter documents based on relevance and quality
        3. Rank documents by relevance to user queries
        4. Provide comprehensive document retrieval results
        
        You have access to:
        - Weaviate vector database with document embeddings
        - Document metadata including entities and types
        - Relevance scoring and ranking capabilities
        
        Always ensure retrieved documents are highly relevant and of good quality.
        """
