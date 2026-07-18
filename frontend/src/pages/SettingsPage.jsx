import { useState, useContext } from 'react';
import { ThemeContext } from '../context/ThemeContext';
import { checkHealth } from '../services/api';
import { APP_NAME } from '../utils/constants';
import { Sun, Moon, Activity } from 'lucide-react';

export default function SettingsPage() {
  const { theme, toggleTheme } = useContext(ThemeContext);
  const [healthStatus, setHealthStatus] = useState(null);
  const [checking, setChecking] = useState(false);

  const handleHealthCheck = async () => {
    setChecking(true);
    try {
      const res = await checkHealth();
      setHealthStatus(res.status || 'ok');
    } catch (e) {
      setHealthStatus('error');
    }
    setChecking(false);
  };

  return (
    <div className="page animate-fade-in">
      <div className="page-header">
        <h1>Settings</h1>
      </div>

      <div className="flex flex-col gap-xl" style={{ maxWidth: 600 }}>
        <div className="card">
          <h4 style={{ marginBottom: 'var(--spacing-md)' }}>Appearance</h4>
          <div className="flex justify-between items-center">
            <div className="flex items-center gap-md">
              {theme === 'dark' ? <Moon size={18} /> : <Sun size={18} />}
              <div>
                <p className="font-medium text-sm">Theme</p>
                <p className="text-xs text-muted">{theme === 'dark' ? 'Dark mode' : 'Light mode'}</p>
              </div>
            </div>
            <button className="btn btn-secondary btn-sm" onClick={toggleTheme}>
              Switch to {theme === 'dark' ? 'Light' : 'Dark'}
            </button>
          </div>
        </div>

        <div className="card">
          <h4 style={{ marginBottom: 'var(--spacing-md)' }}>API Configuration</h4>
          <div className="form-group">
            <label className="form-label">Base URL</label>
            <input className="form-input" value="/api" readOnly style={{ opacity: 0.7 }} />
          </div>
        </div>

        <div className="card">
          <h4 style={{ marginBottom: 'var(--spacing-md)' }}>System Information</h4>
          <div className="grid grid-2 gap-md">
            <div><p className="text-xs text-muted">Application</p><p className="font-medium text-sm">{APP_NAME}</p></div>
            <div><p className="text-xs text-muted">Version</p><p className="font-medium text-sm">1.0.0</p></div>
            <div><p className="text-xs text-muted">Frontend</p><p className="font-medium text-sm">React + Vite</p></div>
            <div><p className="text-xs text-muted">Backend</p><p className="font-medium text-sm">FastAPI + Python</p></div>
          </div>
        </div>

        <div className="card">
          <h4 style={{ marginBottom: 'var(--spacing-md)' }}>Health Check</h4>
          <div className="flex items-center gap-md">
            <button className="btn btn-secondary btn-sm" onClick={handleHealthCheck} disabled={checking}>
              <Activity size={14} /> {checking ? 'Checking...' : 'Check API Health'}
            </button>
            {healthStatus && (
              <div className="flex items-center gap-sm">
                <span className={`status-dot ${healthStatus === 'ok' ? 'online' : 'offline'}`} />
                <span className="text-sm">{healthStatus === 'ok' ? 'All systems operational' : 'Service unavailable'}</span>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
