// Simple auth API wrapper for login and registration
// Adjust BASE_URL via VITE_API_BASE_URL in .env

const BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1/auth';

async function handleResponse(res) {
  let data = null;
  try {
    data = await res.json();
  } catch {
    // ignore json parse errors
  }
  if (!res.ok) {
    const message = data?.detail || data?.error || `Request failed (${res.status})`;
    const error = new Error(message);
    error.status = res.status;
    error.data = data;
    throw error;
  }
  return data;
}

export async function login({ login, password }) {
  const res = await fetch(`${BASE_URL}/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ login, password }),
  });
  return handleResponse(res); // expecting { access_token, token_type }
}

export async function register({ username, email, password }) {
  const res = await fetch(`${BASE_URL}/register`, {
    method: 'POST',
    credentials: 'include',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ username, email, password }),
  });
  return handleResponse(res); // expecting created user object
}

export function setTokenCookie(token, remember = false, days = 30) {
  try {
    const base = `auth_token=${encodeURIComponent(token)}; Path=/; SameSite=Strict`;
    if (remember) {
      const maxAge = Math.max(1, Math.floor(days * 24 * 60 * 60));
      const expires = new Date(Date.now() + maxAge * 1000).toUTCString();
      document.cookie = `${base}; Expires=${expires}; Max-Age=${maxAge}`;
    } else {
      // session cookie (no Expires/Max-Age)
      document.cookie = base;
    }
  } catch {
    // ignore cookie set error
  }
}

export function getTokenCookie() {
  try {
    return document.cookie
      .split(';')
      .map(v => v.trim())
      .find(v => v.startsWith('auth_token='))?.split('=')[1] || null;
  } catch {
    return null;
  }
}

export function getToken() {
  try {
    const fromCookie = (typeof document !== 'undefined') ? document.cookie
      .split(';')
      .map(v => v.trim())
      .find(v => v.startsWith('auth_token='))?.split('=')[1] : null;
    if (fromCookie) return decodeURIComponent(fromCookie);
  } catch {
    // ignore cookie read error
  }
  try {
    return (typeof localStorage !== 'undefined') ? localStorage.getItem('auth_token') : null;
  } catch {
    return null;
  }
}

export async function logoutServer() {
  try {
    await fetch(`${BASE_URL}/logout`, {
      method: 'POST',
      credentials: 'include'
    });
  } catch {
    // ignore
  }
}

export function clearToken() {
  try {
    document.cookie = 'auth_token=; Path=/; Max-Age=0; Expires=Thu, 01 Jan 1970 00:00:00 GMT; SameSite=Strict';
  } catch {
    // ignore
  }
  try {
    if (typeof localStorage !== 'undefined') localStorage.removeItem('auth_token');
  } catch {
    // ignore
  }
}
