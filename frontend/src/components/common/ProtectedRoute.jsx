import React from "react";
import { Navigate } from "react-router-dom";
import { useAuth } from "../../context/AuthContext";

/**
 * Wraps a route so that unauthenticated users are redirected to /auth.
 * Shows a simple loading spinner while the auth state is being determined.
 *
 * Usage in App.jsx:
 *   <Route path="/dashboard" element={<ProtectedRoute><Dashboard /></ProtectedRoute>} />
 */
export default function ProtectedRoute({ children }) {
  const { isAuthenticated, loading } = useAuth();

  if (loading) {
    return (
      <div
        style={{
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          minHeight: "100vh",
          backgroundColor: "#f8f9ff",
          fontFamily: "'Inter', sans-serif",
        }}
      >
        <div style={{ textAlign: "center" }}>
          <span
            className="material-symbols-outlined"
            style={{
              fontSize: 48,
              color: "#003ec7",
              animation: "spin 1s linear infinite",
            }}
          >
            progress_activity
          </span>
          <p style={{ marginTop: 16, color: "#434656", fontSize: 14 }}>Loading...</p>
        </div>
      </div>
    );
  }

  if (!isAuthenticated) {
    return <Navigate to="/auth" replace />;
  }

  return children;
}
