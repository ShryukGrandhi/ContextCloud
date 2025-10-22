# ContextCloud Agents - Setup Instructions

## Quick Start Guide

This guide will help you set up and run ContextCloud Agents for the AWS AI Agents Hack Day.

## Prerequisites

- Python 3.9+
- Node.js 18+
- AWS CLI configured
- Friendli AI API key
- Weaviate instance (local or cloud)

## Environment Variables

Create a `.env` file in the `backend` directory with the following variables:

```bash
# Friendli AI Configuration
FRIENDLI_API_KEY=flp_XnVsxL4Y513ExPArCtvZa9qfoPMbLOCjA0PYVXXJShs06e
FRIENDLI_MODEL_NAME=llama-2-70b-chat

# Weaviate Configuration
WEAVIATE_URL=http://localhost:8080
WEAVIATE_API_KEY=SmVNbzFEaWJrRW42TDNsRF9GRUJ1dDF1QlRaZkg1QW0yblhHOStVU1hYTi9mbWdTcDhhVmNuL01KL284PV92MjAw

# AWS Configuration
AWS_ACCESS_KEY_ID=your_aws_access_key
AWS_SECRET_ACCESS_KEY=your_aws_secret_key
AWS_REGION=us-east-1
S3_BUCKET_NAME=contextcloud-documents

# Application Configuration
DEBUG=True
LOG_LEVEL=INFO
MAX_FILE_SIZE_MB=50
ALLOWED_FILE_TYPES=pdf,txt,docx,md
```

## Backend Setup

1. **Navigate to backend directory:**
   ```bash
   cd contextcloud/backend
   ```

2. **Create virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set environment variables:**
   ```bash
   export FRIENDLI_API_KEY="your_key_here"
   export AWS_ACCESS_KEY_ID="your_key"
   export AWS_SECRET_ACCESS_KEY="your_secret"
   export WEAVIATE_URL="your_weaviate_url"
   ```

5. **Run the backend:**
   ```bash
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```

## Frontend Setup

1. **Navigate to frontend directory:**
   ```bash
   cd contextcloud/frontend
   ```

2. **Install dependencies:**
   ```bash
   npm install
   ```

3. **Create environment file:**
   ```bash
   echo "REACT_APP_API_URL=http://localhost:8000" > .env
   ```

4. **Start the frontend:**
   ```bash
   npm start
   ```

## AWS Deployment

1. **Configure AWS CLI:**
   ```bash
   aws configure
   ```

2. **Set environment variables:**
   ```bash
   export AWS_REGION=us-east-1
   export S3_BUCKET_NAME=contextcloud-documents
   ```

3. **Run deployment script:**
   ```bash
   cd contextcloud/aws
   chmod +x deploy.sh
   ./deploy.sh
   ```

4. **Update frontend API URL:**
   ```bash
   # Update .env file with the API Gateway URL from deployment output
   echo "REACT_APP_API_URL=https://your-api-id.execute-api.region.amazonaws.com/prod" > .env
   ```

## Weaviate Setup

### Local Weaviate

1. **Run Weaviate with Docker:**
   ```bash
   docker run -p 8080:8080 -p 50051:50051 \
     -e QUERY_DEFAULTS_LIMIT=25 \
     -e AUTHENTICATION_ANONYMOUS_ACCESS_ENABLED=true \
     -e PERSISTENCE_DATA_PATH='/var/lib/weaviate' \
     -e DEFAULT_VECTORIZER_MODULE='none' \
     -e CLUSTER_HOSTNAME='node1' \
     semitechnologies/weaviate:latest
   ```

2. **Verify Weaviate is running:**
   ```bash
   curl http://localhost:8080/v1/meta
   ```

### Cloud Weaviate

1. **Sign up for Weaviate Cloud Services:**
   - Visit [Weaviate Cloud Services](https://console.weaviate.cloud)
   - Create a new cluster
   - Get your cluster URL and API key

2. **Update environment variables:**
   ```bash
   export WEAVIATE_URL="https://your-cluster.weaviate.network"
   export WEAVIATE_API_KEY="your-api-key"
   ```

## Testing the System

1. **Health Check:**
   ```bash
   curl http://localhost:8000/health
   ```

2. **Upload a Document:**
   ```bash
   curl -X POST "http://localhost:8000/upload" \
     -H "Content-Type: multipart/form-data" \
     -F "file=@sample-document.pdf" \
     -F "document_type=policy"
   ```

3. **Run Agent Workflow:**
   ```bash
   curl -X POST "http://localhost:8000/agents/run" \
     -H "Content-Type: application/json" \
     -d '{"query": "What are our compliance requirements?"}'
   ```

4. **Get Knowledge Graph:**
   ```bash
   curl http://localhost:8000/graph
   ```

## Frontend Testing

1. **Open the application:**
   - Navigate to `http://localhost:3000`
   - You should see the ContextCloud Agents dashboard

2. **Test Features:**
   - Upload a document using the file upload
   - Ask a question using the search bar
   - View agent activity in the console
   - Explore the knowledge graph visualization

## Troubleshooting

### Common Issues

1. **Weaviate Connection Error:**
   - Verify Weaviate is running on the correct port
   - Check WEAVIATE_URL environment variable
   - Ensure network connectivity

2. **AWS Credentials Error:**
   - Run `aws configure` to set up credentials
   - Verify AWS_REGION is set correctly
   - Check IAM permissions

3. **Friendli AI Error:**
   - Verify FRIENDLI_API_KEY is set
   - Check API key validity
   - Ensure sufficient API credits

4. **Frontend Build Error:**
   - Run `npm install` to install dependencies
   - Check Node.js version (18+ required)
   - Clear npm cache if needed

### Logs and Debugging

1. **Backend Logs:**
   ```bash
   # Check FastAPI logs
   tail -f logs/contextcloud.log
   ```

2. **Frontend Logs:**
   ```bash
   # Check browser console for errors
   # Check network tab for API calls
   ```

3. **AWS Logs:**
   ```bash
   # Check CloudWatch logs for Lambda functions
   aws logs describe-log-groups
   ```

## Production Deployment

For production deployment:

1. **Use production environment variables:**
   - Set DEBUG=False
   - Use production Weaviate instance
   - Configure proper AWS IAM roles

2. **Enable monitoring:**
   - Set up CloudWatch alarms
   - Configure log aggregation
   - Monitor API Gateway metrics

3. **Security considerations:**
   - Enable API authentication
   - Use HTTPS endpoints
   - Implement rate limiting

## Support

For issues and questions:
- Check the troubleshooting section above
- Review the architecture documentation
- Consult the API documentation
- Check the GitHub issues page

## Demo Script

1. **Start the system:**
   ```bash
   # Terminal 1: Start backend
   cd contextcloud/backend && uvicorn main:app --reload

   # Terminal 2: Start frontend
   cd contextcloud/frontend && npm start
   ```

2. **Demo workflow:**
   - Open `http://localhost:3000`
   - Upload a sample document
   - Ask: "What are our compliance requirements?"
   - Show agent activity in console
   - Demonstrate knowledge graph visualization
   - Highlight real-time agent collaboration

3. **Key talking points:**
   - Multi-agent orchestration with LlamaIndex
   - Vector memory with Weaviate
   - AI inference with Friendli AI
   - AWS services integration
   - Real-time visualization
   - Enterprise compliance focus

This setup will give you a fully functional ContextCloud Agents system ready for the AWS AI Agents Hack Day!
