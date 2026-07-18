import React from 'react';
import { Link } from 'react-router-dom';
import {
  Brain, FileText, GitBranch, MessageSquare, Wrench, Shield, BookOpen,
  ArrowRight, Zap, ChevronRight
} from 'lucide-react';
import { APP_NAME } from '../utils/constants';

const features = [
  {
    icon: <FileText size={28} />,
    title: 'Universal Document Ingestion',
    description: 'Ingest and process P&IDs, SOPs, maintenance manuals, incident reports, and engineering specs from any format.',
    color: '#3b82f6',
  },
  {
    icon: <GitBranch size={28} />,
    title: 'Knowledge Graph',
    description: 'Automatically build an interconnected graph linking equipment, procedures, failures, and compliance requirements.',
    color: '#8b5cf6',
  },
  {
    icon: <MessageSquare size={28} />,
    title: 'AI Expert Copilot',
    description: 'Ask complex engineering questions and get context-aware answers grounded in your organization\'s knowledge base.',
    color: '#06b6d4',
  },
  {
    icon: <Wrench size={28} />,
    title: 'Maintenance Intelligence',
    description: 'Predict equipment failures, optimize maintenance schedules, and perform root cause analysis with AI-driven insights.',
    color: '#f59e0b',
  },
  {
    icon: <Shield size={28} />,
    title: 'Compliance Intelligence',
    description: 'Automatically track regulatory requirements, identify compliance gaps, and generate audit-ready documentation.',
    color: '#10b981',
  },
  {
    icon: <BookOpen size={28} />,
    title: 'Lessons Learned',
    description: 'Capture institutional knowledge from incidents and maintenance events to prevent recurrence and accelerate onboarding.',
    color: '#ef4444',
  },
];

const LandingPage = () => {
  return (
    <div className="landing-page">
      <nav className="landing-nav">
        <div className="landing-nav-brand">
          <Brain size={28} />
          <span>{APP_NAME}</span>
        </div>
        <div className="landing-nav-actions">
          <Link to="/login" className="btn btn-ghost">Sign In</Link>
          <Link to="/login" className="btn btn-primary">Get Started</Link>
        </div>
      </nav>

      <section className="landing-hero">
        <div className="landing-hero-content animate-fade-in-up">
          <div className="landing-hero-badge">
            <Zap size={14} />
            <span>AI-Powered Industrial Intelligence</span>
          </div>
          <h1 className="landing-hero-title">
            <span className="gradient-text">{APP_NAME}</span>
          </h1>
          <p className="landing-hero-subtitle">
            Transform your industrial knowledge into actionable intelligence. Unify documents,
            predict failures, ensure compliance, and empower your team with AI-driven insights
            across your entire operation.
          </p>
          <div className="landing-hero-actions">
            <Link to="/login" className="btn btn-primary btn-lg">
              Get Started
              <ArrowRight size={18} />
            </Link>
            <Link to="/" className="btn btn-secondary btn-lg">
              Explore Dashboard
              <ChevronRight size={18} />
            </Link>
          </div>
        </div>
        <div className="landing-hero-glow" />
      </section>

      <section className="landing-features">
        <div className="landing-features-header animate-fade-in-up">
          <h2>Everything You Need for Industrial Intelligence</h2>
          <p>Six powerful modules working together to transform how your organization manages knowledge, maintenance, and compliance.</p>
        </div>
        <div className="landing-features-grid">
          {features.map((feature, index) => (
            <div
              className="landing-feature-card animate-fade-in-up"
              key={feature.title}
              style={{ animationDelay: `${index * 80}ms` }}
            >
              <div
                className="landing-feature-icon"
                style={{ background: feature.color + '18', color: feature.color }}
              >
                {feature.icon}
              </div>
              <h3>{feature.title}</h3>
              <p>{feature.description}</p>
            </div>
          ))}
        </div>
      </section>

      <section className="landing-cta">
        <div className="landing-cta-content animate-fade-in-up">
          <h2>Ready to Transform Your Operations?</h2>
          <p>Join leading industrial organizations using ForgeMinds to unlock the full value of their engineering knowledge.</p>
          <Link to="/login" className="btn btn-primary btn-lg">
            Start Now <ArrowRight size={18} />
          </Link>
        </div>
      </section>

      <footer className="landing-footer">
        <div className="landing-footer-content">
          <div className="landing-footer-brand">
            <Brain size={20} />
            <span>{APP_NAME}</span>
          </div>
          <p className="landing-footer-copy">
            &copy; {new Date().getFullYear()} {APP_NAME}. Industrial Knowledge Intelligence Platform.
          </p>
        </div>
      </footer>
    </div>
  );
};

export default LandingPage;
