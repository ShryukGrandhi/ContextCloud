#!/bin/bash

# ContextCloud Agents - AWS Deployment Script
# AWS AI Agents Hack Day

set -e

echo "🚀 Deploying ContextCloud Agents to AWS..."

# Configuration
REGION=${AWS_REGION:-us-east-1}
STACK_NAME="contextcloud-agents"
S3_BUCKET_NAME=${S3_BUCKET_NAME:-contextcloud-documents}

# Check if AWS CLI is configured
if ! aws sts get-caller-identity &> /dev/null; then
    echo "❌ AWS CLI not configured. Please run 'aws configure' first."
    exit 1
fi

echo "✅ AWS CLI configured"

# Create S3 bucket for documents if it doesn't exist
echo "📦 Creating S3 bucket for documents..."
if ! aws s3 ls "s3://$S3_BUCKET_NAME" &> /dev/null; then
    if [ "$REGION" = "us-east-1" ]; then
        aws s3 mb "s3://$S3_BUCKET_NAME"
    else
        aws s3 mb "s3://$S3_BUCKET_NAME" --region "$REGION"
    fi
    echo "✅ S3 bucket created: $S3_BUCKET_NAME"
else
    echo "✅ S3 bucket already exists: $S3_BUCKET_NAME"
fi

# Create deployment package for Lambda functions
echo "📦 Creating Lambda deployment packages..."
mkdir -p dist

# Package upload lambda
cd lambdas
zip -r ../dist/upload_lambda.zip upload_lambda.py
echo "✅ Upload lambda packaged"

# Package run agents lambda
zip -r ../dist/run_agents_lambda.zip run_agents_lambda.py
echo "✅ Run agents lambda packaged"

# Package ask lambda
zip -r ../dist/ask_lambda.zip ask_lambda.py
echo "✅ Ask lambda packaged"

# Package get graph lambda
zip -r ../dist/get_graph_lambda.zip get_graph_lambda.py
echo "✅ Get graph lambda packaged"

cd ..

# Deploy Lambda functions
echo "🚀 Deploying Lambda functions..."

# Upload Lambda function
aws lambda create-function \
    --function-name contextcloud-upload \
    --runtime python3.9 \
    --role arn:aws:iam::$(aws sts get-caller-identity --query Account --output text):role/lambda-execution-role \
    --handler upload_lambda.lambda_handler \
    --zip-file fileb://dist/upload_lambda.zip \
    --region "$REGION" \
    --timeout 300 \
    --memory-size 512 \
    --environment Variables="{S3_BUCKET_NAME=$S3_BUCKET_NAME}" \
    || echo "⚠️ Upload lambda may already exist"

# Run Agents Lambda function
aws lambda create-function \
    --function-name contextcloud-run-agents \
    --runtime python3.9 \
    --role arn:aws:iam::$(aws sts get-caller-identity --query Account --output text):role/lambda-execution-role \
    --handler run_agents_lambda.lambda_handler \
    --zip-file fileb://dist/run_agents_lambda.zip \
    --region "$REGION" \
    --timeout 300 \
    --memory-size 512 \
    || echo "⚠️ Run agents lambda may already exist"

# Ask Lambda function
aws lambda create-function \
    --function-name contextcloud-ask \
    --runtime python3.9 \
    --role arn:aws:iam::$(aws sts get-caller-identity --query Account --output text):role/lambda-execution-role \
    --handler ask_lambda.lambda_handler \
    --zip-file fileb://dist/ask_lambda.zip \
    --region "$REGION" \
    --timeout 300 \
    --memory-size 512 \
    || echo "⚠️ Ask lambda may already exist"

# Get Graph Lambda function
aws lambda create-function \
    --function-name contextcloud-get-graph \
    --runtime python3.9 \
    --role arn:aws:iam::$(aws sts get-caller-identity --query Account --output text):role/lambda-execution-role \
    --handler get_graph_lambda.lambda_handler \
    --zip-file fileb://dist/get_graph_lambda.zip \
    --region "$REGION" \
    --timeout 300 \
    --memory-size 512 \
    || echo "⚠️ Get graph lambda may already exist"

echo "✅ Lambda functions deployed"

# Create API Gateway
echo "🌐 Creating API Gateway..."

# Create REST API
API_ID=$(aws apigateway create-rest-api \
    --name "ContextCloud Agents API" \
    --description "Multi-agent enterprise knowledge platform API" \
    --region "$REGION" \
    --query 'id' \
    --output text)

echo "✅ API Gateway created with ID: $API_ID"

