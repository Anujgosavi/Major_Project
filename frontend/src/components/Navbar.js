// src/components/Navbar.js
import React, { useState, useEffect } from 'react';
import { Link, useLocation, NavLink } from 'react-router-dom';
import './Navbar.css';

function Navbar() {
  const [isScrolled, setIsScrolled] = useState(false);
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
  const location = useLocation();

  useEffect(() => {
    const handleScroll = () => {
      setIsScrolled(window.scrollY > 20);
    };
    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  // Close mobile menu on route change
  useEffect(() => {
    setIsMobileMenuOpen(false);
  }, [location]);

  const isActive = (path) => {
    return location.pathname === path;
  };

  return (
    <nav className={`navbar-enhanced ${isScrolled ? 'scrolled' : ''}`}>
      <div className="navbar-container">
        {/* Logo / Brand */}
        <Link to="/" className="navbar-brand">
          <div className="brand-icon">
            <i className="fa-solid fa-camera"></i>
            <div className="brand-icon-glow"></div>
          </div>
          <div className="brand-text">
            <span className="brand-name">AI Ergonomics</span>
            <span className="brand-tagline">Monitor</span>
          </div>
        </Link>

        {/* Desktop Navigation Links */}
        <div className="navbar-links-desktop">
          <NavLink 
            to="/dashboard" 
            className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}
          >
            <i className="fa-solid fa-chart-pie"></i>
            <span>Dashboard</span>
          </NavLink>
          <NavLink 
            to="/live" 
            className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}
          >
            <i className="fa-solid fa-video"></i>
            <span>Live Monitor</span>
          </NavLink>
          <NavLink 
            to="/reports" 
            className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}
          >
            <i className="fa-solid fa-file-chart-line"></i>
            <span>Reports</span>
          </NavLink>
        </div>

        {/* Auth Buttons */}
        <div className="navbar-actions">
          <Link to="/signup" className="btn-auth btn-signup">
            <i className="fa-regular fa-user-plus"></i>
            <span>Sign Up</span>
          </Link>
          <Link to="/login" className="btn-auth btn-login">
            <i className="fa-regular fa-user"></i>
            <span>Login</span>
          </Link>
          <Link to="/dashboard" className="btn-auth btn-profile">
            <i className="fa-regular fa-circle-user"></i>
          </Link>
        </div>

        {/* Mobile Menu Toggle */}
        <button 
          className="mobile-menu-toggle"
          onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
          aria-label="Toggle menu"
        >
          <span className={`hamburger-icon ${isMobileMenuOpen ? 'active' : ''}`}>
            <span></span>
            <span></span>
            <span></span>
          </span>
        </button>
      </div>

      {/* Mobile Menu */}
      <div className={`mobile-menu ${isMobileMenuOpen ? 'open' : ''}`}>
        <div className="mobile-menu-content">
          <div className="mobile-menu-header">
            <div className="mobile-brand">
              <i className="fa-solid fa-camera"></i>
              <span>AI Ergonomics</span>
            </div>
            <button 
              className="mobile-close-btn"
              onClick={() => setIsMobileMenuOpen(false)}
            >
              <i className="fa-solid fa-xmark"></i>
            </button>
          </div>
          
          <div className="mobile-nav-links">
            <Link to="/dashboard" className="mobile-nav-link">
              <i className="fa-solid fa-chart-pie"></i>
              <span>Dashboard</span>
            </Link>
            <Link to="/live" className="mobile-nav-link">
              <i className="fa-solid fa-video"></i>
              <span>Live Monitor</span>
            </Link>
            <Link to="/reports" className="mobile-nav-link">
              <i className="fa-solid fa-file-chart-line"></i>
              <span>Reports</span>
            </Link>
          </div>
          
          <div className="mobile-auth-actions">
            <Link to="/signup" className="mobile-btn-primary">
              <i className="fa-regular fa-user-plus"></i>
              Sign Up
            </Link>
            <Link to="/login" className="mobile-btn-secondary">
              <i className="fa-regular fa-user"></i>
              Login
            </Link>
          </div>
        </div>
      </div>
    </nav>
  );
}

export default Navbar;