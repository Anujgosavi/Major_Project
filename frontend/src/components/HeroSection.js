// src/components/HeroSection.js
import React, { useEffect, useRef } from 'react';
import { Link } from 'react-router-dom';
import Navbar from './Navbar';
import './HeroSection.css';

function HeroSection() {
  const heroRef = useRef(null);
  
  useEffect(() => {
    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            entry.target.classList.add('visible');
          }
        });
      },
      { threshold: 0.1 }
    );
    
    const elements = document.querySelectorAll('.animate-on-scroll');
    elements.forEach((el) => observer.observe(el));
    
    return () => observer.disconnect();
  }, []);
  
  return (
    <header className="hero-wrapper" ref={heroRef}>
      <Navbar />
      
      <section className="hero-section">
        {/* Background Effects */}
        <div className="hero-bg-effects">
          <div className="hero-glow-orb orb-1"></div>
          <div className="hero-glow-orb orb-2"></div>
          <div className="hero-glow-orb orb-3"></div>
          <div className="hero-grid-overlay"></div>
        </div>
        
        {/* Floating Particles */}
        <div className="hero-particles">
          {[...Array(12)].map((_, i) => (
            <div 
              key={i} 
              className="particle" 
              style={{
                left: `${Math.random() * 100}%`,
                animationDelay: `${Math.random() * 8}s`,
                animationDuration: `${8 + Math.random() * 12}s`,
                width: `${2 + Math.random() * 4}px`,
                height: `${2 + Math.random() * 4}px`
              }}
            />
          ))}
        </div>
        
        {/* Main Content */}
        <div className="hero-container">
          <div className="hero-content">
            {/* Badge */}
            <div className="hero-badge animate-on-scroll">
              <span className="badge-dot"></span>
              <span className="badge-text">AI-Powered Health Monitoring</span>
              <span className="badge-pulse">●</span>
            </div>
            
            {/* Main Title */}
            <h1 className="hero-title animate-on-scroll">
              <span className="title-line">Transform Your</span>
              <span className="title-line gradient-text">Digital Wellness</span>
              <span className="title-line">with AI Ergonomics</span>
            </h1>
            
            {/* Description */}
            <p className="hero-description animate-on-scroll">
              AI Ergonomics is an intelligent posture and wellness platform where users can 
              monitor, correct, and manage their ergonomic health with real-time AI-driven 
              insights. Designed to help you build healthier habits while using your 
              digital devices.
            </p>
            
            {/* CTA Buttons */}
            <div className="hero-actions animate-on-scroll">
              <Link to="/dashboard" className="btn-primary">
                <span>Get Started</span>
                <i className="fa-solid fa-arrow-right"></i>
              </Link>
              <Link to="/live" className="btn-secondary">
                <i className="fa-regular fa-play-circle"></i>
                <span>Live Demo</span>
              </Link>
            </div>
            
            {/* Stats */}
            <div className="hero-stats animate-on-scroll">
              <div className="stat-item">
                <span className="stat-number">98%</span>
                <span className="stat-label">Accuracy Rate</span>
              </div>
              <div className="stat-divider"></div>
              <div className="stat-item">
                <span className="stat-number">2.5K+</span>
                <span className="stat-label">Active Users</span>
              </div>
              <div className="stat-divider"></div>
              <div className="stat-item">
                <span className="stat-number">24/7</span>
                <span className="stat-label">Real-time Monitoring</span>
              </div>
            </div>
          </div>
          
          {/* Visual Element / Illustration */}
          <div className="hero-visual animate-on-scroll">
            <div className="visual-container">
              <div className="visual-orb">
                <div className="orb-inner"></div>
                <div className="orb-ring"></div>
                <div className="orb-ring ring-2"></div>
              </div>
              <div className="visual-icons">
                <div className="icon-item icon-1">
                  <i className="fa-solid fa-camera"></i>
                </div>
                <div className="icon-item icon-2">
                  <i className="fa-solid fa-microchip"></i>
                </div>
                <div className="icon-item icon-3">
                  <i className="fa-solid fa-chart-line"></i>
                </div>
                <div className="icon-item icon-4">
                  <i className="fa-solid fa-shield-alt"></i>
                </div>
              </div>
            </div>
          </div>
        </div>
        
        {/* Scroll Indicator */}
        <div className="hero-scroll-indicator">
          <span>Scroll to explore</span>
          <div className="scroll-arrow">
            <span></span>
          </div>
        </div>
      </section>
    </header>
  );
}

export default HeroSection;