import React, { createContext, useContext, useState, useEffect } from 'react';

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const token = localStorage.getItem('ergonomics_token');
    if (token) {
      setUser({ token, username: 'DemoUser' });
    }
    setLoading(false);
  }, []);

  const login = (username, password) => {
    // Dummy login
    if (username && password) {
      const token = 'dummy_token_' + Date.now();
      localStorage.setItem('ergonomics_token', token);
      setUser({ token, username });
      return true;
    }
    return false;
  };

  const signup = (username, password) => {
    // Dummy signup
    if (username && password) {
      const token = 'dummy_token_' + Date.now();
      localStorage.setItem('ergonomics_token', token);
      setUser({ token, username });
      return true;
    }
    return false;
  };

  const logout = () => {
    localStorage.removeItem('ergonomics_token');
    setUser(null);
  };

  if (loading) return <div>Loading...</div>;

  return (
    <AuthContext.Provider value={{ user, login, signup, logout }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => useContext(AuthContext);
