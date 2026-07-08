import React, { useState } from 'react';
import { Play, Pause, SkipForward, SkipBack, Volume2, VolumeX, Maximize2, Repeat, Shuffle } from 'lucide-react';

export default function PlayerBar() {
  const [isPlaying, setIsPlaying] = useState(false);
  const [isMuted, setIsMuted] = useState(false);
  const [volume, setVolume] = useState(70);
  const [progress, setProgress] = useState(35); // mock current percentage

  // Mock song metadata for design rendering
  const currentSong = {
    title: 'Midnight Horizon (Demo)',
    artist: 'Horizon Wave',
    duration: '3:42',
    currentTime: '1:18',
    coverUrl: 'https://images.unsplash.com/photo-1614613535308-eb5fbd3d2c17?q=80&w=120&auto=format&fit=crop', // nice music graphic
  };

  const handlePlayPause = () => {
    setIsPlaying(!isPlaying);
  };

  const handleMuteToggle = () => {
    setIsMuted(!isMuted);
  };

  return (
    <div className="glass-panel" style={{
      position: 'fixed',
      bottom: 0,
      left: 0,
      right: 0,
      height: '90px',
      display: 'grid',
      gridTemplateColumns: '1fr 2fr 1fr',
      alignItems: 'center',
      padding: '0 32px',
      borderBottom: 'none',
      borderLeft: 'none',
      borderRight: 'none',
      zIndex: 1000,
    }}>
      {/* 1. Active Song Info */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '14px' }}>
        <img 
          src={currentSong.coverUrl} 
          alt="Cover Art" 
          style={{
            width: '56px',
            height: '56px',
            borderRadius: '6px',
            objectFit: 'cover',
            boxShadow: '0 4px 10px rgba(0, 0, 0, 0.4)'
          }}
        />
        <div style={{ display: 'flex', flexDirection: 'column', minWidth: 0 }}>
          <span style={{ 
            fontSize: '0.92rem', 
            fontWeight: 600,
            whiteSpace: 'nowrap',
            overflow: 'hidden',
            textOverflow: 'ellipsis',
          }}>
            {currentSong.title}
          </span>
          <span style={{ 
            fontSize: '0.78rem', 
            color: 'var(--text-muted)',
            whiteSpace: 'nowrap',
            overflow: 'hidden',
            textOverflow: 'ellipsis',
            marginTop: '2px',
          }}>
            {currentSong.artist}
          </span>
        </div>
      </div>

      {/* 2. Central Player Controls */}
      <div style={{ 
        display: 'flex', 
        flexDirection: 'column', 
        alignItems: 'center', 
        gap: '8px',
        width: '100%',
      }}>
        {/* Buttons */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '20px' }}>
          <button style={{ color: 'var(--text-muted)' }} className="glow-hover">
            <Shuffle size={16} />
          </button>
          <button style={{ color: 'var(--text-main)' }}>
            <SkipBack size={18} fill="currentColor" />
          </button>
          
          <button 
            onClick={handlePlayPause}
            style={{ 
              backgroundColor: 'var(--text-main)', 
              color: 'var(--bg-primary)', 
              width: '38px', 
              height: '38px', 
              borderRadius: '50%',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.transform = 'scale(1.08)';
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.transform = 'scale(1)';
            }}
          >
            {isPlaying ? (
              <Pause size={18} fill="currentColor" strokeWidth={3} />
            ) : (
              <Play size={18} fill="currentColor" style={{ marginLeft: '2px' }} strokeWidth={3} />
            )}
          </button>
          
          <button style={{ color: 'var(--text-main)' }}>
            <SkipForward size={18} fill="currentColor" />
          </button>
          <button style={{ color: 'var(--text-muted)' }} className="glow-hover">
            <Repeat size={16} />
          </button>
        </div>

        {/* Playback progress slider */}
        <div style={{ 
          display: 'flex', 
          alignItems: 'center', 
          gap: '8px', 
          width: '100%',
          maxWidth: '500px',
          fontSize: '0.75rem',
          color: 'var(--text-muted)',
        }}>
          <span>{currentSong.currentTime}</span>
          <div style={{
            flex: 1,
            height: '4px',
            backgroundColor: '#3e3e3e',
            borderRadius: '2px',
            position: 'relative',
            cursor: 'pointer',
          }}
          onMouseEnter={(e) => {
            e.currentTarget.firstElementChild.style.backgroundColor = 'var(--primary-accent)';
          }}
          onMouseLeave={(e) => {
            e.currentTarget.firstElementChild.style.backgroundColor = 'var(--text-main)';
          }}
          >
            <div style={{
              width: `${progress}%`,
              height: '100%',
              backgroundColor: 'var(--text-main)',
              borderRadius: '2px',
              transition: 'background-color 0.2s',
            }}/>
          </div>
          <span>{currentSong.duration}</span>
        </div>
      </div>

      {/* 3. Right Volume & Extra controls */}
      <div style={{ 
        display: 'flex', 
        alignItems: 'center', 
        justifyContent: 'flex-end', 
        gap: '16px',
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <button onClick={handleMuteToggle} style={{ color: 'var(--text-muted)' }} className="glow-hover">
            {isMuted || volume === 0 ? <VolumeX size={18} /> : <Volume2 size={18} />}
          </button>
          <input 
            type="range" 
            min="0" 
            max="100" 
            value={isMuted ? 0 : volume}
            onChange={(e) => setVolume(Number(e.target.value))}
            style={{
              width: '80px',
              accentColor: 'var(--primary-accent)',
              cursor: 'pointer',
              height: '4px',
            }}
          />
        </div>
        <button style={{ color: 'var(--text-muted)' }} className="glow-hover">
          <Maximize2 size={16} />
        </button>
      </div>
    </div>
  );
}
