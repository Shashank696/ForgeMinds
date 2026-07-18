import { useState, useEffect } from 'react';
import { FileText, Brain, Settings2, MessageSquare, Timer } from 'lucide-react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip as RechartsTooltip, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';
import { fetchAnalyticsOverview, fetchAnalyticsTrends } from '../services/api';
import { formatNumber } from '../utils/formatters';
import { DOCUMENT_CATEGORY_LABELS, ENTITY_TYPE_COLORS, ENTITY_TYPE_LABELS } from '../utils/constants';
import StatCard from '../components/dashboard/StatCard';
import ChartCard from '../components/analytics/ChartCard';
import TrendGraph from '../components/analytics/TrendGraph';
import AnalyticsDashboard from '../components/analytics/AnalyticsDashboard';

const tooltipStyle = { backgroundColor: 'var(--color-bg-card)', border: '1px solid var(--color-border)', borderRadius: 8, fontSize: 12 };

export default function AnalyticsPage() {
  const [data, setData] = useState(null);
  const [trends, setTrends] = useState([]);
  const [loading, setLoading] = useState(true);
  const [period, setPeriod] = useState('30d');

  useEffect(() => {
    const load = async () => {
      try {
        const [overview, trendData] = await Promise.all([fetchAnalyticsOverview(), fetchAnalyticsTrends({ period })]);
        setData(overview);
        setTrends(Array.isArray(trendData) ? trendData : []);
      } catch (e) { console.error(e); }
      setLoading(false);
    };
    load();
  }, [period]);

  if (loading) {
    return <div className="page"><div className="stats-grid">{[1,2,3,4,5].map(i => <div key={i} className="skeleton skeleton-card" />)}</div></div>;
  }

  const catData = data?.documents_by_category ? Object.entries(data.documents_by_category).map(([k, v]) => ({ name: DOCUMENT_CATEGORY_LABELS[k] || k, value: v })) : [];
  const entityData = data?.entities_by_type ? Object.entries(data.entities_by_type).map(([k, v]) => ({ name: ENTITY_TYPE_LABELS[k] || k, value: v, color: ENTITY_TYPE_COLORS[k] || '#666' })) : [];

  return (
    <div className="page animate-fade-in">
      <div className="page-header">
        <div>
          <h1>Analytics</h1>
          <p className="page-subtitle">Platform usage and knowledge base metrics</p>
        </div>
        <div className="flex gap-xs">
          {['7d', '30d', '90d'].map((p) => (
            <button key={p} className={`btn ${period === p ? 'btn-primary' : 'btn-secondary'} btn-sm`} onClick={() => setPeriod(p)}>{p}</button>
          ))}
        </div>
      </div>

      <div className="stats-grid">
        <StatCard title="Total Documents" value={formatNumber(data?.total_documents || 0)} icon={FileText} color="var(--color-accent-primary)" />
        <StatCard title="Total Entities" value={formatNumber(data?.total_entities || 0)} icon={Brain} color="var(--color-accent-secondary)" />
        <StatCard title="Equipment" value={formatNumber(data?.total_equipment || 0)} icon={Settings2} color="#f59e0b" />
        <StatCard title="AI Queries" value={formatNumber(data?.total_queries || 0)} icon={MessageSquare} color="var(--color-success)" />
        <StatCard title="Avg Response" value={`${data?.avg_response_time_ms || 0}ms`} icon={Timer} color="var(--color-info)" />
      </div>

      <div className="charts-grid" style={{ marginTop: 'var(--spacing-2xl)' }}>
        <ChartCard title="Documents by Category" subtitle="Distribution across document types">
          <ResponsiveContainer width="100%" height={280}>
            <BarChart data={catData}>
              <CartesianGrid strokeDasharray="3 3" stroke="var(--color-border)" />
              <XAxis dataKey="name" tick={{ fontSize: 10, fill: 'var(--color-text-muted)' }} angle={-25} textAnchor="end" height={70} />
              <YAxis tick={{ fontSize: 11, fill: 'var(--color-text-muted)' }} />
              <RechartsTooltip contentStyle={tooltipStyle} />
              <Bar dataKey="value" fill="var(--color-accent-primary)" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </ChartCard>

        <ChartCard title="Entities by Type" subtitle="Knowledge graph entity distribution">
          <ResponsiveContainer width="100%" height={280}>
            <PieChart>
              <Pie data={entityData} dataKey="value" nameKey="name" cx="50%" cy="50%" innerRadius={60} outerRadius={90} paddingAngle={2}>
                {entityData.map((entry, i) => <Cell key={i} fill={entry.color} />)}
              </Pie>
              <RechartsTooltip contentStyle={tooltipStyle} />
            </PieChart>
          </ResponsiveContainer>
        </ChartCard>
      </div>

      <div style={{ marginTop: 'var(--spacing-2xl)' }}>
        <ChartCard title="Platform Trends" subtitle="Document ingestion, queries, and entity growth over time">
          <TrendGraph data={trends} />
        </ChartCard>
      </div>

      <AnalyticsDashboard data={data} />
    </div>
  );
}
