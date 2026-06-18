const API_BASE_URL = "http://localhost:8000";

/**
 * Register a new user.
 * POST /auth/register
 */
export async function registerUser({ name, email, password }) {
  const res = await fetch(`${API_BASE_URL}/auth/register`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ name, email, password }),
  });

  const data = await res.json();
  if (!res.ok) {
    throw new Error(data.detail || "Registration failed");
  }
  return data;
}

/**
 * Login an existing user.
 * POST /auth/login
 * Returns { access_token, token_type }
 */
export async function loginUser({ email, password }) {
  const res = await fetch(`${API_BASE_URL}/auth/login`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, password }),
  });

  const data = await res.json();
  if (!res.ok) {
    throw new Error(data.detail || "Login failed");
  }
  return data;
}

/**
 * Fetch the current authenticated user's profile.
 * GET /auth/me
 * Requires Authorization: Bearer <token>
 */
export async function fetchCurrentUser(token) {
  const res = await fetch(`${API_BASE_URL}/auth/me`, {
    method: "GET",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${token}`,
    },
  });

  const data = await res.json();
  if (!res.ok) {
    throw new Error(data.detail || "Failed to fetch user");
  }
  return data;
}

/**
 * Check if the authenticated user has a Candidate Profile.
 * GET /profile/status
 */
export async function checkProfileStatus(token) {
  const res = await fetch(`${API_BASE_URL}/profile/status`, {
    method: "GET",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${token}`,
    },
  });

  const data = await res.json();
  if (!res.ok) {
    throw new Error(data.detail || "Failed to check profile status");
  }
  return data.profile_exists;
}
