const API_BASE = import.meta.env.VITE_API_URL || "http://127.0.0.1:8005";

async function request(path, options = {}) {
  const res = await fetch(`${API_BASE}${path}`, {
    headers: { "Content-Type": "application/json", ...options.headers },
    ...options,
  });
  if (!res.ok) throw new Error(`API ${res.status}: ${res.statusText}`);
  return res.json();
}

export const api = {
  getPosts: (limit = 50) => request(`/posts?limit=${limit}`),
  getUserFeed: (userId, limit = 50) => request(`/posts/feed/${userId}?limit=${limit}`),
  getPost: (id) => request(`/posts/${id}`),
  likePost: (id) => request(`/posts/${id}/like`, { method: "POST" }),

  getUsers: (limit = 50) => request(`/users?limit=${limit}`),
  getUser: (id) => request(`/users/${id}`),
  getFollowers: (id) => request(`/users/${id}/followers`),
  getFollowing: (id) => request(`/users/${id}/following`),

  getInbox: (userId, limit = 50) => request(`/messages/inbox/${userId}?limit=${limit}`),
  getConversation: (userId, otherId) => request(`/messages/conversation/${userId}/${otherId}`),

  createReport: (reporterId, payload) =>
    request(`/reports?reporter_id=${reporterId}`, {
      method: "POST",
      body: JSON.stringify(payload),
    }),

  analyzePost: (postId) => request(`/analysis/post/${postId}`),
  analyzeMessage: (msgId) => request(`/analysis/message/${msgId}`),
  fullScan: () => request(`/analysis/scan`),
};
