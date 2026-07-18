import { useRef, useEffect, useState, useCallback } from 'react';
import ForceGraph2D from 'react-force-graph-2d';
import { ENTITY_TYPE_COLORS } from '../../utils/constants';

export default function GraphViewer({ nodes = [], edges = [], onNodeClick }) {
  const containerRef = useRef(null);
  const graphRef = useRef(null);
  const [dimensions, setDimensions] = useState({ width: 800, height: 600 });

  useEffect(() => {
    const el = containerRef.current;
    if (!el) return;
    const update = () => setDimensions({ width: el.clientWidth, height: el.clientHeight });
    update();
    const obs = new ResizeObserver(update);
    obs.observe(el);
    return () => obs.disconnect();
  }, []);

  const graphData = {
    nodes: nodes.map((n) => ({ ...n, color: ENTITY_TYPE_COLORS[n.entity_type] || '#666' })),
    links: edges.map((e) => ({ source: e.source_id, target: e.target_id, label: e.relationship_type })),
  };

  const paintNode = useCallback((node, ctx) => {
    const r = Math.max(4, Math.min(8, (node.connection_count || 1)));
    ctx.beginPath();
    ctx.arc(node.x, node.y, r, 0, 2 * Math.PI);
    ctx.fillStyle = node.color;
    ctx.fill();
    ctx.font = '3px Inter, sans-serif';
    ctx.fillStyle = 'rgba(255,255,255,0.8)';
    ctx.textAlign = 'center';
    ctx.fillText(node.name || '', node.x, node.y + r + 4);
  }, []);

  return (
    <div ref={containerRef} style={{ width: '100%', height: '100%', position: 'relative' }}>
      <ForceGraph2D
        ref={graphRef}
        graphData={graphData}
        width={dimensions.width}
        height={dimensions.height}
        backgroundColor="transparent"
        nodeCanvasObject={paintNode}
        nodePointerAreaPaint={(node, color, ctx) => {
          ctx.beginPath();
          ctx.arc(node.x, node.y, 10, 0, 2 * Math.PI);
          ctx.fillStyle = color;
          ctx.fill();
        }}
        linkColor={() => 'rgba(99,102,241,0.15)'}
        linkWidth={1}
        onNodeClick={(node) => onNodeClick?.(node)}
        cooldownTicks={100}
        enableNodeDrag={true}
      />
    </div>
  );
}
