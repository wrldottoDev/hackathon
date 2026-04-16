import { API_URL } from "./config";

export async function analyticsRequest(
  path,
  { method = "GET", apiKey, body, params } = {},
) {
  const search = new URLSearchParams();
  if (params) {
    Object.entries(params).forEach(([key, value]) => {
      if (value !== undefined && value !== null && value !== "") {
        search.set(key, String(value));
      }
    });
  }

  const query = search.toString();
  const response = await fetch(
    `${API_URL.replace(/\/$/, "")}${path}${query ? `?${query}` : ""}`,
    {
      method,
      headers: {
        "Content-Type": "application/json",
        ...(apiKey ? { "X-Analytics-Key": apiKey } : {}),
      },
      body: body ? JSON.stringify(body) : undefined,
    },
  );

  const contentType = response.headers.get("content-type") || "";
  const payload = contentType.includes("application/json") ? await response.json() : null;

  if (!response.ok) {
    if (Array.isArray(payload?.detail)) {
      throw new Error(
        payload.detail
          .map((item) => {
            const field = item.loc?.[item.loc.length - 1] || "campo";
            return `${field}: ${item.msg}`;
          })
          .join(" | "),
      );
    }
    throw new Error(payload?.detail || payload?.message || `Error ${response.status}`);
  }

  return payload;
}

export function formatCurrency(value) {
  return new Intl.NumberFormat("es-CR", {
    style: "currency",
    currency: "CRC",
    maximumFractionDigits: 2,
  }).format(value || 0);
}

export function formatDate(value) {
  return new Intl.DateTimeFormat("es-CR", {
    dateStyle: "medium",
    timeStyle: "short",
  }).format(new Date(value));
}

export function maskKey(value) {
  if (!value) {
    return "";
  }
  if (value.length <= 8) {
    return "•".repeat(value.length);
  }
  return `${value.slice(0, 4)}••••${value.slice(-4)}`;
}
