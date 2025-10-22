# ContextCloud Agents - Project Structure

## Overview

ContextCloud Agents is a comprehensive multi-agent enterprise knowledge platform built for the AWS AI Agents Hack Day. This document outlines the complete project structure and organization.

## Root Directory Structure

```
contextcloud/
├── README.md                    # Main project documentation
├── SETUP.md                     # Setup and installation instructions
├── PROJECT_STRUCTURE.md         # This file - project structure overview
├── backend/                     # FastAPI backend application
├── frontend/                    # React frontend application
├── aws/                        # AWS deployment configurations
├── docs/                       # Additional documentation
└── tests/                      # Test files and configurations
```

## Backend Structure (`/backend`)

```
backend/
├── main.py                     # FastAPI application entry point
├── requirements.txt            # Python dependencies
├── env.example                 # Environment variables template
├── agents/                     # Multi-agent system implementation
│   ├── __init__.py
│   ├── orchestrator.py         # Agent orchestration coordinator
│   ├── planner.py              # PlannerAgent implementation
│   ├── retriever.py            # RetrieverAgent implementation
│   ├── analyzer.py             # AnalyzerAgent implementation
│   └── reporter.py             # ReporterAgent implementation
├── services/                   # External service clients
│   ├── __init__.py
│   ├── weaviate_client.py      # Weaviate vector database client
│   └── friendli_client.py      # Friendli AI client
├── tools/                      # AWS and external tool integrations
│   ├── __init__.py
│   └── aws_tools.py            # AWS Textract, Comprehend, S3 tools
└── utils/                      # Utility functions and helpers
    ├── __init__.py
    └── logger.py               # Logging utilities
```

## Frontend Structure (`/frontend`)

```
frontend/
├── package.json                # Node.js dependencies and scripts
├── tailwind.config.js          # Tailwind CSS configuration
├── public/                     # Static public assets
│   ├── index.html              # Main HTML template
│   └── manifest.json           # Web app manifest
├── src/                        # React source code
│   ├── index.js                # React application entry point
│   ├── index.css               # Global styles and Tailwind imports
│   ├── App.jsx                 # Main React application component
│   ├── components/             # React components
│   │   ├── Header.jsx          # Application header
│   │   ├── SearchBar.jsx       # Search and query interface
│   │   ├── GraphView.jsx       # Knowledge graph visualization
│   │   ├── AgentConsole.jsx    # Agent activity monitoring
│   │   ├── StatsPanel.jsx      # System statistics display
│   │   └── ParticleBackground.jsx # Animated background
│   └── context/                # React context providers
│       └── ContextCloudContext.jsx # Application state management
```

## AWS Structure (`/aws`)

```
aws/
├── deploy.sh                   # AWS deployment script
├── gateway_config.json         # API Gateway configuration
└── lambdas/                    # AWS Lambda functions
    ├── upload_lambda.py        # Document upload and processing
    ├── run_agents_lambda.py    # Multi-agent workflow execution
    ├── ask_lambda.py           # Direct Friendli AI queries
    └── get_graph_lambda.py     # Knowledge graph data retrieval
```

## Documentation Structure (`/docs`)

```
docs/
└── architecture.md             # System architecture documentation
```

## Key Components

### Multi-Agent System

The core of ContextCloud Agents is the multi-agent system built with LlamaIndex:

1. **PlannerAgent** (`agents/planner.py`)
   - Interprets user queries
   - Creates workflow plans
   - Coordinates agent execution

2. **RetrieverAgent** (`agents/retriever.py`)
   - Queries Weaviate vector database
   - Retrieves relevant documents
   - Ranks results by relevance

3. **AnalyzerAgent** (`agents/analyzer.py`)
   - Analyzes documents with Friendli AI
   - Extracts entities with AWS Comprehend
   - Performs reasoning and pattern detection

4. **ReporterAgent** (`agents/reporter.py`)
   - Generates comprehensive reports
   - Creates summaries and insights
   - Updates knowledge graph

### Service Integrations

