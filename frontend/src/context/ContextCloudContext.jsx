import React, { createContext, useContext, useState, useCallback } from 'react';
import axios from 'axios';
import toast from 'react-hot-toast';

const ContextCloudContext = createContext();

export const useContextCloud = () => {
  const context = useContext(ContextCloudContext);
  if (!context) {
    throw new Error('useContextCloud must be used within a ContextCloudProvider');
  }
  return context;
};

export const ContextCloudProvider = ({ children }) => {
  const [isLoading, setIsLoading] = useState(false);
  const [currentQuery, setCurrentQuery] = useState('');
  const [agentStatus, setAgentStatus] = useState({});
  const [knowledgeGraph, setKnowledgeGraph] = useState(null);
  const [recentResults, setRecentResults] = useState([]);

  // API base URL
  const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

  const api = axios.create({
    baseURL: API_BASE_URL,
    timeout: 30000,
  });

  // Run agents workflow
  const runAgents = useCallback(async (query) => {
    setIsLoading(true);
    setCurrentQuery(query);
    
    try {
      const response = await api.post('/agents/run', { query });
      const result = response.data;
      
      // Update knowledge graph if available
      if (result.result?.final_report?.formatted_output?.visualization_data) {
        setKnowledgeGraph(result.result.final_report.formatted_output.visualization_data);
      }
      
      // Add to recent results
      setRecentResults(prev => [result, ...prev.slice(0, 9)]);
      
      return result;
    } catch (error) {
      console.error('Agent execution failed:', error);
      throw new Error(error.response?.data?.detail || 'Failed to run agents');
    } finally {
      setIsLoading(false);
    }
  }, [api]);

  // Upload document
  const uploadDocument = useCallback(async (file) => {
    setIsLoading(true);
    
    try {
      const formData = new FormData();
      formData.append('file', file);
      formData.append('document_type', 'general');
      formData.append('metadata', JSON.stringify({ uploaded_at: new Date().toISOString() }));
      
      const response = await api.post('/upload', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      
      const result = response.data;
      
      // Refresh knowledge graph after upload
      await getKnowledgeGraph();
      
      return result;
    } catch (error) {
      console.error('Document upload failed:', error);
      throw new Error(error.response?.data?.detail || 'Failed to upload document');
    } finally {
      setIsLoading(false);
    }
  }, [api]);

  // Get knowledge graph
  const getKnowledgeGraph = useCallback(async () => {
    try {
      const response = await api.get('/graph');
      const result = response.data;
      setKnowledgeGraph(result.graph);
      return result;
    } catch (error) {
      console.error('Failed to get knowledge graph:', error);
      throw new Error(error.response?.data?.detail || 'Failed to get knowledge graph');
    }
  }, [api]);

  // Ask Friendli AI directly
  const askFriendli = useCallback(async (query) => {
    try {
      const response = await api.post('/ask', { query });
      return response.data;
    } catch (error) {
      console.error('Friendli query failed:', error);
      throw new Error(error.response?.data?.detail || 'Failed to query Friendli AI');
    }
  }, [api]);

  // Get agent status
  const getAgentStatus = useCallback(async () => {
    try {
      const response = await api.get('/agents/status');
      const result = response.data;
      setAgentStatus(result.agents);
      return result;
    } catch (error) {
      console.error('Failed to get agent status:', error);
      throw new Error(error.response?.data?.detail || 'Failed to get agent status');
    }
  }, [api]);

  // Health check
  const healthCheck = useCallback(async () => {
    try {
      const response = await api.get('/health');
      return response.data;
    } catch (error) {
      console.error('Health check failed:', error);
      throw new Error(error.response?.data?.detail || 'Health check failed');
    }
  }, [api]);

  // Clear recent results
  const clearRecentResults = useCallback(() => {
    setRecentResults([]);
  }, []);

  // Clear knowledge graph
  const clearKnowledgeGraph = useCallback(() => {
    setKnowledgeGraph(null);
  }, []);

  const value = {
    // State
    isLoading,
    currentQuery,
    agentStatus,
    knowledgeGraph,
    recentResults,
    
    // Actions
    runAgents,
    uploadDocument,
    getKnowledgeGraph,
    askFriendli,
    getAgentStatus,
    healthCheck,
    clearRecentResults,
    clearKnowledgeGraph,
    setCurrentQuery,
    setAgentStatus,
  };

  return (
    <ContextCloudContext.Provider value={value}>
      {children}
    </ContextCloudContext.Provider>
  );
};
