"""
AWS Tools for ContextCloud Agents
Handles Textract, Comprehend, and S3 operations
"""

import os
import json
import logging
import boto3
from typing import Dict, Any, List, Optional
from botocore.exceptions import ClientError, NoCredentialsError
from fastapi import UploadFile
from utils.logger import setup_logger

logger = setup_logger(__name__)

class AWSTools:
    """AWS tools for document processing and storage"""
    
    def __init__(self):
        self.region = os.getenv("AWS_REGION", "us-east-1")
        self.s3_bucket = os.getenv("S3_BUCKET_NAME", "contextcloud-documents")
        
        # Initialize AWS clients
        self.s3_client = None
        self.textract_client = None
        self.comprehend_client = None
        
    async def initialize(self):
        """Initialize AWS clients"""
        try:
            logger.info(f"☁️ Initializing AWS clients in region: {self.region}")
            
            # Initialize S3 client
            self.s3_client = boto3.client(
                's3',
                region_name=self.region
            )
            
            # Initialize Textract client
            self.textract_client = boto3.client(
                'textract',
                region_name=self.region
            )
            
            # Initialize Comprehend client
            self.comprehend_client = boto3.client(
                'comprehend',
                region_name=self.region
            )
            
            # Test connections
            await self._test_connections()
            
            logger.info("✅ AWS clients initialized successfully")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize AWS clients: {e}")
            raise
    
    async def _test_connections(self):
        """Test AWS service connections"""
        try:
            # Test S3
            self.s3_client.head_bucket(Bucket=self.s3_bucket)
            logger.info(f"✅ S3 bucket accessible: {self.s3_bucket}")
            
            # Test Textract
            # Note: We can't test Textract without a document, so we'll just verify the client is created
            logger.info("✅ Textract client initialized")
            
            # Test Comprehend
            # Note: We can't test Comprehend without text, so we'll just verify the client is created
            logger.info("✅ Comprehend client initialized")
            
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == '404':
                logger.warning(f"⚠️ S3 bucket {self.s3_bucket} does not exist. Creating...")
                await self._create_s3_bucket()
            else:
                raise
        except Exception as e:
            logger.error(f"❌ AWS connection test failed: {e}")
            raise
    
    async def _create_s3_bucket(self):
        """Create S3 bucket if it doesn't exist"""
        try:
            if self.region == 'us-east-1':
                # us-east-1 doesn't need LocationConstraint
                self.s3_client.create_bucket(Bucket=self.s3_bucket)
            else:
                self.s3_client.create_bucket(
                    Bucket=self.s3_bucket,
                    CreateBucketConfiguration={'LocationConstraint': self.region}
                )
            
            logger.info(f"✅ Created S3 bucket: {self.s3_bucket}")
            
        except ClientError as e:
            if e.response['Error']['Code'] == 'BucketAlreadyExists':
                logger.info(f"✅ S3 bucket already exists: {self.s3_bucket}")
            else:
                raise
    
    async def extract_text_from_document(self, file: UploadFile) -> str:
        """Extract text from document using AWS Textract"""
        try:
            logger.info(f"📄 Extracting text from: {file.filename}")
            
            # Read file content
            file_content = await file.read()
            file.file.seek(0)  # Reset file pointer
            
            # Use Textract to extract text
            response = self.textract_client.detect_document_text(
                Document={'Bytes': file_content}
            )
            
            # Extract text from response
            extracted_text = ""
            for block in response.get('Blocks', []):
                if block['BlockType'] == 'LINE':
                    extracted_text += block['Text'] + '\n'
            
            logger.info(f"✅ Extracted {len(extracted_text)} characters from document")
            return extracted_text.strip()
            
        except ClientError as e:
            logger.error(f"❌ Textract extraction failed: {e}")
            raise Exception(f"Text extraction failed: {str(e)}")
        except Exception as e:
            logger.error(f"❌ Document processing failed: {e}")
            raise
    
    async def store_document_in_s3(self, file: UploadFile, extracted_text: str) -> str:
        """Store document and metadata in S3"""
        try:
            logger.info(f"☁️ Storing document in S3: {file.filename}")
            
            # Generate S3 key
            import uuid
            doc_id = str(uuid.uuid4())
            s3_key = f"documents/{doc_id}/{file.filename}"
            
            # Reset file pointer
            await file.seek(0)
            
            # Upload original file
            self.s3_client.upload_fileobj(
                file.file,
                self.s3_bucket,
                s3_key
            )
            
            # Store extracted text as metadata
            metadata_key = f"documents/{doc_id}/extracted_text.txt"
            self.s3_client.put_object(
                Bucket=self.s3_bucket,
                Key=metadata_key,
                Body=extracted_text,
                ContentType='text/plain'
            )
            
            s3_uri = f"s3://{self.s3_bucket}/{s3_key}"
            logger.info(f"✅ Document stored in S3: {s3_uri}")
            
            return s3_uri
            
        except Exception as e:
            logger.error(f"❌ S3 storage failed: {e}")
            raise
    
    async def extract_entities(self, text: str) -> List[str]:
        """Extract entities from text using AWS Comprehend"""
        try:
            logger.info(f"🔍 Extracting entities from text ({len(text)} chars)")
            
            # Comprehend has a 5000 character limit, so we'll truncate if necessary
            if len(text) > 5000:
                text = text[:5000]
                logger.info("⚠️ Text truncated to 5000 characters for Comprehend processing")
            
            # Detect entities
            response = self.comprehend_client.detect_entities(
                Text=text,
                LanguageCode='en'
            )
            
            # Extract entity names
            entities = []
            for entity in response.get('Entities', []):
                if entity['Score'] > 0.7:  # Only include high-confidence entities
                    entities.append(entity['Text'])
            
            # Remove duplicates and return
            unique_entities = list(set(entities))
            logger.info(f"✅ Extracted {len(unique_entities)} unique entities")
            
            return unique_entities
            
        except ClientError as e:
            logger.error(f"❌ Comprehend entity extraction failed: {e}")
            return []  # Return empty list on failure
        except Exception as e:
            logger.error(f"❌ Entity extraction failed: {e}")
            return []
    
    async def detect_sentiment(self, text: str) -> Dict[str, Any]:
        """Detect sentiment using AWS Comprehend"""
        try:
            logger.info(f"😊 Detecting sentiment from text ({len(text)} chars)")
            
            # Comprehend has a 5000 character limit
            if len(text) > 5000:
                text = text[:5000]
            
            response = self.comprehend_client.detect_sentiment(
                Text=text,
                LanguageCode='en'
            )
            
            sentiment_result = {
                "sentiment": response['Sentiment'],
                "confidence": {
                    "positive": response['SentimentScore']['Positive'],
                    "negative": response['SentimentScore']['Negative'],
                    "neutral": response['SentimentScore']['Neutral'],
                    "mixed": response['SentimentScore']['Mixed']
                }
            }
            
            logger.info(f"✅ Detected sentiment: {sentiment_result['sentiment']}")
            return sentiment_result
            
        except Exception as e:
            logger.error(f"❌ Sentiment detection failed: {e}")
            return {"sentiment": "unknown", "confidence": {}}
    
    async def detect_key_phrases(self, text: str) -> List[str]:
        """Detect key phrases using AWS Comprehend"""
        try:
            logger.info(f"🔑 Detecting key phrases from text ({len(text)} chars)")
            
            if len(text) > 5000:
                text = text[:5000]
            
            response = self.comprehend_client.detect_key_phrases(
                Text=text,
                LanguageCode='en'
            )
            
            key_phrases = []
            for phrase in response.get('KeyPhrases', []):
                if phrase['Score'] > 0.7:  # Only include high-confidence phrases
                    key_phrases.append(phrase['Text'])
            
            logger.info(f"✅ Detected {len(key_phrases)} key phrases")
            return key_phrases
            
        except Exception as e:
            logger.error(f"❌ Key phrase detection failed: {e}")
            return []
    
    async def health_check(self) -> str:
        """Check AWS services health"""
        try:
            # Test S3
            self.s3_client.head_bucket(Bucket=self.s3_bucket)
            
            # Test other services by checking if clients are initialized
            if not self.textract_client or not self.comprehend_client:
                return "partial"
            
            return "healthy"
            
        except ClientError as e:
            logger.error(f"❌ AWS health check failed: {e}")
            return "error"
        except Exception as e:
            logger.error(f"❌ AWS health check failed: {e}")
            return "error"