1. **Weaviate Client** (`services/weaviate_client.py`)
   - Vector database operations
   - Document embedding storage
   - Semantic search capabilities

2. **Friendli AI Client** (`services/friendli_client.py`)
   - AI inference and reasoning
   - Document analysis
   - Insight generation

3. **AWS Tools** (`tools/aws_tools.py`)
   - Textract for OCR
   - Comprehend for NLP
   - S3 for document storage

### Frontend Components

1. **Graph View** (`components/GraphView.jsx`)
   - Interactive knowledge graph
   - Real-time visualization
   - Node and edge interactions

2. **Agent Console** (`components/AgentConsole.jsx`)
   - Real-time agent monitoring
   - Activity logging
   - Status tracking

3. **Search Interface** (`components/SearchBar.jsx`)
   - Query input
   - Document upload
   - Example queries

## API Endpoints

### Backend API (`main.py`)

- `GET /` - Health check
- `GET /health` - Detailed health status
- `POST /upload` - Document upload and processing
- `POST /agents/run` - Multi-agent workflow execution
- `POST /ask` - Direct Friendli AI queries
- `GET /graph` - Knowledge graph data
- `GET /agents/status` - Agent status information

### AWS Lambda Functions

- `POST /upload` - Document processing with AWS services
- `POST /agents/run` - Serverless agent workflow
- `POST /ask` - Serverless Friendli AI queries
- `GET /graph` - Serverless graph data retrieval

## Configuration Files

### Backend Configuration

- `requirements.txt` - Python dependencies
- `env.example` - Environment variables template
- `main.py` - FastAPI application configuration

### Frontend Configuration

- `package.json` - Node.js dependencies and scripts
- `tailwind.config.js` - Tailwind CSS configuration
- `src/index.css` - Global styles and animations

### AWS Configuration

- `deploy.sh` - Automated deployment script
- `gateway_config.json` - API Gateway OpenAPI specification
- Lambda functions - Serverless function implementations

## Development Workflow

### Local Development

1. **Backend Development:**
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   uvicorn main:app --reload
   ```

2. **Frontend Development:**
   ```bash
   cd frontend
   npm install
   npm start
   ```

3. **Testing:**
   ```bash
   # Backend tests
   cd backend
   pytest

   # Frontend tests
   cd frontend
   npm test
   ```

### AWS Deployment

1. **Configure AWS CLI:**
   ```bash
   aws configure
   ```

2. **Deploy to AWS:**
   ```bash
   cd aws
   ./deploy.sh
   ```

3. **Update Frontend:**
   ```bash
   # Update API URL with deployed endpoint
   echo "REACT_APP_API_URL=https://your-api-id.execute-api.region.amazonaws.com/prod" > .env
   ```

## File Naming Conventions

- **Python files**: snake_case (e.g., `weaviate_client.py`)
- **React components**: PascalCase (e.g., `GraphView.jsx`)
- **Configuration files**: lowercase with dots (e.g., `package.json`)
- **Documentation**: lowercase with underscores (e.g., `setup_instructions.md`)

## Dependencies

### Backend Dependencies

- FastAPI - Web framework
- LlamaIndex - Multi-agent orchestration
- Weaviate Client - Vector database
- Friendli AI - AI inference
- Boto3 - AWS SDK
- Uvicorn - ASGI server

### Frontend Dependencies

- React - Frontend framework
- Tailwind CSS - Styling
- Framer Motion - Animations
- React Force Graph - Graph visualization
- Axios - HTTP client
- React Hot Toast - Notifications

## Security Considerations

- Environment variables for sensitive data
- CORS configuration for cross-origin requests
- API authentication and authorization
- AWS IAM roles and policies
- Input validation and sanitization

## Performance Optimizations

- Vector indexing for efficient search
- Response caching
- Lazy loading of components
- Optimized bundle sizes
- Serverless auto-scaling

This project structure provides a comprehensive, production-ready multi-agent system that demonstrates advanced AI orchestration, vector memory, and enterprise knowledge management capabilities.
