"""
AWS Lambda function for retrieving knowledge graph data
ContextCloud Agents - AWS AI Agents Hack Day
"""

import json
import os
from datetime import datetime

def lambda_handler(event, context):
    """
    Lambda function to retrieve knowledge graph data
    """
    try:
        # Simulate knowledge graph data retrieval
        # In a real implementation, this would query Weaviate or another vector database
        graph_data = generate_sample_graph_data()
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'message': 'Knowledge graph retrieved',
                'graph': graph_data,
                'node_count': len(graph_data.get('nodes', [])),
                'edge_count': len(graph_data.get('edges', []))
            })
        }
        
    except Exception as e:
        print(f"Error retrieving knowledge graph: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'error': f'Graph retrieval failed: {str(e)}'
            })
        }

def generate_sample_graph_data():
    """Generate sample knowledge graph data"""
    
    # Sample nodes representing documents, entities, and insights
    nodes = [
        # Document nodes
        {
            'id': 'doc_1',
            'label': 'Policy Manual 2024',
            'type': 'document',
            'entities': ['GDPR', 'Compliance', 'Data Protection'],
            'content_preview': 'Comprehensive policy manual covering all enterprise policies and procedures...',
            'size': 15,
            'color': '#00ff88'
        },
        {
            'id': 'doc_2',
            'label': 'Compliance Guide',
            'type': 'document',
            'entities': ['Regulation', 'Standards', 'Requirements'],
            'content_preview': 'Detailed compliance guide with regulatory requirements and best practices...',
            'size': 15,
            'color': '#00ff88'
        },
        {
            'id': 'doc_3',
            'label': 'Data Privacy Report',
            'type': 'document',
            'entities': ['Privacy', 'Security', 'Protection'],
            'content_preview': 'Annual data privacy report with compliance status and recommendations...',
            'size': 15,
            'color': '#00ff88'
        },
        {
            'id': 'doc_4',
            'label': 'Security Framework',
            'type': 'document',
            'entities': ['Security', 'Framework', 'Controls'],
            'content_preview': 'Enterprise security framework with implementation guidelines...',
            'size': 15,
            'color': '#00ff88'
        },
        
        # Entity nodes
        {
            'id': 'entity_gdpr',
            'label': 'GDPR',
            'type': 'entity',
            'size': 12,
            'color': '#b347d9'
        },
        {
            'id': 'entity_compliance',
            'label': 'Compliance',
            'type': 'entity',
            'size': 12,
            'color': '#b347d9'
        },
        {
            'id': 'entity_data_protection',
            'label': 'Data Protection',
            'type': 'entity',
            'size': 12,
            'color': '#b347d9'
        },
        {
            'id': 'entity_security',
            'label': 'Security',
            'type': 'entity',
            'size': 12,
            'color': '#b347d9'
        },
        {
            'id': 'entity_privacy',
            'label': 'Privacy',
            'type': 'entity',
            'size': 12,
            'color': '#b347d9'
        },
        
        # Insight nodes
        {
            'id': 'insight_1',
            'label': 'Privacy Requirements',
            'type': 'insight',
            'size': 10,
            'color': '#ff6b9d'
        },
        {
            'id': 'insight_2',
            'label': 'Risk Assessment',
            'type': 'insight',
            'size': 10,
            'color': '#ff6b9d'
        },
        {
            'id': 'insight_3',
            'label': 'Compliance Framework',
            'type': 'insight',
            'size': 10,
            'color': '#ff6b9d'
        },
        {
            'id': 'insight_4',
            'label': 'Security Controls',
            'type': 'insight',
            'size': 10,
            'color': '#ff6b9d'
        }
    ]
    
    # Sample edges representing relationships
    edges = [
        # Document to entity relationships
        {'source': 'doc_1', 'target': 'entity_gdpr', 'label': 'contains', 'strength': 0.9},
        {'source': 'doc_1', 'target': 'entity_compliance', 'label': 'contains', 'strength': 0.8},
        {'source': 'doc_1', 'target': 'entity_data_protection', 'label': 'contains', 'strength': 0.7},
        
        {'source': 'doc_2', 'target': 'entity_compliance', 'label': 'contains', 'strength': 0.9},
        {'source': 'doc_2', 'target': 'entity_gdpr', 'label': 'contains', 'strength': 0.6},
        
        {'source': 'doc_3', 'target': 'entity_privacy', 'label': 'contains', 'strength': 0.9},
        {'source': 'doc_3', 'target': 'entity_data_protection', 'label': 'contains', 'strength': 0.8},
        
        {'source': 'doc_4', 'target': 'entity_security', 'label': 'contains', 'strength': 0.9},
        {'source': 'doc_4', 'target': 'entity_compliance', 'label': 'contains', 'strength': 0.7},
        
        # Entity to insight relationships
        {'source': 'entity_gdpr', 'target': 'insight_1', 'label': 'generates', 'strength': 0.8},
        {'source': 'entity_privacy', 'target': 'insight_1', 'label': 'generates', 'strength': 0.9},
        
        {'source': 'entity_compliance', 'target': 'insight_2', 'label': 'generates', 'strength': 0.7},
        {'source': 'entity_data_protection', 'target': 'insight_2', 'label': 'generates', 'strength': 0.8},
        
        {'source': 'entity_compliance', 'target': 'insight_3', 'label': 'generates', 'strength': 0.9},
        {'source': 'entity_gdpr', 'target': 'insight_3', 'label': 'generates', 'strength': 0.8},
        
        {'source': 'entity_security', 'target': 'insight_4', 'label': 'generates', 'strength': 0.9},
        {'source': 'entity_compliance', 'target': 'insight_4', 'label': 'generates', 'strength': 0.6},
        
        # Cross-document relationships
        {'source': 'doc_1', 'target': 'doc_2', 'label': 'relates_to', 'strength': 0.6},
        {'source': 'doc_2', 'target': 'doc_3', 'label': 'relates_to', 'strength': 0.5},
        {'source': 'doc_3', 'target': 'doc_4', 'label': 'relates_to', 'strength': 0.7}
    ]
    
    return {
        'nodes': nodes,
        'edges': edges,
        'metadata': {
            'generated_at': datetime.now().isoformat(),
            'total_nodes': len(nodes),
            'total_edges': len(edges),
            'node_types': {
                'document': len([n for n in nodes if n['type'] == 'document']),
                'entity': len([n for n in nodes if n['type'] == 'entity']),
                'insight': len([n for n in nodes if n['type'] == 'insight'])
            },
            'edge_types': {
                'contains': len([e for e in edges if e['label'] == 'contains']),
                'generates': len([e for e in edges if e['label'] == 'generates']),
                'relates_to': len([e for e in edges if e['label'] == 'relates_to'])
            }
        }
    }
