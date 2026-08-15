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
            {/* Search */}
            <div className="header-search">
              <i className="fa-solid fa-search search-icon"></i>
              <input 
                type="text" 
                placeholder="Search..." 
                className="search-input"
                aria-label="Search"
              />
              <kbd className="search-shortcut">⌘K</kbd>
            </div>

            {/* Notifications */}
            <button className="header-icon-btn" aria-label="Notifications">
              <i className="fa-regular fa-bell"></i>
              <span className="notification-dot"></span>
            </button>

            {/* User Profile */}
            <div className="header-profile">
              <div className="profile-avatar">
                <img 
                  src={user?.photoURL || `https://ui-avatars.com/api/?name=${user?.displayName || 'User'}&background=2563eb&color=fff&size=32`} 
                  alt={user?.displayName || 'User'}
                  className="avatar-image"
                />
                <span className="avatar-status online"></span>
              </div>
              <div className="profile-info">
                <span className="profile-name">{user?.displayName || 'User'}</span>
                <span className="profile-role">Admin</span>
              </div>
              <button 
                className="profile-dropdown-btn"
                onClick={() => {/* Toggle dropdown */}}
                aria-label="User menu"
              >
                <i className="fa-solid fa-chevron-down"></i>
              </button>
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
            {/* Page Header */}
            <div className="page-header">
              <div className="page-header-left">
                <h1 className="page-title">
                  {location.pathname === '/' ? 'Dashboard' : 
                   location.pathname.split('/').pop().charAt(0).toUpperCase() + 
                   location.pathname.split('/').pop().slice(1)}
                </h1>
                <p className="page-subtitle">
                  Welcome back, {user?.displayName || 'User'}! Here's what's happening with your ergonomics.
                </p>
              </div>
              <div className="page-header-right">
                <button className="page-action-btn">
                  <i className="fa-regular fa-file-pdf"></i>
                  <span>Export Report</span>
                </button>
                <button className="page-action-btn primary">
                  <i className="fa-regular fa-plus"></i>
                  <span>New Session</span>
                </button>
              </div>
            </div>

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