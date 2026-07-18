import { useContext } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Brain, Search, Sun, Moon, Menu } from 'lucide-react';
import { ThemeContext } from '../../context/ThemeContext';

export default function Navbar() {
  const { theme, toggleTheme } = useContext(ThemeContext);
  const navigate = useNavigate();

  const handleSearch = (e) => {
    if (e.key === 'Enter' && e.target.value.trim()) {
      navigate(`/search?q=${encodeURIComponent(e.target.value.trim())}`);
      e.target.value = '';
    }
  };

  return (
    <div className="navbar">
      <div className="flex items-center gap-md">
        <button className="btn btn-icon btn-ghost" style={{ display: 'none' }}
          id="mobile-menu-btn"
          onClick={() => window.dispatchEvent(new CustomEvent('toggle-sidebar'))}>
          <Menu size={20} />
        </button>
        <Link to="/" className="navbar-brand">
          <Brain size={24} />
          <span>Forge<span style={{ color: 'var(--color-accent-primary)' }}>Minds</span></span>
        </Link>
      </div>

      <div className="navbar-search">
        <Search size={16} />
        <input type="text" placeholder="Search documents, equipment, knowledge..." onKeyDown={handleSearch} />
      </div>

      <div className="navbar-actions">
        <button className="btn btn-icon btn-ghost" onClick={toggleTheme} title={`Switch to ${theme === 'dark' ? 'light' : 'dark'} mode`}>
          {theme === 'dark' ? <Sun size={18} /> : <Moon size={18} />}
        </button>
        <div className="navbar-avatar">U</div>
      </div>

      <style>{`
        @media (max-width: 768px) {
          #mobile-menu-btn { display: flex !important; }
        }
      `}</style>
    </div>
  );
}
