import { useState, useCallback } from 'react';
import { fetchGraphNodes, fetchSubgraph, fetchGraphStats } from '../services/api';

export default function useKnowledgeGraph() {
  const [nodes, setNodes] = useState([]);
  const [edges, setEdges] = useState([]);
  const [stats, setStats] = useState(null);
  const [selectedNode, setSelectedNode] = useState(null);
  const [isLoading, setIsLoading] = useState(false);

  const loadNodes = useCallback(async (params = {}) => {
    setIsLoading(true);
    try {
      const data = await fetchGraphNodes(params);
      setNodes(data.nodes || data || []);
    } catch (e) {
      console.error('Failed to load graph nodes', e);
    } finally {
      setIsLoading(false);
    }
  }, []);

  const loadSubgraph = useCallback(async (nodeId, depth = 2) => {
    setIsLoading(true);
    try {
      const data = await fetchSubgraph(nodeId, { depth });
      setNodes(data.nodes || []);
      setEdges(data.edges || []);
    } catch (e) {
      console.error('Failed to load subgraph', e);
    } finally {
      setIsLoading(false);
    }
  }, []);

  const loadStats = useCallback(async () => {
    try {
      const data = await fetchGraphStats();
      setStats(data);
    } catch (e) {
      console.error('Failed to load graph stats', e);
    }
  }, []);

  return {
    nodes, edges, stats, selectedNode, isLoading,
    setSelectedNode, loadNodes, loadSubgraph, loadStats,
  };
}
