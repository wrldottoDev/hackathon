import { API_URL } from "./config";

export async function apiRequest(path, options = {}, token = null) {
  const headers = {
    "Content-Type": "application/json",
    ...options.headers,
  };
  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }

  const res = await fetch(`${API_URL}${path}`, { ...options, headers });

  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: "Error desconocido" }));
    const detail = err.detail;
    if (Array.isArray(detail)) {
      const message = detail
        .map((item) => {
          const field = item.loc?.[item.loc.length - 1] || "campo";
          return `${field}: ${item.msg}`;
        })
        .join(" | ");
      throw new Error(message || `Error ${res.status}`);
    }
    throw new Error(detail || `Error ${res.status}`);
  }

  return res.json();
}

export function formatCurrency(amount, currency = "CRC") {
  return new Intl.NumberFormat("es-CR", {
    style: "currency",
    currency,
    minimumFractionDigits: 2,
  }).format(amount);
}

export function formatDate(dateStr) {
  return new Intl.DateTimeFormat("es-CR", {
    year: "numeric",
    month: "short",
    day: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  }).format(new Date(dateStr + "Z"));
}
