// src/pages/LandingPage.js
import React, { useEffect, useRef } from 'react';
import { Link } from 'react-router-dom';
import { 
  Camera, 
  LayoutDashboard, 
  FileText, 
  Shield, 
  Zap, 
  TrendingUp,
  Award,
  Clock,
  CheckCircle,
  ArrowRight,
  Play,
  Star,
  Users,
  BarChart3,
  Activity,
  Eye,
  Brain,
  Sparkles
} from 'lucide-react';
import HeroSection from '../components/HeroSection';
import Footer from '../components/Footer';
import './LandingPage.css';

export default function LandingPage() {
  const statsRef = useRef(null);
  
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

  const services = [
    {
      id: 'live',
      title: 'Live Posture Monitor',
      icon: Camera,
      gradient: 'blue',
      description: 'Real-time webcam analysis using MediaPipe to track posture, head angles, eye openness, blink rate, and screen distance with instant safety alerts.',
      link: '/live',
      features: ['Real-time tracking', 'AI-powered analysis', 'Instant alerts'],
      badge: 'Live'
    },
    {
      id: 'dashboard',
      title: 'Wellness Dashboard',
      icon: LayoutDashboard,
      gradient: 'green',
      description: 'View your posture scores, session history, blink stats, and wellness trends all in one place with an intuitive analytics dashboard.',
      link: '/dashboard',
      features: ['Analytics dashboard', 'History tracking', 'Trend visualization'],
      badge: 'Popular'
    },
    {
      id: 'reports',
      title: 'AI PDF Reports',
      icon: FileText,
      gradient: 'orange',
      description: 'Get detailed AI-generated ergonomic reports powered by Gemini 2.5 Flash with personalized recommendations and the 20-20-20 rule insights.',
      link: '/reports',
      features: ['AI-generated', 'Personalized insights', 'PDF export'],
      badge: 'New'
    }
  ];

  const features = [
    { icon: Zap, title: 'Real-time Analysis', description: 'Instant feedback on your posture and ergonomics' },
    { icon: Shield, title: 'Privacy First', description: 'All processing happens locally on your device' },
    { icon: TrendingUp, title: 'Progress Tracking', description: 'Monitor your improvement over time' },
    { icon: Award, title: 'Smart Recommendations', description: 'Personalized tips for better health' },
    { icon: Clock, title: '20-20-20 Rule', description: 'Smart reminders for eye health breaks' },
    { icon: Brain, title: 'AI-Powered', description: 'Advanced AI for accurate posture analysis' }
  ];

  const testimonials = [
    {
      name: 'Sarah Johnson',
      role: 'Software Engineer',
      content: 'This tool has completely transformed how I work. My posture has improved significantly and I feel much more energetic throughout the day.',
      rating: 5,
      avatar: 'SJ'
    },
    {
      name: 'Mike Chen',
      role: 'Product Designer',
      content: 'The real-time feedback is incredible. I love how it gently reminds me to adjust my posture without being intrusive.',
      rating: 5,
      avatar: 'MC'
    },
    {
      name: 'Emily Rodriguez',
      role: 'Remote Worker',
      content: 'The AI reports are spot on! The personalized recommendations have helped me create better ergonomic habits.',
      rating: 4,
      avatar: 'ER'
    }
  ];

  const renderStars = (rating) => {
    return Array.from({ length: 5 }, (_, i) => (
      <Star key={i} className={`star ${i < rating ? 'filled' : 'empty'}`} />
    ));
  };

  return (
    <div className="landing-page">
      <HeroSection />

      {/* Features Section */}
      <section className="features-section">
        <div className="features-container">
          <div className="section-header animate-on-scroll">
            <span className="section-badge">Why Choose Us</span>
            <h2 className="section-title">Smart Features for <span className="gradient-text">Better Health</span></h2>
            <p className="section-subtitle">
              AI-powered tools designed to keep you healthy and productive at your desk
            </p>
          </div>

          <div className="features-grid">
            {features.map((feature, index) => {
              const Icon = feature.icon;
              return (
                <div key={index} className="feature-card animate-on-scroll" style={{ animationDelay: `${index * 0.1}s` }}>
                  <div className="feature-icon-wrapper">
                    <Icon className="feature-icon" />
                  </div>
                  <h3 className="feature-title">{feature.title}</h3>
                  <p className="feature-description">{feature.description}</p>
                </div>
              );
            })}
          </div>
        </div>
      </section>

      {/* Services Section */}
      <section className="services-section">
        <div className="services-container">
          <div className="section-header animate-on-scroll">
            <span className="section-badge">Our Services</span>
            <h2 className="section-title">AI-Powered <span className="gradient-text">Ergonomic Tools</span></h2>
            <p className="section-subtitle">
              Advanced technology to monitor, analyze, and improve your ergonomic health
            </p>
          </div>

          <div className="services-grid">
            {services.map((service, index) => {
              const Icon = service.icon;
              return (
                <Link 
                  key={service.id} 
                  to={service.link} 
                  className={`service-card ${service.gradient} animate-on-scroll`}
                  style={{ animationDelay: `${index * 0.15}s` }}
                >
                  <div className={`service-card-glow ${service.gradient}`}></div>
                  <div className="service-card-content">
                    <div className={`service-icon-wrapper ${service.gradient}`}>
                      <Icon className="service-icon" />
                    </div>
                    <span className={`service-badge ${service.gradient}`}>{service.badge}</span>
                    <h3 className="service-title">{service.title}</h3>
                    <p className="service-description">{service.description}</p>
                    <div className="service-features">
                      {service.features.map((feature, i) => (
                        <span key={i} className="service-feature">
                          <CheckCircle className="feature-check" />
                          {feature}
                        </span>
                      ))}
                    </div>
                    <span className="service-link">
                      Learn More <ArrowRight className="link-arrow" />
                    </span>
                  </div>
                </Link>
              );
            })}
          </div>
        </div>
      </section>

      {/* Stats Section */}
      <section className="stats-section">
        <div className="stats-container">
          <div className="stats-grid">
            <div className="stat-item animate-on-scroll">
              <div className="stat-number">98%</div>
              <div className="stat-label">Posture Accuracy</div>
              <div className="stat-trend up">
                <TrendingUp className="trend-icon" />
                <span>+12% this month</span>
              </div>
            </div>
            <div className="stat-divider"></div>
            <div className="stat-item animate-on-scroll" style={{ animationDelay: '0.15s' }}>
              <div className="stat-number">2.5K+</div>
              <div className="stat-label">Active Users</div>
              <div className="stat-trend up">
                <Users className="trend-icon" />
                <span>+350 this week</span>
              </div>
            </div>
            <div className="stat-divider"></div>
            <div className="stat-item animate-on-scroll" style={{ animationDelay: '0.3s' }}>
              <div className="stat-number">24/7</div>
              <div className="stat-label">Real-time Monitoring</div>
              <div className="stat-trend up">
                <Activity className="trend-icon" />
                <span>Always active</span>
              </div>
            </div>
            <div className="stat-divider"></div>
            <div className="stat-item animate-on-scroll" style={{ animationDelay: '0.45s' }}>
              <div className="stat-number">4.9★</div>
              <div className="stat-label">User Rating</div>
              <div className="stat-trend up">
                <Star className="trend-icon" />
                <span>Based on 200+ reviews</span>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Testimonials Section */}
      <section className="testimonials-section">
        <div className="testimonials-container">
          <div className="section-header animate-on-scroll">
            <span className="section-badge">Testimonials</span>
            <h2 className="section-title">What Our <span className="gradient-text">Users Say</span></h2>
            <p className="section-subtitle">
              Real experiences from people who've improved their ergonomic health
            </p>
          </div>

          <div className="testimonials-grid">
            {testimonials.map((testimonial, index) => (
              <div key={index} className="testimonial-card animate-on-scroll" style={{ animationDelay: `${index * 0.15}s` }}>
                <div className="testimonial-header">
                  <div className="testimonial-avatar">
                    {testimonial.avatar}
                  </div>
                  <div className="testimonial-info">
                    <div className="testimonial-name">{testimonial.name}</div>
                    <div className="testimonial-role">{testimonial.role}</div>
                    <div className="testimonial-stars">
                      {renderStars(testimonial.rating)}
                    </div>
                  </div>
                </div>
                <p className="testimonial-content">"{testimonial.content}"</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="cta-section">
        <div className="cta-container">
          <div className="cta-content animate-on-scroll">
            <div className="cta-badge">
              <Sparkles className="cta-badge-icon" />
              <span>Get Started Free</span>
            </div>
            <h2 className="cta-title">Ready to <span className="gradient-text">Transform</span> Your Workday?</h2>
            <p className="cta-description">
              Join thousands of users who've improved their ergonomic health with AI-powered monitoring.
              Start your journey to better posture and wellness today.
            </p>
            <div className="cta-actions">
              <Link to="/signup" className="cta-btn-primary">
                Start Free Trial
                <ArrowRight className="cta-btn-icon" />
              </Link>
              <Link to="/live" className="cta-btn-secondary">
                <Play className="cta-btn-icon" />
                Watch Demo
              </Link>
            </div>
            <div className="cta-features">
              <span className="cta-feature">
                <CheckCircle className="cta-feature-icon" />
                No credit card required
              </span>
              <span className="cta-feature">
                <CheckCircle className="cta-feature-icon" />
                Free 14-day trial
              </span>
              <span className="cta-feature">
                <CheckCircle className="cta-feature-icon" />
                Cancel anytime
              </span>
            </div>
          </div>
        </div>
      </section>

      <Footer />
    </div>
  );
}