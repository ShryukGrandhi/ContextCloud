import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Database, FileText, Brain, TrendingUp, Users, Clock } from 'lucide-react';

const StatsPanel = () => {
  const [stats, setStats] = useState({
    documents: 0,
    entities: 0,
    queries: 0,
    insights: 0,
    agents: 4,
    uptime: '99.9%'
  });

  useEffect(() => {
    // Simulate stats loading
    const interval = setInterval(() => {
      setStats(prev => ({
        ...prev,
        documents: Math.floor(Math.random() * 1000) + 500,
        entities: Math.floor(Math.random() * 500) + 200,
        queries: Math.floor(Math.random() * 100) + 50,
        insights: Math.floor(Math.random() * 200) + 100
      }));
    }, 5000);

    return () => clearInterval(interval);
  }, []);

  const statItems = [
    {
      icon: FileText,
      label: 'Documents',
      value: stats.documents,
      color: 'neon-green',
      change: '+12%'
    },
    {
      icon: Database,
      label: 'Entities',
      value: stats.entities,
      color: 'neon-blue',
      change: '+8%'
    },
    {
      icon: Brain,
      label: 'Queries',
      value: stats.queries,
      color: 'neon-purple',
      change: '+15%'
    },
    {
      icon: TrendingUp,
      label: 'Insights',
      value: stats.insights,
      color: 'neon-pink',
      change: '+22%'
    }
  ];

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
      className="glass-dark rounded-xl p-6 space-y-4"
    >
      <div className="flex items-center space-x-2 mb-4">
        <TrendingUp className="w-5 h-5 text-neon-blue" />
        <h3 className="text-lg font-semibold text-white">System Stats</h3>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-2 gap-4">
        {statItems.map((stat, index) => {
          const IconComponent = stat.icon;
          return (
            <motion.div
              key={stat.label}
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ delay: index * 0.1 }}
              className="p-4 bg-white/5 border border-white/20 rounded-lg"
            >
              <div className="flex items-center justify-between mb-2">
                <IconComponent className={`w-5 h-5 text-${stat.color}`} />
                <span className="text-xs text-green-400">{stat.change}</span>
              </div>
              <div className="text-2xl font-bold text-white">{stat.value.toLocaleString()}</div>
              <div className="text-sm text-gray-400">{stat.label}</div>
            </motion.div>
          );
        })}
      </div>

      {/* System Status */}
      <div className="space-y-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <Users className="w-4 h-4 text-neon-green" />
            <span className="text-sm text-gray-300">Active Agents</span>
          </div>
          <span className="text-sm font-medium text-white">{stats.agents}</span>
        </div>
        
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <Clock className="w-4 h-4 text-neon-blue" />
            <span className="text-sm text-gray-300">System Uptime</span>
          </div>
          <span className="text-sm font-medium text-white">{stats.uptime}</span>
        </div>
      </div>

      {/* Performance Indicators */}
      <div className="space-y-2">
        <div className="flex items-center justify-between text-xs text-gray-400">
          <span>CPU Usage</span>
          <span>23%</span>
        </div>
        <div className="w-full bg-white/10 rounded-full h-1">
          <motion.div
            initial={{ width: 0 }}
            animate={{ width: '23%' }}
            transition={{ duration: 1 }}
            className="bg-neon-green h-1 rounded-full"
          />
        </div>
        
        <div className="flex items-center justify-between text-xs text-gray-400">
          <span>Memory Usage</span>
          <span>67%</span>
        </div>
        <div className="w-full bg-white/10 rounded-full h-1">
          <motion.div
            initial={{ width: 0 }}
            animate={{ width: '67%' }}
            transition={{ duration: 1, delay: 0.2 }}
            className="bg-neon-blue h-1 rounded-full"
          />
        </div>
        
        <div className="flex items-center justify-between text-xs text-gray-400">
          <span>Storage Usage</span>
          <span>45%</span>
        </div>
        <div className="w-full bg-white/10 rounded-full h-1">
          <motion.div
            initial={{ width: 0 }}
            animate={{ width: '45%' }}
            transition={{ duration: 1, delay: 0.4 }}
            className="bg-neon-purple h-1 rounded-full"
          />
        </div>
      </div>
    </motion.div>
  );
};

export default StatsPanel;
