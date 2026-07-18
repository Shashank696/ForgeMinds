import { useEffect } from 'react';
import useKnowledgeGraph from '../hooks/useKnowledgeGraph';
import GraphViewer from '../components/knowledge-graph/GraphViewer';
import GraphFilters from '../components/knowledge-graph/GraphFilters';
import NodeDetail from '../components/knowledge-graph/NodeDetail';
import LoadingSpinner from '../components/common/LoadingSpinner';
import { ENTITY_TYPE_COLORS, ENTITY_TYPE_LABELS } from '../utils/constants';
import { formatNumber } from '../utils/formatters';

export default function KnowledgeGraphPage() {
  const { nodes, edges, stats, selectedNode, isLoading, setSelectedNode, loadNodes, loadSubgraph, loadStats } = useKnowledgeGraph();

  useEffect(() => {
    loadNodes();
    loadStats();
  }, [loadNodes, loadStats]);

  const handleFilter = ({ search, types }) => {
    loadNodes({ search, entity_types: types?.join(',') });
  };

  return (
    <div className="kg-layout">
      <div className="kg-canvas">
        {isLoading ? (
          <LoadingSpinner message="Loading knowledge graph..." />
        ) : (
          <>
            <GraphViewer nodes={nodes} edges={edges} onNodeClick={(n) => setSelectedNode(n)} />
            <div className="kg-stats-bar">
              <span className="badge badge-primary">{formatNumber(stats?.total_nodes || nodes.length)} nodes</span>
              <span className="badge badge-secondary">{formatNumber(stats?.total_edges || edges.length)} edges</span>
            </div>
          </>
        )}
      </div>

      <div className="kg-panel">
        <h3 style={{ marginBottom: 'var(--spacing-lg)' }}>Knowledge Graph</h3>
        <GraphFilters onFilter={handleFilter} stats={stats} />

        <div style={{ marginTop: 'var(--spacing-lg)' }}>
          <p className="text-xs font-semibold text-muted" style={{ textTransform: 'uppercase', marginBottom: 'var(--spacing-sm)' }}>Legend</p>
          <div className="kg-legend">
            {Object.entries(ENTITY_TYPE_LABELS).map(([key, label]) => (
              <div key={key} className="kg-legend-item">
                <span className="kg-legend-dot" style={{ background: ENTITY_TYPE_COLORS[key] }} />
                {label}
              </div>
            ))}
          </div>
        </div>

        <NodeDetail node={selectedNode} onClose={() => setSelectedNode(null)} />
      </div>
    </div>
  );
}
