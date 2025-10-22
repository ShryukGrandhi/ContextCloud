# ContextCloud Agents - Architecture Overview

## System Architecture

ContextCloud Agents is a multi-agent enterprise knowledge platform built for the AWS AI Agents Hack Day. The system demonstrates advanced AI orchestration using LlamaIndex, vector memory with Weaviate, and real-time inference with Friendli AI.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                              ContextCloud Agents Platform                      │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                 │
│  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐             │
│  │   React Frontend │    │   FastAPI Backend │    │   AWS Services  │             │
│  │                 │    │                 │    │                 │             │
│  │ • Graph View    │◄──►│ • Multi-Agordo │◄──►│ • Textract     │             │
│  │ • Agent Console │    │ • LlamaIndex    │    │ • Comprehend   │             │
│  │ • Search Bar    │    │ • Weaviate      │    │ • S3 Storage   │             │
│  │ • Real-time Logs│    │ • Friendli AI   │    │ • Lambda       │             │
│  │ • Stats Panel   │    │ • Agent System  │    │ • API Gateway  │             │
│  └─────────────────┘    └─────────────────┘    └─────────────────┘             │
│                                                                                 │
├─────────────────────────────────────────────────────────────────────────────────┤
│                              Multi-Agent Workflow                              │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                 │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐     │
│  │ PlannerAgent│───►│RetrieverAgent│───►│AnalyzerAgent│───►│ReporterAgent│     │
│  │             │    │             │    │             │    │             │     │
│  │ • Query     │    │ • Weaviate  │    │ • Friendli  │    │ • Summary   │     │
│  │ Analysis    │    │ • Vector    │    │ • AWS       │    │ • Graph     │     │
│  │ • Workflow  │    │ • Search    │    │ • Comprehend│    │ • Reports   │     │
│  │ Planning    │    │ • Ranking   │    │ • Reasoning │    │ • Output    │     │
│  └─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘     │
│                                                                                 │
├─────────────────────────────────────────────────────────────────────────────────┤
│                              Data Flow & Integration                           │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                 │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐     │
│  │ Document    │    │ Vector      │    │ AI          │    │ Knowledge   │     │
│  │ Ingestion   │    │ Storage     │    │ Inference   │    │ Graph       │     │
│  │             │    │             │    │             │    │             │     │
│  │ S3 ← PDF    │    │ Weaviate    │    │ Friendli AI │    │ Real-time   │     │
│  │ Textract ←  │    │ Embeddings  │    │ LlamaIndex  │    │ Visualization│     │
│  │ Comprehend ←│    │ Metadata    │    │ Tool Calls  │    │ Frontend    │     │
│  └─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘     │
│                                                                                 │
└─────────────────────────────────────────────────────────────────────────────────┘
```

## Component Details

### Frontend (React + Tailwind)
- **Graph View**: Interactive knowledge graph visualization using react-force-graph
- **Agent Console**: Real-time agent activity monitoring and logging
- **Search Bar**: Query interface with document upload capabilities
- **Stats Panel**: System performance and usage statistics
- **Glassmorphic UI**: Modern, responsive design with dark theme

### Backend (FastAPI + Python)
- **Agent Orchestrator**: Coordinates multi-agent workflow execution
- **LlamaIndex Integration**: Agent framework and tool calling
- **Weaviate Client**: Vector database operations and embeddings
- **Friendli AI Client**: AI inference and reasoning capabilities
- **AWS Tools**: Textract, Comprehend, and S3 integration

### Multi-Agent System
1. **PlannerAgent**: Interprets queries and creates workflow plans
2. **RetrieverAgent**: Searches Weaviate for relevant documents
3. **AnalyzerAgent**: Analyzes documents using Friendli AI and AWS Comprehend
4. **ReporterAgent**: Generates summaries and updates knowledge graph

### AWS Services
- **S3**: Document storage and retrieval
- **Textract**: OCR and text extraction from documents
- **Comprehend**: Entity extraction and NLP processing
- **Lambda**: Serverless function execution
- **API Gateway**: RESTful API endpoints and routing

### Vector Database (Weaviate)
- **Document Storage**: Vector embeddings and metadata
- **Semantic Search**: Similarity-based document retrieval
- **Knowledge Graph**: Entity relationships and connections

## Data Flow

1. **Document Upload**: Files uploaded to S3, processed with Textract
2. **Entity Extraction**: AWS Comprehend extracts entities and metadata
3. **Vector Storage**: Documents embedded and stored in Weaviate
4. **Query Processing**: User queries trigger multi-agent workflow
5. **Document Retrieval**: RetrieverAgent finds relevant documents
6. **Analysis**: AnalyzerAgent processes documents with Friendli AI
7. **Reporting**: ReporterAgent generates summaries and insights
8. **Visualization**: Frontend displays results in interactive graph

## Technology Stack

### Backend
- **Python 3.9+**: Core programming language
- **FastAPI**: Web framework and API development
- **LlamaIndex**: Multi-agent orchestration framework
- **Weaviate**: Vector database and semantic search
- **Friendli AI**: AI inference and reasoning
- **Boto3**: AWS SDK for Python

### Frontend
- **React 18**: Frontend framework
- **Tailwind CSS**: Styling and responsive design
- **Framer Motion**: Animations and transitions
- **React Force Graph**: Graph visualization library
- **Axios**: HTTP client for API calls

### AWS Services
- **S3**: Object storage
- **Textract**: Document text extraction
- **Comprehend**: Natural language processing
- **Lambda**: Serverless computing
- **API Gateway**: API management

### DevOps
- **Docker**: Containerization (optional)
- **AWS CLI**: Deployment and management
- **Git**: Version control

## Security & Compliance

- **CORS Configuration**: Cross-origin resource sharing
- **API Authentication**: JWT tokens and API keys
- **Data Encryption**: At rest and in transit
- **Access Control**: IAM roles and policies
- **Audit Logging**: Comprehensive activity tracking

## Performance & Scalability

- **Serverless Architecture**: Auto-scaling with AWS Lambda
- **Vector Indexing**: Efficient semantic search
- **Caching**: Response caching and optimization
- **Load Balancing**: Distributed request handling
- **Monitoring**: CloudWatch integration

## Deployment

The system can be deployed using:
1. **Local Development**: Docker Compose for local testing
2. **AWS Deployment**: Automated deployment script
3. **Hybrid Approach**: Local backend with cloud services

## Judging Criteria Alignment

✅ **Multi-Agent System**: LlamaIndex orchestration with distinct agent roles  
✅ **Tool-Calling**: AWS Textract, Comprehend, Friendli AI integration  
✅ **Vector Memory**: Weaviate for persistent document embeddings  
✅ **Enterprise Relevance**: Compliance intelligence use case  
✅ **Visualization**: Real-time graph with agent activity logs  
✅ **Architecture**: Production-grade with proper error handling  

This architecture demonstrates a complete, production-ready multi-agent system that showcases the power of AI orchestration, vector memory, and enterprise knowledge management.
