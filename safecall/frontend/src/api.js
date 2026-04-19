const API_BASE = import.meta.env.VITE_API_URL || "http://127.0.0.1:8006";

async function request(path, options = {}) {
  const res = await fetch(`${API_BASE}${path}`, {
    headers: { "Content-Type": "application/json", ...options.headers },
    ...options,
  });
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new Error(body.detail || `API ${res.status}: ${res.statusText}`);
  }
  return res.json();
}

export const api = {
  lookup: (number) => request(`/api/lookup/${encodeURIComponent(number)}`),
  listPhoneNumbers: (skip = 0, limit = 100) =>
    request(`/api/phone-numbers?skip=${skip}&limit=${limit}`),

  createReport: (data) =>
    request("/api/report", { method: "POST", body: JSON.stringify(data) }),
  listReports: (skip = 0, limit = 50) =>
    request(`/api/reports?skip=${skip}&limit=${limit}`),

  listUsers: (skip = 0, limit = 50) =>
    request(`/api/users/?skip=${skip}&limit=${limit}`),
  getUser: (id) => request(`/api/users/${id}`),
  registerUser: (data) =>
    request("/api/users/", { method: "POST", body: JSON.stringify(data) }),
};