# Get root resource ID
ROOT_RESOURCE_ID=$(aws apigateway get-resources \
    --rest-api-id "$API_ID" \
    --region "$REGION" \
    --query 'items[0].id' \
    --output text)

echo "✅ Root resource ID: $ROOT_RESOURCE_ID"

# Create resources and methods
echo "🔧 Setting up API Gateway resources and methods..."

# Create /upload resource
UPLOAD_RESOURCE_ID=$(aws apigateway create-resource \
    --rest-api-id "$API_ID" \
    --parent-id "$ROOT_RESOURCE_ID" \
    --path-part "upload" \
    --region "$REGION" \
    --query 'id' \
    --output text)

# Create POST method for /upload
aws apigateway put-method \
    --rest-api-id "$API_ID" \
    --resource-id "$UPLOAD_RESOURCE_ID" \
    --http-method POST \
    --authorization-type NONE \
    --region "$REGION"

# Set up Lambda integration for /upload
aws apigateway put-integration \
    --rest-api-id "$API_ID" \
    --resource-id "$UPLOAD_RESOURCE_ID" \
    --http-method POST \
    --type AWS_PROXY \
    --integration-http-method POST \
    --uri "arn:aws:apigateway:$REGION:lambda:path/2015-03-31/functions/arn:aws:lambda:$REGION:$(aws sts get-caller-identity --query Account --output text):function:contextcloud-upload/invocations" \
    --region "$REGION"

# Create /agents resource
AGENTS_RESOURCE_ID=$(aws apigateway create-resource \
    --rest-api-id "$API_ID" \
    --parent-id "$ROOT_RESOURCE_ID" \
    --path-part "agents" \
    --region "$REGION" \
    --query 'id' \
    --output text)

# Create /agents/run resource
RUN_RESOURCE_ID=$(aws apigateway create-resource \
    --rest-api-id "$API_ID" \
    --parent-id "$AGENTS_RESOURCE_ID" \
    --path-part "run" \
    --region "$REGION" \
    --query 'id' \
    --output text)

# Create POST method for /agents/run
aws apigateway put-method \
    --rest-api-id "$API_ID" \
    --resource-id "$RUN_RESOURCE_ID" \
    --http-method POST \
    --authorization-type NONE \
    --region "$REGION"

# Set up Lambda integration for /agents/run
aws apigateway put-integration \
    --rest-api-id "$API_ID" \
    --resource-id "$RUN_RESOURCE_ID" \
    --http-method POST \
    --type AWS_PROXY \
    --integration-http-method POST \
    --uri "arn:aws:apigateway:$REGION:lambda:path/2015-03-31/functions/arn:aws:lambda:$REGION:$(aws sts get-caller-identity --query Account --output text):function:contextcloud-run-agents/invocations" \
    --region "$REGION"

# Create /ask resource
ASK_RESOURCE_ID=$(aws apigateway create-resource \
    --rest-api-id "$API_ID" \
    --parent-id "$ROOT_RESOURCE_ID" \
    --path-part "ask" \
    --region "$REGION" \
    --query 'id' \
    --output text)

# Create POST method for /ask
aws apigateway put-method \
    --rest-api-id "$API_ID" \
    --resource-id "$ASK_RESOURCE_ID" \
    --http-method POST \
    --authorization-type NONE \
    --region "$REGION"

# Set up Lambda integration for /ask
aws apigateway put-integration \
    --rest-api-id "$API_ID" \
    --resource-id "$ASK_RESOURCE_ID" \
    --http-method POST \
    --type AWS_PROXY \
    --integration-http-method POST \
    --uri "arn:aws:apigateway:$REGION:lambda:path/2015-03-31/functions/arn:aws:lambda:$REGION:$(aws sts get-caller-identity --query Account --output text):function:contextcloud-ask/invocations" \
    --region "$REGION"

# Create /graph resource
GRAPH_RESOURCE_ID=$(aws apigateway create-resource \
    --rest-api-id "$API_ID" \
    --parent-id "$ROOT_RESOURCE_ID" \
    --path-part "graph" \
    --region "$REGION" \
    --query 'id' \
    --output text)

# Create GET method for /graph
aws apigateway put-method \
    --rest-api-id "$API_ID" \
    --resource-id "$GRAPH_RESOURCE_ID" \
    --http-method GET \
    --authorization-type NONE \
    --region "$REGION"

# Set up Lambda integration for /graph
aws apigateway put-integration \
    --rest-api-id "$API_ID" \
    --resource-id "$GRAPH_RESOURCE_ID" \
    --http-method GET \
    --type AWS_PROXY \
    --integration-http-method POST \
    --uri "arn:aws:apigateway:$REGION:lambda:path/2015-03-31/functions/arn:aws:lambda:$REGION:$(aws sts get-caller-identity --query Account --output text):function:contextcloud-get-graph/invocations" \
    --region "$REGION"

