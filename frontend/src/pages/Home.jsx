import React from 'react';
import { Link } from 'react-router-dom';
import { Music, ShieldCheck, BarChart3, Radio } from 'lucide-react';

export default function Home() {
  const token = localStorage.getItem('access_token');

  return (
    <div style={{
      maxWidth: '1200px',
      margin: '0 auto',
      padding: '60px 24px 140px 24px',
      display: 'flex',
      flexDirection: 'column',
      gap: '80px',
    }}>
      {/* Hero Welcome */}
      <section style={{
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        textAlign: 'center',
        gap: '24px',
        marginTop: '20px',
      }}>
        <div style={{
          backgroundColor: 'rgba(29, 185, 84, 0.1)',
          color: 'var(--primary-accent)',
          border: '1px solid rgba(29, 185, 84, 0.2)',
          padding: '8px 16px',
          borderRadius: '500px',
          fontSize: '0.85rem',
          fontWeight: 600,
          letterSpacing: '1px',
          textTransform: 'uppercase',
        }}>
          Now Play for Creators
        </div>
        
        <h1 style={{
          fontFamily: 'var(--font-display)',
          fontSize: '3.8rem',
          fontWeight: 800,
          lineHeight: 1.1,
          letterSpacing: '-1.5px',
          maxWidth: '800px',
        }}>
          Manage & Distribute Your <br/>
          <span style={{
            backgroundImage: 'linear-gradient(90deg, #1DB954 0%, #1ed760 100%)',
            WebkitBackgroundClip: 'text',
            WebkitTextFillColor: 'transparent',
          }}>Music Catalog</span> Effortlessly
        </h1>
        
        <p style={{
          fontSize: '1.2rem',
          color: 'var(--text-muted)',
          maxWidth: '600px',
          lineHeight: 1.6,
        }}>
          The ultimate platform for modern creators. Upload MP3 tracks up to 50MB, parse metadata automatically, track listener metrics, and Jamendo seed files.
        </p>

        <div style={{ display: 'flex', gap: '16px', marginTop: '16px' }}>
          {token ? (
            <Link to="/dashboard" className="spotify-btn">
              Go to Dashboard
            </Link>
          ) : (
            <>
              <Link to="/login" className="spotify-btn">
                Start for Free
              </Link>
              <Link to="/dashboard" style={{
                display: 'inline-flex',
                alignItems: 'center',
                padding: '12px 32px',
                fontWeight: 600,
                borderRadius: '500px',
                border: '1px solid var(--border-color)',
                backgroundColor: 'transparent',
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.backgroundColor = '#181818';
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.backgroundColor = 'transparent';
              }}
              >
                Learn More
              </Link>
            </>
          )}
        </div>
      </section>

      {/* Feature Grid */}
      <section style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))',
        gap: '24px',
      }}>
        {/* Card 1 */}
        <div className="glass-panel" style={{
          padding: '32px',
          borderRadius: '16px',
          display: 'flex',
          flexDirection: 'column',
          gap: '16px',
          transition: 'var(--transition-smooth)',
        }}
        onMouseEnter={(e) => {
          e.currentTarget.style.transform = 'translateY(-4px)';
          e.currentTarget.style.borderColor = 'rgba(29, 185, 84, 0.3)';
        }}
        onMouseLeave={(e) => {
          e.currentTarget.style.transform = 'translateY(0)';
          e.currentTarget.style.borderColor = 'var(--glass-border)';
        }}
        >
          <div style={{
            color: 'var(--primary-accent)',
            backgroundColor: 'rgba(29, 185, 84, 0.1)',
            width: '48px',
            height: '48px',
            borderRadius: '12px',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
          }}>
            <Music size={24} />
          </div>
          <h3 style={{ fontSize: '1.25rem', fontWeight: 600 }}>Catalog Management</h3>
          <p style={{ color: 'var(--text-muted)', fontSize: '0.92rem', lineHeight: 1.5 }}>
            Upload high-fidelity MP3 tracks. Set artists, albums, genres, and track positions in albums.
          </p>
        </div>

        {/* Card 2 */}
        <div className="glass-panel" style={{
          padding: '32px',
          borderRadius: '16px',
          display: 'flex',
          flexDirection: 'column',
          gap: '16px',
          transition: 'var(--transition-smooth)',
        }}
        onMouseEnter={(e) => {
          e.currentTarget.style.transform = 'translateY(-4px)';
          e.currentTarget.style.borderColor = 'rgba(29, 185, 84, 0.3)';
        }}
        onMouseLeave={(e) => {
          e.currentTarget.style.transform = 'translateY(0)';
          e.currentTarget.style.borderColor = 'var(--glass-border)';
        }}
        >
          <div style={{
            color: '#1e90ff',
            backgroundColor: 'rgba(30, 144, 255, 0.1)',
            width: '48px',
            height: '48px',
            borderRadius: '12px',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
          }}>
            <ShieldCheck size={24} />
          </div>
          <h3 style={{ fontSize: '1.25rem', fontWeight: 600 }}>ID3 Auto Parsing</h3>
          <p style={{ color: 'var(--text-muted)', fontSize: '0.92rem', lineHeight: 1.5 }}>
            Our backend automatically reads ID3 metadata tags (Title, Artist, Album, Genre, Track Number) from your MP3 uploads.
          </p>
        </div>

        {/* Card 3 */}
        <div className="glass-panel" style={{
          padding: '32px',
          borderRadius: '16px',
          display: 'flex',
          flexDirection: 'column',
          gap: '16px',
          transition: 'var(--transition-smooth)',
        }}
        onMouseEnter={(e) => {
          e.currentTarget.style.transform = 'translateY(-4px)';
          e.currentTarget.style.borderColor = 'rgba(29, 185, 84, 0.3)';
        }}
        onMouseLeave={(e) => {
          e.currentTarget.style.transform = 'translateY(0)';
          e.currentTarget.style.borderColor = 'var(--glass-border)';
        }}
        >
          <div style={{
            color: '#ff4444',
            backgroundColor: 'rgba(255, 68, 68, 0.1)',
            width: '48px',
            height: '48px',
            borderRadius: '12px',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
          }}>
            <BarChart3 size={24} />
          </div>
          <h3 style={{ fontSize: '1.25rem', fontWeight: 600 }}>Real-time Analytics</h3>
          <p style={{ color: 'var(--text-muted)', fontSize: '0.92rem', lineHeight: 1.5 }}>
            Track total plays, unique listeners, and top tracks. Discover trends in listener engagement.
          </p>
        </div>

        {/* Card 4 */}
        <div className="glass-panel" style={{
          padding: '32px',
          borderRadius: '16px',
          display: 'flex',
          flexDirection: 'column',
          gap: '16px',
          transition: 'var(--transition-smooth)',
        }}
        onMouseEnter={(e) => {
          e.currentTarget.style.transform = 'translateY(-4px)';
          e.currentTarget.style.borderColor = 'rgba(29, 185, 84, 0.3)';
        }}
        onMouseLeave={(e) => {
          e.currentTarget.style.transform = 'translateY(0)';
          e.currentTarget.style.borderColor = 'var(--glass-border)';
        }}
        >
          <div style={{
            color: '#a020f0',
            backgroundColor: 'rgba(160, 32, 240, 0.1)',
            width: '48px',
            height: '48px',
            borderRadius: '12px',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
          }}>
            <Radio size={24} />
          </div>
          <h3 style={{ fontSize: '1.25rem', fontWeight: 600 }}>Jamendo Import</h3>
          <p style={{ color: 'var(--text-muted)', fontSize: '0.92rem', lineHeight: 1.5 }}>
            Need content? Seed your catalog using public assets via integration with Jamendo API v3.0.
          </p>
        </div>
      </section>
    </div>
  );
}
