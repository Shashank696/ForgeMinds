import { useState, useEffect } from 'react';
import { FileText, Brain, Settings2, MessageSquare, Timer, Shield } from 'lucide-react';
import { BarChart, Bar, LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip as RechartsTooltip, ResponsiveContainer } from 'recharts';
import { fetchAnalyticsOverview, fetchAnalyticsTrends } from '../services/api';
import { formatNumber } from '../utils/formatters';
import { DOCUMENT_CATEGORY_LABELS } from '../utils/constants';
import StatCard from '../components/dashboard/StatCard';
import RecentActivity from '../components/dashboard/RecentActivity';
import QuickActions from '../components/dashboard/QuickActions';
import SystemHealth from '../components/dashboard/SystemHealth';

const tooltipStyle = { backgroundColor: 'var(--color-bg-card)', border: '1px solid var(--color-border)', borderRadius: 8, fontSize: 12 };

export default function DashboardPage() {
  const [data, setData] = useState(null);
  const [trends, setTrends] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const load = async () => {
      try {
        const [analytics, trendData] = await Promise.all([fetchAnalyticsOverview(), fetchAnalyticsTrends({ metric: 'all', period: '30d' })]);
        setData(analytics);
        setTrends(Array.isArray(trendData) ? trendData : []);
      } catch (e) { console.error(e); }
      setLoading(false);
    };
    load();
  }, []);

  if (loading) {
    return (
      <div className="page">
        <div className="skeleton skeleton-title" />
        <div className="stats-grid" style={{ marginTop: 'var(--spacing-xl)' }}>
          {[1,2,3,4,5,6].map(i => <div key={i} className="skeleton skeleton-card" />)}
        </div>
      </div>
    );
  }

  const catData = data?.documents_by_category
    ? Object.entries(data.documents_by_category).slice(0, 6).map(([k, v]) => ({ name: DOCUMENT_CATEGORY_LABELS[k] || k, value: v }))
    : [];

  return (
    <div className="page animate-fade-in">
      <div className="page-header">
        <div>
          <h1>Dashboard</h1>
          <p className="page-subtitle">Industrial Knowledge Intelligence Overview</p>
        </div>
      </div>

      <div className="stats-grid">
        <StatCard title="Documents" value={formatNumber(data?.total_documents || 0)} icon={FileText} trend={12} color="var(--color-accent-primary)" />
        <StatCard title="Entities" value={formatNumber(data?.total_entities || 0)} icon={Brain} trend={8} color="var(--color-accent-secondary)" />
        <StatCard title="Equipment" value={formatNumber(data?.total_equipment || 0)} icon={Settings2} color="#f59e0b" />
        <StatCard title="AI Queries" value={formatNumber(data?.total_queries || 0)} icon={MessageSquare} trend={15} color="var(--color-success)" />
        <StatCard title="Avg Response" value={`${data?.avg_response_time_ms || 0}ms`} icon={Timer} color="var(--color-info)" />
        <StatCard title="Compliance" value="82%" icon={Shield} color="var(--color-warning)" subtitle="Overall score" />
      </div>

      <div className="charts-grid" style={{ marginTop: 'var(--spacing-2xl)' }}>
        <div className="card">
          <h4 className="section-title">Documents by Category</h4>
          <ResponsiveContainer width="100%" height={260}>
            <BarChart data={catData}>
              <CartesianGrid strokeDasharray="3 3" stroke="var(--color-border)" />
              <XAxis dataKey="name" tick={{ fontSize: 11, fill: 'var(--color-text-muted)' }} angle={-20} textAnchor="end" height={60} />
              <YAxis tick={{ fontSize: 11, fill: 'var(--color-text-muted)' }} />
              <RechartsTooltip contentStyle={tooltipStyle} />
              <Bar dataKey="value" fill="var(--color-accent-primary)" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
        <div className="card">
          <h4 className="section-title">Platform Trends</h4>
          <ResponsiveContainer width="100%" height={260}>
            <LineChart data={trends}>
              <CartesianGrid strokeDasharray="3 3" stroke="var(--color-border)" />
              <XAxis dataKey="date" tick={{ fontSize: 11, fill: 'var(--color-text-muted)' }} />
              <YAxis tick={{ fontSize: 11, fill: 'var(--color-text-muted)' }} />
              <RechartsTooltip contentStyle={tooltipStyle} />
              <Line type="monotone" dataKey="documents" stroke="var(--color-accent-primary)" strokeWidth={2} dot={false} />
              <Line type="monotone" dataKey="queries" stroke="var(--color-accent-secondary)" strokeWidth={2} dot={false} />
              <Line type="monotone" dataKey="entities" stroke="var(--color-success)" strokeWidth={2} dot={false} />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>

      <div className="grid grid-2" style={{ marginTop: 'var(--spacing-2xl)', gap: 'var(--spacing-xl)' }}>
        <div>
          <h4 className="section-title">Quick Actions</h4>
          <QuickActions />
        </div>
        <div className="flex flex-col gap-xl">
          <div className="card">
            <h4 className="section-title" style={{ marginBottom: 'var(--spacing-md)' }}>Recent Activity</h4>
            <RecentActivity activities={data?.recent_activity || []} />
          </div>
          <SystemHealth />
        </div>
      </div>
    </div>
  );
}
