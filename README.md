# 🧠 ContextCloud Agents - AWS AI Agents Hack Day

A production-grade **multi-agent enterprise platform** that transforms company knowledge into a living, collaborative AI system.

## 🎯 Overview

ContextCloud Agents uses **LlamaIndex** for orchestration, **Weaviate** for vector memory, and **Friendli AI** for inference to create a multi-agent system that can retrieve, reason, and summarize enterprise information in real-time.

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   React Frontend │    │   FastAPI Backend │    │   AWS Services  │
│                 │    │                 │    │                 │
│ • Graph View    │◄──►│ • Multi-Agents  │◄──►│ • Textract     │
│ • Agent Console │    │ • LlamaIndex    │    │ • Comprehend   │
│ • Search Bar    │    │ • Weaviate      │    │ • S3 Storage   │
│ • Real-time Logs│    │ • Friendli AI   │    │ • Lambda       │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 🤖 Agent Workflow

1. **PlannerAgent** - Interprets queries and orchestrates workflow
2. **RetrieverAgent** - Queries Weaviate for relevant documents  
3. **AnalyzerAgent** - Processes text using Friendli AI and AWS Comprehend
4. **ReporterAgent** - Summarizes results and updates knowledge graph

## 🚀 Quick Start

### Prerequisites

- Python 3.9+
- Node.js 18+
- AWS CLI configured
- Friendli AI API key
- Weaviate instance

### Backend Setup

```bash
cd contextcloud/backend
pip install -r requirements.txt

# Set up environment with provided API keys
chmod +x ../setup_env.sh
../setup_env.sh

# Update AWS credentials in .env file if needed
uvicorn main:app --reload
```

### Frontend Setup

```bash
cd contextcloud/frontend
npm install
npm start
```

### AWS Deployment

```bash
cd contextcloud/aws
./deploy.sh
```

## 🔧 Environment Variables

```bash
FRIENDLI_API_KEY=your_friendli_key
WEAVIATE_URL=http://localhost:8080
AWS_ACCESS_KEY_ID=your_aws_key
AWS_SECRET_ACCESS_KEY=your_aws_secret
AWS_REGION=us-east-1
S3_BUCKET_NAME=contextcloud-documents
```

## 📊 Demo Features

- **Live Agent Console** - See agents working in real-time
- **Knowledge Graph** - Interactive visualization of document relationships
- **Tool Calling Logs** - Track which APIs each agent is calling
- **Enterprise Focus** - Built for compliance and policy intelligence

## 🏆 Judging Criteria Alignment

✅ **Multi-Agent System** - LlamaIndex orchestration with distinct agent roles  
✅ **Tool-Calling** - AWS Textract, Comprehend, Friendli AI integration  
✅ **Vector Memory** - Weaviate for persistent document embeddings  
✅ **Enterprise Relevance** - Compliance intelligence use case  
✅ **Visualization** - Real-time graph with agent activity logs  
✅ **Architecture** - Production-grade with proper error handling  

## 📁 Project Structure

```
contextcloud/
├── backend/           # FastAPI + LlamaIndex + Multi-Agents
├── frontend/          # React + Tailwind + Graph Visualization  
├── aws/              # Lambda functions + API Gateway
├── docs/             # Architecture diagrams + documentation
└── tests/            # Unit and integration tests
```

## 🎯 Demo Script

> "ContextCloud Agents transforms enterprise document archives into a living, multi-agent brain. Using LlamaIndex for orchestration, Weaviate for memory, and Friendli AI for inference, our agents collaborate to reason across thousands of policies and reports. Watch as each agent calls real tools and renders insights as a glowing interactive graph in real-time."

---

Built for **AWS AI Agents Hack Day** - Showcasing the future of enterprise AI collaboration.
