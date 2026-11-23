import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './context/AuthContext';
import './App.css';

import Login from './pages/Login';
import Signup from './pages/Signup';
import Layout from './components/Layout';
import LandingPage from './pages/LandingPage';
import Dashboard from './pages/Dashboard';
import LiveFeed from './pages/LiveFeed';
import Reports from './pages/Reports';
import Activity from './pages/Activity';
import Achievements from './pages/Achievements';

function SmartFallback() {
  const { user } = useAuth();
  return <Navigate to={user ? "/dashboard" : "/login"} replace />;
}

function App() {
  return (
    <AuthProvider>
      <Router>
        <Routes>
          {/* Public Routes */}
          <Route path="/" element={<LandingPage />} />
          <Route path="/login" element={<Login />} />
          <Route path="/signup" element={<Signup />} />
          
          {/* Protected Routes */}
          <Route element={<Layout />}>
            <Route path="/dashboard" element={<Dashboard />} />
            <Route path="/live" element={<LiveFeed />} />
            <Route path="/reports" element={<Reports />} />
            <Route path="/activity" element={<Activity />} />
            <Route path="/achievements" element={<Achievements />} />
          </Route>
          
          {/* Smart Fallback */}
          <Route path="*" element={<SmartFallback />} />
        </Routes>
      </Router>
    </AuthProvider>
  );
}

export default App;
