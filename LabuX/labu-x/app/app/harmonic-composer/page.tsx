'use client';

import { useState, useCallback } from 'react';
import Link from 'next/link';
import { useDropzone } from 'react-dropzone';

export default function HarmonicComposerPage() {
  const [file, setFile] = useState<File | null>(null);
  const [processing, setProcessing] = useState(false);
  const [status, setStatus] = useState<string>('');
  const [progress, setProgress] = useState(0);
  const [videoUrl, setVideoUrl] = useState<string | null>(null);
  const [theme, setTheme] = useState<'cosmic' | 'minimal'>('cosmic');

  const onDrop = useCallback((acceptedFiles: File[]) => {
    if (acceptedFiles.length > 0) {
      setFile(acceptedFiles[0]);
      setVideoUrl(null);
      setStatus('');
    }
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'audio/*': ['.m4a', '.mp3', '.wav', '.aac']
    },
    maxFiles: 1,
    maxSize: 100 * 1024 * 1024 // 100MB
  });

  const handleGenerate = async () => {
    if (!file) return;

    setProcessing(true);
    setProgress(0);
    setStatus('Uploading audio file...');

    const formData = new FormData();
    formData.append('file', file);
    formData.append('theme', theme);

    try {
      const response = await fetch('/api/harmonic-composer/generate', {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        throw new Error('Generation failed');
      }

      const blob = await response.blob();
      const url = URL.createObjectURL(blob);
      setVideoUrl(url);
      setStatus('✅ Video generated successfully!');
      setProgress(100);
    } catch (error: any) {
      console.error('Error:', error);
      setStatus(`❌ Error: ${error.message}`);
    } finally {
      setProcessing(false);
    }
  };

  return (
    <div className="container" style={{ maxWidth: '1000px', margin: '0 auto', padding: '2rem' }}>
      {/* Header */}
      <div style={{ textAlign: 'center', marginBottom: '3rem' }}>
        <Link href="/" style={{ color: '#8b5cf6', textDecoration: 'none', fontSize: '0.9rem' }}>
          ← Back to Genesis Fund
        </Link>
      </div>

      <div style={{ textAlign: 'center', marginBottom: '3rem' }}>
        <h1 style={{
          fontSize: '3rem',
          background: 'linear-gradient(135deg, #8b5cf6, #6366f1)',
          WebkitBackgroundClip: 'text',
          WebkitTextFillColor: 'transparent',
          marginBottom: '1rem'
        }}>
          🌌 Harmonic Video Composer
        </h1>
        <p style={{ fontSize: '1.2rem', color: '#9ca3af' }}>
          Transform NotebookLM Deep Dives into Cosmic Video Content
        </p>
        <p style={{ fontSize: '0.9rem', color: '#666', marginTop: '0.5rem' }}>
          MVP Demo - Basic text overlay videos with harmonic theme detection
        </p>
      </div>

      {/* Upload Area */}
      <div
        {...getRootProps()}
        style={{
          border: '2px dashed ' + (isDragActive ? '#8b5cf6' : '#4b5563'),
          borderRadius: '12px',
          padding: '3rem 2rem',
          textAlign: 'center',
          cursor: 'pointer',
          background: isDragActive ? 'rgba(139, 92, 246, 0.1)' : 'rgba(31, 41, 55, 0.5)',
          transition: 'all 0.3s',
          marginBottom: '2rem'
        }}
      >
        <input {...getInputProps()} />
        <div style={{ fontSize: '4rem', marginBottom: '1rem' }}>
          {file ? '✅' : '🎙️'}
        </div>
        {file ? (
          <div>
            <p style={{ fontSize: '1.2rem', color: '#a78bfa', marginBottom: '0.5rem' }}>
              {file.name}
            </p>
            <p style={{ fontSize: '0.9rem', color: '#666' }}>
              {(file.size / 1024 / 1024).toFixed(2)} MB
            </p>
          </div>
        ) : (
          <div>
            <p style={{ fontSize: '1.2rem', color: '#9ca3af', marginBottom: '0.5rem' }}>
              {isDragActive ? 'Drop your audio file here' : 'Drag & drop audio file'}
            </p>
            <p style={{ fontSize: '0.9rem', color: '#666' }}>
              or click to browse (m4a, mp3, wav - max 100MB)
            </p>
          </div>
        )}
      </div>

      {/* Theme Selection */}
      {file && (
        <div style={{ marginBottom: '2rem' }}>
          <label style={{ display: 'block', marginBottom: '1rem', color: '#9ca3af', fontSize: '0.9rem' }}>
            Visual Theme:
          </label>
          <div style={{ display: 'flex', gap: '1rem' }}>
            <button
              onClick={() => setTheme('cosmic')}
              style={{
                flex: 1,
                padding: '1rem',
                border: theme === 'cosmic' ? '2px solid #8b5cf6' : '2px solid #4b5563',
                borderRadius: '8px',
                background: theme === 'cosmic' ? 'rgba(139, 92, 246, 0.2)' : 'rgba(31, 41, 55, 0.5)',
                color: theme === 'cosmic' ? '#a78bfa' : '#9ca3af',
                cursor: 'pointer',
                transition: 'all 0.3s'
              }}
            >
              <div style={{ fontSize: '2rem', marginBottom: '0.5rem' }}>🌌</div>
              <div style={{ fontWeight: 'bold' }}>Cosmic</div>
              <div style={{ fontSize: '0.8rem', marginTop: '0.3rem' }}>Black holes & galaxies</div>
            </button>
            <button
              onClick={() => setTheme('minimal')}
              style={{
                flex: 1,
                padding: '1rem',
                border: theme === 'minimal' ? '2px solid #8b5cf6' : '2px solid #4b5563',
                borderRadius: '8px',
                background: theme === 'minimal' ? 'rgba(139, 92, 246, 0.2)' : 'rgba(31, 41, 55, 0.5)',
                color: theme === 'minimal' ? '#a78bfa' : '#9ca3af',
                cursor: 'pointer',
                transition: 'all 0.3s'
              }}
            >
              <div style={{ fontSize: '2rem', marginBottom: '0.5rem' }}>◼️</div>
              <div style={{ fontWeight: 'bold' }}>Minimal</div>
              <div style={{ fontSize: '0.8rem', marginTop: '0.3rem' }}>Clean & professional</div>
            </button>
          </div>
        </div>
      )}

      {/* Generate Button */}
      {file && !processing && !videoUrl && (
        <button
          onClick={handleGenerate}
          style={{
            width: '100%',
            padding: '1.5rem',
            background: 'linear-gradient(135deg, #8b5cf6, #6366f1)',
            color: 'white',
            border: 'none',
            borderRadius: '8px',
            fontSize: '1.2rem',
            fontWeight: 'bold',
            cursor: 'pointer',
            transition: 'transform 0.2s',
            marginBottom: '2rem'
          }}
          onMouseEnter={(e) => e.currentTarget.style.transform = 'scale(1.02)'}
          onMouseLeave={(e) => e.currentTarget.style.transform = 'scale(1)'}
        >
          🎬 Generate Harmonic Video
        </button>
      )}

      {/* Processing Status */}
      {processing && (
        <div style={{
          background: 'rgba(139, 92, 246, 0.1)',
          border: '1px solid rgba(139, 92, 246, 0.3)',
          borderRadius: '12px',
          padding: '2rem',
          marginBottom: '2rem'
        }}>
          <div style={{ textAlign: 'center', marginBottom: '1rem' }}>
            <div style={{ fontSize: '3rem', marginBottom: '0.5rem' }}>⚡</div>
            <div style={{ fontSize: '1.2rem', color: '#a78bfa', marginBottom: '0.5rem' }}>
              {status}
            </div>
          </div>
          <div style={{
            width: '100%',
            height: '8px',
            background: 'rgba(75, 85, 99, 0.5)',
            borderRadius: '4px',
            overflow: 'hidden'
          }}>
            <div style={{
              width: `${progress}%`,
              height: '100%',
              background: 'linear-gradient(90deg, #8b5cf6, #6366f1)',
              transition: 'width 0.3s'
            }}></div>
          </div>
          <div style={{ textAlign: 'center', marginTop: '0.5rem', fontSize: '0.9rem', color: '#666' }}>
            This may take 2-5 minutes depending on audio length
          </div>
        </div>
      )}

      {/* Video Result */}
      {videoUrl && (
        <div style={{
          background: 'rgba(139, 92, 246, 0.1)',
          border: '2px solid rgba(139, 92, 246, 0.4)',
          borderRadius: '12px',
          padding: '2rem',
          marginBottom: '2rem'
        }}>
          <div style={{ textAlign: 'center', marginBottom: '2rem' }}>
            <div style={{ fontSize: '3rem', marginBottom: '0.5rem' }}>✨</div>
            <div style={{ fontSize: '1.5rem', color: '#a78bfa', marginBottom: '0.5rem' }}>
              {status}
            </div>
          </div>

          <video
            controls
            style={{
              width: '100%',
              borderRadius: '8px',
              marginBottom: '1.5rem',
              boxShadow: '0 4px 6px rgba(0, 0, 0, 0.3)'
            }}
            src={videoUrl}
          />

          <div style={{ display: 'flex', gap: '1rem' }}>
            <a
              href={videoUrl}
              download={`harmonic-video-${Date.now()}.mp4`}
              style={{
                flex: 1,
                padding: '1rem',
                background: 'linear-gradient(135deg, #8b5cf6, #6366f1)',
                color: 'white',
                textDecoration: 'none',
                borderRadius: '8px',
                textAlign: 'center',
                fontWeight: 'bold',
                cursor: 'pointer'
              }}
            >
              📥 Download Video
            </a>
            <button
              onClick={() => {
                setFile(null);
                setVideoUrl(null);
                setStatus('');
                setProgress(0);
              }}
              style={{
                flex: 1,
                padding: '1rem',
                background: 'rgba(75, 85, 99, 0.5)',
                color: 'white',
                border: 'none',
                borderRadius: '8px',
                fontWeight: 'bold',
                cursor: 'pointer'
              }}
            >
              🔄 Create Another
            </button>
          </div>
        </div>
      )}

      {/* Info Section */}
      <div style={{
        background: 'rgba(31, 41, 55, 0.5)',
        borderRadius: '12px',
        padding: '2rem',
        marginTop: '3rem'
      }}>
        <h3 style={{ color: '#f59e0b', marginBottom: '1rem' }}>How It Works</h3>
        <ol style={{ color: '#9ca3af', lineHeight: '1.8', paddingLeft: '1.5rem' }}>
          <li>Upload your NotebookLM "Deep Dive" audio or any philosophical content</li>
          <li>AI transcribes the audio and detects harmonic themes</li>
          <li>Each theme gets matched with cosmic visualizations</li>
          <li>Video is automatically composed with subtitles and effects</li>
          <li>Download and share your cosmic video!</li>
        </ol>
        <p style={{ color: '#666', fontSize: '0.9rem', marginTop: '1.5rem', fontStyle: 'italic' }}>
          MVP Version - Basic functionality. Full theme detection, advanced visuals, and $TGF integration coming soon!
        </p>
      </div>

      {/* CTA */}
      <div style={{ textAlign: 'center', marginTop: '3rem', paddingTop: '2rem', borderTop: '1px solid rgba(139, 92, 246, 0.2)' }}>
        <p style={{ color: '#9ca3af', marginBottom: '1rem' }}>
          Powered by the Genesis Fund Temporal Attractor
        </p>
        <Link
          href="/philosophy"
          style={{
            color: '#8b5cf6',
            textDecoration: 'underline'
          }}
        >
          Learn about the philosophy →
        </Link>
      </div>
    </div>
  );
}
