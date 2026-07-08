import React, { useState, useRef } from 'react';
import { UploadCloud, Music, FileText, CheckCircle, AlertTriangle } from 'lucide-react';

export default function Upload() {
  const [file, setFile] = useState(null);
  const [dragActive, setDragActive] = useState(false);
  const [error, setError] = useState(null);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadSuccess, setUploadSuccess] = useState(false);
  const fileInputRef = useRef(null);

  // File size limit: 50MB in bytes
  const MAX_FILE_SIZE = 50 * 1024 * 1024;

  const validateFile = (file) => {
    setError(null);
    setUploadSuccess(false);

    if (!file) return false;

    // Validate type (MP3)
    // Note: check extension as well in case MIME type is missing or incorrect
    const fileExtension = file.name.split('.').pop().toLowerCase();
    if (file.type !== 'audio/mpeg' && fileExtension !== 'mp3') {
      setError('Only MP3 files are supported for the MVP catalog.');
      return false;
    }

    // Validate size (max 50MB)
    if (file.size > MAX_FILE_SIZE) {
      setError('File size exceeds the 50MB limit.');
      return false;
    }

    setFile(file);
    return true;
  };

  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);

    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      validateFile(e.dataTransfer.files[0]);
    }
  };

  const handleChange = (e) => {
    e.preventDefault();
    if (e.target.files && e.target.files[0]) {
      validateFile(e.target.files[0]);
    }
  };

  const triggerFileInput = () => {
    fileInputRef.current.click();
  };

  const handleUploadSubmit = async (e) => {
    e.preventDefault();
    if (!file) return;

    setIsUploading(true);
    setError(null);

    // Mock upload delay / backend parsing
    setTimeout(() => {
      setIsUploading(false);
      setUploadSuccess(true);
      setFile(null);
    }, 2500);
  };

  return (
    <div style={{
      maxWidth: '800px',
      margin: '0 auto',
      padding: '40px 24px 140px 24px',
      display: 'flex',
      flexDirection: 'column',
      gap: '32px',
    }}>
      <div>
        <h1 style={{ fontFamily: 'var(--font-display)', fontSize: '2.5rem', fontWeight: 800 }}>
          Upload Music
        </h1>
        <p style={{ color: 'var(--text-muted)', marginTop: '4px' }}>
          Upload your high-fidelity MP3 tracks. Metadata tags (ID3) will be parsed automatically.
        </p>
      </div>

      <div className="glass-panel" style={{
        borderRadius: '16px',
        padding: '32px',
        display: 'flex',
        flexDirection: 'column',
        gap: '24px',
      }}>
        {/* Drag & Drop Box */}
        <div 
          onDragEnter={handleDrag}
          onDragOver={handleDrag}
          onDragLeave={handleDrag}
          onDrop={handleDrop}
          onClick={triggerFileInput}
          style={{
            border: dragActive ? '2px dashed var(--primary-accent)' : '2px dashed var(--border-color)',
            borderRadius: '12px',
            backgroundColor: dragActive ? 'rgba(29, 185, 84, 0.03)' : '#141414',
            padding: '60px 20px',
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            justifyContent: 'center',
            gap: '16px',
            cursor: 'pointer',
            transition: 'var(--transition-smooth)',
          }}
          onMouseEnter={(e) => {
            if (!dragActive) e.currentTarget.style.borderColor = 'rgba(255, 255, 255, 0.2)';
          }}
          onMouseLeave={(e) => {
            if (!dragActive) e.currentTarget.style.borderColor = 'var(--border-color)';
          }}
        >
          <input 
            type="file" 
            ref={fileInputRef}
            onChange={handleChange}
            accept="audio/mpeg,audio/mp3"
            style={{ display: 'none' }}
          />

          <div style={{
            width: '64px',
            height: '64px',
            borderRadius: '50%',
            backgroundColor: '#1d1d1d',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            color: 'var(--primary-accent)',
          }}>
            <UploadCloud size={32} />
          </div>

          <div style={{ textAlign: 'center' }}>
            <p style={{ fontWeight: 600, fontSize: '1.05rem' }}>Drag & drop your MP3 file here</p>
            <p style={{ color: 'var(--text-muted)', fontSize: '0.85rem', marginTop: '6px' }}>
              or click to browse from your device
            </p>
          </div>

          <div style={{
            fontSize: '0.75rem',
            color: 'var(--text-muted)',
            backgroundColor: '#1b1b1b',
            padding: '6px 12px',
            borderRadius: '4px',
            border: '1px solid var(--border-color)',
          }}>
            Maximum file size: 50MB (MP3 only)
          </div>
        </div>

        {/* Error Message */}
        {error && (
          <div style={{
            backgroundColor: 'rgba(255, 68, 68, 0.1)',
            border: '1px solid rgba(255, 68, 68, 0.2)',
            borderRadius: '8px',
            padding: '12px 16px',
            display: 'flex',
            alignItems: 'center',
            gap: '12px',
            color: '#ff4444',
            fontSize: '0.9rem',
          }}>
            <AlertTriangle size={18} />
            <span>{error}</span>
          </div>
        )}

        {/* Selected File Details */}
        {file && !error && (
          <div className="glass-panel" style={{
            padding: '16px',
            borderRadius: '8px',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            border: '1px solid var(--border-color)',
            backgroundColor: '#161616',
          }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '12px', minWidth: 0 }}>
              <Music style={{ color: 'var(--primary-accent)' }} size={20} />
              <div style={{ minWidth: 0 }}>
                <p style={{ fontWeight: 600, fontSize: '0.9rem', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                  {file.name}
                </p>
                <p style={{ color: 'var(--text-muted)', fontSize: '0.75rem', marginTop: '2px' }}>
                  {(file.size / (1024 * 1024)).toFixed(2)} MB
                </p>
              </div>
            </div>
            
            <button 
              onClick={handleUploadSubmit}
              disabled={isUploading}
              className="spotify-btn"
              style={{ padding: '8px 24px', fontSize: '0.85rem' }}
            >
              {isUploading ? 'Extracting ID3...' : 'Upload'}
            </button>
          </div>
        )}

        {/* Upload Success */}
        {uploadSuccess && (
          <div style={{
            backgroundColor: 'rgba(29, 185, 84, 0.1)',
            border: '1px solid rgba(29, 185, 84, 0.2)',
            borderRadius: '8px',
            padding: '16px',
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            gap: '8px',
            color: 'var(--primary-accent)',
            textAlign: 'center',
          }}>
            <CheckCircle size={28} />
            <span style={{ fontWeight: 600 }}>File Uploaded Successfully!</span>
            <span style={{ fontSize: '0.82rem', color: 'var(--text-muted)' }}>
              Backend successfully processed the audio track and extracted the ID3 tags.
            </span>
          </div>
        )}
      </div>
    </div>
  );
}
