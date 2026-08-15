// src/pages/Signup.js
import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { 
  Shield, 
  Lock, 
  User, 
  Mail, 
  Eye, 
  EyeOff, 
  ArrowRight,
  CheckCircle,
  AlertCircle,
  Sparkles,
  Fingerprint,
  Star
} from 'lucide-react';
import './Signup.css';

export default function Signup() {
  const [username, setUsername] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState(false);
  const [passwordStrength, setPasswordStrength] = useState(0);
  const [acceptedTerms, setAcceptedTerms] = useState(false);
  const { signup } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    
    // Validation
    if (password.length < 6) {
      setError('Password must be at least 6 characters long');
      return;
    }
    
    if (password !== confirmPassword) {
      setError('Passwords do not match');
      return;
    }
    
    if (!acceptedTerms) {
      setError('Please accept the Terms of Service');
      return;
    }
    
    setIsLoading(true);

    try {
      await new Promise(resolve => setTimeout(resolve, 800));
      
      if (signup(username, password)) {
        setSuccess(true);
        setTimeout(() => {
          navigate('/dashboard');
        }, 1000);
      } else {
        setError('Username already exists. Please try another.');
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

  const toggleConfirmPasswordVisibility = () => {
    setShowConfirmPassword(!showConfirmPassword);
  };

  const checkPasswordStrength = (pwd) => {
    let strength = 0;
    if (pwd.length >= 6) strength++;
    if (pwd.length >= 10) strength++;
    if (/[A-Z]/.test(pwd) && /[a-z]/.test(pwd)) strength++;
    if (/\d/.test(pwd)) strength++;
    if (/[^A-Za-z0-9]/.test(pwd)) strength++;
    setPasswordStrength(strength);
  };

  const handlePasswordChange = (e) => {
    const pwd = e.target.value;
    setPassword(pwd);
    checkPasswordStrength(pwd);
  };

  const getStrengthLabel = () => {
    const labels = ['', 'Weak', 'Fair', 'Good', 'Strong', 'Excellent'];
    return labels[passwordStrength] || '';
  };

  const getStrengthColor = () => {
    const colors = ['', '#ef4444', '#f59e0b', '#3b82f6', '#10b981', '#10b981'];
    return colors[passwordStrength] || '#94a3b8';
  };

  return (
    <div className="signup-page">
      {/* Background Effects */}
      <div className="signup-bg-effects">
        <div className="signup-glow-orb orb-1"></div>
        <div className="signup-glow-orb orb-2"></div>
        <div className="signup-glow-orb orb-3"></div>
        <div className="signup-grid-overlay"></div>
      </div>

      {/* Floating Particles */}
      <div className="signup-particles">
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

      <div className="signup-container">
        <div className="signup-card">
          {/* Brand Header */}
          <div className="signup-header">
            <div className="signup-logo-wrapper">
              <div className="signup-logo-icon">
                <Shield className="signup-logo-shield" />
                <div className="signup-logo-glow"></div>
              </div>
              <div className="signup-brand-text">
                <span className="signup-brand-name">AI Ergonomics</span>
                <span className="signup-brand-tagline">Monitor</span>
              </div>
            </div>
            
            <div className="signup-badge">
              <Sparkles className="signup-badge-icon" />
              <span>Free Trial</span>
            </div>

            <h1 className="signup-title">Create Your Account</h1>
            <p className="signup-subtitle">
              Join thousands of users improving their ergonomic health
            </p>
          </div>

          {/* Success Message */}
          {success && (
            <div className="signup-success">
              <CheckCircle className="success-icon" />
              <div>
                <span className="success-title">Account Created!</span>
                <span className="success-message">Redirecting to dashboard...</span>
              </div>
            </div>
          )}

          {/* Error Message */}
          {error && (
            <div className="signup-error">
              <AlertCircle className="error-icon" />
              <span>{error}</span>
            </div>
          )}

          {/* Signup Form */}
          <form className="signup-form" onSubmit={handleSubmit}>
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
                  placeholder="Choose a username"
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                  required
                  autoFocus
                />
              </div>
            </div>

            {/* Email Field */}
            <div className="form-group">
              <label className="form-label">
                <Mail className="form-label-icon" />
                Email Address
              </label>
              <div className="input-wrapper">
                <Mail className="input-icon" />
                <input
                  type="email"
                  className="form-input"
                  placeholder="Enter your email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  required
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
                  placeholder="Create a password"
                  value={password}
                  onChange={handlePasswordChange}
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
              
              {/* Password Strength Indicator */}
              {password && (
                <div className="password-strength">
                  <div className="strength-bar-wrapper">
                    <div 
                      className="strength-bar"
                      style={{ 
                        width: `${(passwordStrength / 5) * 100}%`,
                        backgroundColor: getStrengthColor()
                      }}
                    />
                  </div>
                  <span className="strength-label" style={{ color: getStrengthColor() }}>
                    {getStrengthLabel()}
                  </span>
                </div>
              )}
            </div>

            {/* Confirm Password Field */}
            <div className="form-group">
              <label className="form-label">
                <Lock className="form-label-icon" />
                Confirm Password
              </label>
              <div className="input-wrapper">
                <Lock className="input-icon" />
                <input
                  type={showConfirmPassword ? 'text' : 'password'}
                  className="form-input"
                  placeholder="Confirm your password"
                  value={confirmPassword}
                  onChange={(e) => setConfirmPassword(e.target.value)}
                  required
                />
                <button
                  type="button"
                  className="password-toggle"
                  onClick={toggleConfirmPasswordVisibility}
                  aria-label={showConfirmPassword ? 'Hide password' : 'Show password'}
                >
                  {showConfirmPassword ? <EyeOff className="toggle-icon" /> : <Eye className="toggle-icon" />}
                </button>
              </div>
              
              {/* Password Match Indicator */}
              {confirmPassword && password && (
                <div className="password-match">
                  {password === confirmPassword ? (
                    <>
                      <CheckCircle className="match-icon success" />
                      <span className="match-text success">Passwords match</span>
                    </>
                  ) : (
                    <>
                      <AlertCircle className="match-icon error" />
                      <span className="match-text error">Passwords do not match</span>
                    </>
                  )}
                </div>
              )}
            </div>

            {/* Terms & Conditions */}
            <div className="form-options">
              <label className="terms-checkbox">
                <input
                  type="checkbox"
                  checked={acceptedTerms}
                  onChange={(e) => setAcceptedTerms(e.target.checked)}
                  required
                />
                <span className="checkmark">
                  <CheckCircle className="check-icon" />
                </span>
                <span className="terms-text">
                  I agree to the{' '}
                  <Link to="/terms" className="terms-link">Terms of Service</Link>
                  {' '}and{' '}
                  <Link to="/privacy" className="terms-link">Privacy Policy</Link>
                </span>
              </label>
            </div>

            {/* Submit Button */}
            <button
              type="submit"
              className="signup-btn"
              disabled={isLoading || success}
            >
              {isLoading ? (
                <>
                  <span className="spinner"></span>
                  Creating Account...
                </>
              ) : (
                <>
                  Create Account
                  <ArrowRight className="btn-arrow" />
                </>
              )}
            </button>

            {/* Biometric Option */}
            <button
              type="button"
              className="biometric-btn"
              onClick={() => {
                setError('');
                setIsLoading(true);
                setTimeout(() => {
                  setIsLoading(false);
                  setError('Biometric registration not available on this device');
                }, 1500);
              }}
            >
              <Fingerprint className="biometric-icon" />
              <span>Use Biometric Registration</span>
            </button>
          </form>

          {/* Footer */}
          <div className="signup-footer">
            <p className="signup-footer-text">
              Already have an account?{' '}
              <Link to="/login" className="login-link">
                Sign in
                <ArrowRight className="login-arrow" />
              </Link>
            </p>
            
            <div className="signup-divider">
              <span className="divider-line"></span>
              <span className="divider-text">or</span>
              <span className="divider-line"></span>
            </div>

            <div className="signup-social">
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

        {/* Trust Indicators */}
        <div className="signup-trust">
          <div className="trust-item">
            <Star className="trust-icon" />
            <div>
              <span className="trust-label">4.9/5 Rating</span>
              <span className="trust-description">From 200+ users</span>
            </div>
          </div>
          <div className="trust-divider"></div>
          <div className="trust-item">
            <Shield className="trust-icon" />
            <div>
              <span className="trust-label">Secure & Private</span>
              <span className="trust-description">Your data is protected</span>
            </div>
          </div>
          <div className="trust-divider"></div>
          <div className="trust-item">
            <CheckCircle className="trust-icon" />
            <div>
              <span className="trust-label">Free 14-Day Trial</span>
              <span className="trust-description">No credit card required</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}