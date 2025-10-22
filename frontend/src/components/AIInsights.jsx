import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useContextCloud } from '../context/ContextCloudContext';
import { 
  Brain, 
  TrendingUp, 
  AlertCircle, 
  Lightbulb, 
  Target, 
  CheckCircle,
  ArrowRight,
  Loader,
  Eye,
  BarChart3
} from 'lucide-react';

const AIInsights = ({ currentQuery, visibleNodes, isLoading, onRelevantNodesChange }) => {
  const [insights, setInsights] = useState(null);
  const [insightsLoading, setInsightsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [expandedSection, setExpandedSection] = useState('summary');
  // add ask states
  const [askResult, setAskResult] = useState(null);
  const [isAsking, setIsAsking] = useState(false);

  useEffect(() => {
    if (currentQuery && visibleNodes && visibleNodes.length > 0) {
      generateInsights();
    } else if (!currentQuery && onRelevantNodesChange) {
      // Clear filter when no query is active
      onRelevantNodesChange(null);
    }
  }, [currentQuery, visibleNodes]);

  const { generateAIInsights, searchWithGemini } = useContextCloud();

  const generateInsights = async () => {
    if (!currentQuery) return;
    
    setInsightsLoading(true);
    setError(null);
    
    try {
      const data = await generateAIInsights(currentQuery, visibleNodes || []);
      setInsights(data.insights);
    } catch (err) {
      console.error('Failed to generate insights:', err);
      setError(err.message);
    } finally {
      setInsightsLoading(false);
    }
  };

  const askContextCloud = async () => {
    if (!currentQuery) return;
    setIsAsking(true);
    setError(null);
    try {
      const data = await searchWithGemini(currentQuery, visibleNodes || []);
      setAskResult(data);
      
      // Update relevant nodes for filtering if onRelevantNodesChange is provided
      if (onRelevantNodesChange && data.relevant_nodes) {
        const relevantNodeIds = data.relevant_nodes.map(node => node.id);
        onRelevantNodesChange(relevantNodeIds);
      }
    } catch (err) {
      console.error('Failed to ask ContextCloud:', err);
      setError(err.message);
    } finally {
      setIsAsking(false);
    }
  };

  const getConfidenceColor = (score) => {
    if (score >= 80) return 'text-green-400';
    if (score >= 60) return 'text-yellow-400';
    return 'text-red-400';
  };

  const getConfidenceLabel = (score) => {
    if (score >= 80) return 'High Confidence';
    if (score >= 60) return 'Medium Confidence';
    return 'Low Confidence';
  };

  const insightSections = [
    {
      id: 'summary',
      title: 'Executive Summary',
      icon: <Brain className="w-5 h-5" />,
      color: 'neon-blue'
    },
    {
      id: 'key_findings',
      title: 'Key Findings',
      icon: <TrendingUp className="w-5 h-5" />,
      color: 'neon-green'
    },
    {
      id: 'relationship_patterns',
      title: 'Relationship Patterns',
      icon: <BarChart3 className="w-5 h-5" />,
      color: 'neon-purple'
    },
    {
      id: 'knowledge_gaps',
      title: 'Knowledge Gaps',
      icon: <AlertCircle className="w-5 h-5" />,
      color: 'neon-orange'
    },
    {
      id: 'strategic_insights',
      title: 'Strategic Insights',
      icon: <Lightbulb className="w-5 h-5" />,
      color: 'neon-yellow'
    },
    {
      id: 'suggested_next_steps',
      title: 'Next Steps',
      icon: <Target className="w-5 h-5" />,
      color: 'neon-pink'
    }
  ];

  if (!currentQuery) {
    return (
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="glass-dark rounded-xl p-6"
      >
        <div className="text-center">
          <Brain className="w-12 h-12 text-gray-600 mx-auto mb-4" />
          <p className="text-gray-400">Enter a query to generate AI insights</p>
        </div>
      </motion.div>
    );
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
      className="glass-dark rounded-xl p-6"
    >
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center space-x-3">
          <div className="w-8 h-8 bg-gradient-to-r from-neon-blue to-neon-purple rounded-lg flex items-center justify-center">
            <Brain className="w-4 h-4 text-white" />
          </div>
          <div>
            <h3 className="text-lg font-semibold text-white">AI Insights</h3>
            <p className="text-sm text-gray-400">Intelligent analysis of your knowledge graph</p>
          </div>
        </div>
        
        {insights && (
          <div className="flex items-center space-x-4">
            <div className="flex items-center space-x-2 text-sm">
              <Eye className="w-4 h-4 text-neon-blue" />
              <span className="text-gray-300">{insights.nodes_analyzed} nodes analyzed</span>
            </div>
            <div className={`flex items-center space-x-2 text-sm ${getConfidenceColor(insights.confidence_score)}`}>
              <CheckCircle className="w-4 h-4" />
              <span>{getConfidenceLabel(insights.confidence_score)}</span>
            </div>
          </div>
        )}
      </div>

      {/* Loading State */}
      {(insightsLoading || isLoading) && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="flex items-center justify-center py-12"
        >
          <div className="text-center">
            <Loader className="w-8 h-8 text-neon-blue animate-spin mx-auto mb-4" />
            <p className="text-white">Generating AI insights...</p>
            <p className="text-sm text-gray-400 mt-2">Analyzing {visibleNodes?.length || 0} nodes</p>
          </div>
        </motion.div>
      )}

      {/* Error State */}
      {error && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="bg-red-500/10 border border-red-500/30 rounded-lg p-4 mb-6"
        >
          <div className="flex items-center space-x-2">
            <AlertCircle className="w-5 h-5 text-red-400" />
            <span className="text-red-400">Failed to generate insights: {error}</span>
          </div>
          <button
            onClick={generateInsights}
            className="mt-3 px-4 py-2 bg-red-500/20 hover:bg-red-500/30 text-red-400 rounded-lg text-sm transition-colors"
          >
            Retry
          </button>
        </motion.div>
      )}

      {/* Insights Content */}
      {insights && !insightsLoading && (
        <div className="space-y-4">
          {/* Section Navigation */}
          <div className="flex flex-wrap gap-2 mb-6">
            {insightSections.map((section) => (
              <button
                key={section.id}
                onClick={() => setExpandedSection(section.id)}
                className={`flex items-center space-x-2 px-3 py-2 rounded-lg text-sm transition-all ${
                  expandedSection === section.id
                    ? `bg-${section.color}/20 text-${section.color} border border-${section.color}/30`
                    : 'bg-white/5 text-gray-400 hover:bg-white/10'
                }`}
              >
                {section.icon}
                <span>{section.title}</span>
              </button>
            ))}
          </div>

          {/* Content Sections */}
          <AnimatePresence mode="wait">
            <motion.div
              key={expandedSection}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
              transition={{ duration: 0.3 }}
              className="bg-white/5 rounded-lg p-4"
            >
              {expandedSection === 'summary' && (
                <div>
                  <h4 className="text-white font-medium mb-3 flex items-center space-x-2">
                    <Brain className="w-4 h-4 text-neon-blue" />
                    <span>Executive Summary</span>
                  </h4>
                  <p className="text-gray-300 leading-relaxed">{insights.summary}</p>
                </div>
              )}

              {expandedSection === 'key_findings' && (
                <div>
                  <h4 className="text-white font-medium mb-3 flex items-center space-x-2">
                    <TrendingUp className="w-4 h-4 text-neon-green" />
                    <span>Key Findings</span>
                  </h4>
                  <ul className="space-y-2">
                    {Array.isArray(insights.key_findings) ? (
                      insights.key_findings.map((finding, index) => (
                        <li key={index} className="flex items-start space-x-2 text-gray-300">
                          <ArrowRight className="w-4 h-4 text-neon-green mt-0.5 flex-shrink-0" />
                          <span>{finding}</span>
                        </li>
                      ))
                    ) : (
                      <p className="text-gray-300">{insights.key_findings}</p>
                    )}
                  </ul>
                </div>
              )}

              {expandedSection === 'relationship_patterns' && (
                <div>
                  <h4 className="text-white font-medium mb-3 flex items-center space-x-2">
                    <BarChart3 className="w-4 h-4 text-neon-purple" />
                    <span>Relationship Patterns</span>
                  </h4>
                  <p className="text-gray-300 leading-relaxed">{insights.relationship_patterns}</p>
                </div>
              )}

              {expandedSection === 'knowledge_gaps' && (
                <div>
                  <h4 className="text-white font-medium mb-3 flex items-center space-x-2">
                    <AlertCircle className="w-4 h-4 text-neon-orange" />
                    <span>Knowledge Gaps</span>
                  </h4>
                  <p className="text-gray-300 leading-relaxed">{insights.knowledge_gaps}</p>
                </div>
              )}

              {expandedSection === 'strategic_insights' && (
                <div>
                  <h4 className="text-white font-medium mb-3 flex items-center space-x-2">
                    <Lightbulb className="w-4 h-4 text-neon-yellow" />
                    <span>Strategic Insights</span>
                  </h4>
                  <p className="text-gray-300 leading-relaxed">{insights.strategic_insights}</p>
                </div>
              )}

              {expandedSection === 'suggested_next_steps' && (
                <div>
                  <h4 className="text-white font-medium mb-3 flex items-center space-x-2">
                    <Target className="w-4 h-4 text-neon-pink" />
                    <span>Suggested Next Steps</span>
                  </h4>
                  <ul className="space-y-2">
                    {Array.isArray(insights.suggested_next_steps) ? (
                      insights.suggested_next_steps.map((step, index) => (
                        <li key={index} className="flex items-start space-x-2 text-gray-300">
                          <ArrowRight className="w-4 h-4 text-neon-pink mt-0.5 flex-shrink-0" />
                          <span>{step}</span>
                        </li>
                      ))
                    ) : (
                      <p className="text-gray-300">{insights.suggested_next_steps}</p>
                    )}
                  </ul>
                </div>
              )}
            </motion.div>
          </AnimatePresence>

          {/* Data Quality Assessment */}
          <div className="mt-6 p-4 bg-white/5 rounded-lg border border-white/10">
            <div className="flex items-center justify-between">
              <div>
                <h5 className="text-white font-medium">Data Quality Assessment</h5>
                <div className="text-sm text-gray-400 mt-1">
                  {typeof insights.data_quality_assessment === 'string' ? (
                    <p>{insights.data_quality_assessment}</p>
                  ) : typeof insights.data_quality_assessment === 'object' && insights.data_quality_assessment ? (
                    <div className="space-y-1">
                      {insights.data_quality_assessment.completeness && (
                        <div>Completeness: {insights.data_quality_assessment.completeness}</div>
                      )}
                      {insights.data_quality_assessment.reliability && (
                        <div>Reliability: {insights.data_quality_assessment.reliability}</div>
                      )}
                      {insights.data_quality_assessment.timeliness && (
                        <div>Timeliness: {insights.data_quality_assessment.timeliness}</div>
                      )}
                    </div>
                  ) : (
                    <p>Data quality assessment not available</p>
                  )}
                </div>
              </div>
              <div className="text-right">
                <div className={`text-2xl font-bold ${getConfidenceColor(insights.confidence_score)}`}>
                  {insights.confidence_score}%
                </div>
                <div className="text-xs text-gray-400">Confidence</div>
              </div>
            </div>
          </div>

          {/* Refresh Button */}
          <div className="flex justify-center mt-6 gap-3">
            <button
              onClick={generateInsights}
              disabled={insightsLoading}
              className="flex items-center space-x-2 px-4 py-2 bg-neon-blue/20 hover:bg-neon-blue/30 text-neon-blue rounded-lg transition-colors disabled:opacity-50"
            >
              <Brain className="w-4 h-4" />
              <span>Regenerate Insights</span>
            </button>
            <button
              onClick={askContextCloud}
              disabled={isAsking || isLoading}
              className="flex items-center space-x-2 px-4 py-2 bg-emerald-600/30 hover:bg-emerald-600/40 text-emerald-300 rounded-lg transition-colors disabled:opacity-50"
            >
              <Brain className="w-4 h-4" />
              <span>Ask ContextCloud</span>
            </button>
            {onRelevantNodesChange && (
              <button
                onClick={() => onRelevantNodesChange(null)}
                className="flex items-center space-x-2 px-4 py-2 bg-gray-600/30 hover:bg-gray-600/40 text-gray-300 rounded-lg transition-colors"
              >
                <Eye className="w-4 h-4" />
                <span>Clear Filter</span>
              </button>
            )}
          </div>
          {/* Ask Result */}
          {askResult && (
            <div className="mt-6 bg-white/5 rounded-lg p-4">
              <h4 className="text-white font-medium mb-3">ContextCloud Answer</h4>
              {askResult.summary && (
                <p className="text-gray-300 leading-relaxed whitespace-pre-wrap">{askResult.summary}</p>
              )}
              {Array.isArray(askResult.relevant_nodes) && askResult.relevant_nodes.length > 0 && (
                <div className="mt-3">
                  <div className="text-sm text-gray-400 mb-1">Relevant Nodes</div>
                  <ul className="space-y-1">
                    {askResult.relevant_nodes.map((n) => (
                      <li key={n.id} className="flex items-center gap-2 text-sm">
                        <span>{n.label || n.name}</span>
                        <span className="text-gray-500">· {n.type}</span>
                        {n.score !== undefined && (
                          <span className="text-gray-600">score: {Math.round(n.score * 100) / 100}</span>
                        )}
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          )}
        </div>
      )}
    </motion.div>
  );
};

export default AIInsights;