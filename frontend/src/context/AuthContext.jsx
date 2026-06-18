import React, { createContext, useContext, useState, useEffect, useCallback } from "react";
import { loginUser as apiLogin, registerUser as apiRegister, fetchCurrentUser, checkProfileStatus } from "../services/authApi";

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [token, setToken] = useState(() => localStorage.getItem("token"));
  const [loading, setLoading] = useState(true);
  const [hasProfile, setHasProfile] = useState(null);

  // On mount (or when token changes), try to restore the session
  const loadUser = useCallback(async () => {
    if (!token) {
      setLoading(false);
      return;
    }
    try {
      const userData = await fetchCurrentUser(token);
      setUser(userData);
      
      const profileExists = await checkProfileStatus(token);
      setHasProfile(profileExists);
    } catch {
      // Token is invalid or expired — clear everything
      localStorage.removeItem("token");
      setToken(null);
      setUser(null);
      setHasProfile(null);
    } finally {
      setLoading(false);
    }
  }, [token]);

  useEffect(() => {
    loadUser();
  }, [loadUser]);

  /**
   * Register a new user.
   * Does NOT auto-login — returns success so the Auth page can show a message.
   */
  const register = async ({ name, email, password }) => {
    const data = await apiRegister({ name, email, password });
    return data;
  };

  /**
   * Login: calls the API, stores the token, then fetches the user profile.
   */
  const login = async ({ email, password }) => {
    const data = await apiLogin({ email, password });
    localStorage.setItem("token", data.access_token);
    setToken(data.access_token);

    // Immediately fetch user profile with the new token
    const userData = await fetchCurrentUser(data.access_token);
    setUser(userData);

    const profileExists = await checkProfileStatus(data.access_token);
    setHasProfile(profileExists);
    
    return { user: userData, hasProfile: profileExists };
  };

  /**
   * Logout: clear token and user state.
   */
  const logout = () => {
    localStorage.removeItem("token");
    setToken(null);
    setUser(null);
    setHasProfile(null);
  };

  const value = {
    user,
    token,
    loading,
    hasProfile,
    setHasProfile,
    isAuthenticated: !!user,
    login,
    register,
    logout,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

/**
 * Custom hook to consume auth context.
 * Usage: const { user, login, logout, hasProfile } = useAuth();
 */
export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
}
