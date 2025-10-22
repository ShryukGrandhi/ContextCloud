import React, { useState, useEffect, useRef } from 'react';
import { motion } from 'framer-motion';
import ForceGraph2D from 'react-force-graph-2d';
import { Zap, Database, Brain, FileText, Users, TrendingUp } from 'lucide-react';

const GraphView = ({ currentQuery, isLoading }) => {
  const [graphData, setGraphData] = useState({ nodes: [], links: [] });
  const [selectedNode, setSelectedNode] = useState(null);
  const [graphStats, setGraphStats] = useState({
    nodes: 0,
    links: 0,
    documents: 0,
    entities: 0
  });
  const graphRef = useRef();

  // Sample data for demonstration
  const sampleData = {
    nodes: [
      { id: 'query', name: currentQuery || 'Enterprise Knowledge', type: 'query', size: 20, color: '#00d4ff' },
      { id: 'doc1', name: 'Policy Manual 2024', type: 'document', size: 15, color: '#00ff88' },
      { id: 'doc2', name: 'Compliance Guide', type: 'document', size: 15, color: '#00ff88' },
      { id: 'doc3', name: 'Data Privacy Report', type: 'document', size: 15, color: '#00ff88' },
      { id: 'entity1', name: 'GDPR', type: 'entity', size: 10, color: '#b347d9' },
      { id: 'entity2', name: 'Data Protection', type: 'entity', size: 10, color: '#b347d9' },
      { id: 'entity3', name: 'Compliance', type: 'entity', size: 10, color: '#b347d9' },
      { id: 'insight1', name: 'Privacy Requirements', type: 'insight', size: 12, color: '#ff6b9d' },
      { id: 'insight2', name: 'Risk Assessment', type: 'insight', size: 12, color: '#ff6b9d' }
    ],
    links: [
      { source: 'query', target: 'doc1', type: 'retrieves', strength: 0.8 },
      { source: 'query', target: 'doc2', type: 'retrieves', strength: 0.7 },
      { source: 'query', target: 'doc3', type: 'retrieves', strength: 0.6 },
      { source: 'doc1', target: 'entity1', type: 'contains', strength: 0.9 },
      { source: 'doc2', target: 'entity2', type: 'contains', strength: 0.8 },
      { source: 'doc3', target: 'entity3', type: 'contains', strength: 0.7 },
      { source: 'entity1', target: 'insight1', type: 'generates', strength: 0.6 },
      { source: 'entity2', target: 'insight2', type: 'generates', strength: 0.5 }
    ]
  };

  useEffect(() => {
    // Simulate data loading
    if (currentQuery) {
      setGraphData(sampleData);
      setGraphStats({
        nodes: sampleData.nodes.length,
        links: sampleData.links.length,
        documents: sampleData.nodes.filter(n => n.type === 'document').length,
        entities: sampleData.nodes.filter(n => n.type === 'entity').length
      });
    }
  }, [currentQuery]);

  const getNodeIcon = (type) => {
    switch (type) {
      case 'query': return <Brain className="w-4 h-4" />;
      case 'document': return <FileText className="w-4 h-4" />;
      case 'entity': return <Database className="w-4 h-4" />;
      case 'insight': return <TrendingUp className="w-4 h-4" />;
      default: return <Zap className="w-4 h-4" />;
    }
  };

  const nodePaint = (node, ctx, globalScale) => {
    const size = node.size || 10;
    const color = node.color || '#00d4ff';
    
    // Create glow effect
    ctx.shadowColor = color;
    ctx.shadowBlur = 20;
    ctx.fillStyle = color;
    ctx.beginPath();
    ctx.arc(node.x, node.y, size, 0, 2 * Math.PI);
    ctx.fill();
    
    // Add node label
    ctx.fillStyle = '#ffffff';
    ctx.font = '12px Inter';
    ctx.textAlign = 'center';
    ctx.fillText(node.name, node.x, node.y + size + 15);
  };

  const linkPaint = (link, ctx) => {
    const color = '#00d4ff';
    ctx.strokeStyle = color;
    ctx.lineWidth = 2;
    ctx.shadowColor = color;
    ctx.shadowBlur = 5;
    ctx.beginPath();
    ctx.moveTo(link.source.x, link.source.y);
    ctx.lineTo(link.target.x, link.target.y);
    ctx.stroke();
  };

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.9 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ duration: 0.5 }}
      className="glass-dark rounded-xl p-6 h-full flex flex-col"
    >
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center space-x-3">
          <div className="w-8 h-8 bg-gradient-to-r from-neon-blue to-neon-purple rounded-lg flex items-center justify-center">
            <Database className="w-4 h-4 text-white" />
          </div>
          <div>
            <h3 className="text-lg font-semibold text-white">Knowledge Graph</h3>
            <p className="text-sm text-gray-400">Interactive visualization of enterprise knowledge</p>
          </div>
        </div>
        
        {/* Stats */}
        <div className="flex items-center space-x-4 text-sm">
          <div className="flex items-center space-x-1 text-neon-blue">
            <div className="w-2 h-2 bg-neon-blue rounded-full"></div>
            <span>{graphStats.nodes} Nodes</span>
          </div>
          <div className="flex items-center space-x-1 text-neon-green">
            <div className="w-2 h-2 bg-neon-green rounded-full"></div>
            <span>{graphStats.links} Links</span>
          </div>
        </div>
      </div>

      {/* Graph Container */}
      <div className="flex-1 relative">
        {graphData.nodes.length > 0 ? (
          <ForceGraph2D
            ref={graphRef}
            graphData={graphData}
            nodeCanvasObject={nodePaint}
            linkCanvasObject={linkPaint}
            onNodeClick={setSelectedNode}
            nodePointerAreaPaint={(node, color, ctx) => {
              ctx.fillStyle = color;
              const size = (node.size || 10) * 2;
              ctx.fillRect(node.x - size/2, node.y - size/2, size, size);
            }}
            linkDirectionalArrowLength={6}
            linkDirectionalArrowRelPos={1}
            linkDirectionalArrowColor="#00d4ff"
            linkColor="#00d4ff"
            backgroundColor="transparent"
            width={800}
            height={500}
            cooldownTicks={100}
            onEngineStop={() => graphRef.current.zoomToFit(400)}
          />
        ) : (
          <div className="flex items-center justify-center h-full">
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="text-center"
            >
              <Database className="w-16 h-16 text-gray-600 mx-auto mb-4" />
              <p className="text-gray-400 mb-2">No knowledge graph data available</p>
              <p className="text-sm text-gray-500">Upload documents or run a query to build the graph</p>
            </motion.div>
          </div>
        )}

        {/* Loading Overlay */}
        {isLoading && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="absolute inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center"
          >
            <div className="text-center">
              <div className="w-8 h-8 border-2 border-neon-blue border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
              <p className="text-white">Agents building knowledge graph...</p>
            </div>
          </motion.div>
        )}
      </div>

      {/* Node Details Panel */}
      {selectedNode && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="mt-4 p-4 bg-white/5 border border-white/20 rounded-lg"
        >
          <div className="flex items-center space-x-3 mb-3">
            <div className="w-6 h-6 bg-neon-blue rounded-lg flex items-center justify-center">
              {getNodeIcon(selectedNode.type)}
            </div>
            <div>
              <h4 className="text-white font-medium">{selectedNode.name}</h4>
              <p className="text-sm text-gray-400 capitalize">{selectedNode.type}</p>
            </div>
          </div>
          
          <div className="space-y-2 text-sm text-gray-300">
            <p><span className="text-gray-500">Type:</span> {selectedNode.type}</p>
            <p><span className="text-gray-500">Size:</span> {selectedNode.size}</p>
            <p><span className="text-gray-500">Connections:</span> {
              graphData.links.filter(link => 
                link.source.id === selectedNode.id || link.target.id === selectedNode.id
              ).length
            }</p>
          </div>
        </motion.div>
      )}

      {/* Legend */}
      <div className="mt-4 flex items-center justify-center space-x-6 text-xs">
        <div className="flex items-center space-x-2">
          <div className="w-3 h-3 bg-neon-blue rounded-full"></div>
          <span className="text-gray-400">Query</span>
        </div>
        <div className="flex items-center space-x-2">
          <div className="w-3 h-3 bg-neon-green rounded-full"></div>
          <span className="text-gray-400">Document</span>
        </div>
        <div className="flex items-center space-x-2">
          <div className="w-3 h-3 bg-neon-purple rounded-full"></div>
          <span className="text-gray-400">Entity</span>
        </div>
        <div className="flex items-center space-x-2">
          <div className="w-3 h-3 bg-neon-pink rounded-full"></div>
          <span className="text-gray-400">Insight</span>
        </div>
      </div>
    </motion.div>
  );
};

export default GraphView;