echo "✅ API Gateway resources and methods created"

# Deploy API
echo "🚀 Deploying API Gateway..."
aws apigateway create-deployment \
    --rest-api-id "$API_ID" \
    --stage-name "prod" \
    --region "$REGION"

echo "✅ API Gateway deployed"

# Add CORS support
echo "🔧 Adding CORS support..."
aws apigateway put-gateway-response \
    --rest-api-id "$API_ID" \
    --response-type DEFAULT_4XX \
    --response-parameters '{"gatewayresponse.header.Access-Control-Allow-Origin":"'"'"'*'"'"'","gatewayresponse.header.Access-Control-Allow-Headers":"'"'"'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token'"'"'","gatewayresponse.header.Access-Control-Allow-Methods":"'"'"'GET,POST,PUT,DELETE,OPTIONS'"'"'"}'

aws apigateway put-gateway-response \
    --rest-api-id "$API_ID" \
    --response-type DEFAULT_5XX \
    --response-parameters '{"gatewayresponse.header.Access-Control-Allow-Origin":"'"'"'*'"'"'","gatewayresponse.header.Access-Control-Allow-Headers":"'"'"'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token'"'"'","gatewayresponse.header.Access-Control-Allow-Methods":"'"'"'GET,POST,PUT,DELETE,OPTIONS'"'"'"}'

echo "✅ CORS support added"

# Grant API Gateway permission to invoke Lambda functions
echo "🔐 Setting up Lambda permissions..."
aws lambda add-permission \
    --function-name contextcloud-upload \
    --statement-id "apigateway-invoke-upload" \
    --action lambda:InvokeFunction \
    --principal apigateway.amazonaws.com \
    --source-arn "arn:aws:execute-api:$REGION:$(aws sts get-caller-identity --query Account --output text):$API_ID/*/*" \
    --region "$REGION" || echo "⚠️ Permission may already exist"

aws lambda add-permission \
    --function-name contextcloud-run-agents \
    --statement-id "apigateway-invoke-run-agents" \
    --action lambda:InvokeFunction \
    --principal apigateway.amazonaws.com \
    --source-arn "arn:aws:execute-api:$REGION:$(aws sts get-caller-identity --query Account --output text):$API_ID/*/*" \
    --region "$REGION" || echo "⚠️ Permission may already exist"

aws lambda add-permission \
    --function-name contextcloud-ask \
    --statement-id "apigateway-invoke-ask" \
    --action lambda:InvokeFunction \
    --principal apigateway.amazonaws.com \
    --source-arn "arn:aws:execute-api:$REGION:$(aws sts get-caller-identity --query Account --output text):$API_ID/*/*" \
    --region "$REGION" || echo "⚠️ Permission may already exist"

aws lambda add-permission \
    --function-name contextcloud-get-graph \
    --statement-id "apigateway-invoke-get-graph" \
    --action lambda:InvokeFunction \
    --principal apigateway.amazonaws.com \
    --source-arn "arn:aws:execute-api:$REGION:$(aws sts get-caller-identity --query Account --output text):$API_ID/*/*" \
    --region "$REGION" || echo "⚠️ Permission may already exist"

echo "✅ Lambda permissions configured"

# Output deployment information
echo ""
echo "🎉 Deployment completed successfully!"
echo ""
echo "📋 Deployment Summary:"
echo "  Region: $REGION"
echo "  API Gateway ID: $API_ID"
echo "  API Gateway URL: https://$API_ID.execute-api.$REGION.amazonaws.com/prod"
echo "  S3 Bucket: $S3_BUCKET_NAME"
echo ""
echo "🔗 API Endpoints:"
echo "  POST https://$API_ID.execute-api.$REGION.amazonaws.com/prod/upload"
echo "  POST https://$API_ID.execute-api.$REGION.amazonaws.com/prod/agents/run"
echo "  POST https://$API_ID.execute-api.$REGION.amazonaws.com/prod/ask"
echo "  GET  https://$API_ID.execute-api.$REGION.amazonaws.com/prod/graph"
echo ""
echo "🚀 ContextCloud Agents is now deployed and ready to use!"
echo ""
echo "Next steps:"
echo "1. Update your frontend to use the API Gateway URL"
echo "2. Test the endpoints using the provided URLs"
echo "3. Upload documents and run queries"
echo ""

# Clean up
rm -rf dist

echo "✅ Cleanup completed"
