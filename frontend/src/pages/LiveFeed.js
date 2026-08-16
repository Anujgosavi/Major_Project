// src/pages/LiveFeed.js
import React, { useState, useEffect, useRef } from 'react';
import { 
  Camera, 
  Square, 
  Play, 
  Loader2, 
  FileText, 
  CheckCircle, 
  AlertTriangle, 
  X, 
  Activity, 
  Eye, 
  Clock, 
  Ruler, 
  Zap, 
  Minimize2, 
  Maximize2, 
  RefreshCw 
} from 'lucide-react';
import './LiveFeed.css';

const API_BASE = '';

// Notification config
const ALERT_CONFIG = {
  BREAK: { 
    icon: '👁️', 
    title: '20-20-20 Rule', 
    message: 'Look at something 20 feet away for 20 seconds to rest your eyes.',
    color: '#3b82f6',
    gradient: 'linear-gradient(135deg, #3b82f6, #1d4ed8)'
  },
  WATER: { 
    icon: '💧', 
    title: 'Hydration Reminder', 
    message: 'Time to drink a glass of water to stay hydrated and focused.',
    color: '#06b6d4',
    gradient: 'linear-gradient(135deg, #06b6d4, #0891b2)'
  },
  POSTURE: { 
    icon: '⚠️', 
    title: 'Posture Warning', 
    message: 'Your posture needs attention. Please sit up straight!',
    color: '#ef4444',
    gradient: 'linear-gradient(135deg, #ef4444, #dc2626)'
  },
};

