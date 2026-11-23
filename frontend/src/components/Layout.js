// src/components/Layout.js
import React, { useState, useEffect, useRef } from 'react';
import { Outlet, Navigate, useLocation } from 'react-router-dom';
import Sidebar from './Sidebar';
import { useAuth } from '../context/AuthContext';
import './Layout.css';

export default function Layout() {
  const { user, logout } = useAuth();
  const location = useLocation();
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const mainRef = useRef(null);
  
  // Simulate loading state
  useEffect(() => {
    const timer = setTimeout(() => setIsLoading(false), 500);
    return () => clearTimeout(timer);
  }, []);

  // Close mobile menu on route change
  useEffect(() => {
    setIsMobileMenuOpen(false);
  }, [location]);

  // Handle escape key
  useEffect(() => {
    const handleEscape = (e) => {
      if (e.key === 'Escape') setIsMobileMenuOpen(false);
    };
    document.addEventListener('keydown', handleEscape);
    return () => document.removeEventListener('keydown', handleEscape);
  }, []);

  const userName = user?.displayName || user?.name || (user?.email ? user.email.split('@')[0] : 'User');

  if (!user) {
    return <Navigate to="/login" replace />;
  }

  return (
    <div className="layout-container">
      {/* Loading Overlay */}
      {isLoading && (
        <div className="layout-loader">
          <div className="loader-spinner">
            <div className="spinner-ring"></div>
            <div className="spinner-ring"></div>
            <div className="spinner-ring"></div>
          </div>
          <p className="loader-text">Loading Dashboard...</p>
        </div>
      )}

      {/* Mobile Overlay */}
      {isMobileMenuOpen && (
        <div 
          className="mobile-overlay"
          onClick={() => setIsMobileMenuOpen(false)}
        />
      )}

      {/* Sidebar */}
      <Sidebar 
        isMobileOpen={isMobileMenuOpen}
        onClose={() => setIsMobileMenuOpen(false)}
      />

      {/* Main Content */}
      <div className="layout-main">
        {/* Top Navigation Bar */}
        <header className="layout-header">
          <div className="header-left">
            <button 
              className="header-menu-btn"
              onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
              aria-label="Toggle menu"
            >
              <span className={`hamburger ${isMobileMenuOpen ? 'active' : ''}`}>
                <span className="hamburger-line"></span>
                <span className="hamburger-line"></span>
                <span className="hamburger-line"></span>
              </span>
            </button>
            
            <div className="header-breadcrumb">
              <span className="breadcrumb-separator">/</span>
              <span className="breadcrumb-current">
                {location.pathname.split('/').pop() || 'Dashboard'}
              </span>
            </div>
          </div>

          <div className="header-right">
            {/* User Profile */}
            <div className="header-profile">
              <div className="profile-avatar">
                <img 
                  src={user?.photoURL || `https://ui-avatars.com/api/?name=${encodeURIComponent(userName)}&background=d47a5b&color=fff&size=32`} 
                  alt={userName}
                  className="avatar-image"
                />
                <span className="avatar-status online"></span>
              </div>
              <div className="profile-info">
                <span className="profile-name">{userName}</span>
                <span className="profile-role">Active</span>
              </div>
            </div>

            {/* Logout Button */}
            <button 
              className="header-logout-btn"
              onClick={logout}
              aria-label="Logout"
              title="Logout"
            >
              <i className="fa-solid fa-right-from-bracket"></i>
            </button>
          </div>
        </header>

        {/* Page Content */}
        <main className="layout-content" ref={mainRef}>
          <div className="content-wrapper">
            {/* Outlet */}
            <div className="page-content">
              <Outlet />
            </div>
          </div>
        </main>

        {/* Footer */}
        <footer className="layout-footer">
          <div className="footer-left">
            <span>© 2025 AI Ergonomics Monitor</span>
            <span className="footer-divider">|</span>
            <span>v2.1.0</span>
          </div>
          <div className="footer-right">
            <span className="footer-status">
              <span className="status-dot"></span>
              All systems operational
            </span>
          </div>
        </footer>
      </div>
    </div>
  );
}