import React, { useState, useEffect } from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { Music, LayoutDashboard, UploadCloud, BarChart2, LogOut, User, LogIn } from 'lucide-react';

export default function Navbar() {
  const navigate = useNavigate();
  const location = useLocation();
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [username, setUsername] = useState('');

  // Check auth state on mount and location changes
  useEffect(() => {
    const token = localStorage.getItem('access_token');
    setIsAuthenticated(!!token);
    // Simple mock/placeholder for user name, to be populated from user API later
    setUsername(localStorage.getItem('username') || 'Creator');
  }, [location]);

  const handleLogout = () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    localStorage.removeItem('username');
    setIsAuthenticated(false);
    navigate('/');
  };

  const isActive = (path) => location.pathname === path;

  return (
    <nav className="glass-panel" style={{
      position: 'sticky',
      top: 0,
      zIndex: 100,
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'space-between',
      padding: '16px 32px',
      borderTop: 'none',
      borderLeft: 'none',
      borderRight: 'none',
    }}>
      {/* Brand logo */}
      <Link to="/" style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
        <div style={{
          backgroundColor: 'var(--primary-accent)',
          color: '#000000',
          padding: '8px',
          borderRadius: '50%',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
        }}>
          <Music size={20} strokeWidth={2.5} />
        </div>
        <span style={{
          fontFamily: 'var(--font-display)',
          fontSize: '1.4rem',
          fontWeight: 800,
          letterSpacing: '-0.5px',
        }}>
          Now Play <span style={{ color: 'var(--primary-accent)', fontWeight: 500 }}>Creators</span>
        </span>
      </Link>

      {/* Navigation links */}
      <div style={{ display: 'flex', gap: '24px' }}>
        <Link 
          to="/" 
          className={isActive('/') ? 'glow-hover' : ''}
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '8px',
            color: isActive('/') ? 'var(--primary-accent)' : 'var(--text-muted)',
            fontWeight: isActive('/') ? '600' : '400',
            fontSize: '0.95rem',
          }}
        >
          Home
        </Link>
        
        {isAuthenticated && (
          <>
            <Link 
              to="/dashboard"
              className={isActive('/dashboard') ? 'glow-hover' : ''}
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '8px',
                color: isActive('/dashboard') ? 'var(--primary-accent)' : 'var(--text-muted)',
                fontWeight: isActive('/dashboard') ? '600' : '400',
                fontSize: '0.95rem',
              }}
            >
              <LayoutDashboard size={16} />
              Dashboard
            </Link>
            
            <Link 
              to="/upload"
              className={isActive('/upload') ? 'glow-hover' : ''}
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '8px',
                color: isActive('/upload') ? 'var(--primary-accent)' : 'var(--text-muted)',
                fontWeight: isActive('/upload') ? '600' : '400',
                fontSize: '0.95rem',
              }}
            >
              <UploadCloud size={16} />
              Upload
            </Link>
            
            <Link 
              to="/analytics"
              className={isActive('/analytics') ? 'glow-hover' : ''}
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '8px',
                color: isActive('/analytics') ? 'var(--primary-accent)' : 'var(--text-muted)',
                fontWeight: isActive('/analytics') ? '600' : '400',
                fontSize: '0.95rem',
              }}
            >
              <BarChart2 size={16} />
              Analytics
            </Link>
          </>
        )}
      </div>

      {/* User profile / actions */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
        {isAuthenticated ? (
          <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <div style={{
                width: '32px',
                height: '32px',
                borderRadius: '50%',
                backgroundColor: '#282828',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                border: '1px solid var(--border-color)'
              }}>
                <User size={16} className="text-muted" />
              </div>
              <span style={{ fontSize: '0.9rem', color: 'var(--text-muted)' }}>{username}</span>
            </div>
            
            <button 
              onClick={handleLogout}
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '8px',
                color: '#ff4444',
                fontSize: '0.9rem',
                fontWeight: 500,
                padding: '8px 16px',
                borderRadius: '8px',
                border: '1px solid rgba(255, 68, 68, 0.2)',
                backgroundColor: 'rgba(255, 68, 68, 0.05)',
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.backgroundColor = 'rgba(255, 68, 68, 0.15)';
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.backgroundColor = 'rgba(255, 68, 68, 0.05)';
              }}
            >
              <LogOut size={14} />
              Logout
            </button>
          </div>
        ) : (
          <Link 
            to="/login"
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '8px',
              color: 'var(--text-main)',
              fontSize: '0.9rem',
              fontWeight: 600,
              padding: '8px 20px',
              borderRadius: '500px',
              backgroundColor: '#1f1f1f',
              border: '1px solid var(--border-color)',
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.backgroundColor = '#2a2a2a';
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.backgroundColor = '#1f1f1f';
            }}
          >
            <LogIn size={14} />
            Login / Register
          </Link>
        )}
      </div>
    </nav>
  );
}
