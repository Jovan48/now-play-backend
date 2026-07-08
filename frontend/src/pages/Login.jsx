import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { ShieldCheck, Mail, Lock, User } from 'lucide-react';

export default function Login() {
  const navigate = useNavigate();
  const [isRegister, setIsRegister] = useState(false);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [username, setUsername] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    // Simulate stateless JWT generation and write to localStorage
    localStorage.setItem('access_token', 'mock-access-token-jwt-string');
    localStorage.setItem('refresh_token', 'mock-refresh-token-jwt-string');
    localStorage.setItem('username', isRegister ? username : email.split('@')[0]);
    navigate('/dashboard');
  };

  return (
    <div style={{
      maxWidth: '450px',
      margin: '80px auto 140px auto',
      padding: '0 24px',
      width: '100%',
    }}>
      <div className="glass-panel" style={{
        padding: '40px 32px',
        borderRadius: '16px',
        display: 'flex',
        flexDirection: 'column',
        gap: '28px',
      }}>
        {/* Title */}
        <div style={{ textAlign: 'center', display: 'flex', flexDirection: 'column', gap: '8px' }}>
          <h2 style={{ fontFamily: 'var(--font-display)', fontSize: '2rem', fontWeight: 800 }}>
            {isRegister ? 'Create Account' : 'Welcome Back'}
          </h2>
          <p style={{ color: 'var(--text-muted)', fontSize: '0.88rem' }}>
            {isRegister ? 'Join Now Play for Creators' : 'Sign in to manage your music catalog'}
          </p>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
          {isRegister && (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
              <label style={{ fontSize: '0.85rem', fontWeight: 600, color: 'var(--text-muted)' }}>Username</label>
              <div style={{
                display: 'flex',
                alignItems: 'center',
                gap: '12px',
                backgroundColor: '#161616',
                border: '1px solid var(--border-color)',
                borderRadius: '8px',
                padding: '10px 16px',
              }}>
                <User size={16} style={{ color: 'var(--text-muted)' }} />
                <input 
                  type="text" 
                  placeholder="Your creator name" 
                  required
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                  style={{
                    background: 'none',
                    border: 'none',
                    outline: 'none',
                    color: 'var(--text-main)',
                    fontSize: '0.9rem',
                    width: '100%',
                  }}
                />
              </div>
            </div>
          )}

          <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
            <label style={{ fontSize: '0.85rem', fontWeight: 600, color: 'var(--text-muted)' }}>Email address</label>
            <div style={{
              display: 'flex',
              alignItems: 'center',
              gap: '12px',
              backgroundColor: '#161616',
              border: '1px solid var(--border-color)',
              borderRadius: '8px',
              padding: '10px 16px',
            }}>
              <Mail size={16} style={{ color: 'var(--text-muted)' }} />
              <input 
                type="email" 
                placeholder="creator@nowplay.com" 
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                style={{
                  background: 'none',
                  border: 'none',
                  outline: 'none',
                  color: 'var(--text-main)',
                  fontSize: '0.9rem',
                  width: '100%',
                }}
              />
            </div>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
            <label style={{ fontSize: '0.85rem', fontWeight: 600, color: 'var(--text-muted)' }}>Password</label>
            <div style={{
              display: 'flex',
              alignItems: 'center',
              gap: '12px',
              backgroundColor: '#161616',
              border: '1px solid var(--border-color)',
              borderRadius: '8px',
              padding: '10px 16px',
            }}>
              <Lock size={16} style={{ color: 'var(--text-muted)' }} />
              <input 
                type="password" 
                placeholder="••••••••" 
                required
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                style={{
                  background: 'none',
                  border: 'none',
                  outline: 'none',
                  color: 'var(--text-main)',
                  fontSize: '0.9rem',
                  width: '100%',
                }}
              />
            </div>
          </div>

          <button 
            type="submit" 
            className="spotify-btn"
            style={{
              justifyContent: 'center',
              width: '100%',
              marginTop: '10px',
            }}
          >
            {isRegister ? 'Register' : 'Login'}
          </button>
        </form>

        {/* Toggle */}
        <div style={{ textAlign: 'center', fontSize: '0.85rem', color: 'var(--text-muted)' }}>
          {isRegister ? 'Already have an account?' : "Don't have a creator account?"}{' '}
          <button 
            onClick={() => setIsRegister(!isRegister)}
            style={{ color: 'var(--primary-accent)', fontWeight: 600 }}
          >
            {isRegister ? 'Login' : 'Register here'}
          </button>
        </div>
      </div>
    </div>
  );
}
