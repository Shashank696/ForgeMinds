import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { Toaster } from 'react-hot-toast';
import { AuthProvider } from './context/AuthContext';
import { ThemeProvider } from './context/ThemeContext';
import Navbar from './components/common/Navbar';
import Sidebar from './components/common/Sidebar';
import DashboardPage from './pages/DashboardPage';
import DocumentsPage from './pages/DocumentsPage';
import DocumentDetailPage from './pages/DocumentDetailPage';
import ChatPage from './pages/ChatPage';
import KnowledgeGraphPage from './pages/KnowledgeGraphPage';
import MaintenancePage from './pages/MaintenancePage';
import CompliancePage from './pages/CompliancePage';
import AnalyticsPage from './pages/AnalyticsPage';
import SearchPage from './pages/SearchPage';
import LoginPage from './pages/LoginPage';
import EquipmentDetailPage from './pages/EquipmentDetailPage';
import SettingsPage from './pages/SettingsPage';
import RCAPage from './pages/RCAPage';
import LandingPage from './pages/LandingPage';
import './App.css';

function AppLayout({ children }) {
  return (
    <div className="app-layout">
      <Navbar />
      <div className="app-body">
        <Sidebar />
        <main className="app-main">
          {children}
        </main>
      </div>
    </div>
  );
}

function App() {
  return (
    <ThemeProvider>
      <AuthProvider>
        <BrowserRouter>
          <Routes>
            {/* Standalone pages (no sidebar/navbar) */}
            <Route path="/landing" element={<LandingPage />} />
            <Route path="/login" element={<LoginPage />} />

            {/* App pages (with layout) */}
            <Route path="/" element={<AppLayout><DashboardPage /></AppLayout>} />
            <Route path="/documents" element={<AppLayout><DocumentsPage /></AppLayout>} />
            <Route path="/documents/:id" element={<AppLayout><DocumentDetailPage /></AppLayout>} />
            <Route path="/chat" element={<AppLayout><ChatPage /></AppLayout>} />
            <Route path="/knowledge-graph" element={<AppLayout><KnowledgeGraphPage /></AppLayout>} />
            <Route path="/maintenance" element={<AppLayout><MaintenancePage /></AppLayout>} />
            <Route path="/maintenance/rca" element={<AppLayout><RCAPage /></AppLayout>} />
            <Route path="/compliance" element={<AppLayout><CompliancePage /></AppLayout>} />
            <Route path="/analytics" element={<AppLayout><AnalyticsPage /></AppLayout>} />
            <Route path="/search" element={<AppLayout><SearchPage /></AppLayout>} />
            <Route path="/equipment/:id" element={<AppLayout><EquipmentDetailPage /></AppLayout>} />
            <Route path="/settings" element={<AppLayout><SettingsPage /></AppLayout>} />

            {/* Fallback */}
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>

          <Toaster
            position="top-right"
            toastOptions={{
              style: {
                background: 'var(--color-bg-card)',
                color: 'var(--color-text-primary)',
                border: '1px solid var(--color-border)',
                borderRadius: 'var(--radius-md)',
                fontSize: 'var(--font-sm)',
              },
            }}
          />
        </BrowserRouter>
      </AuthProvider>
    </ThemeProvider>
  );
}

export default App;