export default function LiveFeed() {
  const [status, setStatus] = useState('idle');
  const [stats, setStats] = useState({});
  const [pdfPath, setPdfPath] = useState(null);
  const [backendOnline, setBackendOnline] = useState(false);
  const [notifications, setNotifications] = useState([]);
  const [isFullscreen, setIsFullscreen] = useState(false);
  const [sessionTime, setSessionTime] = useState(0);
  const pollRef = useRef(null);
  const seenAlertsRef = useRef(new Set());
  const videoRef = useRef(null);
  const pcRef = useRef(null);

  // WebRTC Cleanup
  useEffect(() => {
    if (status !== 'running') {
      if (pcRef.current) {
        pcRef.current.close();
        pcRef.current = null;
      }
      if (videoRef.current) {
        videoRef.current.srcObject = null;
      }
    }
  }, [status]);

  const startWebRTC = async () => {
    try {
      const pc = new RTCPeerConnection();
      pcRef.current = pc;

      pc.ontrack = (event) => {
        if (videoRef.current && event.track.kind === 'video') {
          if (event.streams && event.streams[0]) {
            videoRef.current.srcObject = event.streams[0];
          } else {
            videoRef.current.srcObject = new MediaStream([event.track]);
          }
        }
      };

      pc.addTransceiver('video', { direction: 'recvonly' });

      const offer = await pc.createOffer();
      await pc.setLocalDescription(offer);

      const response = await fetch(`${API_BASE}/api/webrtc/offer`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          sdp: pc.localDescription.sdp,
          type: pc.localDescription.type
        })
      });
      
      const answer = await response.json();
      await pc.setRemoteDescription(answer);

    } catch (err) {
      console.error('Failed to start WebRTC:', err);
    }
  };

  // Poll backend status every 500ms
  useEffect(() => {
    const checkStatus = async () => {
      try {
        const res = await fetch(`${API_BASE}/api/status`);
        const data = await res.json();
        setBackendOnline(true);

        if (data.running) {
          setStatus('running');
          setStats(data.stats || {});
        } else if (data.pdf_generating) {
          setStatus('pdf_generating');
        } else {
          setStatus((prev) => {
            if (prev === 'stopping' || prev === 'pdf_generating' || prev === 'running') {
              return 'idle';
            }
            return prev;
          });
          if (data.pdf_path) {
            setPdfPath(data.pdf_path);
          }
        }
      } catch {
        setBackendOnline(false);
      }
    };

    pollRef.current = setInterval(checkStatus, 500);
    checkStatus();
    return () => clearInterval(pollRef.current);
  }, []);

  // Session timer
  useEffect(() => {
    let timer;
    if (status === 'running') {
      timer = setInterval(() => {
        setSessionTime(prev => prev + 1);
      }, 1000);
    } else {
      setSessionTime(0);
    }
    return () => clearInterval(timer);
  }, [status]);

  // Ensure WebRTC is connected when running
  useEffect(() => {
    if (status === 'running' && !pcRef.current) {
      // Small delay to allow camera to initialize if just starting
      const timer = setTimeout(() => {
        if (!pcRef.current) {
          startWebRTC();
        }
      }, 1000);
      return () => clearTimeout(timer);
    }
  }, [status]);

  const handleStart = async () => {
    try {
      await fetch(`${API_BASE}/api/start`, { method: 'POST' });
      setStatus('running');
      setPdfPath(null);
      setSessionTime(0);
    } catch (err) {
      console.error('Failed to start:', err);
    }
  };

  const handleStop = async () => {
    try {
      setStatus('stopping');
      await fetch(`${API_BASE}/api/stop`, { method: 'POST' });
    } catch (err) {
      console.error('Failed to stop:', err);
    }
  };

  const handleDismissAlert = async (alertType) => {
    try {
      await fetch(`${API_BASE}/api/dismiss_alert`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ alert_type: alertType })
      });
      setNotifications((prev) => prev.filter((n) => n.type !== alertType));
      seenAlertsRef.current.delete(alertType);
    } catch (err) {
      console.error('Failed to dismiss alert:', err);
    }
  };

  // Spawn toast notifications
  useEffect(() => {
    const activeAlerts = stats?.active_alerts || [];

    const playBeep = () => {
      try {
        const ctx = new (window.AudioContext || window.webkitAudioContext)();
        const osc = ctx.createOscillator();
        const gain = ctx.createGain();
        osc.type = 'sine';
        osc.frequency.setValueAtTime(880, ctx.currentTime);
        gain.gain.setValueAtTime(0.1, ctx.currentTime);
        osc.connect(gain);
        gain.connect(ctx.destination);
        osc.start();
        osc.stop(ctx.currentTime + 0.3);
      } catch (e) {}
    };

    let beeped = false;

    activeAlerts.forEach((alertType) => {
      if (!seenAlertsRef.current.has(alertType)) {
        seenAlertsRef.current.add(alertType);
        setNotifications((prev) => [...prev, { type: alertType, timestamp: Date.now() }]);
        if (!beeped) {
          playBeep();
          beeped = true;
        }
      }
    });

    seenAlertsRef.current.forEach((alertType) => {
      if (!activeAlerts.includes(alertType)) {
        seenAlertsRef.current.delete(alertType);
      }
    });
  }, [stats?.active_alerts]);

  // Auto-dismiss notifications after 60 seconds
  useEffect(() => {
    if (notifications.length === 0) return;
    const timer = setInterval(() => {
      const now = Date.now();
      setNotifications((prev) => {
        const expired = prev.filter((n) => now - n.timestamp >= 60000);
        expired.forEach((n) => {
          seenAlertsRef.current.delete(n.type);
          fetch(`${API_BASE}/api/dismiss_alert`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ alert_type: n.type })
          }).catch(() => {});
        });
        return prev.filter((n) => now - n.timestamp < 60000);
      });
    }, 1000);
    return () => clearInterval(timer);
  }, [notifications.length]);

  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${String(mins).padStart(2, '0')}:${String(secs).padStart(2, '0')}`;
  };

  const getStatusColor = (status) => {
    const colors = {
      'SAFE': '#10b981',
      'WARNING': '#f59e0b',
      'DANGER': '#ef4444'
    };
    return colors[status] || '#94a3b8';
  };

  const getStatusBg = (status) => {
    const colors = {
      'SAFE': 'rgba(16, 185, 129, 0.1)',
      'WARNING': 'rgba(245, 158, 11, 0.1)',
      'DANGER': 'rgba(239, 68, 68, 0.1)'
    };
    return colors[status] || 'rgba(148, 163, 184, 0.1)';
  };

  // Backend offline state
  if (!backendOnline) {
    return (
      <div className="live-feed offline">
        <div className="offline-container">
          <div className="offline-content">
            <div className="offline-icon-wrapper">
              <Camera className="offline-icon" />
            </div>
            <h2 className="offline-title">Backend Server Offline</h2>
            <p className="offline-description">
              Start the Flask API server first, then come back here.
            </p>
            <div className="offline-command">
              <code>python backend/api/server.py</code>
            </div>
            <button 
              className="offline-refresh-btn"
              onClick={() => window.location.reload()}
            >
              <RefreshCw className="offline-refresh-icon" />
              Refresh
            </button>
          </div>
        </div>
      </div>
    );
  }

  const statusColor = getStatusColor(stats.status);
  const statusBg = getStatusBg(stats.status);

  // Stat items for 2-column compact layout
  const statItems = [
    { label: 'DISTANCE', value: `${stats.distance_cm || 0} cm`, icon: Ruler },
    { label: 'PITCH', value: `${stats.pitch_deg || 0}°`, icon: Activity },
    { label: 'YAW', value: `${stats.yaw_deg || 0}°`, icon: Activity },
    { label: 'SHOULDER', value: `${stats.shoulder_deg || 0}°`, icon: Activity },
    { label: 'EYE OPEN', value: stats.eye_open || 0, icon: Eye },
    { label: 'BLINKS', value: stats.total_blinks || 0, icon: Eye },
    { label: 'BLINK RATE', value: `${stats.blink_rate || 0}/min`, icon: Zap },
    { label: 'INFERENCE', value: `${stats.inference_ms || 0} ms`, icon: Zap },
    { label: 'NEXT BREAK', value: stats.countdown || '02:00', icon: Clock },
    { label: 'FRAMES', value: stats.frame_count || 0, icon: Activity },
  ];

  return (
    <div className="live-feed">
      {/* Header */}
      <div className="live-header">
        <div className="header-left">
          <div className="header-badge">
            <span className="badge-dot"></span>
            <span>Live Monitor</span>
          </div>
          <h1 className="page-title">Live Posture Monitor</h1>
          <p className="page-subtitle">Real-time AI-powered ergonomic analysis</p>
        </div>
        <div className="header-right">
          {status === 'idle' && (
            <button onClick={handleStart} className="btn-start">
              <Play className="btn-icon" />
              Start Monitor
            </button>
          )}
          {status === 'running' && (
            <button onClick={handleStop} className="btn-stop">
              <Square className="btn-icon" />
              Stop & Generate PDF
            </button>
          )}
          {(status === 'stopping' || status === 'pdf_generating') && (
            <div className="btn-generating">
              <Loader2 className="btn-icon spinning" />
              Generating PDF Report...
            </div>
          )}
        </div>
      </div>

      {/* Main Content - Side by Side */}
      <div className="live-content">
        {/* Video Feed */}
        <div className="video-container">
          <div className="video-wrapper">
            {status === 'running' ? (
              <div className="video-feed">
                <video
                  ref={videoRef}
                  autoPlay
                  playsInline
                  muted
                  className="video-stream"
                />
                
                {/* Live Badge */}
                <div className="live-badge">
                  <span className="live-dot"></span>
                  <span className="live-text">LIVE</span>
                  <span className="live-time">{formatTime(sessionTime)}</span>
                </div>

                {/* Status Overlay */}
                {stats.status && (
                  <div className={`status-overlay ${stats.status.toLowerCase()}`}>
                    <span className="status-dot"></span>
                    <span className="status-text">{stats.status}</span>
                  </div>
                )}

                {/* Posture Warning Overlay */}
                {stats?.active_alerts?.includes('POSTURE') && (
                  <div className="warning-overlay">
                    <AlertTriangle className="warning-icon" />
                    <span className="warning-text">POSTURE WARNING</span>
                  </div>
                )}

                {/* Break Alert Overlay */}
                {stats?.active_alerts?.includes('BREAK') && (
                  <div className="break-overlay">
                    <button 
                      onClick={() => handleDismissAlert('BREAK')}
                      className="break-dismiss"
                    >
                      <X className="dismiss-icon" />
                    </button>
                    <div className="break-content">
                      <span className="break-emoji">👁️</span>
                      <h2 className="break-title">20-20-20 RULE</h2>
                      <p className="break-message">
                        Look at something 20 feet away for 20 seconds
                      </p>
                    </div>
                  </div>
                )}

                {/* Water Reminder */}
                {stats?.active_alerts?.includes('WATER') && (
                  <div className="water-overlay">
                    <button 
                      onClick={() => handleDismissAlert('WATER')}
                      className="water-dismiss"
                    >
                      <X className="dismiss-icon" />
                    </button>
                    <div className="water-content">
                      <span className="water-emoji">💧</span>
                      <span className="water-text">Hydration Reminder</span>
                    </div>
                  </div>
                )}
              </div>
            ) : (
              <div className="video-placeholder">
                <div className="placeholder-content">
                  <div className="placeholder-icon-wrapper">
                    <Camera className="placeholder-icon" />
                  </div>
                  <h3 className="placeholder-title">
                    {status === 'idle' ? 'Ready to Start' : 'Processing...'}
                  </h3>
                  <p className="placeholder-text">
                    {status === 'idle' 
                      ? 'Click "Start Monitor" to begin your session.' 
                      : 'Please wait while we prepare your session...'}
                  </p>
                </div>
              </div>
            )}

            {/* Video Controls */}
            <div className="video-controls">
              <button 
                className="control-btn"
                onClick={() => setIsFullscreen(!isFullscreen)}
              >
                {isFullscreen ? 
                  <Minimize2 className="control-icon" /> : 
                  <Maximize2 className="control-icon" />
                }
              </button>
            </div>
          </div>

          {/* Notifications */}
          {notifications.length > 0 && (
            <div className="notifications-container">
              {notifications.map((notif) => {
                const config = ALERT_CONFIG[notif.type];
                if (!config) return null;
                const elapsed = Math.floor((Date.now() - notif.timestamp) / 1000);
                const remaining = Math.max(0, 60 - elapsed);
                return (
                  <div key={notif.type} className="notification-card">
                    <div className="notification-icon" style={{ background: config.gradient }}>
                      <span>{config.icon}</span>
                    </div>
                    <div className="notification-content">
                      <h4 className="notification-title">{config.title}</h4>
                      <p className="notification-message">{config.message}</p>
                      <span className="notification-timer">Auto-dismiss in {remaining}s</span>
                    </div>
                    <button
                      onClick={() => handleDismissAlert(notif.type)}
                      className="notification-action"
                    >
                      <CheckCircle className="action-icon" />
                      Accept
                    </button>
                  </div>
                );
              })}
            </div>
          )}
        </div>

        {/* Stats Sidebar - Compact 2-Column Layout */}
        {status === 'running' && (
          <div className="stats-sidebar-compact">
            {/* Status Header */}
            <div className="stats-status-header" style={{ background: statusBg }}>
              <div className="stats-status-label">LIVE METRICS</div>
              <div className="stats-status-value" style={{ color: statusColor }}>
                {stats.status || '—'}
              </div>
            </div>

            {/* 2-Column Stats Grid */}
            <div className="stats-grid-compact">
              {statItems.map((item, index) => (
                <div key={index} className="stat-item-compact">
                  <div className="stat-item-label">
                    {item.icon && <item.icon className="stat-item-icon" />}
                    <span>{item.label}</span>
                  </div>
                  <div className="stat-item-value">{item.value}</div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* PDF Ready Banner */}
      {pdfPath && status === 'idle' && (
        <div className="pdf-banner">
          <div className="pdf-banner-content">
            <div className="pdf-banner-icon">
              <FileText className="pdf-icon" />
            </div>
            <div className="pdf-banner-info">
              <h4 className="pdf-banner-title">PDF Report Generated Successfully!</h4>
              <p className="pdf-banner-subtitle">Your AI ergonomic report is ready.</p>
            </div>
            <span className="pdf-banner-path">{pdfPath}</span>
          </div>
        </div>
      )}
    </div>
  );
}