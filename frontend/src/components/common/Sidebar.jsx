import { useState, useEffect } from 'react';
import { NavLink } from 'react-router-dom';
import { LayoutDashboard, FileText, MessageSquare, GitBranch, Search, Wrench, Shield, BarChart3, Settings } from 'lucide-react';
import { NAV_SECTIONS } from '../../utils/constants';

const iconMap = { LayoutDashboard, FileText, MessageSquare, GitBranch, Search, Wrench, Shield, BarChart3, Settings };

export default function Sidebar() {
  const [isOpen, setIsOpen] = useState(false);

  useEffect(() => {
    const handler = () => setIsOpen((v) => !v);
    window.addEventListener('toggle-sidebar', handler);
    return () => window.removeEventListener('toggle-sidebar', handler);
  }, []);

  const closeSidebar = () => setIsOpen(false);

  return (
    <>
      {isOpen && <div className="sidebar-mobile-overlay" onClick={closeSidebar} />}
      <nav className={`sidebar ${isOpen ? 'open' : ''}`}>
        {NAV_SECTIONS.map((section) => (
          <div className="sidebar-section" key={section.label}>
            <div className="sidebar-section-label">{section.label}</div>
            {section.items.map((item) => {
              const Icon = iconMap[item.icon];
              return (
                <NavLink
                  key={item.path}
                  to={item.path}
                  end={item.path === '/'}
                  className={({ isActive }) => `sidebar-link ${isActive ? 'active' : ''}`}
                  onClick={closeSidebar}
                >
                  {Icon && <Icon size={18} />}
                  <span>{item.label}</span>
                </NavLink>
              );
            })}
          </div>
        ))}
        <div className="sidebar-footer">
          <NavLink to="/settings" className={({ isActive }) => `sidebar-link ${isActive ? 'active' : ''}`} onClick={closeSidebar}>
            <Settings size={18} />
            <span>Settings</span>
          </NavLink>
        </div>
      </nav>
    </>
  );
}
