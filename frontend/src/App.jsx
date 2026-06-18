import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';
import ProtectedRoute from './components/common/ProtectedRoute';
import LandingPage from './pages/LandingPage';

// Pages
import Auth from './pages/Auth';
import Onboarding from './pages/Onboarding';
import Dashboard from './pages/Dashboard';
import JobSearch from './pages/JobSearch';
import JobDetail from './pages/JobDetail';
import Resumes from './pages/Resumes';
import Profile from './pages/Profile';

function App() {
  return (
    <Router>
      <AuthProvider>
        <Routes>
          {/* Public routes */}
          <Route path="/" element={<LandingPage />} />
          <Route path="/auth" element={<Auth />} />
          <Route path="/onboarding" element={<Onboarding />} />

          {/* Protected routes — require valid JWT */}
          <Route path="/dashboard" element={<ProtectedRoute><Dashboard /></ProtectedRoute>} />
          <Route path="/search" element={<ProtectedRoute><JobSearch /></ProtectedRoute>} />
          <Route path="/job-detail" element={<ProtectedRoute><JobDetail /></ProtectedRoute>} />
          <Route path="/resumes" element={<ProtectedRoute><Resumes /></ProtectedRoute>} />
          <Route path="/profile" element={<ProtectedRoute><Profile /></ProtectedRoute>} />
        </Routes>
      </AuthProvider>
    </Router>
  );
}

export default App;
