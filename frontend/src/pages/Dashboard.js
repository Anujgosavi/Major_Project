// src/pages/Dashboard.js
import React, { useState, useEffect } from 'react';
import { 
  Activity, 
  Clock, 
  ShieldAlert, 
  Eye, 
  TrendingUp, 
  TrendingDown,
  ArrowUpRight,
  ArrowDownRight,
  Calendar,
  Filter,
  Download,
  RefreshCw,
  AlertCircle,
  CheckCircle,
  XCircle,
  BarChart3,
  LineChart,
  PieChart,
  ChevronRight,
  MoreVertical,
  Bell,
  Settings
} from 'lucide-react';
import './Dashboard.css';

export default function Dashboard() {
  const [isLoading, setIsLoading] = useState(true);
  const [selectedPeriod, setSelectedPeriod] = useState('week');
  const [showRefresh, setShowRefresh] = useState(false);

  useEffect(() => {
    // Simulate loading
    const timer = setTimeout(() => setIsLoading(false), 800);
    return () => clearTimeout(timer);
  }, []);

  const stats = [
    { 
      name: 'Posture Score', 
      value: '94%', 
      change: '+5.2%',
      trend: 'up',
      icon: Activity, 
      color: 'green',
      bg: 'rgba(16, 185, 129, 0.1)',
      description: 'Above average'
    },
    { 
      name: 'Avg Screen Time', 
      value: '4.2 hrs', 
      change: '-0.8%',
      trend: 'down',
      icon: Clock, 
      color: 'blue',
      bg: 'rgba(37, 99, 235, 0.1)',
      description: '2% decrease'
    },
    { 
      name: 'Safety Violations', 
      value: '3', 
      change: '+1.2%',
      trend: 'up',
      icon: ShieldAlert, 
      color: 'red',
      bg: 'rgba(239, 68, 68, 0.1)',
      description: 'Needs attention'
    },
    { 
      name: 'Avg Blink Rate', 
      value: '14 / min', 
      change: '+3.1%',
      trend: 'up',
      icon: Eye, 
      color: 'purple',
      bg: 'rgba(124, 58, 237, 0.1)',
      description: 'Healthy range'
    },
    {
      name: 'Global Notifications',
      value: 'System Alerts',
      change: 'Enabled',
      trend: 'up',
      icon: Bell,
      color: 'blue',
      bg: 'rgba(37, 99, 235, 0.1)',
      description: 'Implementation pending...'
    },
    {
      name: 'System Settings',
      value: 'Preferences',
      change: 'Configured',
      trend: 'up',
      icon: Settings,
      color: 'green',
      bg: 'rgba(16, 185, 129, 0.1)',
      description: 'Implementation pending...'
    }
  ];

  const recentSessions = [
    { 
      id: 1,
      date: 'Today, 10:00 AM',
      duration: '45 mins',
      status: 'Excellent',
      score: 96,
      posture: 'Good',
      breaks: 3
    },
    { 
      id: 2,
      date: 'Yesterday, 2:00 PM',
      duration: '120 mins',
      status: 'Needs Improvement',
      score: 72,
      posture: 'Fair',
      breaks: 1
    },
    { 
      id: 3,
      date: 'Yesterday, 9:30 AM',
      duration: '60 mins',
      status: 'Good',
      score: 85,
      posture: 'Good',
      breaks: 2
    },
    { 
      id: 4,
      date: 'Jan 15, 3:00 PM',
      duration: '90 mins',
      status: 'Excellent',
      score: 92,
      posture: 'Excellent',
      breaks: 4
    },
  ];

  const getStatusConfig = (status) => {
    const configs = {
      'Excellent': { icon: CheckCircle, color: 'success', bg: 'rgba(16, 185, 129, 0.1)' },
      'Good': { icon: CheckCircle, color: 'info', bg: 'rgba(37, 99, 235, 0.1)' },
      'Needs Improvement': { icon: AlertCircle, color: 'warning', bg: 'rgba(245, 158, 11, 0.1)' },
      'Poor': { icon: XCircle, color: 'danger', bg: 'rgba(239, 68, 68, 0.1)' },
    };
    return configs[status] || configs['Good'];
  };

  const getScoreColor = (score) => {
    if (score >= 90) return 'var(--score-excellent)';
    if (score >= 75) return 'var(--score-good)';
    if (score >= 60) return 'var(--score-fair)';
    return 'var(--score-poor)';
  };

  return (
    <div className="dashboard-enhanced">
      {/* Loading State */}
      {isLoading ? (
        <div className="dashboard-loader">
          <div className="loader-spinner">
            <div className="spinner-ring"></div>
          </div>
          <p>Loading dashboard...</p>
        </div>
      ) : (
        <>
          {/* Page Header */}
          <div className="dashboard-header">
            <div className="header-left">
              <div className="header-badge">
                <span className="badge-dot"></span>
                Live Data
              </div>
              <h1 className="page-title">Dashboard</h1>
              <p className="page-subtitle">
                Overview of your recent ergonomic sessions and health metrics
              </p>
            </div>
            <div className="header-right">
              <div className="period-selector">
                <button 
                  className={`period-btn ${selectedPeriod === 'day' ? 'active' : ''}`}
                  onClick={() => setSelectedPeriod('day')}
                >
                  Day
                </button>
                <button 
                  className={`period-btn ${selectedPeriod === 'week' ? 'active' : ''}`}
                  onClick={() => setSelectedPeriod('week')}
                >
                  Week
                </button>
                <button 
                  className={`period-btn ${selectedPeriod === 'month' ? 'active' : ''}`}
                  onClick={() => setSelectedPeriod('month')}
                >
                  Month
                </button>
              </div>
              <button 
                className="action-btn"
                onClick={() => setShowRefresh(!showRefresh)}
              >
                <RefreshCw className={`action-icon ${showRefresh ? 'spinning' : ''}`} />
                <span>Refresh</span>
              </button>
              <button className="action-btn primary">
                <Download className="action-icon" />
                <span>Export</span>
              </button>
            </div>
          </div>

          {/* Stats Grid */}
          <div className="stats-grid">
            {stats.map((item, index) => {
              const Icon = item.icon;
              const TrendIcon = item.trend === 'up' ? TrendingUp : TrendingDown;
              return (
                <div 
                  key={item.name} 
                  className="stat-card"
                  style={{ animationDelay: `${index * 0.1}s` }}
                >
                  <div className="stat-card-header">
                    <div className="stat-icon-wrapper" style={{ background: item.bg }}>
                      <Icon className={`stat-icon ${item.color}`} />
                    </div>
                    <span className="stat-change">
                      <TrendIcon className={`change-icon ${item.trend}`} />
                      {item.change}
                    </span>
                  </div>
                  <div className="stat-card-body">
                    <h3 className="stat-value">{item.value}</h3>
                    <p className="stat-name">{item.name}</p>
                    <p className="stat-description">{item.description}</p>
                  </div>
                </div>
              );
            })}
          </div>

          {/* Charts Section */}
          <div className="charts-grid">
            <div className="chart-card">
              <div className="chart-header">
                <div className="chart-title-wrapper">
                  <BarChart3 className="chart-icon" />
                  <div>
                    <h3 className="chart-title">Weekly Activity</h3>
                    <p className="chart-subtitle">Posture score trend over the last 7 days</p>
                  </div>
                </div>
                <button className="chart-more-btn">
                  <MoreVertical className="more-icon" />
                </button>
              </div>
              <div className="chart-body">
                <div className="chart-placeholder">
                  <div className="chart-bars">
                    {[85, 92, 78, 88, 95, 82, 94].map((value, index) => (
                      <div key={index} className="chart-bar-wrapper">
                        <div 
                          className="chart-bar"
                          style={{ 
                            height: `${value}%`,
                            backgroundColor: getScoreColor(value),
                            animationDelay: `${index * 0.1}s`
                          }}
                        >
                          <span className="bar-label">{value}%</span>
                        </div>
                        <span className="bar-day">Day {index + 1}</span>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </div>

            <div className="chart-card">
              <div className="chart-header">
                <div className="chart-title-wrapper">
                  <PieChart className="chart-icon" />
                  <div>
                    <h3 className="chart-title">Posture Distribution</h3>
                    <p className="chart-subtitle">Breakdown of your posture quality</p>
                  </div>
                </div>
                <button className="chart-more-btn">
                  <MoreVertical className="more-icon" />
                </button>
              </div>
              <div className="chart-body">
                <div className="donut-placeholder">
                  <div className="donut-chart">
                    <div className="donut-segment" style={{ 
                      transform: 'rotate(0deg)',
                      background: 'conic-gradient(var(--score-excellent) 0% 65%, var(--score-good) 65% 80%, var(--score-fair) 80% 90%, var(--score-poor) 90% 100%)'
                    }}></div>
                    <div className="donut-center">
                      <span className="donut-value">88%</span>
                      <span className="donut-label">Overall</span>
                    </div>
                  </div>
                  <div className="donut-legend">
                    <div className="legend-item">
                      <span className="legend-color excellent"></span>
                      <span className="legend-label">Excellent (65%)</span>
                    </div>
                    <div className="legend-item">
                      <span className="legend-color good"></span>
                      <span className="legend-label">Good (15%)</span>
                    </div>
                    <div className="legend-item">
                      <span className="legend-color fair"></span>
                      <span className="legend-label">Fair (10%)</span>
                    </div>
                    <div className="legend-item">
                      <span className="legend-color poor"></span>
                      <span className="legend-label">Poor (10%)</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Recent Sessions Table */}
          <div className="sessions-card">
            <div className="sessions-header">
              <div className="sessions-title-wrapper">
                <LineChart className="sessions-icon" />
                <div>
                  <h3 className="sessions-title">Recent Sessions</h3>
                  <p className="sessions-subtitle">Your latest ergonomic monitoring sessions</p>
                </div>
              </div>
              <div className="sessions-actions">
                <button className="filter-btn">
                  <Filter className="filter-icon" />
                  <span>Filter</span>
                </button>
                <button className="view-all-btn">
                  <span>View All</span>
                  <ChevronRight className="view-all-icon" />
                </button>
              </div>
            </div>

            <div className="sessions-table-wrapper">
              <table className="sessions-table">
                <thead>
                  <tr>
                    <th>Date & Time</th>
                    <th>Duration</th>
                    <th>Score</th>
                    <th>Posture</th>
                    <th>Breaks</th>
                    <th>Status</th>
                    <th></th>
                  </tr>
                </thead>
                <tbody>
                  {recentSessions.map((session, index) => {
                    const statusConfig = getStatusConfig(session.status);
                    const StatusIcon = statusConfig.icon;
                    return (
                      <tr key={session.id} style={{ animationDelay: `${index * 0.05}s` }}>
                        <td>
                          <div className="session-date">
                            <Calendar className="session-date-icon" />
                            <span>{session.date}</span>
                          </div>
                        </td>
                        <td>
                          <span className="session-duration">{session.duration}</span>
                        </td>
                        <td>
                          <div className="score-indicator">
                            <div 
                              className="score-bar"
                              style={{ 
                                width: `${session.score}%`,
                                backgroundColor: getScoreColor(session.score)
                              }}
                            />
                            <span className="score-text">{session.score}%</span>
                          </div>
                        </td>
                        <td>
                          <span className="posture-badge" style={{ 
                            background: getStatusConfig(session.posture).bg 
                          }}>
                            {session.posture}
                          </span>
                        </td>
                        <td>
                          <span className="breaks-count">{session.breaks}</span>
                        </td>
                        <td>
                          <span className={`status-badge ${statusConfig.color}`}>
                            <StatusIcon className="status-icon" />
                            {session.status}
                          </span>
                        </td>
                        <td>
                          <button className="row-action-btn">
                            <MoreVertical className="row-action-icon" />
                          </button>
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          </div>
        </>
      )}
    </div>
  );
}