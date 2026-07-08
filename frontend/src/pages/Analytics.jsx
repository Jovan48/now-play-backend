import React from 'react';
import { BarChart3, TrendingUp, Users, Play, ArrowUpRight } from 'lucide-react';

export default function Analytics() {
  // Mock data for graphs
  const topTracks = [
    { title: 'Nebula Breeze', plays: 2310, percentage: 100 },
    { title: 'Midnight Horizon (Demo)', plays: 1420, percentage: 61 },
    { title: 'Solar Flare', plays: 890, percentage: 38 },
    { title: 'Starry Canopy', plays: 420, percentage: 18 },
  ];

  const weeklyStats = [
    { day: 'Mon', plays: 240 },
    { day: 'Tue', plays: 320 },
    { day: 'Wed', plays: 480 },
    { day: 'Thu', plays: 380 },
    { day: 'Fri', plays: 600 },
    { day: 'Sat', plays: 720 },
    { day: 'Sun', plays: 850 },
  ];

  return (
    <div style={{
      maxWidth: '1200px',
      margin: '0 auto',
      padding: '40px 24px 140px 24px',
      display: 'flex',
      flexDirection: 'column',
      gap: '32px',
    }}>
      <div>
        <h1 style={{ fontFamily: 'var(--font-display)', fontSize: '2.5rem', fontWeight: 800 }}>
          Music Analytics
        </h1>
        <p style={{ color: 'var(--text-muted)', marginTop: '4px' }}>
          Real-time metrics tracking track plays and listener reach.
        </p>
      </div>

      {/* Main metrics row */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))',
        gap: '24px',
      }}>
        {/* Card 1 */}
        <div className="glass-panel" style={{ padding: '24px', borderRadius: '16px', display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
          <div>
            <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)', fontWeight: 600, textTransform: 'uppercase' }}>Total Playback Counts</span>
            <h2 style={{ fontSize: '2.4rem', fontWeight: 700, marginTop: '8px' }}>5,040</h2>
            <div style={{ display: 'flex', alignItems: 'center', gap: '4px', color: 'var(--primary-accent)', fontSize: '0.8rem', marginTop: '8px', fontWeight: 600 }}>
              <TrendingUp size={14} />
              <span>+18.4% this week</span>
            </div>
          </div>
          <div style={{ backgroundColor: 'rgba(29, 185, 84, 0.1)', color: 'var(--primary-accent)', padding: '12px', borderRadius: '12px' }}>
            <Play size={20} fill="currentColor" />
          </div>
        </div>

        {/* Card 2 */}
        <div className="glass-panel" style={{ padding: '24px', borderRadius: '16px', display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
          <div>
            <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)', fontWeight: 600, textTransform: 'uppercase' }}>Unique Listeners</span>
            <h2 style={{ fontSize: '2.4rem', fontWeight: 700, marginTop: '8px' }}>1,290</h2>
            <div style={{ display: 'flex', alignItems: 'center', gap: '4px', color: 'var(--primary-accent)', fontSize: '0.8rem', marginTop: '8px', fontWeight: 600 }}>
              <TrendingUp size={14} />
              <span>+8.2% this week</span>
            </div>
          </div>
          <div style={{ backgroundColor: 'rgba(30, 144, 255, 0.1)', color: '#1e90ff', padding: '12px', borderRadius: '12px' }}>
            <Users size={20} />
          </div>
        </div>

        {/* Card 3 */}
        <div className="glass-panel" style={{ padding: '24px', borderRadius: '16px', display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
          <div>
            <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)', fontWeight: 600, textTransform: 'uppercase' }}>Global Catalog Share</span>
            <h2 style={{ fontSize: '2.4rem', fontWeight: 700, marginTop: '8px' }}>0.04%</h2>
            <div style={{ display: 'flex', alignItems: 'center', gap: '4px', color: '#ff4444', fontSize: '0.8rem', marginTop: '8px', fontWeight: 600 }}>
              <ArrowUpRight size={14} />
              <span>Ranked #1,420</span>
            </div>
          </div>
          <div style={{ backgroundColor: 'rgba(255, 68, 68, 0.1)', color: '#ff4444', padding: '12px', borderRadius: '12px' }}>
            <BarChart3 size={20} />
          </div>
        </div>
      </div>

      {/* Graphs section */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(450px, 1fr))',
        gap: '24px',
      }}>
        {/* Weekly Trend (Bar Chart) */}
        <div className="glass-panel" style={{
          padding: '32px',
          borderRadius: '16px',
          display: 'flex',
          flexDirection: 'column',
          gap: '24px',
        }}>
          <h3 style={{ fontSize: '1.2rem', fontWeight: 600 }}>Weekly Play Count Trend</h3>
          <div style={{
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'flex-end',
            height: '240px',
            paddingTop: '20px',
            borderBottom: '1px solid var(--border-color)',
            gap: '8px',
          }}>
            {weeklyStats.map(stat => (
              <div 
                key={stat.day} 
                style={{ 
                  display: 'flex', 
                  flexDirection: 'column', 
                  alignItems: 'center', 
                  flex: 1,
                  gap: '12px',
                }}
              >
                <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)', fontWeight: 500 }}>{stat.plays}</span>
                <div style={{
                  width: '100%',
                  maxWidth: '36px',
                  height: `${(stat.plays / 900) * 160}px`,
                  backgroundColor: 'rgba(29, 185, 84, 0.15)',
                  border: '1px solid rgba(29, 185, 84, 0.4)',
                  borderBottom: 'none',
                  borderRadius: '4px 4px 0 0',
                  transition: 'var(--transition-smooth)',
                  cursor: 'pointer',
                }}
                onMouseEnter={(e) => {
                  e.currentTarget.style.backgroundColor = 'var(--primary-accent)';
                  e.currentTarget.style.boxShadow = '0 0 15px rgba(29, 185, 84, 0.4)';
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.backgroundColor = 'rgba(29, 185, 84, 0.15)';
                  e.currentTarget.style.boxShadow = 'none';
                }}
                />
                <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)', paddingBottom: '8px' }}>{stat.day}</span>
              </div>
            ))}
          </div>
        </div>

        {/* Top Performing Tracks */}
        <div className="glass-panel" style={{
          padding: '32px',
          borderRadius: '16px',
          display: 'flex',
          flexDirection: 'column',
          gap: '24px',
        }}>
          <h3 style={{ fontSize: '1.2rem', fontWeight: 600 }}>Top Performing Tracks</h3>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
            {topTracks.map((track, idx) => (
              <div key={idx} style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.9rem', fontWeight: 500 }}>
                  <span>{track.title}</span>
                  <span style={{ color: 'var(--text-muted)' }}>{track.plays.toLocaleString()} plays</span>
                </div>
                {/* Progress bar */}
                <div style={{
                  height: '8px',
                  backgroundColor: '#222222',
                  borderRadius: '4px',
                  overflow: 'hidden',
                }}>
                  <div style={{
                    width: `${track.percentage}%`,
                    height: '100%',
                    backgroundColor: 'var(--primary-accent)',
                    borderRadius: '4px',
                    boxShadow: '0 0 10px rgba(29, 185, 84, 0.3)',
                  }}/>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
