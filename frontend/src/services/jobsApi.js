const API_BASE_URL = 'http://localhost:8000';

function authHeaders() {
  const token = localStorage.getItem('token');
  return token ? { Authorization: `Bearer ${token}` } : {};
}

/**
 * Triggers a new job search.
 * Returns the Response object so the caller can read the SSE stream.
 */
export async function startJobSearchStream(query) {
  const res = await fetch(`${API_BASE_URL}/api/job-search/run`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', ...authHeaders() },
    body: JSON.stringify({
      query: query
    }),
  });
  
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || 'Search failed to start');
  }
  
  // Return the raw response so the component can consume res.body as a stream
  return res;
}

/**
 * Resumes a failed or paused job search stream.
 * Returns the Response object so the caller can read the SSE stream.
 */
export async function resumeJobSearchStream(threadId) {
  const res = await fetch(`${API_BASE_URL}/api/job-search/resume/${threadId}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', ...authHeaders() },
  });
  
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || 'Failed to resume search');
  }
  
  return res;
}

/**
 * Fetches the history of job searches for a specific candidate.
 */
export async function fetchSearchHistory() {
  const res = await fetch(`${API_BASE_URL}/api/job-search/history`, {
    headers: authHeaders(),
  });
  if (!res.ok) throw new Error('Failed to fetch search history');
  return res.json();
}

/**
 * Fetches the fully assembled scored jobs for a completed search thread.
 */
export async function fetchSearchResults(threadId) {
  const res = await fetch(`${API_BASE_URL}/api/job-search/${threadId}/results`, {
    headers: authHeaders(),
  });
  if (!res.ok) throw new Error('Failed to fetch search results');
  return res.json();
}

/**
 * Renames a job search session.
 */
export async function renameJobSearch(threadId, newName) {
  const res = await fetch(`${API_BASE_URL}/api/job-search/${threadId}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json', ...authHeaders() },
    body: JSON.stringify({ name: newName }),
  });
  if (!res.ok) throw new Error('Failed to rename search');
  return res.json();
}

/**
 * Deletes a job search session.
 */
export async function deleteJobSearch(threadId) {
  const res = await fetch(`${API_BASE_URL}/api/job-search/${threadId}`, {
    method: 'DELETE',
    headers: authHeaders(),
  });
  if (!res.ok) throw new Error('Failed to delete search');
  return res.json();
}
