// src/pages/Reports.js
import React, { useState, useMemo } from 'react';
import { 
  FileText, 
  Download, 
  Calendar, 
  Search,
  Filter,
  ArrowUpDown,
  Eye,
  Trash2,
  TrendingUp,
  TrendingDown,
  BarChart3,
  PieChart,
  Clock,
  User,
  CheckCircle,
  AlertCircle,
  MoreVertical,
  ChevronRight,
  Sparkles,
  FileArchive
} from 'lucide-react';
import './Reports.css';

export default function Reports() {
  const [searchTerm, setSearchTerm] = useState('');
  const [sortBy, setSortBy] = useState('date');
  const [sortOrder, setSortOrder] = useState('desc');
  const [selectedReport, setSelectedReport] = useState(null);
  const [viewMode, setViewMode] = useState('list');

  const reports = [
    { 
      id: 1, 
      name: 'Ergonomic_Report_Aug_14.pdf', 
      date: 'August 14, 2026', 
      size: '1.2 MB', 
      score: 94,
      status: 'excellent',
      duration: '45 mins',
      sessions: 3,
      hasRecommendations: true
    },
    { 
      id: 2, 
      name: 'Ergonomic_Report_Aug_13.pdf', 
      date: 'August 13, 2026', 
      size: '1.4 MB', 
      score: 88,
      status: 'good',
      duration: '120 mins',
      sessions: 5,
      hasRecommendations: true
    },
    { 
      id: 3, 
      name: 'Ergonomic_Report_Aug_10.pdf', 
      date: 'August 10, 2026', 
      size: '1.1 MB', 
      score: 92,
      status: 'excellent',
      duration: '60 mins',
      sessions: 2,
      hasRecommendations: false
    },
    { 
      id: 4, 
      name: 'Ergonomic_Report_Aug_05.pdf', 
      date: 'August 05, 2026', 
      size: '1.5 MB', 
      score: 75,
      status: 'fair',
      duration: '90 mins',
      sessions: 4,
      hasRecommendations: true
    },
    { 
      id: 5, 
      name: 'Ergonomic_Report_Jul_28.pdf', 
      date: 'July 28, 2026', 
      size: '1.3 MB', 
      score: 82,
      status: 'good',
      duration: '55 mins',
      sessions: 3,
      hasRecommendations: false
    },
    { 
      id: 6, 
      name: 'Ergonomic_Report_Jul_20.pdf', 
      date: 'July 20, 2026', 
      size: '1.6 MB', 
      score: 68,
      status: 'poor',
      duration: '75 mins',
      sessions: 3,
      hasRecommendations: true
    },
  ];

  const getStatusConfig = (status) => {
    const configs = {
      'excellent': { 
        label: 'Excellent', 
        color: '#10b981', 
        bg: 'rgba(16, 185, 129, 0.1)',
        icon: CheckCircle,
        barColor: '#10b981'
      },
      'good': { 
        label: 'Good', 
        color: '#3b82f6', 
        bg: 'rgba(37, 99, 235, 0.1)',
        icon: CheckCircle,
        barColor: '#3b82f6'
      },
      'fair': { 
        label: 'Fair', 
        color: '#f59e0b', 
        bg: 'rgba(245, 158, 11, 0.1)',
        icon: AlertCircle,
        barColor: '#f59e0b'
      },
      'poor': { 
        label: 'Needs Improvement', 
        color: '#ef4444', 
        bg: 'rgba(239, 68, 68, 0.1)',
        icon: AlertCircle,
        barColor: '#ef4444'
      },
    };
    return configs[status] || configs['good'];
  };

  const getScoreColor = (score) => {
    if (score >= 90) return '#10b981';
    if (score >= 75) return '#3b82f6';
    if (score >= 60) return '#f59e0b';
    return '#ef4444';
  };

  const getScoreBarWidth = (score) => {
    // Map score to percentage width (minimum 10%, maximum 100%)
    return Math.max(10, score);
  };

  const filteredReports = useMemo(() => {
    let result = [...reports];
    
    // Search filter
    if (searchTerm) {
      result = result.filter(report => 
        report.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
        report.date.toLowerCase().includes(searchTerm.toLowerCase())
      );
    }
    
    // Sorting
    result.sort((a, b) => {
      let comparison = 0;
      switch (sortBy) {
        case 'date':
          comparison = new Date(a.date) - new Date(b.date);
          break;
        case 'score':
          comparison = a.score - b.score;
          break;
        case 'name':
          comparison = a.name.localeCompare(b.name);
          break;
        case 'size':
          comparison = parseFloat(a.size) - parseFloat(b.size);
          break;
        default:
          comparison = 0;
      }
      return sortOrder === 'asc' ? comparison : -comparison;
    });
    
    return result;
  }, [reports, searchTerm, sortBy, sortOrder]);

  const handleSort = (field) => {
    if (sortBy === field) {
      setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc');
    } else {
      setSortBy(field);
      setSortOrder('desc');
    }
  };

  const handleDownload = (report) => {
    // Simulate download
    const link = document.createElement('a');
    link.href = '#';
    link.download = report.name;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  const handleDelete = (reportId) => {
    if (window.confirm('Are you sure you want to delete this report?')) {
      // Delete logic would go here
      console.log('Deleting report:', reportId);
    }
  };

  const getStats = () => {
    const total = reports.length;
    const avgScore = Math.round(reports.reduce((sum, r) => sum + r.score, 0) / total);
    const excellent = reports.filter(r => r.status === 'excellent').length;
    const needsWork = reports.filter(r => r.status === 'poor' || r.status === 'fair').length;
    return { total, avgScore, excellent, needsWork };
  };

  const stats = getStats();

  return (
    <div className="reports-page">
      {/* Header */}
      <div className="reports-header">
        <div className="header-left">
          <div className="header-badge">
            <Sparkles className="badge-icon" />
            <span>AI-Generated Reports</span>
          </div>
          <h1 className="page-title">Reports Archive</h1>
          <p className="page-subtitle">
            Access your historical AI-generated ergonomic insights and recommendations
          </p>
        </div>
        <div className="header-right">
          <button className="header-action-btn primary">
            <FileArchive className="action-icon" />
            <span>Generate New</span>
          </button>
        </div>
      </div>

      {/* Stats Cards */}
      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-icon-wrapper blue">
            <FileText className="stat-icon" />
          </div>
          <div className="stat-content">
            <span className="stat-value">{stats.total}</span>
            <span className="stat-label">Total Reports</span>
          </div>
        </div>
        <div className="stat-card">
          <div className="stat-icon-wrapper green">
            <BarChart3 className="stat-icon" />
          </div>
          <div className="stat-content">
            <span className="stat-value">{stats.avgScore}%</span>
            <span className="stat-label">Average Score</span>
          </div>
        </div>
        <div className="stat-card">
          <div className="stat-icon-wrapper success">
            <CheckCircle className="stat-icon" />
          </div>
          <div className="stat-content">
            <span className="stat-value">{stats.excellent}</span>
            <span className="stat-label">Excellent Reports</span>
          </div>
        </div>
        <div className="stat-card">
          <div className="stat-icon-wrapper warning">
            <AlertCircle className="stat-icon" />
          </div>
          <div className="stat-content">
            <span className="stat-value">{stats.needsWork}</span>
            <span className="stat-label">Needs Improvement</span>
          </div>
        </div>
      </div>

      {/* Toolbar */}
      <div className="reports-toolbar">
        <div className="toolbar-left">
          <div className="search-wrapper">
            <Search className="search-icon" />
            <input
              type="text"
              className="search-input"
              placeholder="Search reports..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
            />
            {searchTerm && (
              <button 
                className="search-clear"
                onClick={() => setSearchTerm('')}
              >
                ✕
              </button>
            )}
          </div>
          <div className="view-toggle">
            <button 
              className={`view-btn ${viewMode === 'list' ? 'active' : ''}`}
              onClick={() => setViewMode('list')}
            >
              <FileText className="view-icon" />
            </button>
            <button 
              className={`view-btn ${viewMode === 'grid' ? 'active' : ''}`}
              onClick={() => setViewMode('grid')}
            >
              <PieChart className="view-icon" />
            </button>
          </div>
        </div>
        <div className="toolbar-right">
          <div className="filter-group">
            <Filter className="filter-icon" />
            <select className="filter-select">
              <option value="all">All Reports</option>
              <option value="excellent">Excellent</option>
              <option value="good">Good</option>
              <option value="fair">Fair</option>
              <option value="poor">Needs Improvement</option>
            </select>
          </div>
        </div>
      </div>

      {/* Reports List */}
      {viewMode === 'list' ? (
        <div className="reports-list">
          <div className="reports-table-header">
            <div className="header-cell name" onClick={() => handleSort('name')}>
              <span>Report Name</span>
              <ArrowUpDown className="sort-icon" />
            </div>
            <div className="header-cell date" onClick={() => handleSort('date')}>
              <span>Date</span>
              <ArrowUpDown className="sort-icon" />
            </div>
            <div className="header-cell score" onClick={() => handleSort('score')}>
              <span>Score</span>
              <ArrowUpDown className="sort-icon" />
            </div>
            <div className="header-cell status">Status</div>
            <div className="header-cell actions">Actions</div>
          </div>

          {filteredReports.length === 0 ? (
            <div className="empty-state">
              <FileText className="empty-icon" />
              <h3 className="empty-title">No reports found</h3>
              <p className="empty-description">
                Try adjusting your search or filter criteria
              </p>
            </div>
          ) : (
            filteredReports.map((report, index) => {
              const statusConfig = getStatusConfig(report.status);
              const StatusIcon = statusConfig.icon;
              const scoreColor = getScoreColor(report.score);
              const barWidth = getScoreBarWidth(report.score);
              
              return (
                <div 
                  key={report.id} 
                  className="report-item"
                  style={{ animationDelay: `${index * 0.05}s` }}
                >
                  <div className="report-item-content">
                    <div className="report-info">
                      <div className="report-icon-wrapper">
                        <FileText className="report-icon" />
                      </div>
                      <div className="report-details">
                        <div className="report-name-wrapper">
                          <span className="report-name">{report.name}</span>
                          {report.hasRecommendations && (
                            <span className="recommendation-badge">
                              <Sparkles className="recommendation-icon" />
                              Recommendations
                            </span>
                          )}
                        </div>
                        <div className="report-meta">
                          <span className="meta-item">
                            <Calendar className="meta-icon" />
                            {report.date}
                          </span>
                          <span className="meta-divider">•</span>
                          <span className="meta-item">
                            <Clock className="meta-icon" />
                            {report.duration}
                          </span>
                          <span className="meta-divider">•</span>
                          <span className="meta-item">
                            <User className="meta-icon" />
                            {report.sessions} sessions
                          </span>
                          <span className="meta-divider">•</span>
                          <span className="meta-item">{report.size}</span>
                        </div>
                      </div>
                    </div>

                    <div className="report-score">
                      <div className="score-bar-wrapper">
                        <div 
                          className="score-bar"
                          style={{ 
                            width: `${barWidth}%`,
                            backgroundColor: scoreColor
                          }}
                        />
                      </div>
                      <span className="score-value" style={{ color: scoreColor }}>
                        {report.score}%
                      </span>
                    </div>

                    <div className="report-status">
                      <span 
                        className="status-badge"
                        style={{ 
                          background: statusConfig.bg,
                          color: statusConfig.color
                        }}
                      >
                        <StatusIcon className="status-icon" />
                        {statusConfig.label}
                      </span>
                    </div>

                    <div className="report-actions">
                      <button 
                        className="action-btn view"
                        onClick={() => setSelectedReport(report)}
                      >
                        <Eye className="action-icon" />
                      </button>
                      <button 
                        className="action-btn download"
                        onClick={() => handleDownload(report)}
                      >
                        <Download className="action-icon" />
                      </button>
                      <button 
                        className="action-btn delete"
                        onClick={() => handleDelete(report.id)}
                      >
                        <Trash2 className="action-icon" />
                      </button>
                      <button className="action-btn more">
                        <MoreVertical className="action-icon" />
                      </button>
                    </div>
                  </div>
                </div>
              );
            })
          )}
        </div>
      ) : (
        <div className="reports-grid-view">
          {filteredReports.map((report) => {
            const statusConfig = getStatusConfig(report.status);
            const StatusIcon = statusConfig.icon;
            const scoreColor = getScoreColor(report.score);
            
            return (
              <div key={report.id} className="report-grid-card">
                <div className="grid-card-header">
                  <div className="grid-card-icon">
                    <FileText className="grid-icon" />
                  </div>
                  <div className="grid-card-badge" style={{ 
                    background: statusConfig.bg,
                    color: statusConfig.color
                  }}>
                    <StatusIcon className="grid-badge-icon" />
                    {statusConfig.label}
                  </div>
                </div>
                <h4 className="grid-card-name">{report.name}</h4>
                <div className="grid-card-meta">
                  <span className="grid-meta-item">
                    <Calendar className="grid-meta-icon" />
                    {report.date}
                  </span>
                  <span className="grid-meta-item">{report.size}</span>
                </div>
                <div className="grid-card-score">
                  <div className="grid-score-wrapper">
                    <div 
                      className="grid-score-bar"
                      style={{ 
                        width: `${getScoreBarWidth(report.score)}%`,
                        backgroundColor: scoreColor
                      }}
                    />
                  </div>
                  <span className="grid-score-value" style={{ color: scoreColor }}>
                    {report.score}%
                  </span>
                </div>
                <div className="grid-card-actions">
                  <button className="grid-action-btn">
                    <Eye className="grid-action-icon" />
                    View
                  </button>
                  <button className="grid-action-btn primary">
                    <Download className="grid-action-icon" />
                    Download
                  </button>
                </div>
              </div>
            );
          })}
        </div>
      )}

      {/* Footer Info */}
      <div className="reports-footer">
        <p>
          New reports are generated automatically when you end a live session.
          <span className="footer-highlight"> AI-powered insights</span> available for every session.
        </p>
      </div>
    </div>
  );
}