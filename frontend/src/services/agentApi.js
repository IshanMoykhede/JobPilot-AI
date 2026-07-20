const API_BASE_URL = 'http://localhost:8000';

export async function submitChat(message, conversationId = null) {
  const token = localStorage.getItem('token');
  const res = await fetch(`${API_BASE_URL}/agent/chat`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      ...(token && { Authorization: `Bearer ${token}` })
    },
    body: JSON.stringify({ message, conversation_id: conversationId })
  });

  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new Error(errorData.detail || 'Failed to communicate with agent');
  }

  return res.json();
}

export async function fetchConversations() {
  const token = localStorage.getItem('token');
  const res = await fetch(`${API_BASE_URL}/agent/conversations`, {
    headers: {
      ...(token && { Authorization: `Bearer ${token}` })
    }
  });

  if (!res.ok) {
    throw new Error('Failed to fetch conversations');
  }

  return res.json();
}

export async function fetchConversationMessages(conversationId) {
  const token = localStorage.getItem('token');
  const res = await fetch(`${API_BASE_URL}/agent/conversations/${conversationId}`, {
    headers: {
      ...(token && { Authorization: `Bearer ${token}` })
    }
  });

  if (!res.ok) {
    throw new Error('Failed to fetch conversation messages');
  }

  return res.json();
}

export async function deleteConversation(conversationId) {
  const token = localStorage.getItem('token');
  const res = await fetch(`${API_BASE_URL}/agent/conversations/${conversationId}`, {
    method: 'DELETE',
    headers: {
      ...(token && { Authorization: `Bearer ${token}` })
    }
  });

  if (!res.ok) {
    throw new Error('Failed to delete conversation');
  }

  return res.json();
}

export const testSerp = async (query, location = "") => {
  const token = localStorage.getItem("token");
  if (!token) throw new Error("No token found");

  const url = new URL(`${API_BASE_URL}/agent/test-serp`);
  url.searchParams.append("query", query);
  if (location) {
    url.searchParams.append("location", location);
  }

  const response = await fetch(url, {
    method: "GET",
    headers: {
      Authorization: `Bearer ${token}`
    }
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.detail || "Failed to test SerpAPI");
  }

  return response.json();
};
