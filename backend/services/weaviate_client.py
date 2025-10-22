"""
Weaviate client for ContextCloud Agents
Handles vector storage and retrieval for the knowledge base
"""

import os
import json
import logging
from typing import List, Dict, Any, Optional
import weaviate
from weaviate import WeaviateClient as WeaviateClientV4
from utils.logger import setup_logger

logger = setup_logger(__name__)

class WeaviateClient:
    """Weaviate client for vector storage and retrieval"""
    
    def __init__(self):
        self.client: Optional[WeaviateClientV4] = None
        self.url = os.getenv("WEAVIATE_URL", "http://localhost:8080")
        self.api_key = os.getenv("WEAVIATE_API_KEY")
        
    async def initialize(self):
        """Initialize Weaviate client and create schema"""
        try:
            logger.info(f"🔗 Connecting to Weaviate at {self.url}")
            
            # For now, skip actual Weaviate connection and use mock data
            logger.info("⚠️ Using mock Weaviate client for testing")
            self.client = None  # Mock client
            
            logger.info("✅ Weaviate client initialized successfully (mock mode)")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize Weaviate client: {e}")
            raise
    
    async def _create_schema(self):
        """Create the document schema in Weaviate"""
        try:
            schema = {
                "class": "Document",
                "description": "Enterprise documents for ContextCloud Agents",
                "vectorizer": "text2vec-transformers",
                "properties": [
                    {
                        "name": "content",
                        "dataType": ["text"],
                        "description": "Document content"
                    },
                    {
                        "name": "filename",
                        "dataType": ["string"],
                        "description": "Original filename"
                    },
                    {
                        "name": "document_type",
                        "dataType": ["string"],
                        "description": "Type of document (policy, manual, report, etc.)"
                    },
                    {
                        "name": "s3_uri",
                        "dataType": ["string"],
                        "description": "S3 storage URI"
                    },
                    {
                        "name": "entities",
                        "dataType": ["text[]"],
                        "description": "Extracted entities"
                    },
                    {
                        "name": "upload_metadata",
                        "dataType": ["object"],
                        "description": "Additional metadata"
                    },
                    {
                        "name": "created_at",
                        "dataType": ["date"],
                        "description": "Document creation timestamp"
                    }
                ]
            }
            
            # Check if schema exists
            if self.client.schema.exists("Document"):
                logger.info("📋 Document schema already exists")
            else:
                self.client.schema.create_class(schema)
                logger.info("📋 Created Document schema")
                
        except Exception as e:
            logger.error(f"❌ Failed to create schema: {e}")
            raise
    
    async def store_document(self, content: str, metadata: Dict[str, Any]) -> str:
        """Store a document in Weaviate"""
        try:
            logger.info(f"💾 Storing document: {metadata.get('filename', 'unnamed')}")
            
            doc_object = {
                "content": content,
                "filename": metadata.get("filename", ""),
                "document_type": metadata.get("document_type", "general"),
                "s3_uri": metadata.get("s3_uri", ""),
                "entities": metadata.get("entities", []),
                "upload_metadata": metadata.get("upload_metadata", {}),
                "created_at": metadata.get("created_at", "2024-01-01T00:00:00Z")
            }
            
            result = self.client.data_object.create(
                data_object=doc_object,
                class_name="Document"
            )
            
            doc_id = result["id"]
            logger.info(f"✅ Document stored with ID: {doc_id}")
            
            return doc_id
            
        except Exception as e:
            logger.error(f"❌ Failed to store document: {e}")
            raise
    
    async def query_documents(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Query documents using vector similarity"""
        try:
            logger.info(f"🔍 Querying documents: {query[:50]}...")
            
            query_result = (
                self.client.query
                .get("Document", ["content", "filename", "document_type", "entities", "s3_uri"])
                .with_near_text({"concepts": [query]})
                .with_limit(limit)
                .with_additional(["certainty", "distance"])
                .do()
            )
            
            documents = []
            if "data" in query_result and "Get" in query_result["data"]:
                for doc in query_result["data"]["Get"]["Document"]:
                    documents.append({
                        "content": doc.get("content", ""),
                        "filename": doc.get("filename", ""),
                        "document_type": doc.get("document_type", ""),
                        "entities": doc.get("entities", []),
                        "s3_uri": doc.get("s3_uri", ""),
                        "certainty": doc.get("_additional", {}).get("certainty", 0),
                        "distance": doc.get("_additional", {}).get("distance", 0)
                    })
            
            logger.info(f"✅ Found {len(documents)} relevant documents")
            return documents
            
        except Exception as e:
            logger.error(f"❌ Failed to query documents: {e}")
            raise
    
    async def get_knowledge_graph(self) -> Dict[str, Any]:
        """Get knowledge graph data for visualization"""
        try:
            logger.info("📊 Building knowledge graph")
            
            # In mock mode, always use sample data
            if self.client is None:
                logger.info("🎭 Using sample knowledge graph data (mock mode)")
                return self._generate_comprehensive_sample_graph()
            
            # Try to get real documents first (when Weaviate is actually connected)
            try:
                query_result = (
                    self.client.query
                    .get("Document", ["content", "filename", "document_type", "entities"])
                    .with_limit(100)
                    .do()
                )
            except:
                logger.info("🎭 Falling back to sample knowledge graph data")
                return self._generate_comprehensive_sample_graph()
            
            nodes = []
            edges = []
            
            # Check if we have real documents
            has_real_documents = False
            if "data" in query_result and "Get" in query_result["data"] and query_result["data"]["Get"]["Document"]:
                has_real_documents = True
                for i, doc in enumerate(query_result["data"]["Get"]["Document"]):
                    # Create document node
                    node = {
                        "id": f"doc_{i}",
                        "label": doc.get("filename", f"Document {i}"),
                        "type": doc.get("document_type", "general"),
                        "entities": doc.get("entities", []),
                        "content_preview": doc.get("content", "")[:100] + "...",
                        "summary": f"Document containing information about {', '.join(doc.get('entities', [])[:3])}",
                        "key_terms": doc.get("entities", [])[:5]
                    }
                    nodes.append(node)
                    
                    # Create entity nodes and edges
                    entities = doc.get("entities", [])
                    for entity in entities:
                        entity_node = {
                            "id": f"entity_{entity}",
                            "label": entity,
                            "type": "entity",
                            "summary": f"Entity extracted from enterprise documents",
                            "key_terms": [entity.lower()]
                        }
                        
                        if entity_node not in nodes:
                            nodes.append(entity_node)
                        
                        # Create edge between document and entity
                        edge = {
                            "source": f"doc_{i}",
                            "target": f"entity_{entity}",
                            "label": "contains"
                        }
                        edges.append(edge)
            
            # If no real documents, generate comprehensive sample data
            if not has_real_documents:
                logger.info("📊 No real documents found, generating comprehensive sample knowledge graph")
                sample_data = self._generate_comprehensive_sample_graph()
                nodes = sample_data["nodes"]
                edges = sample_data["edges"]
            
            logger.info(f"✅ Generated graph with {len(nodes)} nodes and {len(edges)} edges")
            
            return {
                "nodes": nodes,
                "edges": edges
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to generate knowledge graph: {e}")
            raise
    
    def _generate_comprehensive_sample_graph(self) -> Dict[str, Any]:
        """Generate massive interconnected knowledge graph with 200+ nodes and extensive relationships"""
        nodes = []
        edges = []
        
        # Core Enterprise Departments (expanded)
        departments = [
            {
                "name": "Human Resources", "color": "#FF6B6B",
                "documents": [
                    {"name": "Employee Handbook 2024", "type": "policy", "summary": "Comprehensive guide covering employee policies, benefits, code of conduct, and workplace procedures", "key_terms": ["employee", "benefits", "policy", "conduct", "workplace", "handbook", "procedures"]},
                    {"name": "Diversity & Inclusion Policy", "type": "policy", "summary": "Framework for promoting diversity, equity, and inclusion across all organizational levels", "key_terms": ["diversity", "inclusion", "equity", "discrimination", "workplace", "framework", "organizational"]},
                    {"name": "Remote Work Guidelines", "type": "procedure", "summary": "Detailed procedures for remote work arrangements, equipment, and productivity standards", "key_terms": ["remote", "work", "equipment", "productivity", "guidelines", "arrangements", "standards"]},
                    {"name": "Performance Review Process", "type": "procedure", "summary": "Annual performance evaluation methodology, criteria, and improvement planning", "key_terms": ["performance", "review", "evaluation", "improvement", "criteria", "annual", "methodology"]},
                    {"name": "Compensation Structure", "type": "policy", "summary": "Salary bands, bonus structures, and equity compensation frameworks", "key_terms": ["salary", "compensation", "bonus", "equity", "benefits", "structure", "framework"]},
                    {"name": "Training & Development Program", "type": "program", "summary": "Comprehensive learning and development initiatives for skill enhancement", "key_terms": ["training", "development", "learning", "skills", "enhancement", "program", "initiatives"]},
                    {"name": "Employee Wellness Initiative", "type": "program", "summary": "Health and wellness programs promoting work-life balance", "key_terms": ["wellness", "health", "work-life", "balance", "employee", "program", "initiative"]},
                    {"name": "Recruitment Strategy", "type": "strategy", "summary": "Talent acquisition and recruitment process optimization", "key_terms": ["recruitment", "talent", "acquisition", "hiring", "strategy", "process", "optimization"]}
                ]
            },
            {
                "name": "Information Technology", "color": "#4ECDC4",
                "documents": [
                    {"name": "Cybersecurity Framework", "type": "policy", "summary": "Comprehensive security protocols, threat detection, and incident response procedures", "key_terms": ["cybersecurity", "threats", "incident", "response", "protocols", "security", "detection"]},
                    {"name": "Data Governance Policy", "type": "policy", "summary": "Data classification, retention, privacy, and compliance management guidelines", "key_terms": ["data", "governance", "privacy", "compliance", "retention", "classification", "management"]},
                    {"name": "Cloud Infrastructure Guide", "type": "technical", "summary": "AWS cloud architecture, deployment strategies, and cost optimization practices", "key_terms": ["cloud", "aws", "infrastructure", "deployment", "optimization", "architecture", "strategies"]},
                    {"name": "Software Development Standards", "type": "procedure", "summary": "Coding standards, testing protocols, and deployment pipeline requirements", "key_terms": ["development", "coding", "testing", "deployment", "standards", "pipeline", "protocols"]},
                    {"name": "IT Asset Management", "type": "procedure", "summary": "Hardware and software inventory, lifecycle management, and procurement processes", "key_terms": ["assets", "inventory", "lifecycle", "procurement", "management", "hardware", "software"]},
                    {"name": "DevOps Methodology", "type": "framework", "summary": "Continuous integration and deployment practices", "key_terms": ["devops", "continuous", "integration", "deployment", "automation", "methodology", "practices"]},
                    {"name": "API Documentation Standards", "type": "technical", "summary": "REST API design patterns and documentation requirements", "key_terms": ["api", "rest", "documentation", "design", "patterns", "standards", "requirements"]},
                    {"name": "Database Management Procedures", "type": "procedure", "summary": "Database optimization, backup, and recovery protocols", "key_terms": ["database", "optimization", "backup", "recovery", "procedures", "management", "protocols"]}
                ]
            },
            {
                "name": "Finance", "color": "#45B7D1",
                "documents": [
                    {"name": "Financial Reporting Standards", "type": "policy", "summary": "GAAP compliance, quarterly reporting, and audit preparation procedures", "key_terms": ["financial", "reporting", "gaap", "audit", "compliance", "quarterly", "standards"]},
                    {"name": "Budget Planning Process", "type": "procedure", "summary": "Annual budget creation, departmental allocations, and variance analysis", "key_terms": ["budget", "planning", "allocation", "variance", "analysis", "annual", "departmental"]},
                    {"name": "Expense Management Policy", "type": "policy", "summary": "Travel expenses, procurement approvals, and reimbursement procedures", "key_terms": ["expense", "travel", "procurement", "approval", "reimbursement", "management", "procedures"]},
                    {"name": "Risk Management Framework", "type": "policy", "summary": "Financial risk assessment, mitigation strategies, and monitoring protocols", "key_terms": ["risk", "assessment", "mitigation", "monitoring", "financial", "framework", "strategies"]},
                    {"name": "Vendor Payment Procedures", "type": "procedure", "summary": "Invoice processing, payment terms, and vendor relationship management", "key_terms": ["vendor", "payment", "invoice", "terms", "relationship", "processing", "procedures"]},
                    {"name": "Investment Policy", "type": "policy", "summary": "Corporate investment guidelines and portfolio management", "key_terms": ["investment", "portfolio", "corporate", "guidelines", "management", "policy", "financial"]},
                    {"name": "Tax Compliance Manual", "type": "manual", "summary": "Tax obligations, filing procedures, and compliance requirements", "key_terms": ["tax", "compliance", "filing", "obligations", "requirements", "manual", "procedures"]},
                    {"name": "Financial Controls Framework", "type": "framework", "summary": "Internal controls and financial oversight mechanisms", "key_terms": ["controls", "oversight", "internal", "financial", "framework", "mechanisms", "governance"]}
                ]
            },
            {
                "name": "Legal & Compliance", "color": "#96CEB4",
                "documents": [
                    {"name": "GDPR Compliance Manual", "type": "policy", "summary": "European data protection regulations, consent management, and breach procedures", "key_terms": ["gdpr", "data protection", "consent", "breach", "privacy", "european", "regulations"]},
                    {"name": "Contract Management System", "type": "procedure", "summary": "Contract lifecycle, approval workflows, and legal review processes", "key_terms": ["contract", "lifecycle", "approval", "legal", "review", "workflows", "management"]},
                    {"name": "Intellectual Property Policy", "type": "policy", "summary": "Patent protection, trademark management, and trade secret protocols", "key_terms": ["intellectual property", "patent", "trademark", "trade secret", "protection", "management", "protocols"]},
                    {"name": "Regulatory Compliance Framework", "type": "policy", "summary": "Industry regulations, compliance monitoring, and reporting requirements", "key_terms": ["regulatory", "compliance", "monitoring", "reporting", "requirements", "industry", "framework"]},
                    {"name": "Ethics and Conduct Code", "type": "policy", "summary": "Ethical guidelines, conflict of interest, and whistleblower procedures", "key_terms": ["ethics", "conduct", "conflict", "whistleblower", "guidelines", "ethical", "procedures"]},
                    {"name": "Litigation Management", "type": "procedure", "summary": "Legal dispute resolution and litigation handling processes", "key_terms": ["litigation", "dispute", "resolution", "legal", "management", "processes", "handling"]},
                    {"name": "Corporate Governance Policy", "type": "policy", "summary": "Board oversight, executive accountability, and governance structures", "key_terms": ["governance", "board", "oversight", "accountability", "corporate", "structures", "executive"]},
                    {"name": "Privacy Impact Assessment", "type": "framework", "summary": "Privacy risk evaluation and mitigation procedures", "key_terms": ["privacy", "impact", "assessment", "risk", "evaluation", "mitigation", "procedures"]}
                ]
            },
            {
                "name": "Operations", "color": "#FECA57",
                "documents": [
                    {"name": "Quality Management System", "type": "procedure", "summary": "ISO 9001 compliance, quality control processes, and continuous improvement", "key_terms": ["quality", "iso", "control", "improvement", "management", "continuous", "compliance"]},
                    {"name": "Supply Chain Management", "type": "procedure", "summary": "Supplier selection, logistics coordination, and inventory optimization", "key_terms": ["supply chain", "supplier", "logistics", "inventory", "optimization", "coordination", "selection"]},
                    {"name": "Business Continuity Plan", "type": "policy", "summary": "Disaster recovery, emergency procedures, and operational resilience", "key_terms": ["continuity", "disaster", "recovery", "emergency", "resilience", "operational", "procedures"]},
                    {"name": "Customer Service Standards", "type": "procedure", "summary": "Service level agreements, customer satisfaction metrics, and escalation procedures", "key_terms": ["customer service", "sla", "satisfaction", "escalation", "standards", "metrics", "agreements"]},
                    {"name": "Facility Management Guidelines", "type": "procedure", "summary": "Office space management, maintenance schedules, and safety protocols", "key_terms": ["facility", "office", "maintenance", "safety", "management", "schedules", "protocols"]},
                    {"name": "Process Optimization Framework", "type": "framework", "summary": "Lean methodology and process improvement initiatives", "key_terms": ["process", "optimization", "lean", "methodology", "improvement", "framework", "initiatives"]},
                    {"name": "Vendor Management Program", "type": "program", "summary": "Vendor evaluation, performance monitoring, and relationship management", "key_terms": ["vendor", "evaluation", "performance", "monitoring", "relationship", "management", "program"]},
                    {"name": "Environmental Sustainability Policy", "type": "policy", "summary": "Green initiatives, carbon footprint reduction, and sustainability goals", "key_terms": ["environmental", "sustainability", "green", "carbon", "footprint", "reduction", "initiatives"]}
                ]
            },
            {
                "name": "Marketing", "color": "#FF9FF3",
                "documents": [
                    {"name": "Brand Guidelines", "type": "policy", "summary": "Brand identity, visual standards, and messaging consistency requirements", "key_terms": ["brand", "identity", "visual", "messaging", "consistency", "guidelines", "standards"]},
                    {"name": "Digital Marketing Strategy", "type": "strategy", "summary": "SEO optimization, social media campaigns, and content marketing frameworks", "key_terms": ["digital", "marketing", "seo", "social media", "content", "optimization", "campaigns"]},
                    {"name": "Customer Data Privacy", "type": "policy", "summary": "Marketing data collection, consent management, and privacy compliance", "key_terms": ["customer data", "privacy", "consent", "collection", "compliance", "marketing", "management"]},
                    {"name": "Campaign Management Process", "type": "procedure", "summary": "Campaign planning, execution, measurement, and optimization procedures", "key_terms": ["campaign", "planning", "execution", "measurement", "optimization", "management", "procedures"]},
                    {"name": "Public Relations Guidelines", "type": "procedure", "summary": "Media relations, crisis communication, and public statement protocols", "key_terms": ["public relations", "media", "crisis", "communication", "protocols", "guidelines", "statements"]},
                    {"name": "Market Research Framework", "type": "framework", "summary": "Customer insights, market analysis, and competitive intelligence", "key_terms": ["market research", "insights", "analysis", "competitive", "intelligence", "customer", "framework"]},
                    {"name": "Content Strategy", "type": "strategy", "summary": "Content creation, distribution, and engagement optimization", "key_terms": ["content", "creation", "distribution", "engagement", "optimization", "strategy", "marketing"]},
                    {"name": "Lead Generation Process", "type": "procedure", "summary": "Lead qualification, nurturing, and conversion optimization", "key_terms": ["lead", "generation", "qualification", "nurturing", "conversion", "optimization", "process"]}
                ]
            },
            {
                "name": "Sales", "color": "#54A0FF",
                "documents": [
                    {"name": "Sales Methodology", "type": "framework", "summary": "Sales process, qualification criteria, and closing techniques", "key_terms": ["sales", "methodology", "process", "qualification", "closing", "techniques", "framework"]},
                    {"name": "Customer Relationship Management", "type": "procedure", "summary": "CRM usage, customer data management, and relationship building", "key_terms": ["crm", "customer", "relationship", "data", "management", "building", "procedures"]},
                    {"name": "Territory Management", "type": "strategy", "summary": "Sales territory allocation, coverage optimization, and performance tracking", "key_terms": ["territory", "allocation", "coverage", "optimization", "performance", "tracking", "sales"]},
                    {"name": "Pricing Strategy", "type": "strategy", "summary": "Pricing models, discount policies, and competitive positioning", "key_terms": ["pricing", "models", "discount", "policies", "competitive", "positioning", "strategy"]},
                    {"name": "Sales Training Program", "type": "program", "summary": "Sales skills development, product training, and certification", "key_terms": ["sales training", "skills", "development", "product", "certification", "program", "learning"]},
                    {"name": "Channel Partner Management", "type": "procedure", "summary": "Partner onboarding, enablement, and performance management", "key_terms": ["channel", "partner", "onboarding", "enablement", "performance", "management", "procedures"]},
                    {"name": "Sales Forecasting", "type": "procedure", "summary": "Revenue prediction, pipeline analysis, and forecast accuracy", "key_terms": ["forecasting", "revenue", "prediction", "pipeline", "analysis", "accuracy", "sales"]},
                    {"name": "Customer Success Framework", "type": "framework", "summary": "Customer onboarding, retention, and expansion strategies", "key_terms": ["customer success", "onboarding", "retention", "expansion", "strategies", "framework", "satisfaction"]}
                ]
            },
            {
                "name": "Product Management", "color": "#5F27CD",
                "documents": [
                    {"name": "Product Roadmap", "type": "strategy", "summary": "Product vision, feature prioritization, and release planning", "key_terms": ["product", "roadmap", "vision", "prioritization", "release", "planning", "features"]},
                    {"name": "User Experience Guidelines", "type": "guidelines", "summary": "UX design principles, usability standards, and user research", "key_terms": ["ux", "design", "usability", "user research", "principles", "standards", "experience"]},
                    {"name": "Product Requirements Document", "type": "technical", "summary": "Feature specifications, acceptance criteria, and technical requirements", "key_terms": ["requirements", "specifications", "acceptance", "criteria", "technical", "features", "product"]},
                    {"name": "Agile Development Process", "type": "framework", "summary": "Scrum methodology, sprint planning, and iterative development", "key_terms": ["agile", "scrum", "sprint", "planning", "iterative", "development", "methodology"]},
                    {"name": "Product Analytics Framework", "type": "framework", "summary": "Metrics tracking, user behavior analysis, and performance monitoring", "key_terms": ["analytics", "metrics", "tracking", "behavior", "analysis", "performance", "monitoring"]},
                    {"name": "Go-to-Market Strategy", "type": "strategy", "summary": "Product launch, market positioning, and customer acquisition", "key_terms": ["go-to-market", "launch", "positioning", "acquisition", "customer", "strategy", "market"]},
                    {"name": "Competitive Analysis", "type": "analysis", "summary": "Market research, competitor evaluation, and positioning strategy", "key_terms": ["competitive", "analysis", "market research", "competitor", "evaluation", "positioning", "strategy"]},
                    {"name": "Product Lifecycle Management", "type": "framework", "summary": "Product development stages, lifecycle optimization, and end-of-life planning", "key_terms": ["lifecycle", "development", "stages", "optimization", "end-of-life", "planning", "product"]}
                ]
            }
        ]
        
        # Generate department nodes
        for dept in departments:
            dept_node = {
                "id": f"dept_{dept['name'].lower().replace(' ', '_').replace('&', 'and')}",
                "label": dept['name'],
                "type": "department",
                "color": dept.get("color", "#888888"),
                "summary": f"Enterprise department responsible for {dept['name'].lower()} operations and policies",
                "key_terms": [dept['name'].lower(), "department", "enterprise", "operations"],
                "content_preview": f"{dept['name']} department managing organizational functions..."
            }
            nodes.append(dept_node)
            
            # Generate document nodes for each department
            for doc in dept['documents']:
                doc_node = {
                    "id": f"doc_{dept['name'].lower().replace(' ', '_').replace('&', 'and')}_{doc['name'].lower().replace(' ', '_').replace('&', 'and')}",
                    "label": doc['name'],
                    "type": doc['type'],
                    "summary": doc['summary'],
                    "key_terms": doc['key_terms'],
                    "content_preview": doc['summary'][:100] + "...",
                    "entities": doc['key_terms'][:3]
                }
                nodes.append(doc_node)
                
                # Create edge between department and document
                edges.append({
                    "source": dept_node["id"],
                    "target": doc_node["id"],
                    "label": "manages"
                })
        
        # Generate comprehensive entity nodes
        all_entities = set()
        for node in nodes:
            if node.get("key_terms"):
                all_entities.update(node["key_terms"])
        
        # Create entity nodes with enhanced metadata
        for entity in all_entities:
            entity_node = {
                "id": f"entity_{entity.replace(' ', '_').replace('&', 'and')}",
                "label": entity.title(),
                "type": "entity",
                "summary": f"Key concept or term related to enterprise operations: {entity}",
                "key_terms": [entity, "concept", "enterprise"],
                "content_preview": f"Entity representing {entity} across various enterprise documents..."
            }
            nodes.append(entity_node)
        
        # Create edges between documents and entities (creates spider web effect)
        for node in nodes:
            if node["type"] in ["policy", "procedure", "technical", "strategy", "framework", "program", "manual", "guidelines", "analysis"]:
                for term in node.get("key_terms", []):
                    entity_id = f"entity_{term.replace(' ', '_').replace('&', 'and')}"
                    if any(n["id"] == entity_id for n in nodes):
                        edges.append({
                            "source": node["id"],
                            "target": entity_id,
                            "label": "contains"
                        })
        
        # Add extensive cross-departmental connections
        cross_connections = [
            ("dept_human_resources", "dept_legal_and_compliance", "collaborates"),
            ("dept_information_technology", "dept_finance", "supports"),
            ("dept_operations", "dept_marketing", "coordinates"),
            ("dept_legal_and_compliance", "dept_finance", "oversees"),
            ("dept_information_technology", "dept_operations", "enables"),
            ("dept_marketing", "dept_human_resources", "partners"),
            ("dept_sales", "dept_marketing", "collaborates"),
            ("dept_product_management", "dept_sales", "supports"),
            ("dept_product_management", "dept_marketing", "coordinates"),
            ("dept_information_technology", "dept_product_management", "develops"),
            ("dept_operations", "dept_sales", "fulfills"),
            ("dept_finance", "dept_sales", "tracks"),
            ("dept_human_resources", "dept_product_management", "staffs"),
            ("dept_legal_and_compliance", "dept_product_management", "reviews"),
            ("dept_operations", "dept_finance", "reports_to"),
            ("dept_marketing", "dept_finance", "budgets_with"),
            ("dept_sales", "dept_finance", "forecasts_with"),
            ("dept_information_technology", "dept_legal_and_compliance", "secures_for"),
            ("dept_human_resources", "dept_operations", "trains_for"),
            ("dept_product_management", "dept_operations", "delivers_through")
        ]
        
        for source, target, label in cross_connections:
            edges.append({
                "source": source,
                "target": target,
                "label": label
            })
        
        # Add comprehensive system and process nodes
        systems_and_processes = [
            # Core Systems
            {"id": "system_erp", "label": "ERP System", "type": "system", "summary": "Enterprise Resource Planning system integrating business processes", "key_terms": ["erp", "integration", "business process", "automation", "enterprise"], "connects_to": ["dept_finance", "dept_operations", "dept_human_resources"]},
            {"id": "system_crm", "label": "CRM Platform", "type": "system", "summary": "Customer Relationship Management platform", "key_terms": ["crm", "customer", "sales", "service", "relationship"], "connects_to": ["dept_sales", "dept_marketing", "dept_operations"]},
            {"id": "system_hrms", "label": "HRMS", "type": "system", "summary": "Human Resource Management System", "key_terms": ["hrms", "human resources", "employee", "management", "payroll"], "connects_to": ["dept_human_resources", "dept_finance"]},
            {"id": "system_bi", "label": "Business Intelligence", "type": "system", "summary": "Data analytics and reporting platform", "key_terms": ["business intelligence", "analytics", "reporting", "data", "insights"], "connects_to": ["dept_finance", "dept_marketing", "dept_sales", "dept_operations"]},
            {"id": "system_cms", "label": "Content Management", "type": "system", "summary": "Content creation and management platform", "key_terms": ["cms", "content", "management", "publishing", "digital"], "connects_to": ["dept_marketing", "dept_product_management"]},
            
            # Infrastructure
            {"id": "infra_cloud", "label": "Cloud Infrastructure", "type": "infrastructure", "summary": "AWS cloud computing infrastructure", "key_terms": ["cloud", "aws", "infrastructure", "computing", "scalability"], "connects_to": ["dept_information_technology", "dept_operations"]},
            {"id": "infra_network", "label": "Network Infrastructure", "type": "infrastructure", "summary": "Corporate network and connectivity", "key_terms": ["network", "connectivity", "infrastructure", "security", "bandwidth"], "connects_to": ["dept_information_technology", "dept_operations"]},
            {"id": "infra_security", "label": "Security Infrastructure", "type": "infrastructure", "summary": "Cybersecurity and data protection systems", "key_terms": ["security", "cybersecurity", "protection", "firewall", "encryption"], "connects_to": ["dept_information_technology", "dept_legal_and_compliance"]},
            
            # Business Processes
            {"id": "process_onboarding", "label": "Employee Onboarding", "type": "process", "summary": "New employee integration process", "key_terms": ["onboarding", "employee", "integration", "training", "orientation"], "connects_to": ["dept_human_resources", "dept_information_technology"]},
            {"id": "process_procurement", "label": "Procurement Process", "type": "process", "summary": "Vendor selection and purchasing workflow", "key_terms": ["procurement", "vendor", "purchasing", "approval", "workflow"], "connects_to": ["dept_finance", "dept_operations", "dept_legal_and_compliance"]},
            {"id": "process_product_dev", "label": "Product Development", "type": "process", "summary": "Product ideation to launch process", "key_terms": ["product development", "ideation", "launch", "innovation", "lifecycle"], "connects_to": ["dept_product_management", "dept_information_technology", "dept_marketing"]},
            {"id": "process_customer_support", "label": "Customer Support", "type": "process", "summary": "Customer service and issue resolution", "key_terms": ["customer support", "service", "resolution", "satisfaction", "helpdesk"], "connects_to": ["dept_operations", "dept_sales", "dept_information_technology"]},
            
            # Frameworks and Methodologies
            {"id": "framework_agile", "label": "Agile Framework", "type": "framework", "summary": "Agile development methodology", "key_terms": ["agile", "methodology", "scrum", "development", "iterative"], "connects_to": ["dept_information_technology", "dept_product_management"]},
            {"id": "framework_lean", "label": "Lean Methodology", "type": "framework", "summary": "Lean process optimization", "key_terms": ["lean", "optimization", "efficiency", "waste", "continuous improvement"], "connects_to": ["dept_operations", "dept_product_management"]},
            {"id": "framework_devops", "label": "DevOps Framework", "type": "framework", "summary": "Development and operations integration", "key_terms": ["devops", "integration", "automation", "deployment", "collaboration"], "connects_to": ["dept_information_technology", "dept_operations"]},
            
            # Compliance and Governance
            {"id": "compliance_sox", "label": "SOX Compliance", "type": "compliance", "summary": "Sarbanes-Oxley compliance framework", "key_terms": ["sox", "compliance", "financial", "reporting", "controls"], "connects_to": ["dept_finance", "dept_legal_and_compliance"]},
            {"id": "compliance_iso", "label": "ISO Standards", "type": "compliance", "summary": "International Organization for Standardization compliance", "key_terms": ["iso", "standards", "quality", "management", "certification"], "connects_to": ["dept_operations", "dept_legal_and_compliance"]},
            {"id": "governance_data", "label": "Data Governance", "type": "governance", "summary": "Data management and privacy governance", "key_terms": ["data governance", "privacy", "management", "quality", "stewardship"], "connects_to": ["dept_information_technology", "dept_legal_and_compliance"]},
            
            # Analytics and Metrics
            {"id": "metrics_kpi", "label": "KPI Dashboard", "type": "metrics", "summary": "Key Performance Indicators tracking", "key_terms": ["kpi", "metrics", "performance", "dashboard", "tracking"], "connects_to": ["dept_finance", "dept_operations", "dept_sales", "dept_marketing"]},
            {"id": "analytics_customer", "label": "Customer Analytics", "type": "analytics", "summary": "Customer behavior and satisfaction analysis", "key_terms": ["customer analytics", "behavior", "satisfaction", "analysis", "insights"], "connects_to": ["dept_marketing", "dept_sales", "dept_operations"]},
            {"id": "analytics_financial", "label": "Financial Analytics", "type": "analytics", "summary": "Financial performance and forecasting", "key_terms": ["financial analytics", "performance", "forecasting", "budgeting", "variance"], "connects_to": ["dept_finance", "dept_operations"]},
            
            # Communication and Collaboration
            {"id": "platform_collaboration", "label": "Collaboration Platform", "type": "platform", "summary": "Team communication and collaboration tools", "key_terms": ["collaboration", "communication", "teams", "productivity", "remote"], "connects_to": ["dept_human_resources", "dept_information_technology"]},
            {"id": "platform_knowledge", "label": "Knowledge Management", "type": "platform", "summary": "Organizational knowledge sharing platform", "key_terms": ["knowledge management", "sharing", "documentation", "wiki", "learning"], "connects_to": ["dept_human_resources", "dept_information_technology", "dept_operations"]},
            
            # External Integrations
            {"id": "integration_banking", "label": "Banking Integration", "type": "integration", "summary": "Financial institution connectivity", "key_terms": ["banking", "integration", "payments", "transactions", "financial"], "connects_to": ["dept_finance", "dept_information_technology"]},
            {"id": "integration_partners", "label": "Partner Integrations", "type": "integration", "summary": "Third-party partner system connections", "key_terms": ["partners", "integration", "third-party", "api", "connectivity"], "connects_to": ["dept_sales", "dept_operations", "dept_information_technology"]},
            
            # Innovation and Research
            {"id": "innovation_lab", "label": "Innovation Lab", "type": "innovation", "summary": "Research and development initiatives", "key_terms": ["innovation", "research", "development", "experimentation", "emerging"], "connects_to": ["dept_product_management", "dept_information_technology"]},
            {"id": "research_market", "label": "Market Research", "type": "research", "summary": "Market analysis and competitive intelligence", "key_terms": ["market research", "analysis", "competitive", "intelligence", "trends"], "connects_to": ["dept_marketing", "dept_product_management", "dept_sales"]}
        ]
        
        # Add all system and process nodes
        for item in systems_and_processes:
            node = {
                "id": item["id"],
                "label": item["label"],
                "type": item["type"],
                "summary": item["summary"],
                "key_terms": item["key_terms"],
                "content_preview": item["summary"][:100] + "..."
            }
            nodes.append(node)
            
            # Connect to relevant departments
            for dept_connection in item["connects_to"]:
                edges.append({
                    "source": item["id"],
                    "target": dept_connection,
                    "label": "supports" if item["type"] in ["system", "platform", "infrastructure"] else "implements"
                })
        
        # Add entity connections to systems and processes
        for node in nodes:
            if node["type"] in ["system", "platform", "infrastructure", "process", "framework", "compliance", "governance", "metrics", "analytics", "integration", "innovation", "research"]:
                for term in node.get("key_terms", []):
                    entity_id = f"entity_{term.replace(' ', '_').replace('&', 'and')}"
                    if any(n["id"] == entity_id for n in nodes):
                        edges.append({
                            "source": node["id"],
                            "target": entity_id,
                            "label": "utilizes"
                        })
        
        # Add cross-system connections for more spider web effect
        system_connections = [
            ("system_erp", "system_crm", "integrates_with"),
            ("system_crm", "system_bi", "feeds_data_to"),
            ("system_hrms", "system_erp", "synchronizes_with"),
            ("infra_cloud", "system_erp", "hosts"),
            ("infra_cloud", "system_crm", "hosts"),
            ("infra_security", "infra_cloud", "protects"),
            ("infra_network", "infra_cloud", "connects_to"),
            ("process_onboarding", "system_hrms", "uses"),
            ("process_procurement", "system_erp", "managed_by"),
            ("framework_agile", "process_product_dev", "guides"),
            ("framework_lean", "process_procurement", "optimizes"),
            ("compliance_sox", "system_erp", "governs"),
            ("governance_data", "system_bi", "oversees"),
            ("metrics_kpi", "system_bi", "displayed_in"),
            ("analytics_customer", "system_crm", "analyzes_data_from"),
            ("analytics_financial", "system_erp", "processes_data_from"),
            ("platform_collaboration", "process_onboarding", "facilitates"),
            ("platform_knowledge", "framework_agile", "documents"),
            ("integration_banking", "system_erp", "connects_to"),
            ("integration_partners", "system_crm", "extends"),
            ("innovation_lab", "process_product_dev", "influences"),
            ("research_market", "analytics_customer", "informs")
        ]
        
        for source, target, label in system_connections:
            edges.append({
                "source": source,
                "target": target,
                "label": label
            })
        
        # Add entity-to-entity relationships for maximum interconnection
        entity_relationships = [
            ("entity_employee", "entity_training", "requires"),
            ("entity_security", "entity_compliance", "ensures"),
            ("entity_data", "entity_privacy", "protected_by"),
            ("entity_customer", "entity_satisfaction", "measured_by"),
            ("entity_process", "entity_optimization", "improved_through"),
            ("entity_technology", "entity_innovation", "drives"),
            ("entity_financial", "entity_reporting", "documented_in"),
            ("entity_quality", "entity_management", "maintained_by"),
            ("entity_risk", "entity_mitigation", "addressed_through"),
            ("entity_performance", "entity_metrics", "tracked_by"),
            ("entity_development", "entity_methodology", "follows"),
            ("entity_integration", "entity_automation", "enables"),
            ("entity_governance", "entity_oversight", "provides"),
            ("entity_analysis", "entity_insights", "generates"),
            ("entity_collaboration", "entity_productivity", "enhances")
        ]
        
        for source, target, label in entity_relationships:
            if any(n["id"] == source for n in nodes) and any(n["id"] == target for n in nodes):
                edges.append({
                    "source": source,
                    "target": target,
                    "label": label
                })
        
        return {
            "nodes": nodes,
            "edges": edges
        }
    
    async def health_check(self) -> str:
        """Check Weaviate health"""
        try:
            if not self.client:
                return "not_initialized"
            
            if self.client.is_ready():
                return "healthy"
            else:
                return "unhealthy"
                
        except Exception as e:
            logger.error(f"❌ Weaviate health check failed: {e}")
            return "error"
