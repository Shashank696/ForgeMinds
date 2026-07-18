import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import Navbar from './components/common/Navbar';
import Sidebar from './components/common/Sidebar';
import DashboardPage from './pages/DashboardPage';
import DocumentsPage from './pages/DocumentsPage';
import ChatPage from './pages/ChatPage';
import KnowledgeGraphPage from './pages/KnowledgeGraphPage';
import MaintenancePage from './pages/MaintenancePage';
import CompliancePage from './pages/CompliancePage';
import AnalyticsPage from './pages/AnalyticsPage';
import SearchPage from './pages/SearchPage';
import LoginPage from './pages/LoginPage';
import EquipmentDetailPage from './pages/EquipmentDetailPage';

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

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<LoginPage />} />
        
        <Route path="/" element={<AppLayout><DashboardPage /></AppLayout>} />
        <Route path="/documents" element={<AppLayout><DocumentsPage /></AppLayout>} />
        <Route path="/chat" element={<AppLayout><ChatPage /></AppLayout>} />
        <Route path="/knowledge-graph" element={<AppLayout><KnowledgeGraphPage /></AppLayout>} />
        <Route path="/maintenance" element={<AppLayout><MaintenancePage /></AppLayout>} />
        <Route path="/compliance" element={<AppLayout><CompliancePage /></AppLayout>} />
        <Route path="/analytics" element={<AppLayout><AnalyticsPage /></AppLayout>} />
        <Route path="/search" element={<AppLayout><SearchPage /></AppLayout>} />
        <Route path="/equipment/:id" element={<AppLayout><EquipmentDetailPage /></AppLayout>} />
        
        <Route path="*" element={<Navigate to="/" />} />
      </Routes>
    </BrowserRouter>
  );
}
