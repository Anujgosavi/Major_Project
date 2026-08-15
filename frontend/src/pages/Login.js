// src/pages/Login.js
import React, { useState, useEffect } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { 
  Shield, 
  Lock, 
  User, 
  Eye, 
  EyeOff, 
  ArrowRight,
  CheckCircle,
  AlertCircle,
  Sparkles,
  Fingerprint
} from 'lucide-react';
import './Login.css';

export default function Login() {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const [rememberMe, setRememberMe] = useState(false);
  const { login } = useAuth();
  const navigate = useNavigate();

  // Load saved username if remember me was checked
  useEffect(() => {
    const savedUsername = localStorage.getItem('rememberedUsername');
    if (savedUsername) {
      setUsername(savedUsername);
      setRememberMe(true);
    }
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setIsLoading(true);

    // Simulate API call
    try {
      await new Promise(resolve => setTimeout(resolve, 800));
      
      if (login(username, password)) {
        if (rememberMe) {
          localStorage.setItem('rememberedUsername', username);
        } else {
          localStorage.removeItem('rememberedUsername');
        }
        navigate('/dashboard');
      } else {
        setError('Invalid username or password. Please try again.');
      }
    } catch (err) {
      setError('An error occurred. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  const togglePasswordVisibility = () => {
    setShowPassword(!showPassword);
  };

  return (
    <div className="login-page">
      {/* Background Effects */}
      <div className="login-bg-effects">
        <div className="login-glow-orb orb-1"></div>
        <div className="login-glow-orb orb-2"></div>
        <div className="login-glow-orb orb-3"></div>
        <div className="login-grid-overlay"></div>
      </div>

      {/* Floating Particles */}
      <div className="login-particles">
        {[...Array(8)].map((_, i) => (
          <div 
            key={i} 
            className="particle" 
            style={{
              left: `${Math.random() * 100}%`,
              animationDelay: `${Math.random() * 10}s`,
              animationDuration: `${15 + Math.random() * 20}s`,
              width: `${2 + Math.random() * 4}px`,
              height: `${2 + Math.random() * 4}px`
            }}
          />
        ))}
      </div>

      <div className="login-container">
        <div className="login-card">
          {/* Brand Header */}
          <div className="login-header">
            <div className="login-logo-wrapper">
              <div className="login-logo-icon">
                <Shield className="login-logo-shield" />
                <div className="login-logo-glow"></div>
              </div>
              <div className="login-brand-text">
                <span className="login-brand-name">AI Ergonomics</span>
                <span className="login-brand-tagline">Monitor</span>
              </div>
            </div>
            
            <div className="login-badge">
              <Sparkles className="login-badge-icon" />
              <span>Secure Login</span>
            </div>

            <h1 className="login-title">Welcome Back</h1>
            <p className="login-subtitle">
              Sign in to continue monitoring your ergonomic health
            </p>
          </div>

          {/* Error Message */}
          {error && (
            <div className="login-error">
              <AlertCircle className="error-icon" />
              <span>{error}</span>
            </div>
          )}

          {/* Login Form */}
          <form className="login-form" onSubmit={handleSubmit}>
            {/* Username Field */}
            <div className="form-group">
              <label className="form-label">
                <User className="form-label-icon" />
                Username
              </label>
              <div className="input-wrapper">
                <User className="input-icon" />
                <input
                  type="text"
                  className="form-input"
                  placeholder="Enter your username"
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                  required
                  autoFocus
                />
              </div>
            </div>

            {/* Password Field */}
            <div className="form-group">
              <label className="form-label">
                <Lock className="form-label-icon" />
                Password
              </label>
              <div className="input-wrapper">
                <Lock className="input-icon" />
                <input
                  type={showPassword ? 'text' : 'password'}
                  className="form-input"
                  placeholder="Enter your password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  required
                />
                <button
                  type="button"
                  className="password-toggle"
                  onClick={togglePasswordVisibility}
                  aria-label={showPassword ? 'Hide password' : 'Show password'}
                >
                  {showPassword ? <EyeOff className="toggle-icon" /> : <Eye className="toggle-icon" />}
                </button>
              </div>
            </div>

            {/* Remember Me & Forgot Password */}
            <div className="form-options">
              <label className="remember-me">
                <input
                  type="checkbox"
                  checked={rememberMe}
                  onChange={(e) => setRememberMe(e.target.checked)}
                />
                <span className="checkmark">
                  <CheckCircle className="check-icon" />
                </span>
                <span className="remember-text">Remember me</span>
              </label>
              <Link to="/forgot-password" className="forgot-link">
                Forgot password?
              </Link>
            </div>

            {/* Submit Button */}
            <button
              type="submit"
              className="login-btn"
              disabled={isLoading}
            >
              {isLoading ? (
                <>
                  <span className="spinner"></span>
                  Signing in...
                </>
              ) : (
                <>
                  Sign in
                  <ArrowRight className="btn-arrow" />
                </>
              )}
            </button>

            {/* Biometric Option */}
            <button
              type="button"
              className="biometric-btn"
              onClick={() => {
                // Simulate biometric login
                setError('');
                setIsLoading(true);
                setTimeout(() => {
                  setIsLoading(false);
                  setError('Biometric authentication not available on this device');
                }, 1500);
              }}
            >
              <Fingerprint className="biometric-icon" />
              <span>Use Biometric Login</span>
            </button>
          </form>

          {/* Footer */}
          <div className="login-footer">
            <p className="login-footer-text">
              Don't have an account?{' '}
              <Link to="/signup" className="signup-link">
                Create one now
                <ArrowRight className="signup-arrow" />
              </Link>
            </p>
            
            <div className="login-divider">
              <span className="divider-line"></span>
              <span className="divider-text">or</span>
              <span className="divider-line"></span>
            </div>

            <div className="login-social">
              <button className="social-btn google">
                <svg className="social-icon" viewBox="0 0 24 24">
                  <path d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92a5.06 5.06 0 0 1-2.2 3.32v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.1z" fill="#4285F4"/>
                  <path d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" fill="#34A853"/>
                  <path d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z" fill="#FBBC05"/>
                  <path d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z" fill="#EA4335"/>
                </svg>
                <span>Continue with Google</span>
              </button>
            </div>
          </div>
        </div>

        {/* Feature Highlights */}
        <div className="login-features">
          <div className="feature-item">
            <CheckCircle className="feature-icon" />
            <span>AI-powered posture analysis</span>
          </div>
          <div className="feature-item">
            <CheckCircle className="feature-icon" />
            <span>Real-time monitoring & alerts</span>
          </div>
          <div className="feature-item">
            <CheckCircle className="feature-icon" />
            <span>Personalized health insights</span>
          </div>
        </div>
      </div>
    </div>
  );
}