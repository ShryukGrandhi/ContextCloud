#!/bin/bash

# ContextCloud Agents - Environment Setup Script
# This script creates the .env file with the provided API keys

echo "🔧 Setting up ContextCloud Agents environment..."

# Create .env file in backend directory
cat > contextcloud/backend/.env << EOF
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

# Database Configuration (if using additional DB)
DATABASE_URL=sqlite:///./contextcloud.db

# Security
SECRET_KEY=your_secret_key_for_jwt_tokens
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
EOF

echo "✅ Environment file created with API keys"
echo ""
echo "📋 Next steps:"
echo "1. Update AWS credentials in contextcloud/backend/.env"
echo "2. Start Weaviate: docker run -p 8080:8080 semitechnologies/weaviate:latest"
echo "3. Run backend: cd contextcloud/backend && uvicorn main:app --reload"
echo "4. Run frontend: cd contextcloud/frontend && npm start"
echo ""
echo "🚀 ContextCloud Agents is ready to use!"
