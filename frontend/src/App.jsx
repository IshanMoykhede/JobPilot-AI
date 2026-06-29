import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';
import { ToastProvider } from './components/common/Toast';
import ProtectedRoute from './components/common/ProtectedRoute';

// Pages
import LandingPage from './pages/LandingPage';
import Auth from './pages/Auth';
import Dashboard from './pages/Dashboard';
import JobSearch from './pages/JobSearch';
import JobDetail from './pages/JobDetail';
import Resumes from './pages/Resumes';
import Profile from './pages/Profile';
import CareerInsights from './pages/CareerInsights';
import EvidenceExplorer from './pages/EvidenceExplorer';

function App() {
  return (
    <Router>
      <AuthProvider>
        <ToastProvider>
          <Routes>
            {/* Public routes */}
            <Route path="/" element={<LandingPage />} />
            <Route path="/auth" element={<Auth />} />

            {/* Redirect old onboarding route to profile */}
            <Route path="/onboarding" element={<Navigate to="/profile" replace />} />

            {/* Protected routes — require valid JWT */}
            <Route path="/dashboard" element={<ProtectedRoute><Dashboard /></ProtectedRoute>} />
            <Route path="/search" element={<ProtectedRoute><JobSearch /></ProtectedRoute>} />
            <Route path="/job-detail" element={<ProtectedRoute><JobDetail /></ProtectedRoute>} />
            <Route path="/resumes" element={<ProtectedRoute><Resumes /></ProtectedRoute>} />
            <Route path="/profile" element={<ProtectedRoute><Profile /></ProtectedRoute>} />
            <Route path="/insights" element={<ProtectedRoute><CareerInsights /></ProtectedRoute>} />
            <Route path="/evidence" element={<ProtectedRoute><EvidenceExplorer /></ProtectedRoute>} />
          </Routes>
        </ToastProvider>
      </AuthProvider>
    </Router>
  );
}

export default App;
