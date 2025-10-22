import React from 'react';
import { motion } from 'framer-motion';
import { Search, FileText, Brain, Users, Building, Settings, Lightbulb } from 'lucide-react';
import { useContextCloud } from '../context/ContextCloudContext';

const SearchResults = () => {
  const { searchResults, currentQuery } = useContextCloud();

  if (!searchResults) {
    return null;
  }

  const getNodeIcon = (nodeType) => {
    switch (nodeType) {
      case 'department':
        return <Building className="w-4 h-4" />;
      case 'policy':
      case 'procedure':
        return <FileText className="w-4 h-4" />;
      case 'system':
        return <Settings className="w-4 h-4" />;
      case 'entity':
        return <Brain className="w-4 h-4" />;
      default:
        return <FileText className="w-4 h-4" />;
    }
  };

  const getNodeColor = (nodeType) => {
    switch (nodeType) {
      case 'department':
        return 'text-purple-400 bg-purple-400/10';
      case 'policy':
        return 'text-blue-400 bg-blue-400/10';
      case 'procedure':
        return 'text-green-400 bg-green-400/10';
      case 'system':
        return 'text-orange-400 bg-orange-400/10';
      case 'entity':
        return 'text-pink-400 bg-pink-400/10';
      default:
        return 'text-gray-400 bg-gray-400/10';
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
      className="glass-dark rounded-xl p-6 space-y-6"
    >
      {/* Header */}
      <div className="flex items-center space-x-3">
        <div className="p-2 bg-neon-blue/20 rounded-lg">
          <Search className="w-5 h-5 text-neon-blue" />
        </div>
        <div>
          <h3 className="text-lg font-semibold text-white">Search Results</h3>
          <p className="text-sm text-gray-400">
            Query: "{currentQuery}" • Found {searchResults.relevant_nodes_found} relevant items
          </p>
        </div>
      </div>

      {/* Summary Section */}
      <div className="space-y-4">
        <div className="flex items-center space-x-2">
          <Lightbulb className="w-5 h-5 text-yellow-400" />
          <h4 className="text-md font-semibold text-white">Summary</h4>
        </div>
        <div className="bg-white/5 border border-white/10 rounded-lg p-4">
          <p className="text-gray-300 leading-relaxed whitespace-pre-wrap">
            {searchResults.summary}
          </p>
        </div>
      </div>

      {/* Relevant Nodes */}
      {searchResults.relevant_nodes && searchResults.relevant_nodes.length > 0 && (
        <div className="space-y-4">
          <div className="flex items-center space-x-2">
            <Brain className="w-5 h-5 text-neon-blue" />
            <h4 className="text-md font-semibold text-white">Relevant Information</h4>
          </div>
          <div className="grid gap-3">
            {searchResults.relevant_nodes.slice(0, 8).map((node, index) => (
              <motion.div
                key={node.id || index}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ duration: 0.3, delay: index * 0.1 }}
                className="bg-white/5 border border-white/10 rounded-lg p-4 hover:bg-white/10 transition-all"
              >
                <div className="flex items-start space-x-3">
                  <div className={`p-2 rounded-lg ${getNodeColor(node.type)}`}>
                    {getNodeIcon(node.type)}
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center space-x-2 mb-2">
                      <h5 className="text-white font-medium truncate">{node.label}</h5>
                      <span className={`px-2 py-1 text-xs rounded-full ${getNodeColor(node.type)}`}>
                        {node.type}
                      </span>
                    </div>
                    <p className="text-gray-400 text-sm leading-relaxed">
                      {node.summary || node.content_preview || 'No description available'}
                    </p>
                    {node.key_terms && node.key_terms.length > 0 && (
                      <div className="flex flex-wrap gap-1 mt-2">
                        {node.key_terms.slice(0, 5).map((term, termIndex) => (
                          <span
                            key={termIndex}
                            className="px-2 py-1 text-xs bg-neon-blue/20 text-neon-blue rounded-full"
                          >
                            {term}
                          </span>
                        ))}
                      </div>
                    )}
                  </div>
                </div>
              </motion.div>
            ))}
          </div>
        </div>
      )}

      {/* Search Statistics */}
      <div className="flex items-center justify-between text-sm text-gray-400 pt-4 border-t border-white/10">
        <span>Searched {searchResults.total_nodes_searched} total nodes</span>
        <span>Found {searchResults.relevant_nodes_found} relevant matches</span>
      </div>
    </motion.div>
  );
};

export default SearchResults;