import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { Music, Plus, Search, Radio, Disc, DiscAlbum } from 'lucide-react';

export default function Dashboard() {
  const [searchTerm, setSearchTerm] = useState('');
  
  // Mock data for catalog items
  const mockSongs = [
    { id: 1, title: 'Midnight Horizon (Demo)', artist: 'Horizon Wave', album: 'Horizon Ep', duration: '3:42', playCount: 1420 },
    { id: 2, title: 'Solar Flare', artist: 'Horizon Wave', album: 'Horizon Ep', duration: '4:10', playCount: 890 },
    { id: 3, title: 'Nebula Breeze', artist: 'Horizon Wave', album: 'Nebula Suite', duration: '2:55', playCount: 2310 },
    { id: 4, title: 'Starry Canopy', artist: 'Nova Synth', album: 'Aether Fields', duration: '5:12', playCount: 420 },
  ];

  const filteredSongs = mockSongs.filter(song => 
    song.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
    song.artist.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <div style={{
      maxWidth: '1200px',
      margin: '0 auto',
      padding: '40px 24px 140px 24px',
      display: 'flex',
      flexDirection: 'column',
      gap: '32px',
    }}>
      {/* Header */}
      <div style={{
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        flexWrap: 'wrap',
        gap: '16px',
      }}>
        <div>
          <h1 style={{ fontFamily: 'var(--font-display)', fontSize: '2.5rem', fontWeight: 800 }}>
            Creator Dashboard
          </h1>
          <p style={{ color: 'var(--text-muted)', marginTop: '4px' }}>
            Manage your songs, albums, and check distributions.
          </p>
        </div>

        <div style={{ display: 'flex', gap: '12px' }}>
          <Link to="/upload" className="spotify-btn">
            <Plus size={16} />
            Upload Song
          </Link>
          <button style={{
            display: 'inline-flex',
            alignItems: 'center',
            gap: '8px',
            padding: '12px 24px',
            borderRadius: '500px',
            backgroundColor: '#1f1f1f',
            border: '1px solid var(--border-color)',
            color: 'var(--text-main)',
            fontWeight: 600,
          }}
          onMouseEnter={(e) => {
            e.currentTarget.style.backgroundColor = '#2a2a2a';
          }}
          onMouseLeave={(e) => {
            e.currentTarget.style.backgroundColor = '#1f1f1f';
          }}
          >
            <Radio size={16} />
            Jamendo Seed
          </button>
        </div>
      </div>

      {/* Stats Quick Cards */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))',
        gap: '20px',
      }}>
        <div className="glass-panel" style={{ padding: '24px', borderRadius: '12px' }}>
          <span style={{ fontSize: '0.82rem', color: 'var(--text-muted)', textTransform: 'uppercase', fontWeight: 600 }}>Total Tracks</span>
          <h2 style={{ fontSize: '2.2rem', fontWeight: 700, marginTop: '8px' }}>4</h2>
        </div>
        <div className="glass-panel" style={{ padding: '24px', borderRadius: '12px' }}>
          <span style={{ fontSize: '0.82rem', color: 'var(--text-muted)', textTransform: 'uppercase', fontWeight: 600 }}>Total Albums</span>
          <h2 style={{ fontSize: '2.2rem', fontWeight: 700, marginTop: '8px' }}>3</h2>
        </div>
        <div className="glass-panel" style={{ padding: '24px', borderRadius: '12px' }}>
          <span style={{ fontSize: '0.82rem', color: 'var(--text-muted)', textTransform: 'uppercase', fontWeight: 600 }}>Total Play Count</span>
          <h2 style={{ fontSize: '2.2rem', fontWeight: 700, marginTop: '8px', color: 'var(--primary-accent)' }}>5,040</h2>
        </div>
      </div>

      {/* Search and Table */}
      <div className="glass-panel" style={{
        borderRadius: '16px',
        padding: '24px',
        display: 'flex',
        flexDirection: 'column',
        gap: '20px',
      }}>
        {/* Search Header */}
        <div style={{
          display: 'flex',
          alignItems: 'center',
          gap: '12px',
          backgroundColor: '#161616',
          border: '1px solid var(--border-color)',
          borderRadius: '8px',
          padding: '8px 16px',
          maxWidth: '400px',
        }}>
          <Search size={18} style={{ color: 'var(--text-muted)' }} />
          <input 
            type="text" 
            placeholder="Search tracks or artists..." 
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
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

        {/* Tracks List */}
        <div style={{ overflowX: 'auto' }}>
          <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left' }}>
            <thead>
              <tr style={{ borderBottom: '1px solid var(--border-color)', color: 'var(--text-muted)', fontSize: '0.85rem' }}>
                <th style={{ padding: '12px 16px' }}># Title</th>
                <th style={{ padding: '12px 16px' }}>Album</th>
                <th style={{ padding: '12px 16px' }}>Duration</th>
                <th style={{ padding: '12px 16px', textAlign: 'right' }}>Plays</th>
              </tr>
            </thead>
            <tbody>
              {filteredSongs.length > 0 ? (
                filteredSongs.map((song, index) => (
                  <tr 
                    key={song.id} 
                    style={{ 
                      borderBottom: '1px solid rgba(255, 255, 255, 0.04)', 
                      fontSize: '0.92rem',
                      cursor: 'pointer',
                      transition: 'background-color 0.2s',
                    }}
                    onMouseEnter={(e) => {
                      e.currentTarget.style.backgroundColor = 'rgba(255, 255, 255, 0.02)';
                    }}
                    onMouseLeave={(e) => {
                      e.currentTarget.style.backgroundColor = 'transparent';
                    }}
                  >
                    <td style={{ padding: '16px', display: 'flex', alignItems: 'center', gap: '12px' }}>
                      <span style={{ color: 'var(--text-muted)', width: '20px' }}>{index + 1}</span>
                      <div style={{
                        width: '40px',
                        height: '40px',
                        backgroundColor: '#282828',
                        borderRadius: '4px',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        color: 'var(--primary-accent)',
                      }}>
                        <Disc size={20} />
                      </div>
                      <div>
                        <div style={{ fontWeight: 600 }}>{song.title}</div>
                        <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>{song.artist}</div>
                      </div>
                    </td>
                    <td style={{ padding: '16px', color: 'var(--text-muted)' }}>{song.album}</td>
                    <td style={{ padding: '16px', color: 'var(--text-muted)' }}>{song.duration}</td>
                    <td style={{ padding: '16px', textAlign: 'right', fontWeight: 600 }}>{song.playCount.toLocaleString()}</td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan="4" style={{ padding: '32px', textAlign: 'center', color: 'var(--text-muted)' }}>
                    No tracks found matching "{searchTerm}"
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
