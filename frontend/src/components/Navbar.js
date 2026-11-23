// src/components/Navbar.js
import React, { useState, useEffect } from 'react';
import { Link, useLocation, NavLink } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { 
  Activity, 
  LayoutDashboard, 
  Video, 
  FileText, 
  UserPlus, 
  LogIn, 
  LogOut,
  User, 
  X 
} from 'lucide-react';
import './Navbar.css';

function Navbar() {
  const { user, logout } = useAuth();
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

  return (
    <nav className={`navbar-enhanced ${isScrolled ? 'scrolled' : ''}`}>
      <div className="navbar-container">
        {/* Logo / Brand */}
        <Link to="/" className="navbar-brand">
          <div className="brand-icon">
            <Activity className="brand-icon-svg" />
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
            <LayoutDashboard size={18} />
            <span>Dashboard</span>
          </NavLink>
          <NavLink 
            to="/live" 
            className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}
          >
            <Video size={18} />
            <span>Live Monitor</span>
          </NavLink>
          <NavLink 
            to="/reports" 
            className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}
          >
            <FileText size={18} />
            <span>Reports</span>
          </NavLink>
        </div>

        {/* Auth Buttons */}
        <div className="navbar-actions">
          {user ? (
            <>
              <Link to="/dashboard" className="btn-auth btn-login" style={{ background: 'rgba(59, 130, 246, 0.15)', borderColor: '#3b82f6' }}>
                <User size={16} />
                <span>{user.displayName || user.name || 'Dashboard'}</span>
              </Link>
              <button 
                onClick={logout} 
                className="btn-auth btn-signup" 
                style={{ background: 'transparent', borderColor: 'rgba(239, 68, 68, 0.4)', color: '#f87171' }}
                title="Logout"
              >
                <LogOut size={16} />
                <span>Logout</span>
              </button>
            </>
          ) : (
            <>
              <Link to="/signup" className="btn-auth btn-signup">
                <UserPlus size={16} />
                <span>Sign Up</span>
              </Link>
              <Link to="/login" className="btn-auth btn-login">
                <LogIn size={16} />
                <span>Login</span>
              </Link>
            </>
          )}
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
            <Link to="/" className="mobile-brand" onClick={() => setIsMobileMenuOpen(false)} style={{ textDecoration: 'none' }} title="Go to Home">
              <Activity size={24} color="#60a5fa" />
              <span>AI Ergonomics</span>
            </Link>
            <button 
              className="mobile-close-btn"
              onClick={() => setIsMobileMenuOpen(false)}
              aria-label="Close menu"
            >
              <X size={20} />
            </button>
          </div>
          
          <div className="mobile-nav-links">
            <Link to="/dashboard" className="mobile-nav-link">
              <LayoutDashboard size={20} />
              <span>Dashboard</span>
            </Link>
            <Link to="/live" className="mobile-nav-link">
              <Video size={20} />
              <span>Live Monitor</span>
            </Link>
            <Link to="/reports" className="mobile-nav-link">
              <FileText size={20} />
              <span>Reports</span>
            </Link>
          </div>
          
          <div className="mobile-auth-actions">
            {user ? (
              <>
                <Link to="/dashboard" className="mobile-btn-primary">
                  <User size={18} />
                  {user.displayName || user.name || 'Dashboard'}
                </Link>
                <button onClick={logout} className="mobile-btn-secondary" style={{ color: '#f87171' }}>
                  <LogOut size={18} />
                  Logout
                </button>
              </>
            ) : (
              <>
                <Link to="/signup" className="mobile-btn-primary">
                  <UserPlus size={18} />
                  Sign Up
                </Link>
                <Link to="/login" className="mobile-btn-secondary">
                  <LogIn size={18} />
                  Login
                </Link>
              </>
            )}
          </div>
        </div>
      </div>
    </nav>
  );
}

export default Navbar;
