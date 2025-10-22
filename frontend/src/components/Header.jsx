import React from 'react';
import { motion } from 'framer-motion';
import { Brain, Zap, Database, Cloud } from 'lucide-react';

const Header = () => {
  return (
    <motion.header
      initial={{ opacity: 0, y: -50 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.6 }}
      className="glass-dark border-b border-white/10"
    >
      <div className="container mx-auto px-4 py-6">
        <div className="flex items-center justify-between">
          {/* Logo and Title */}
          <div className="flex items-center space-x-4">
            <motion.div
              animate={{ rotate: 360 }}
              transition={{ duration: 20, repeat: Infinity, ease: "linear" }}
              className="relative"
            >
              <div className="w-12 h-12 bg-gradient-to-r from-neon-blue to-neon-purple rounded-full flex items-center justify-center">
                <Brain className="w-6 h-6 text-white" />
              </div>
              <div className="absolute -inset-1 bg-gradient-to-r from-neon-blue to-neon-purple rounded-full opacity-30 blur-sm"></div>
            </motion.div>
            
            <div>
              <h1 className="text-2xl font-bold text-white neon-glow">
                ContextCloud Agents
              </h1>
              <p className="text-sm text-gray-300">
                Multi-Agent Enterprise Knowledge Platform
              </p>
            </div>
          </div>
          
          {/* Tech Stack Icons */}
          <div className="flex items-center space-x-6">
            <motion.div
              whileHover={{ scale: 1.1 }}
              className="flex items-center space-x-2 text-gray-300 hover:text-neon-blue transition-colors"
            >
              <Zap className="w-5 h-5" />
              <span className="text-sm font-medium">LlamaIndex</span>
            </motion.div>
            
            <motion.div
              whileHover={{ scale: 1.1 }}
              className="flex items-center space-x-2 text-gray-300 hover:text-neon-purple transition-colors"
            >
              <Database className="w-5 h-5" />
              <span className="text-sm font-medium">Weaviate</span>
            </motion.div>
            
            <motion.div
              whileHover={{ scale: 1.1 }}
              className="flex items-center space-x-2 text-gray-300 hover:text-neon-green transition-colors"
            >
              <Brain className="w-5 h-5" />
              <span className="text-sm font-medium">Friendli AI</span>
            </motion.div>
            
            <motion.div
              whileHover={{ scale: 1.1 }}
              className="flex items-center space-x-2 text-gray-300 hover:text-neon-pink transition-colors"
            >
              <Cloud className="w-5 h-5" />
              <span className="text-sm font-medium">AWS</span>
            </motion.div>
          </div>
        </div>
        
        {/* Status Bar */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.3 }}
          className="mt-4 flex items-center justify-between text-sm"
        >
          <div className="flex items-center space-x-4">
            <div className="flex items-center space-x-2">
              <div className="w-2 h-2 bg-neon-green rounded-full animate-pulse"></div>
              <span className="text-gray-300">System Online</span>
            </div>
            <div className="flex items-center space-x-2">
              <div className="w-2 h-2 bg-neon-blue rounded-full animate-pulse"></div>
              <span className="text-gray-300">4 Agents Ready</span>
            </div>
          </div>
          
          <div className="text-gray-400">
            AWS AI Agents Hack Day 2024
          </div>
        </motion.div>
      </div>
    </motion.header>
  );
};

export default Header;
