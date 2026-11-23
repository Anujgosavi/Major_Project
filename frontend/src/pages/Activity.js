// src/pages/Activity.js
import React, { useState, useEffect } from 'react';
import { 
  Activity as ActivityIcon, 
  Clock, 
  Eye, 
  Download, 
  CheckCircle, 
  AlertTriangle, 
  XCircle, 
  RefreshCw, 
  Search, 
  Filter, 
  ArrowRight,
  TrendingUp,
  Layers
} from 'lucide-react';
import { Link } from 'react-router-dom';
import api from '../utils/api';
import './Activity.css';

export default function Activity() {
  const [sessions, setSessions] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState('all');

  const fetchSessions = async () => {
    setIsLoading(true);
    try {
      const res = await api.get('/api/sessions?limit=50');
      if (res.ok) {
        const data = await res.json();
        setSessions(data.sessions || []);
      }
    } catch (err) {
      console.error('Failed to fetch activity sessions:', err);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchSessions();
  }, []);

  const totalSessions = sessions.length;
  const totalSeconds = sessions.reduce((acc, s) => acc + (s.duration_sec || 0), 0);
  const totalMinutes = Math.round(totalSeconds / 60);
  const totalFrames = sessions.reduce((acc, s) => acc + (s.frame_count || 0), 0);

  const filteredSessions = sessions.filter((s) => {
    const rawStatus = (s.final_stats?.status || s.status || 'SAFE').toUpperCase();
    if (statusFilter !== 'all' && rawStatus !== statusFilter) return false;

    if (searchTerm) {
      const term = searchTerm.toLowerCase();
      const idMatch = s.id?.toLowerCase().includes(term);
      const dateStr = s.started_at ? new Date(s.started_at).toLocaleDateString().toLowerCase() : '';
      return idMatch || dateStr.includes(term);
    }
    return true;
  });

  const getStatusBadge = (statusStr) => {
    const st = (statusStr || 'SAFE').toUpperCase();
    if (st === 'SAFE' || st === 'COMPLETED') {
      return (
        <span className="activity-badge badge-safe">
          <CheckCircle className="badge-icon" />
          Optimal
        </span>
      );
    } else if (st === 'WARNING') {
      return (
        <span className="activity-badge badge-warning">
          <AlertTriangle className="badge-icon" />
          Warning
        </span>
      );
    } else {
      return (
        <span className="activity-badge badge-danger">
          <XCircle className="badge-icon" />
          Strain
        </span>
      );
    }
  };

  return (
    <div className="activity-page">
      {/* Header */}
      <div className="activity-header">
        <div className="header-left">
          <div className="header-badge">
            <ActivityIcon className="badge-icon" />
            <span>Telemetry History</span>
          </div>
          <h1 className="page-title">Session Activity</h1>
          <p className="page-subtitle">
            Comprehensive real-time telemetry logs and posture analytics from your monitoring sessions
          </p>
        </div>
        <div className="header-right">
          <button 
            className="refresh-btn" 
            onClick={fetchSessions} 
            disabled={isLoading}
            title="Refresh sessions"
          >
            <RefreshCw className={`btn-icon ${isLoading ? 'spinning' : ''}`} />
            Refresh
          </button>
          <Link to="/live" className="cta-live-btn">
            <span>New Live Session</span>
            <ArrowRight className="btn-icon" />
          </Link>
        </div>
      </div>

      {/* Summary KPI Cards */}
      <div className="activity-stats-grid">
        <div className="activity-stat-card">
          <div className="stat-card-icon primary">
            <Layers className="stat-icon" />
          </div>
          <div className="stat-card-content">
            <span className="stat-label">Total Sessions</span>
            <span className="stat-value">{totalSessions}</span>
          </div>
        </div>

        <div className="activity-stat-card">
          <div className="stat-card-icon secondary">
            <Clock className="stat-icon" />
          </div>
          <div className="stat-card-content">
            <span className="stat-label">Monitored Time</span>
            <span className="stat-value">{totalMinutes} <span className="stat-unit">mins</span></span>
          </div>
        </div>

        <div className="activity-stat-card">
          <div className="stat-card-icon success">
            <Eye className="stat-icon" />
          </div>
          <div className="stat-card-content">
            <span className="stat-label">Frames Evaluated</span>
            <span className="stat-value">{totalFrames.toLocaleString()}</span>
          </div>
        </div>

        <div className="activity-stat-card">
          <div className="stat-card-icon warning">
            <TrendingUp className="stat-icon" />
          </div>
          <div className="stat-card-content">
            <span className="stat-label">Logged Telemetry</span>
            <span className="stat-value">{sessions.filter(s => s.has_pdf).length} <span className="stat-unit">PDFs</span></span>
          </div>
        </div>
      </div>

      {/* Controls & Filter Bar */}
      <div className="activity-controls">
        <div className="search-box">
          <Search className="search-icon" />
          <input 
            type="text" 
            placeholder="Search by session ID or date..." 
            value={searchTerm} 
            onChange={(e) => setSearchTerm(e.target.value)}
          />
        </div>

        <div className="filter-group">
          <Filter className="filter-icon" />
          <select 
            value={statusFilter} 
            onChange={(e) => setStatusFilter(e.target.value)}
            className="filter-select"
          >
            <option value="all">All Statuses</option>
            <option value="SAFE">Optimal / Safe</option>
            <option value="WARNING">Warning</option>
            <option value="DANGER">Strain / Danger</option>
          </select>
        </div>
      </div>

      {/* Sessions Table */}
      <div className="activity-table-card">
        {isLoading ? (
          <div className="activity-loading">
            <RefreshCw className="spinning-large" />
            <p>Loading session logs...</p>
          </div>
        ) : filteredSessions.length === 0 ? (
          <div className="activity-empty">
            <div className="empty-icon-wrap">
              <ActivityIcon className="empty-icon" />
            </div>
            <h3>No Sessions Found</h3>
            <p>You haven't recorded any posture sessions matching the current criteria.</p>
            <Link to="/live" className="empty-cta-btn">Start Your First Session</Link>
          </div>
        ) : (
          <div className="table-responsive">
            <table className="activity-table">
              <thead>
                <tr>
                  <th>Session ID & Date</th>
                  <th>Duration</th>
                  <th>Frames</th>
                  <th>Posture Status</th>
                  <th>Distance Avg</th>
                  <th>Blink Rate</th>
                  <th>Report</th>
                </tr>
              </thead>
              <tbody>
                {filteredSessions.map((session) => {
                  const startDate = session.started_at ? new Date(session.started_at) : null;
                  const dateStr = startDate 
                    ? startDate.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' }) 
                    : 'Recent';
                  const timeStr = startDate 
                    ? startDate.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' }) 
                    : '';
                  const mins = Math.max(1, Math.round((session.duration_sec || 0) / 60));
                  const stats = session.final_stats || {};
                  const statusRaw = stats.status || session.status;
                  const distance = stats.distance_cm ? `${stats.distance_cm} cm` : '—';
                  const blinkRate = stats.blink_rate ? `${stats.blink_rate}/m` : '—';

                  return (
                    <tr key={session.id}>
                      <td>
                        <div className="session-id-cell">
                          <span className="session-short-id">#{session.id.slice(-6)}</span>
                          <span className="session-date-time">{dateStr} • {timeStr}</span>
                        </div>
                      </td>
                      <td>
                        <div className="duration-cell">
                          <Clock className="cell-mini-icon" />
                          <span>{mins} min{mins > 1 ? 's' : ''} ({Math.round(session.duration_sec || 0)}s)</span>
                        </div>
                      </td>
                      <td>
                        <span className="frames-cell">{session.frame_count?.toLocaleString() || 0}</span>
                      </td>
                      <td>
                        {getStatusBadge(statusRaw)}
                      </td>
                      <td>
                        <span className="metric-cell">{distance}</span>
                      </td>
                      <td>
                        <span className="metric-cell">{blinkRate}</span>
                      </td>
                      <td>
                        {session.has_pdf ? (
                          <a 
                            href={api.downloadUrl(`/api/sessions/${session.id}/pdf`)} 
                            target="_blank" 
                            rel="noreferrer"
                            className="pdf-download-pill"
                            title="Download AI Report PDF"
                          >
                            <Download className="pill-icon" />
                            PDF
                          </a>
                        ) : (
                          <span className="pdf-unavailable">—</span>
                        )}
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}
