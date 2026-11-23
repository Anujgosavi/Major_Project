// src/pages/Achievements.js
import React, { useState, useEffect } from 'react';
import { 
  CheckCircle, 
  Lock, 
  Zap, 
  Clock, 
  ShieldCheck, 
  Flame, 
  RefreshCw,
  Trophy,
  ArrowRight
} from 'lucide-react';
import { Link } from 'react-router-dom';
import api from '../utils/api';
import './Achievements.css';

export default function Achievements() {
  const [sessions, setSessions] = useState([]);
  const [isLoading, setIsLoading] = useState(true);

  const fetchSessionData = async () => {
    setIsLoading(true);
    try {
      const res = await api.get('/api/sessions?limit=100');
      if (res.ok) {
        const data = await res.json();
        setSessions(data.sessions || []);
      }
    } catch (err) {
      console.error('Failed to load achievement telemetry:', err);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchSessionData();
  }, []);

  const totalSessions = sessions.length;
  const completedSessions = sessions.filter(s => s.status === 'completed' || (s.duration_sec && s.duration_sec >= 10)).length;
  const totalSeconds = sessions.reduce((acc, s) => acc + (s.duration_sec || 0), 0);
  const totalMinutes = Math.floor(totalSeconds / 60);
  const hasReport = sessions.some(s => s.has_pdf || s.status === 'completed');

  // Define achievements dynamically calculated from real MongoDB sessions
  const achievementsList = [
    {
      id: 'first_session',
      title: 'First Session',
      description: 'Record your very first ergonomics monitoring session.',
      icon: Flame,
      color: '#f59e0b',
      unlocked: totalSessions >= 1,
      current: Math.min(totalSessions, 1),
      target: 1,
      unit: 'session',
      category: 'Milestone'
    },
    {
      id: 'twenty_min',
      title: 'Twenty Minute Watch',
      description: 'Accumulate at least 20 cumulative minutes of posture tracking.',
      icon: Clock,
      color: '#3b82f6',
      unlocked: totalMinutes >= 20,
      current: Math.min(totalMinutes, 20),
      target: 20,
      unit: 'mins',
      category: 'Endurance'
    },
    {
      id: 'consistency_builder',
      title: 'Consistency Builder',
      description: 'Complete 10 ergonomic tracking sessions to build a healthy routine.',
      icon: Zap,
      color: '#8b5cf6',
      unlocked: completedSessions >= 10,
      current: Math.min(completedSessions, 10),
      target: 10,
      unit: 'sessions',
      category: 'Dedication'
    },
    {
      id: 'ergonomic_explorer',
      title: 'Ergonomic Explorer',
      description: 'Generate and record completed AI telemetry with posture diagnostics.',
      icon: ShieldCheck,
      color: '#10b981',
      unlocked: hasReport,
      current: hasReport ? 1 : 0,
      target: 1,
      unit: 'report',
      category: 'Analysis'
    }
  ];

  const unlockedCount = achievementsList.filter(a => a.unlocked).length;
  const completionPercentage = Math.round((unlockedCount / achievementsList.length) * 100);

  return (
    <div className="achievements-page">
      {/* Header */}
      <div className="achievements-header">
        <div className="header-left">
          <div className="header-badge">
            <Trophy className="badge-icon" />
            <span>Ergonomic Milestones</span>
          </div>
          <h1 className="page-title">Achievements & Badges</h1>
          <p className="page-subtitle">
            Earn badges as you improve posture habits, maintain consistency, and avoid spinal strain
          </p>
        </div>
        <div className="header-right">
          <button 
            className="refresh-btn" 
            onClick={fetchSessionData} 
            disabled={isLoading}
            title="Refresh achievements"
          >
            <RefreshCw className={`btn-icon ${isLoading ? 'spinning' : ''}`} />
            Refresh
          </button>
        </div>
      </div>

      {/* Progress Overview Card */}
      <div className="overview-banner">
        <div className="banner-content">
          <div className="trophy-wrapper">
            <Trophy className="banner-trophy" />
          </div>
          <div className="banner-text">
            <h2>{unlockedCount} of {achievementsList.length} Badges Unlocked</h2>
            <p>Keep your posture upright and take scheduled 20-20-20 breaks to complete all milestones.</p>
            <div className="banner-progress-bar-wrap">
              <div 
                className="banner-progress-fill" 
                style={{ width: `${completionPercentage}%` }}
              ></div>
            </div>
          </div>
        </div>
        <div className="banner-stats">
          <div className="b-stat">
            <span className="b-stat-val">{totalMinutes}m</span>
            <span className="b-stat-lbl">Tracked Time</span>
          </div>
          <div className="b-stat-divider"></div>
          <div className="b-stat">
            <span className="b-stat-val">{totalSessions}</span>
            <span className="b-stat-lbl">Sessions</span>
          </div>
          <div className="b-stat-divider"></div>
          <div className="b-stat">
            <span className="b-stat-val">{completionPercentage}%</span>
            <span className="b-stat-lbl">Completed</span>
          </div>
        </div>
      </div>

      {/* Badges Grid */}
      <div className="achievements-grid">
        {achievementsList.map((ach) => {
          const Icon = ach.icon;
          const progressPercent = Math.min(100, Math.round((ach.current / ach.target) * 100));

          return (
            <div 
              key={ach.id} 
              className={`achievement-card ${ach.unlocked ? 'unlocked' : 'locked'}`}
            >
              <div className="card-top">
                <div 
                  className="badge-icon-box"
                  style={{
                    backgroundColor: ach.unlocked ? `${ach.color}20` : 'rgba(255,255,255,0.04)',
                    color: ach.unlocked ? ach.color : '#64748b',
                    borderColor: ach.unlocked ? `${ach.color}40` : 'rgba(255,255,255,0.06)'
                  }}
                >
                  <Icon className="ach-icon" />
                  {ach.unlocked && <span className="sparkle-dot"></span>}
                </div>

                <div className="status-pill-wrap">
                  {ach.unlocked ? (
                    <span className="status-pill unlocked">
                      <CheckCircle className="pill-ico" />
                      Unlocked
                    </span>
                  ) : (
                    <span className="status-pill locked">
                      <Lock className="pill-ico" />
                      Locked
                    </span>
                  )}
                </div>
              </div>

              <div className="card-body">
                <span className="category-tag">{ach.category}</span>
                <h3 className="ach-title">{ach.title}</h3>
                <p className="ach-desc">{ach.description}</p>
              </div>

              <div className="card-progress">
                <div className="progress-info">
                  <span className="progress-label">Progress</span>
                  <span className="progress-count">
                    {ach.current} / {ach.target} {ach.unit}
                  </span>
                </div>
                <div className="progress-track">
                  <div 
                    className="progress-fill"
                    style={{ 
                      width: `${progressPercent}%`,
                      backgroundColor: ach.unlocked ? ach.color : '#3b82f6'
                    }}
                  ></div>
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {/* Bottom CTA */}
      <div className="achievements-cta">
        <div className="cta-box">
          <div className="cta-text">
            <h3>Ready to unlock more achievements?</h3>
            <p>Start a live monitoring session right now to track posture accuracy and eye relief.</p>
          </div>
          <Link to="/live" className="cta-action-btn">
            <span>Launch Live Monitor</span>
            <ArrowRight className="btn-icon" />
          </Link>
        </div>
      </div>
    </div>
  );
}
