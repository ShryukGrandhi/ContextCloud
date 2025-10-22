import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { Search, Send, FileText, Brain } from 'lucide-react';
import toast from 'react-hot-toast';
import { useContextCloud } from '../context/ContextCloudContext';

const SearchBar = ({ onSearch, isLoading, setIsLoading }) => {
  const [query, setQuery] = useState('');
  const { runAgents, uploadDocument } = useContextCloud();

  const handleSearch = async (e) => {
    e.preventDefault();
    if (!query.trim()) return;

    setIsLoading(true);
    onSearch(query);

    try {
      const result = await runAgents(query);
      toast.success('Agents completed analysis successfully!');
    } catch (error) {
      toast.error('Failed to run agents: ' + error.message);
    } finally {
      setIsLoading(false);
    }
  };

  const handleFileUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    setIsLoading(true);
    try {
      const result = await uploadDocument(file);
      toast.success('Document uploaded and processed successfully!');
    } catch (error) {
      toast.error('Failed to upload document: ' + error.message);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
      className="glass-dark rounded-xl p-6 space-y-4"
    >
      <div className="flex items-center space-x-2 mb-4">
        <Brain className="w-5 h-5 text-neon-blue" />
        <h3 className="text-lg font-semibold text-white">Ask ContextCloud</h3>
      </div>

      {/* Search Form */}
      <form onSubmit={handleSearch} className="space-y-4">
        <div className="relative">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Ask about your enterprise knowledge..."
            className="w-full pl-10 pr-12 py-3 bg-white/5 border border-white/20 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-neon-blue focus:border-transparent transition-all"
            disabled={isLoading}
          />
          <motion.button
            type="submit"
            disabled={isLoading || !query.trim()}
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            className="absolute right-2 top-1/2 transform -translate-y-1/2 p-2 bg-neon-blue text-white rounded-lg hover:bg-neon-blue/80 disabled:opacity-50 disabled:cursor-not-allowed transition-all"
          >
            <Send className="w-4 h-4" />
          </motion.button>
        </div>
      </form>

      {/* File Upload */}
      <div className="space-y-2">
        <label className="flex items-center space-x-2 text-sm text-gray-300 cursor-pointer hover:text-neon-blue transition-colors">
          <FileText className="w-4 h-4" />
          <span>Upload Document</span>
        </label>
        <input
          type="file"
          accept=".pdf,.txt,.docx,.md"
          onChange={handleFileUpload}
          className="w-full text-sm text-gray-400 file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:text-sm file:font-medium file:bg-neon-blue file:text-white hover:file:bg-neon-blue/80 file:cursor-pointer"
          disabled={isLoading}
        />
      </div>

      {/* Example Queries */}
      <div className="space-y-2">
        <p className="text-xs text-gray-400">Example queries:</p>
        <div className="flex flex-wrap gap-2">
          {[
            "What are our compliance requirements?",
            "Summarize the latest policy updates",
            "Find documents about data privacy"
          ].map((example, index) => (
            <motion.button
              key={index}
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              onClick={() => setQuery(example)}
              className="px-3 py-1 text-xs bg-white/10 border border-white/20 rounded-full text-gray-300 hover:text-neon-blue hover:border-neon-blue transition-all"
            >
              {example}
            </motion.button>
          ))}
        </div>
      </div>

      {/* Loading State */}
      {isLoading && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="flex items-center justify-center space-x-2 py-4"
        >
          <div className="w-4 h-4 border-2 border-neon-blue border-t-transparent rounded-full animate-spin"></div>
          <span className="text-sm text-gray-300">Agents working...</span>
        </motion.div>
      )}
    </motion.div>
  );
};

export default SearchBar;
