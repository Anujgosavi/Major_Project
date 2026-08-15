// src/components/Footer.js
import React from 'react';
import { Link } from 'react-router-dom';
import './Footer.css';

function Footer() {
  const currentYear = new Date().getFullYear();
  
  return (
    <footer className="footer-enhanced">
      <div className="footer-wave">
        <svg viewBox="0 0 1200 120" preserveAspectRatio="none">
          <path d="M321.39,56.44c58-10.79,114.16-30.13,172-41.86,82.39-16.72,168.19-17.73,250.45-.39C823.78,31,906.67,72,985.66,92.83c70.05,18.48,146.53,26.09,214.34,3V0H0V27.35A600.21,600.21,0,0,0,321.39,56.44Z" />
        </svg>
      </div>
      
      <div className="footer-content">
        <div className="footer-container">
          {/* Brand Section */}
          <div className="footer-brand-section">
            <div className="footer-logo-wrapper">
              <div className="footer-logo-icon">
                <i className="fa-solid fa-camera"></i>
              </div>
              <div className="footer-logo-text">
                <span className="logo-main">AI Ergonomics</span>
                <span className="logo-sub">Monitor</span>
              </div>
            </div>
            <p className="footer-brand-description">
              Smart posture monitoring powered by artificial intelligence.
              Stay healthy, work better.
            </p>
          </div>

          {/* Navigation Links */}
          <div className="footer-links-wrapper">
            <div className="footer-links-column">
              <h4>Quick Links</h4>
              <Link to="/">Home</Link>
              <Link to="/dashboard">Dashboard</Link>
              <Link to="/live">Live Monitor</Link>
              <Link to="/reports">Reports</Link>
            </div>
            <div className="footer-links-column">
              <h4>Resources</h4>
              <Link to="/about">About Us</Link>
              <Link to="/blog">Blog</Link>
              <Link to="/support">Support</Link>
              <Link to="/privacy">Privacy Policy</Link>
            </div>
            <div className="footer-links-column">
              <h4>Contact</h4>
              <a href="mailto:info@aiergonomics.com">
                <i className="fa-regular fa-envelope"></i> info@aiergonomics.com
              </a>
              <a href="tel:+1234567890">
                <i className="fa-regular fa-phone"></i> +1 (234) 567-890
              </a>
              <div className="footer-social">
                <a href="https://github.com" target="_blank" rel="noreferrer" aria-label="GitHub">
                  <i className="fa-brands fa-github"></i>
                </a>
                <a href="https://linkedin.com" target="_blank" rel="noreferrer" aria-label="LinkedIn">
                  <i className="fa-brands fa-linkedin-in"></i>
                </a>
                <a href="https://twitter.com" target="_blank" rel="noreferrer" aria-label="Twitter">
                  <i className="fa-brands fa-x-twitter"></i>
                </a>
                <a href="https://youtube.com" target="_blank" rel="noreferrer" aria-label="YouTube">
                  <i className="fa-brands fa-youtube"></i>
                </a>
              </div>
            </div>
          </div>

          {/* Bottom Bar */}
          <div className="footer-bottom">
            <div className="footer-bottom-left">
              <span>© {currentYear} AI Ergonomics Monitor</span>
              <span className="footer-divider">|</span>
              <span>All Rights Reserved</span>
            </div>
            <div className="footer-bottom-right">
              <Link to="/terms">Terms of Service</Link>
              <span className="footer-divider">|</span>
              <Link to="/privacy">Privacy Policy</Link>
              <span className="footer-divider">|</span>
              <Link to="/cookies">Cookie Policy</Link>
            </div>
          </div>
        </div>
      </div>
    </footer>
  );
}

export default Footer;