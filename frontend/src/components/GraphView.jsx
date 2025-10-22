import React, { useState, useEffect, useRef } from 'react';
import { motion } from 'framer-motion';
import ForceGraph2D from 'react-force-graph-2d';
import { Zap, Database, Brain, FileText, Users, TrendingUp } from 'lucide-react';

const GraphView = ({ currentQuery, isLoading, onVisibleNodesChange, relevantNodeIds = null }) => {
  const [graphData, setGraphData] = useState({ nodes: [], links: [] });
  const [selectedNode, setSelectedNode] = useState(null);
  const [zoom, setZoom] = useState(1);
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
    const fetchGraphData = async () => {
      if (!currentQuery) return;
      
      try {
        const response = await fetch(`http://localhost:8001/graph?query=${encodeURIComponent(currentQuery)}`);
        if (response.ok) {
          const data = await response.json();
          const graph = data.graph || data; // handle both shapes

          // Transform backend edges -> links for ForceGraph
          const nodes = (graph.nodes || []).map(n => ({
            id: n.id || n.label,
            name: n.label || n.name || n.id,
            type: n.type || 'unknown',
            size: n.size || 10,
            color: n.color || '#00d4ff',
          }));

          const links = (graph.edges || graph.links || []).map(e => ({
            source: e.source,
            target: e.target,
            type: e.label || e.type || 'general',
            width: e.width || 2,
            color: e.color || '#00d4ff',
          }));

          let transformed = { nodes, links };

          // Filter nodes and links if relevantNodeIds is provided
          if (relevantNodeIds && relevantNodeIds.length > 0) {
            const relevantNodeSet = new Set(relevantNodeIds);
            
            // Filter nodes to only show relevant ones
            const filteredNodes = nodes.filter(node => relevantNodeSet.has(node.id));
            
            // Filter links to only show connections between relevant nodes
            const filteredLinks = links.filter(link => 
              relevantNodeSet.has(link.source) && relevantNodeSet.has(link.target)
            );
            
            transformed = { nodes: filteredNodes, links: filteredLinks };
          }

          setGraphData(transformed);
          setGraphStats({
            nodes: transformed.nodes.length,
            links: transformed.links.length,
            documents: transformed.nodes.filter(n => n.type === 'document').length,
            entities: transformed.nodes.filter(n => n.type === 'entity').length
          });
        } else {
          // Fallback to sample data if API fails
          let fallbackData = sampleData;
          
          // Filter sample data if relevantNodeIds is provided
          if (relevantNodeIds && relevantNodeIds.length > 0) {
            const relevantNodeSet = new Set(relevantNodeIds);
            const filteredNodes = sampleData.nodes.filter(node => relevantNodeSet.has(node.id));
            const filteredLinks = sampleData.links.filter(link => 
              relevantNodeSet.has(link.source) && relevantNodeSet.has(link.target)
            );
            fallbackData = { nodes: filteredNodes, links: filteredLinks };
          }
          
          setGraphData(fallbackData);
          setGraphStats({
            nodes: fallbackData.nodes.length,
            links: fallbackData.links.length,
            documents: fallbackData.nodes.filter(n => n.type === 'document').length,
            entities: fallbackData.nodes.filter(n => n.type === 'entity').length
          });
        }
      } catch (error) {
        console.error('Failed to fetch graph data:', error);
        // Fallback to sample data
        let fallbackData = sampleData;
        
        // Filter sample data if relevantNodeIds is provided
        if (relevantNodeIds && relevantNodeIds.length > 0) {
          const relevantNodeSet = new Set(relevantNodeIds);
          const filteredNodes = sampleData.nodes.filter(node => relevantNodeSet.has(node.id));
          const filteredLinks = sampleData.links.filter(link => 
            relevantNodeSet.has(link.source) && relevantNodeSet.has(link.target)
          );
          fallbackData = { nodes: filteredNodes, links: filteredLinks };
        }
        
        setGraphData(fallbackData);
        setGraphStats({
          nodes: fallbackData.nodes.length,
          links: fallbackData.links.length,
          documents: fallbackData.nodes.filter(n => n.type === 'document').length,
          entities: fallbackData.nodes.filter(n => n.type === 'entity').length
        });
      }
    };

    fetchGraphData();
  }, [currentQuery, relevantNodeIds]);

  // Notify parent component when visible nodes change
  useEffect(() => {
    if (onVisibleNodesChange && graphData.nodes.length > 0) {
      onVisibleNodesChange(graphData.nodes);
    }
  }, [graphData.nodes, onVisibleNodesChange]);

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
    // Validate node position and size to prevent canvas errors
    if (!node || typeof node.x !== 'number' || typeof node.y !== 'number' || 
        !isFinite(node.x) || !isFinite(node.y)) {
      return; // Skip rendering if node position is invalid
    }
    
    const baseSize = node.size || 10;
    const validGlobalScale = isFinite(globalScale) ? globalScale : 1;
    const size = baseSize * Math.max(0.8, Math.min(2.5, validGlobalScale));
    
    // Ensure size is valid
    if (!isFinite(size) || size <= 0) {
      return; // Skip rendering if size is invalid
    }
    
    const color = node.color || '#00d4ff';
    
    // Enhanced color palette based on node type
    const getNodeColors = (type, baseColor) => {
      const colorMap = {
        'document': { primary: '#4f46e5', secondary: '#818cf8', accent: '#c7d2fe' },
        'person': { primary: '#059669', secondary: '#34d399', accent: '#a7f3d0' },
        'department': { primary: '#dc2626', secondary: '#f87171', accent: '#fecaca' },
        'project': { primary: '#7c3aed', secondary: '#a78bfa', accent: '#ddd6fe' },
        'technology': { primary: '#ea580c', secondary: '#fb923c', accent: '#fed7aa' },
        'process': { primary: '#0891b2', secondary: '#22d3ee', accent: '#a5f3fc' },
        'location': { primary: '#be123c', secondary: '#fb7185', accent: '#fecdd3' },
        'product': { primary: '#65a30d', secondary: '#84cc16', accent: '#d9f99d' },
        'vendor': { primary: '#7c2d12', secondary: '#f97316', accent: '#fed7aa' },
        'default': { primary: baseColor, secondary: '#00d4ff', accent: '#87ceeb' }
      };
      return colorMap[type] || colorMap['default'];
    };
    
    const colors = getNodeColors(node.type, color);
    
    // Create radial gradient for main node with validated coordinates
    const x1 = node.x - size * 0.3;
    const y1 = node.y - size * 0.3;
    const x2 = node.x;
    const y2 = node.y;
    
    // Validate gradient coordinates
    if (!isFinite(x1) || !isFinite(y1) || !isFinite(x2) || !isFinite(y2)) {
      return; // Skip rendering if gradient coordinates are invalid
    }
    
    const gradient = ctx.createRadialGradient(x1, y1, 0, x2, y2, size);
    gradient.addColorStop(0, colors.accent);
    gradient.addColorStop(0.4, colors.secondary);
    gradient.addColorStop(1, colors.primary);
    
    // Enhanced outer glow with multiple layers
    ctx.save();
    
    // Outer glow layer 1 (largest, most transparent)
    ctx.shadowColor = colors.primary;
    ctx.shadowBlur = 25;
    ctx.globalAlpha = 0.3;
    ctx.fillStyle = colors.primary;
    ctx.beginPath();
    ctx.arc(node.x, node.y, size + 8, 0, 2 * Math.PI);
    ctx.fill();
    
    // Outer glow layer 2 (medium)
    ctx.shadowBlur = 15;
    ctx.globalAlpha = 0.5;
    ctx.beginPath();
    ctx.arc(node.x, node.y, size + 4, 0, 2 * Math.PI);
    ctx.fill();
    
    // Reset for main node
    ctx.shadowBlur = 0;
    ctx.globalAlpha = 1;
    
    // Draw main node circle with gradient
    ctx.fillStyle = gradient;
    ctx.beginPath();
    ctx.arc(node.x, node.y, size, 0, 2 * Math.PI);
    ctx.fill();
    
    // Add inner highlight for 3D effect
    const hx1 = node.x - size * 0.4;
    const hy1 = node.y - size * 0.4;
    const hx2 = node.x - size * 0.2;
    const hy2 = node.y - size * 0.2;
    const hr = size * 0.6;
    
    // Validate highlight gradient coordinates
    if (!isFinite(hx1) || !isFinite(hy1) || !isFinite(hx2) || !isFinite(hy2) || !isFinite(hr)) {
      return; // Skip rendering if highlight gradient coordinates are invalid
    }
    
    const highlightGradient = ctx.createRadialGradient(hx1, hy1, 0, hx2, hy2, hr);
    highlightGradient.addColorStop(0, 'rgba(255, 255, 255, 0.8)');
    highlightGradient.addColorStop(0.5, 'rgba(255, 255, 255, 0.3)');
    highlightGradient.addColorStop(1, 'rgba(255, 255, 255, 0)');
    
    ctx.fillStyle = highlightGradient;
    ctx.beginPath();
    ctx.arc(node.x, node.y, size * 0.7, 0, 2 * Math.PI);
    ctx.fill();
    
    // Enhanced border with gradient
    const bx1 = node.x - size;
    const by1 = node.y - size;
    const bx2 = node.x + size;
    const by2 = node.y + size;
    
    // Validate border gradient coordinates
    if (!isFinite(bx1) || !isFinite(by1) || !isFinite(bx2) || !isFinite(by2)) {
      return; // Skip rendering if border gradient coordinates are invalid
    }
    
    const borderGradient = ctx.createLinearGradient(bx1, by1, bx2, by2);
    borderGradient.addColorStop(0, 'rgba(255, 255, 255, 0.9)');
    borderGradient.addColorStop(0.5, 'rgba(255, 255, 255, 0.6)');
    borderGradient.addColorStop(1, 'rgba(255, 255, 255, 0.3)');
    
    ctx.strokeStyle = borderGradient;
    ctx.lineWidth = Math.max(1, size * 0.08);
    ctx.beginPath();
    ctx.arc(node.x, node.y, size, 0, 2 * Math.PI);
    ctx.stroke();
    
    ctx.restore();
    
    // Add node type indicator
    if (node.type) {
      ctx.fillStyle = '#ffffff';
      ctx.font = `${Math.max(8, size * 0.6)}px Inter`;
      ctx.textAlign = 'center';
      ctx.textBaseline = 'middle';
      
      let typeSymbol = '';
      switch (node.type) {
        case 'document': typeSymbol = '📄'; break;
        case 'person': typeSymbol = '👤'; break;
        case 'department': typeSymbol = '🏢'; break;
        case 'project': typeSymbol = '📋'; break;
        case 'technology': typeSymbol = '⚙️'; break;
        case 'process': typeSymbol = '🔄'; break;
        case 'location': typeSymbol = '📍'; break;
        case 'product': typeSymbol = '📦'; break;
        case 'vendor': typeSymbol = '🤝'; break;
        default: typeSymbol = '●'; break;
      }
      
      ctx.fillText(typeSymbol, node.x, node.y);
    }
    
    // Add node label with background
    if (globalScale > 0.5) {
      const label = node.name || node.id;
      const maxLength = Math.floor(20 / Math.max(0.5, globalScale));
      const displayLabel = label.length > maxLength ? label.substring(0, maxLength) + '...' : label;
      
      ctx.font = `${Math.max(10, 12 * globalScale)}px Inter`;
      ctx.textAlign = 'center';
      ctx.textBaseline = 'top';
      
      // Measure text for background
      const textMetrics = ctx.measureText(displayLabel);
      const textWidth = textMetrics.width;
      const textHeight = 14 * globalScale;
      
      // Draw text background
      ctx.fillStyle = 'rgba(0, 0, 0, 0.7)';
      ctx.fillRect(
        node.x - textWidth/2 - 4,
        node.y + size + 5,
        textWidth + 8,
        textHeight + 4
      );
      
      // Draw text
      ctx.fillStyle = '#ffffff';
      ctx.fillText(displayLabel, node.x, node.y + size + 8);
    }
  };

  const linkPaint = (link, ctx, globalScale) => {
    const linkColor = link.color || '#00d4ff';
    const linkWidth = (link.width || 2) * Math.max(0.5, globalScale);
    
    // Set link style based on relationship type
    let strokeStyle = linkColor;
    let linePattern = [];
    
    switch (link.type) {
      case 'hierarchical':
        strokeStyle = '#ff6b9d';
        break;
      case 'collaborative':
        strokeStyle = '#00ff88';
        linePattern = [5, 5];
        break;
      case 'technical':
        strokeStyle = '#b347d9';
        break;
      case 'geographic':
        strokeStyle = '#ffa500';
        linePattern = [10, 5];
        break;
      case 'temporal':
        strokeStyle = '#ffff00';
        linePattern = [3, 3];
        break;
      default:
        strokeStyle = linkColor;
        break;
    }
    
    // Draw link with glow effect
    ctx.shadowColor = strokeStyle;
    ctx.shadowBlur = 3;
    ctx.strokeStyle = strokeStyle;
    ctx.lineWidth = linkWidth;
    
    // Set line dash pattern if specified
    if (linePattern.length > 0) {
      ctx.setLineDash(linePattern);
    } else {
      ctx.setLineDash([]);
    }
    
    ctx.beginPath();
    ctx.moveTo(link.source.x, link.source.y);
    ctx.lineTo(link.target.x, link.target.y);
    ctx.stroke();
    
    // Reset line dash
    ctx.setLineDash([]);
    
    // Add relationship label for close zoom levels
    if (globalScale > 1.2 && link.type) {
      const midX = (link.source.x + link.target.x) / 2;
      const midY = (link.source.y + link.target.y) / 2;
      
      ctx.fillStyle = 'rgba(0, 0, 0, 0.8)';
      ctx.font = `${Math.max(8, 10 * globalScale)}px Inter`;
      ctx.textAlign = 'center';
      ctx.textBaseline = 'middle';
      
      const label = link.type.replace('_', ' ');
      const textMetrics = ctx.measureText(label);
      
      // Draw label background
      ctx.fillRect(
        midX - textMetrics.width/2 - 3,
        midY - 6,
        textMetrics.width + 6,
        12
      );
      
      // Draw label text
      ctx.fillStyle = '#ffffff';
      ctx.fillText(label, midX, midY);
    }
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
            // Force simulation parameters to prevent node overlap
            d3AlphaDecay={0.0228}
            d3VelocityDecay={0.3}
            nodeRelSize={6}
            linkDistance={(link) => {
              const baseDistance = 120;
              const zoomFactor = Math.max(1, Math.min(3, zoom || 1));
              return baseDistance * zoomFactor;
            }}
            linkStrength={0.3}
            chargeStrength={-400}
            // Enable collision detection to prevent overlap
            d3Force={{
              collision: {
                radius: (node) => {
                  const baseSize = (node.size || 10);
                  const zoomFactor = Math.max(1, Math.min(2.5, zoom || 1));
                  return baseSize * 2.2 * zoomFactor;
                },
                strength: 1.2,
                iterations: 3
              },
              center: { strength: 0.05 },
              charge: { 
                strength: (node) => {
                  const baseCharge = -500;
                  const zoomFactor = Math.max(1, Math.min(2, zoom || 1));
                  return baseCharge * zoomFactor;
                }
              },
              link: { 
                distance: (link) => {
                  const baseDistance = 120;
                  const zoomFactor = Math.max(1, Math.min(3, zoom || 1));
                  return baseDistance * zoomFactor;
                }, 
                strength: 0.3,
                iterations: 2
              },
              x: { strength: 0.02 },
              y: { strength: 0.02 }
            }}
            onZoom={(transform) => {
              if (transform && transform.k) {
                setZoom(transform.k);
              }
            }}
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

      {/* Enhanced Legend */}
      <div className="mt-4 space-y-4">
        {/* Node Types Legend */}
        <div>
          <h5 className="text-white text-sm font-medium mb-2">Node Types</h5>
          <div className="grid grid-cols-3 gap-2 text-xs">
            <div className="flex items-center space-x-2">
              <span className="text-lg">📄</span>
              <span className="text-gray-400">Documents</span>
            </div>
            <div className="flex items-center space-x-2">
              <span className="text-lg">👤</span>
              <span className="text-gray-400">People</span>
            </div>
            <div className="flex items-center space-x-2">
              <span className="text-lg">🏢</span>
              <span className="text-gray-400">Departments</span>
            </div>
            <div className="flex items-center space-x-2">
              <span className="text-lg">📋</span>
              <span className="text-gray-400">Projects</span>
            </div>
            <div className="flex items-center space-x-2">
              <span className="text-lg">⚙️</span>
              <span className="text-gray-400">Technology</span>
            </div>
            <div className="flex items-center space-x-2">
              <span className="text-lg">🔄</span>
              <span className="text-gray-400">Processes</span>
            </div>
            <div className="flex items-center space-x-2">
              <span className="text-lg">📍</span>
              <span className="text-gray-400">Locations</span>
            </div>
            <div className="flex items-center space-x-2">
              <span className="text-lg">📦</span>
              <span className="text-gray-400">Products</span>
            </div>
            <div className="flex items-center space-x-2">
              <span className="text-lg">🤝</span>
              <span className="text-gray-400">Vendors</span>
            </div>
          </div>
        </div>

        {/* Relationship Types Legend */}
        <div>
          <h5 className="text-white text-sm font-medium mb-2">Relationship Types</h5>
          <div className="grid grid-cols-2 gap-2 text-xs">
            <div className="flex items-center space-x-2">
              <div className="w-4 h-0.5 bg-pink-400"></div>
              <span className="text-gray-400">Hierarchical</span>
            </div>
            <div className="flex items-center space-x-2">
              <div className="w-4 h-0.5 bg-green-400 border-dashed border-t"></div>
              <span className="text-gray-400">Collaborative</span>
            </div>
            <div className="flex items-center space-x-2">
              <div className="w-4 h-0.5 bg-purple-400"></div>
              <span className="text-gray-400">Technical</span>
            </div>
            <div className="flex items-center space-x-2">
              <div className="w-4 h-0.5 bg-orange-400"></div>
              <span className="text-gray-400">Geographic</span>
            </div>
            <div className="flex items-center space-x-2">
              <div className="w-4 h-0.5 bg-yellow-400"></div>
              <span className="text-gray-400">Temporal</span>
            </div>
            <div className="flex items-center space-x-2">
              <div className="w-4 h-0.5 bg-blue-400"></div>
              <span className="text-gray-400">General</span>
            </div>
          </div>
        </div>

        {/* Interaction Tips */}
        <div className="text-xs text-gray-500 text-center">
          <p>💡 Click nodes for details • Zoom for relationship labels • Drag to explore</p>
        </div>
      </div>
    </motion.div>
  );
};

export default GraphView;
