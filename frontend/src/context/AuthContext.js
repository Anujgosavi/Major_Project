import React, { createContext, useContext, useState, useEffect } from 'react';
import api from '../utils/api';

const AuthContext = createContext(null);

const normalizeUser = (token, rawUser) => {
  if (!rawUser) return null;
  const displayName = rawUser.displayName || rawUser.name || (rawUser.email ? rawUser.email.split('@')[0] : 'User');
  return {
    token,
    id: rawUser.id || rawUser._id || 'local-user',
    name: displayName,
    displayName,
    email: rawUser.email || '',
    photoURL: rawUser.photoURL || null
  };
};

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(() => {
    try {
      const savedUser = localStorage.getItem('ergonomics_user');
      const token = localStorage.getItem('ergonomics_token');
      if (savedUser && token) {
        return normalizeUser(token, JSON.parse(savedUser));
      }
    } catch (e) {}
    return null;
  });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const initAuth = async () => {
      const token = localStorage.getItem('ergonomics_token');
      if (token) {
        try {
          const res = await api.get('/api/auth/me');
          if (res.ok) {
            const data = await res.json();
            const normalized = normalizeUser(token, data);
            setUser(normalized);
            localStorage.setItem('ergonomics_user', JSON.stringify(normalized));
          } else if (res.status === 401) {
            localStorage.removeItem('ergonomics_token');
            localStorage.removeItem('ergonomics_user');
            setUser(null);
          }
        } catch (err) {
          console.error('Failed to restore session via network:', err);
          // Keep existing user from localStorage on transient network errors
        }
      }
      setLoading(false);
    };

    initAuth();
  }, []);

  const login = async (email, password) => {
    try {
      const res = await api.post('/api/auth/login', { email, password });
      const data = await res.json();
      if (!res.ok) {
        return { success: false, error: data.error || 'Login failed' };
      }
      localStorage.setItem('ergonomics_token', data.token);
      const normalized = normalizeUser(data.token, data.user);
      localStorage.setItem('ergonomics_user', JSON.stringify(normalized));
      setUser(normalized);
      return { success: true };
    } catch (err) {
      return { success: false, error: 'Network error. Please try again.' };
    }
  };

  const signup = async (name, email, password) => {
    try {
      const res = await api.post('/api/auth/register', { name, email, password });
      const data = await res.json();
      if (!res.ok) {
        return { success: false, error: data.error || 'Registration failed' };
      }
      localStorage.setItem('ergonomics_token', data.token);
      const normalized = normalizeUser(data.token, data.user);
      localStorage.setItem('ergonomics_user', JSON.stringify(normalized));
      setUser(normalized);
      return { success: true };
    } catch (err) {
      return { success: false, error: 'Network error. Please try again.' };
    }
  };

  const logout = () => {
    localStorage.removeItem('ergonomics_token');
    localStorage.removeItem('ergonomics_user');
    setUser(null);
  };

  if (loading) {
    return (
      <div style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        height: '100vh',
        background: '#0a0f1d',
        color: '#60a5fa',
        fontFamily: 'Inter, sans-serif'
      }}>
        Loading session...
      </div>
    );
  }

  return (
    <AuthContext.Provider value={{ user, login, signup, logout }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => useContext(AuthContext);
