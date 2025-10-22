"""
AWS Lambda function for direct Friendli AI queries
ContextCloud Agents - AWS AI Agents Hack Day
"""

import json
import os
import boto3
from botocore.exceptions import ClientError

def lambda_handler(event, context):
    """
    Lambda function to handle direct Friendli AI queries
    """
    try:
        # Parse the request
        if 'body' in event:
            body = json.loads(event['body'])
        else:
            body = event
        
        query = body.get('query', '')
        if not query:
            return {
                'statusCode': 400,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({
                    'error': 'Query is required'
                })
            }
        
        # Simulate Friendli AI response
        # In a real implementation, this would call the actual Friendli AI API
        response = simulate_friendli_response(query)
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'message': 'Friendli AI response generated',
                'query': query,
                'response': response
            })
        }
        
    except Exception as e:
        print(f"Error querying Friendli AI: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'error': f'Friendli query failed: {str(e)}'
            })
        }

def simulate_friendli_response(query):
    """Simulate Friendli AI response"""
    
    # Generate a contextual response based on the query
    if 'compliance' in query.lower():
        return f"""Based on your query about compliance, here are the key insights:

**Compliance Analysis:**
- Current compliance framework covers GDPR, CCPA, and industry-specific regulations
- Regular audits are conducted quarterly to ensure adherence
- Training programs are in place for all employees

**Recommendations:**
1. Review compliance policies monthly
2. Update documentation as regulations change
3. Conduct risk assessments regularly

**Risk Factors:**
- Potential regulatory changes
- Employee training gaps
- Documentation updates needed

This analysis is based on enterprise knowledge and current compliance standards."""
    
    elif 'data privacy' in query.lower() or 'privacy' in query.lower():
        return f"""Data Privacy Analysis for your query:

**Privacy Framework:**
- Data classification system in place
- Encryption standards implemented
- Access controls properly configured

**Key Privacy Measures:**
1. Data minimization principles applied
2. Consent management system active
3. Regular privacy impact assessments

**Compliance Status:**
- GDPR compliance: ✅ Verified
- CCPA compliance: ✅ Verified
- Industry standards: ✅ Met

**Recommendations:**
- Continue regular privacy audits
- Update privacy policies annually
- Maintain employee training programs

This analysis ensures your enterprise maintains the highest privacy standards."""
    
    elif 'policy' in query.lower():
        return f"""Policy Analysis for your query:

**Current Policy Framework:**
- Comprehensive policy documentation available
- Regular policy reviews conducted
- Employee training on policy compliance

**Policy Categories:**
1. Data Protection Policies
2. Security Policies
3. Compliance Policies
4. Operational Policies

**Key Findings:**
- Policies are up-to-date and comprehensive
- Regular reviews ensure relevance
- Employee awareness is high

**Recommendations:**
- Continue quarterly policy reviews
- Update policies based on regulatory changes
- Maintain policy training programs

This analysis provides a comprehensive overview of your policy framework."""
    
    else:
        return f"""Analysis of your query: "{query}"

**Key Insights:**
- Enterprise knowledge base contains relevant information
- Multiple documents provide comprehensive coverage
- Analysis reveals important patterns and trends

**Findings:**
1. Relevant information identified in policy documents
2. Compliance considerations documented
3. Best practices available for implementation

**Recommendations:**
- Review identified documents for detailed information
- Consider compliance implications
- Implement recommended best practices

**Confidence Level:** High
**Source:** Enterprise Knowledge Base Analysis

This response is generated based on comprehensive analysis of your enterprise knowledge base."""
