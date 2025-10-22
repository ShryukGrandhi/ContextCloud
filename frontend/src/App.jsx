import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Toaster } from 'react-hot-toast';
import GraphView from './components/GraphView';
import AgentConsole from './components/AgentConsole';
import SearchBar from './components/SearchBar';
import Header from './components/Header';
import StatsPanel from './components/StatsPanel';
import ParticleBackground from './components/ParticleBackground';
import { ContextCloudProvider } from './context/ContextCloudContext';

function App() {
  const [isLoading, setIsLoading] = useState(false);
  const [currentQuery, setCurrentQuery] = useState('');
  const [agentStatus, setAgentStatus] = useState({});

  return (
    <ContextCloudProvider>
      <div className="min-h-screen bg-gradient-to-br from-slate-950 via-slate-900 to-slate-800 relative overflow-hidden">
        {/* Particle Background */}
        <ParticleBackground />
        
        {/* Main Content */}
        <div className="relative z-10">
          {/* Header */}
          <Header />
          
          {/* Main Dashboard */}
          <div className="container mx-auto px-4 py-8">
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
              {/* Left Panel - Search and Controls */}
              <div className="lg:col-span-1 space-y-6">
                <motion.div
                  initial={{ opacity: 0, x: -50 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ duration: 0.5 }}
                >
                  <SearchBar 
                    onSearch={setCurrentQuery}
                    isLoading={isLoading}
                    setIsLoading={setIsLoading}
                  />
                </motion.div>
                
                <motion.div
                  initial={{ opacity: 0, x: -50 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ duration: 0.5, delay: 0.1 }}
                >
                  <StatsPanel />
                </motion.div>
                
                <motion.div
                  initial={{ opacity: 0, x: -50 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ duration: 0.5, delay: 0.2 }}
                >
                  <AgentConsole 
                    currentQuery={currentQuery}
                    agentStatus={agentStatus}
                    setAgentStatus={setAgentStatus}
                  />
                </motion.div>
              </div>
              
              {/* Right Panel - Graph Visualization */}
              <div className="lg:col-span-2">
                <motion.div
                  initial={{ opacity: 0, x: 50 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ duration: 0.5, delay: 0.3 }}
                  className="h-[600px] lg:h-[700px]"
                >
                  <GraphView 
                    currentQuery={currentQuery}
                    isLoading={isLoading}
                  />
                </motion.div>
              </div>
            </div>
          </div>
        </div>
        
        {/* Toast Notifications */}
        <Toaster
          position="top-right"
          toastOptions={{
            duration: 4000,
            style: {
              background: 'rgba(15, 23, 42, 0.9)',
              color: '#fff',
              border: '1px solid rgba(0, 212, 255, 0.3)',
              backdropFilter: 'blur(10px)',
            },
          }}
        />
      </div>
    </ContextCloudProvider>
  );
}

export default App;
