import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Brain, Search, BarChart3, FileText, CheckCircle, Clock, AlertCircle } from 'lucide-react';

const AgentConsole = ({ currentQuery, agentStatus, setAgentStatus }) => {
  const [logs, setLogs] = useState([]);
  const [agents, setAgents] = useState([
    {
      id: 'planner',
      name: 'PlannerAgent',
      status: 'ready',
      description: 'Interprets queries and plans workflow',
      icon: Brain,
      color: 'neon-blue'
    },
    {
      id: 'retriever',
      name: 'RetrieverAgent',
      status: 'ready',
      description: 'Retrieves relevant documents from Weaviate',
      icon: Search,
      color: 'neon-green'
    },
    {
      id: 'analyzer',
      name: 'AnalyzerAgent',
      status: 'ready',
      description: 'Analyzes documents using Friendli AI',
      icon: BarChart3,
      color: 'neon-purple'
    },
    {
      id: 'reporter',
      name: 'ReporterAgent',
      status: 'ready',
      description: 'Generates final reports and summaries',
      icon: FileText,
      color: 'neon-pink'
    }
  ]);

  useEffect(() => {
    if (currentQuery) {
      simulateAgentWorkflow();
    }
  }, [currentQuery]);

  const simulateAgentWorkflow = () => {
    const workflow = [
      { agent: 'planner', status: 'active', message: 'Analyzing query intent...', duration: 2000 },
      { agent: 'planner', status: 'completed', message: 'Workflow plan created', duration: 0 },
      { agent: 'retriever', status: 'active', message: 'Querying Weaviate database...', duration: 3000 },
      { agent: 'retriever', status: 'completed', message: 'Documents retrieved successfully', duration: 0 },
      { agent: 'analyzer', status: 'active', message: 'Analyzing with Friendli AI...', duration: 4000 },
      { agent: 'analyzer', status: 'completed', message: 'Analysis completed', duration: 0 },
      { agent: 'reporter', status: 'active', message: 'Generating final report...', duration: 2000 },
      { agent: 'reporter', status: 'completed', message: 'Report generated successfully', duration: 0 }
    ];

    let delay = 0;
    workflow.forEach((step, index) => {
      setTimeout(() => {
        // Update agent status
        setAgents(prev => prev.map(agent => 
          agent.id === step.agent 
            ? { ...agent, status: step.status }
            : agent
        ));

        // Add log entry
        setLogs(prev => [...prev, {
          id: Date.now() + index,
          agent: step.agent,
          message: step.message,
          status: step.status,
          timestamp: new Date().toLocaleTimeString()
        }]);

        // Reset to ready state after completion
        if (step.status === 'completed') {
          setTimeout(() => {
            setAgents(prev => prev.map(agent => 
              agent.id === step.agent 
                ? { ...agent, status: 'ready' }
                : agent
            ));
          }, 1000);
        }
      }, delay);
      delay += step.duration;
    });
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'active':
        return <Clock className="w-4 h-4 text-yellow-400 animate-pulse" />;
      case 'completed':
        return <CheckCircle className="w-4 h-4 text-green-400" />;
      case 'error':
        return <AlertCircle className="w-4 h-4 text-red-400" />;
      default:
        return <div className="w-4 h-4 rounded-full bg-gray-400"></div>;
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'active':
        return 'border-yellow-400 bg-yellow-400/10';
      case 'completed':
        return 'border-green-400 bg-green-400/10';
      case 'error':
        return 'border-red-400 bg-red-400/10';
      default:
        return 'border-gray-400 bg-gray-400/10';
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
        <h3 className="text-lg font-semibold text-white">Agent Console</h3>
      </div>

      {/* Agent Status Grid */}
      <div className="grid grid-cols-2 gap-3">
        {agents.map((agent) => {
          const IconComponent = agent.icon;
          return (
            <motion.div
              key={agent.id}
              whileHover={{ scale: 1.02 }}
              className={`p-3 rounded-lg border transition-all ${getStatusColor(agent.status)}`}
            >
              <div className="flex items-center space-x-2 mb-2">
                <IconComponent className={`w-4 h-4 text-${agent.color}`} />
                <span className="text-sm font-medium text-white">{agent.name}</span>
                {getStatusIcon(agent.status)}
              </div>
              <p className="text-xs text-gray-400">{agent.description}</p>
            </motion.div>
          );
        })}
      </div>

      {/* Agent Logs */}
      <div className="space-y-2">
        <h4 className="text-sm font-medium text-gray-300">Agent Logs</h4>
        <div className="h-32 overflow-y-auto space-y-1">
          <AnimatePresence>
            {logs.map((log) => (
              <motion.div
                key={log.id}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: 20 }}
                className="flex items-center space-x-2 text-xs p-2 bg-white/5 rounded"
              >
                <span className="text-gray-500 w-16">{log.timestamp}</span>
                <span className="text-neon-blue font-medium w-20">{log.agent}</span>
                <span className="text-gray-300 flex-1">{log.message}</span>
                {getStatusIcon(log.status)}
              </motion.div>
            ))}
          </AnimatePresence>
        </div>
      </div>

      {/* Current Query */}
      {currentQuery && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="p-3 bg-white/5 border border-white/20 rounded-lg"
        >
          <h4 className="text-sm font-medium text-gray-300 mb-2">Current Query</h4>
          <p className="text-sm text-white">{currentQuery}</p>
        </motion.div>
      )}

      {/* System Status */}
      <div className="flex items-center justify-between text-xs text-gray-400">
        <div className="flex items-center space-x-4">
          <div className="flex items-center space-x-1">
            <div className="w-2 h-2 bg-neon-green rounded-full animate-pulse"></div>
            <span>Weaviate Connected</span>
          </div>
          <div className="flex items-center space-x-1">
            <div className="w-2 h-2 bg-neon-blue rounded-full animate-pulse"></div>
            <span>Friendli AI Ready</span>
          </div>
        </div>
        <span>Last updated: {new Date().toLocaleTimeString()}</span>
      </div>
    </motion.div>
  );
};

export default AgentConsole;
