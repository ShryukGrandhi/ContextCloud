"""
AWS Lambda function for document upload and processing
ContextCloud Agents - AWS AI Agents Hack Day
"""

import json
import boto3
import base64
import os
from botocore.exceptions import ClientError

# Initialize AWS clients
s3_client = boto3.client('s3')
textract_client = boto3.client('textract')
comprehend_client = boto3.client('comprehend')

def lambda_handler(event, context):
    """
    Lambda function to handle document upload and processing
    """
    try:
        # Parse the request
        if 'body' in event:
            body = json.loads(event['body'])
        else:
            body = event
        
        # Get file data (assuming base64 encoded)
        file_data = body.get('file_data')
        filename = body.get('filename', 'document.pdf')
        document_type = body.get('document_type', 'general')
        
        if not file_data:
            return {
                'statusCode': 400,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Methods': 'POST, OPTIONS',
                    'Access-Control-Allow-Headers': 'Content-Type'
                },
                'body': json.dumps({
                    'error': 'No file data provided'
                })
            }
        
        # Decode base64 file data
        file_content = base64.b64decode(file_data)
        
        # Generate unique S3 key
        import uuid
        doc_id = str(uuid.uuid4())
        s3_key = f"documents/{doc_id}/{filename}"
        
        # Upload to S3
        bucket_name = os.environ.get('S3_BUCKET_NAME', 'contextcloud-documents')
        s3_client.put_object(
            Bucket=bucket_name,
            Key=s3_key,
            Body=file_content,
            ContentType='application/octet-stream'
        )
        
        # Extract text using Textract
        extracted_text = extract_text_with_textract(file_content)
        
        # Store extracted text in S3
        text_key = f"documents/{doc_id}/extracted_text.txt"
        s3_client.put_object(
            Bucket=bucket_name,
            Key=text_key,
            Body=extracted_text,
            ContentType='text/plain'
        )
        
        # Extract entities using Comprehend
        entities = extract_entities_with_comprehend(extracted_text)
        
        # Prepare response
        response_data = {
            'message': 'Document uploaded and processed successfully',
            'document_id': doc_id,
            's3_uri': f"s3://{bucket_name}/{s3_key}",
            'filename': filename,
            'document_type': document_type,
            'entities_found': len(entities),
            'entities': entities,
            'text_length': len(extracted_text)
        }
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'POST, OPTIONS',
                'Access-Control-Allow-Headers': 'Content-Type'
            },
            'body': json.dumps(response_data)
        }
        
    except Exception as e:
        print(f"Error processing document: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'error': f'Document processing failed: {str(e)}'
            })
        }

def extract_text_with_textract(file_content):
    """Extract text from document using AWS Textract"""
    try:
        response = textract_client.detect_document_text(
            Document={'Bytes': file_content}
        )
        
        extracted_text = ""
        for block in response.get('Blocks', []):
            if block['BlockType'] == 'LINE':
                extracted_text += block['Text'] + '\n'
        
        return extracted_text.strip()
        
    except Exception as e:
        print(f"Textract extraction failed: {str(e)}")
        return ""

def extract_entities_with_comprehend(text):
    """Extract entities from text using AWS Comprehend"""
    try:
        # Comprehend has a 5000 character limit
        if len(text) > 5000:
            text = text[:5000]
        
        response = comprehend_client.detect_entities(
            Text=text,
            LanguageCode='en'
        )
        
        entities = []
        for entity in response.get('Entities', []):
            if entity['Score'] > 0.7:  # Only include high-confidence entities
                entities.append(entity['Text'])
        
        return list(set(entities))  # Remove duplicates
        
    except Exception as e:
        print(f"Comprehend entity extraction failed: {str(e)}")
        return []
