import { createContext, useCallback, useContext, useEffect, useState } from "react";
import { analyticsRequest } from "./api";
import { DEFAULT_ANALYTICS_KEY, STORAGE_PREFIX } from "./config";

const AnalysisAuthContext = createContext(null);

const API_KEY_STORAGE = `${STORAGE_PREFIX}.apiKey`;

export function AnalysisAuthProvider({ children }) {
  const [apiKey, setApiKey] = useState(() => localStorage.getItem(API_KEY_STORAGE) || "");
  const [loading, setLoading] = useState(Boolean(localStorage.getItem(API_KEY_STORAGE)));

  const logout = useCallback(() => {
    setApiKey("");
    localStorage.removeItem(API_KEY_STORAGE);
  }, []);

  useEffect(() => {
    if (!apiKey) {
      setLoading(false);
      return;
    }

    let isMounted = true;
    analyticsRequest("/banks", { apiKey })
      .catch(() => {
        if (isMounted) {
          logout();
        }
      })
      .finally(() => {
        if (isMounted) {
          setLoading(false);
        }
      });

    return () => {
      isMounted = false;
    };
  }, [apiKey, logout]);

  async function login(nextApiKey) {
    const sanitized = nextApiKey.trim() || DEFAULT_ANALYTICS_KEY;
    await analyticsRequest("/banks", { apiKey: sanitized });
    setApiKey(sanitized);
    localStorage.setItem(API_KEY_STORAGE, sanitized);
    return sanitized;
  }

  const value = {
    apiKey,
    loading,
    isAuthenticated: Boolean(apiKey),
    login,
    logout,
  };

  return <AnalysisAuthContext.Provider value={value}>{children}</AnalysisAuthContext.Provider>;
}

export function useAnalysisAuth() {
  const context = useContext(AnalysisAuthContext);
  if (!context) {
    throw new Error("useAnalysisAuth must be used inside AnalysisAuthProvider");
  }
  return context;
}
