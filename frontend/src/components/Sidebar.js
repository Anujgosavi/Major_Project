// src/components/Sidebar.js
import React, { useState, useEffect } from 'react';
import { NavLink, useLocation } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { 
  LayoutDashboard, 
  Video, 
  FileText, 
  LogOut, 
  Shield, 
  Settings,
  HelpCircle,
  User,
  Bell,
  ChevronDown,
  ChevronRight,
  Activity,
  Zap,
  Award,
  Clock
} from 'lucide-react';
import './Sidebar.css';

export default function Sidebar({ isMobileOpen = false, onClose = () => {} }) {
  const { logout, user } = useAuth();
  const location = useLocation();
  const [isExpanded, setIsExpanded] = useState(true);
  const [isSettingsOpen, setIsSettingsOpen] = useState(false);
  const [isMobile, setIsMobile] = useState(window.innerWidth < 1024);

  useEffect(() => {
    const handleResize = () => {
      setIsMobile(window.innerWidth < 1024);
    };
    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  useEffect(() => {
    if (isMobile && isMobileOpen) {
      document.body.style.overflow = 'hidden';
    } else {
      document.body.style.overflow = 'unset';
    }
    return () => {
      document.body.style.overflow = 'unset';
    };
  }, [isMobile, isMobileOpen]);

  const navigation = [
    { 
      name: 'Dashboard', 
      href: '/dashboard', 
      icon: LayoutDashboard,
      description: 'Overview & stats'
    },
    { 
      name: 'Live Monitor', 
      href: '/live', 
      icon: Video,
      description: 'Real-time tracking',
      badge: 'Live',
      badgeColor: 'success'
    },
    { 
      name: 'Reports', 
      href: '/reports', 
      icon: FileText,
      description: 'Analytics & insights'
    },
    { 
      name: 'Activity', 
      href: '/activity', 
      icon: Activity,
      description: 'Session history'
    },
    { 
      name: 'Achievements', 
      href: '/achievements', 
      icon: Award,
      description: 'Your progress',
      badge: '3',
      badgeColor: 'warning'
    },
  ];

  const settingsItems = [
    { name: 'Profile', href: '/profile', icon: User },
    { name: 'Notifications', href: '/notifications', icon: Bell },
    { name: 'Settings', href: '/settings', icon: Settings },
  ];

  const handleLogout = () => {
    if (window.confirm('Are you sure you want to logout?')) {
      logout();
    }
  };

  return (
    <>
      {/* Mobile Backdrop */}
      {isMobile && isMobileOpen && (
        <div className="sidebar-backdrop" onClick={onClose} />
      )}

      <aside 
        className={`sidebar-enhanced ${isMobile ? 'mobile' : 'desktop'} 
          ${isMobileOpen ? 'open' : ''} 
          ${!isExpanded ? 'collapsed' : ''}`}
      >
        {/* Brand Header */}
        <div className="sidebar-header">
          <div className="brand-wrapper">
            <div className="brand-icon-wrapper">
              <Shield className="brand-icon" />
              <div className="brand-icon-glow"></div>
            </div>
            {isExpanded && (
              <div className="brand-text">
                <span className="brand-name">AI Ergonomics</span>
                <span className="brand-status">
                  <span className="status-dot"></span>
                  Online
                </span>
              </div>
            )}
          </div>
          
          {!isMobile && (
            <button 
              className="toggle-btn"
              onClick={() => setIsExpanded(!isExpanded)}
              aria-label={isExpanded ? 'Collapse sidebar' : 'Expand sidebar'}
            >
              <ChevronRight className={`toggle-icon ${!isExpanded ? 'rotated' : ''}`} />
            </button>
          )}
        </div>

        {/* User Profile Summary */}
        {isExpanded && (
          <div className="sidebar-user-profile">
            <div className="user-avatar-wrapper">
              <img 
                src={user?.photoURL || `https://ui-avatars.com/api/?name=${user?.displayName || 'User'}&background=2563eb&color=fff&size=40`} 
                alt={user?.displayName || 'User'}
                className="user-avatar"
              />
              <span className="user-status online"></span>
            </div>
            <div className="user-info">
              <span className="user-name">{user?.displayName || 'Guest User'}</span>
              <span className="user-role">Administrator</span>
            </div>
          </div>
        )}

        {/* Quick Stats */}
        {isExpanded && (
          <div className="sidebar-stats">
            <div className="stat-item">
              <div className="stat-icon-wrapper">
                <Zap className="stat-icon" />
              </div>
              <div className="stat-content">
                <span className="stat-value">98%</span>
                <span className="stat-label">Accuracy</span>
              </div>
            </div>
            <div className="stat-divider"></div>
            <div className="stat-item">
              <div className="stat-icon-wrapper">
                <Clock className="stat-icon" />
              </div>
              <div className="stat-content">
                <span className="stat-value">2.5K</span>
                <span className="stat-label">Sessions</span>
              </div>
            </div>
          </div>
        )}

        {/* Navigation */}
        <nav className="sidebar-nav">
          <div className="nav-section">
            {isExpanded && <span className="nav-section-title">Main Menu</span>}
            <ul className="nav-list">
              {navigation.map((item) => {
                const Icon = item.icon;
                const isActive = location.pathname === item.href;
                return (
                  <li key={item.name}>
                    <NavLink
                      to={item.href}
                      className={`nav-item ${isActive ? 'active' : ''}`}
                      onClick={() => isMobile && onClose()}
                    >
                      <span className="nav-icon-wrapper">
                        <Icon className="nav-icon" />
                        {isActive && <span className="nav-active-indicator"></span>}
                      </span>
                      {isExpanded && (
                        <div className="nav-content">
                          <span className="nav-name">{item.name}</span>
                          <span className="nav-description">{item.description}</span>
                        </div>
                      )}
                      {isExpanded && item.badge && (
                        <span className={`nav-badge ${item.badgeColor}`}>
                          {item.badge}
                        </span>
                      )}
                    </NavLink>
                  </li>
                );
              })}
            </ul>
          </div>

          {/* Settings Section */}
          <div className="nav-section">
            {isExpanded && <span className="nav-section-title">Settings</span>}
            <ul className="nav-list">
              {settingsItems.map((item) => {
                const Icon = item.icon;
                const isActive = location.pathname === item.href;
                return (
                  <li key={item.name}>
                    <NavLink
                      to={item.href}
                      className={`nav-item ${isActive ? 'active' : ''}`}
                      onClick={() => isMobile && onClose()}
                    >
                      <span className="nav-icon-wrapper">
                        <Icon className="nav-icon" />
                      </span>
                      {isExpanded && (
                        <span className="nav-name">{item.name}</span>
                      )}
                    </NavLink>
                  </li>
                );
              })}
            </ul>
          </div>
        </nav>

        {/* Help & Support */}
        {isExpanded && (
          <div className="sidebar-help">
            <div className="help-card">
              <HelpCircle className="help-icon" />
              <div className="help-content">
                <span className="help-title">Need Help?</span>
                <span className="help-text">Check our documentation</span>
              </div>
              <button className="help-btn">Learn More</button>
            </div>
          </div>
        )}

        {/* Logout Button */}
        <div className="sidebar-footer">
          <button
            onClick={handleLogout}
            className="logout-btn"
          >
            <LogOut className="logout-icon" />
            {isExpanded && <span>Logout</span>}
          </button>
        </div>
      </aside>
    </>
  );
}