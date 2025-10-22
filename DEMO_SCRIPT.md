# ContextCloud Agents - Demo Script

## AWS AI Agents Hack Day Demo

This script provides a structured demonstration of ContextCloud Agents for the AWS AI Agents Hack Day competition.

## Pre-Demo Setup

1. **Ensure all services are running:**
   ```bash
   # Terminal 1: Backend
   cd contextcloud/backend
   uvicorn main:app --reload

   # Terminal 2: Frontend
   cd contextcloud/frontend
   npm start
   ```

2. **Verify system health:**
   - Backend: http://localhost:8000/health
   - Frontend: http://localhost:3000

## Demo Script (5-7 minutes)

### Introduction (30 seconds)

"Welcome to ContextCloud Agents, a multi-agent enterprise knowledge platform built for the AWS AI Agents Hack Day. 

Today I'll demonstrate how we've transformed enterprise document archives into a living, collaborative AI system using LlamaIndex orchestration, Weaviate vector memory, and Friendli AI inference."

### System Overview (1 minute)

**Show the dashboard:**
- "This is our main dashboard with a glassmorphic design that shows real-time agent activity"
- "You can see four distinct agents: PlannerAgent, RetrieverAgent, AnalyzerAgent, and ReporterAgent"
- "Each agent has a specific role and calls real tools to accomplish enterprise knowledge tasks"

**Highlight the architecture:**
- "The system integrates multiple AWS services: Textract for OCR, Comprehend for entity extraction, S3 for storage"
- "Weaviate provides vector memory for semantic search"
- "Friendli AI powers the reasoning and analysis capabilities"

### Document Upload Demo (1 minute)

**Upload a sample document:**
- "Let me upload a sample policy document to demonstrate the system"
- "Watch as the system processes this document through AWS Textract for OCR"
- "AWS Comprehend extracts entities and metadata"
- "The document gets embedded and stored in our Weaviate vector database"

**Show the processing:**
- Point to the agent console showing processing steps
- Highlight the real-time logs: "Textract extraction complete", "Entities extracted", "Document stored in Weaviate"

### Multi-Agent Workflow Demo (2 minutes)

**Ask a complex query:**
- "Now let me ask: 'What are our compliance requirements for data privacy?'"
- "Watch as our multi-agent system orchestrates a complete workflow"

**Show each agent in action:**

1. **PlannerAgent:**
   - "PlannerAgent analyzes the query intent and creates a workflow plan"
   - "It determines we need document retrieval, analysis, and summarization"

2. **RetrieverAgent:**
   - "RetrieverAgent queries Weaviate for relevant documents"
   - "It finds 3 relevant documents with high confidence scores"
   - "Documents are ranked by relevance to the query"

3. **AnalyzerAgent:**
   - "AnalyzerAgent processes the retrieved documents"
   - "It calls Friendli AI for reasoning and analysis"
   - "AWS Comprehend extracts additional entities"
   - "Patterns and insights are identified"

4. **ReporterAgent:**
   - "ReporterAgent generates a comprehensive summary"
   - "It creates actionable recommendations"
   - "The knowledge graph is updated with new insights"

### Knowledge Graph Visualization (1 minute)

**Show the interactive graph:**
- "Here's our knowledge graph showing the relationships between documents, entities, and insights"
- "You can see how documents connect to entities like 'GDPR', 'Compliance', 'Data Protection'"
- "The graph updates in real-time as agents process information"
- "Click on nodes to see detailed information"

**Highlight the visualization:**
- "The graph shows document nodes in green, entity nodes in purple, and insight nodes in pink"
- "Edges represent relationships and connections"
- "This provides a visual understanding of enterprise knowledge structure"

### Real-Time Agent Monitoring (30 seconds)

**Show agent console:**
- "The agent console shows real-time activity logs"
- "You can see exactly which tools each agent is calling"
- "System statistics show performance metrics"
- "All agent activities are logged with timestamps"

### Technical Highlights (1 minute)

**Emphasize the technical achievements:**

1. **Multi-Agent Orchestration:**
   - "We built a true multi-agent system using LlamaIndex"
   - "Each agent has distinct responsibilities and calls real tools"
   - "Agents communicate through shared vector memory"

2. **Real Tool Calling:**
   - "PlannerAgent calls workflow planning tools"
   - "RetrieverAgent queries Weaviate vector database"
   - "AnalyzerAgent calls Friendli AI and AWS Comprehend"
   - "ReporterAgent generates reports and updates graphs"

3. **Enterprise Focus:**
   - "Built specifically for compliance intelligence"
   - "Handles enterprise documents and policies"
   - "Provides actionable insights for decision-making"

4. **Production Architecture:**
   - "FastAPI backend with proper error handling"
   - "React frontend with real-time visualization"
   - "AWS Lambda functions for serverless deployment"
   - "Comprehensive logging and monitoring"

### Conclusion (30 seconds)

"ContextCloud Agents demonstrates the future of enterprise AI collaboration. We've built a production-grade system that transforms static document archives into a living, multi-agent brain that can reason, analyze, and provide insights in real-time.

The system showcases advanced AI orchestration, vector memory, and enterprise knowledge management - exactly what the AWS AI Agents Hack Day is looking for."

## Key Talking Points

### For Judges

1. **Multi-Agent System:**
   - "Each agent has a distinct role and calls real tools"
   - "LlamaIndex orchestrates the workflow seamlessly"
   - "Agents communicate through shared vector memory"

2. **Tool Calling:**
   - "Real AWS Textract integration for OCR"
   - "AWS Comprehend for entity extraction"
   - "Friendli AI for reasoning and analysis"
   - "Weaviate for vector search and storage"

3. **Enterprise Relevance:**
   - "Built for compliance intelligence use case"
   - "Handles real enterprise documents and policies"
   - "Provides actionable insights for decision-making"

4. **Visualization:**
   - "Real-time knowledge graph visualization"
   - "Interactive agent activity monitoring"
   - "Beautiful, responsive UI with glassmorphic design"

### Technical Depth

1. **Architecture:**
   - "Production-grade FastAPI backend"
   - "React frontend with real-time updates"
   - "AWS Lambda functions for serverless deployment"
   - "Comprehensive error handling and logging"

2. **Integration:**
   - "Seamless AWS services integration"
   - "Vector database for semantic search"
   - "AI inference with Friendli AI"
   - "Real-time visualization and monitoring"

## Demo Tips

1. **Preparation:**
   - Have sample documents ready
   - Test all endpoints beforehand
   - Ensure stable internet connection
   - Have backup plans for technical issues

2. **Presentation:**
   - Speak clearly and confidently
   - Point to specific features on screen
   - Emphasize the multi-agent collaboration
   - Highlight real tool calling

3. **Engagement:**
   - Ask judges if they have questions
   - Offer to demonstrate specific features
   - Show the code if requested
   - Explain the technical implementation

4. **Timing:**
   - Keep to the 5-7 minute limit
   - Practice the demo multiple times
   - Have a shorter 3-minute version ready
   - Be prepared for follow-up questions

## Backup Plans

1. **If demo fails:**
   - Have screenshots ready
   - Show the code and architecture
   - Explain the implementation verbally
   - Demonstrate individual components

2. **If time is limited:**
   - Focus on core multi-agent workflow
   - Show key visualizations
   - Emphasize technical achievements
   - Highlight enterprise relevance

This demo script ensures a compelling presentation that showcases the full capabilities of ContextCloud Agents while staying within the time constraints and highlighting the key judging criteria.
