import { createContext, useContext, useEffect, useState } from "react";
import { apiRequest } from "./api";
import { BANK_ID } from "./config";

const AuthContext = createContext(null);

const STORAGE_KEYS = {
  token: `${BANK_ID}.token`,
  user: `${BANK_ID}.user`,
};

export function AuthProvider({ children }) {
  const [token, setToken] = useState(localStorage.getItem(STORAGE_KEYS.token));
  const [user, setUser] = useState(() => {
    const rawUser = localStorage.getItem(STORAGE_KEYS.user);
    return rawUser ? JSON.parse(rawUser) : null;
  });
  const [loading, setLoading] = useState(Boolean(token));

  useEffect(() => {
    if (!token) {
      setLoading(false);
      return;
    }

    let isMounted = true;
    apiRequest("/auth/me", { token })
      .then((currentUser) => {
        if (!isMounted) {
          return;
        }
        setUser(currentUser);
        localStorage.setItem(STORAGE_KEYS.user, JSON.stringify(currentUser));
      })
      .catch(() => {
        if (!isMounted) {
          return;
        }
        logout();
      })
      .finally(() => {
        if (isMounted) {
          setLoading(false);
        }
      });

    return () => {
      isMounted = false;
    };
  }, [token]);

  function saveSession(payload) {
    setToken(payload.access_token);
    setUser(payload.user);
    localStorage.setItem(STORAGE_KEYS.token, payload.access_token);
    localStorage.setItem(STORAGE_KEYS.user, JSON.stringify(payload.user));
  }

  async function login(credentials) {
    const payload = await apiRequest("/auth/login", {
      method: "POST",
      body: credentials,
    });
    saveSession(payload);
    return payload;
  }

  async function register(data) {
    const payload = await apiRequest("/auth/register", {
      method: "POST",
      body: data,
    });
    saveSession(payload);
    return payload;
  }

  function logout() {
    setToken(null);
    setUser(null);
    localStorage.removeItem(STORAGE_KEYS.token);
    localStorage.removeItem(STORAGE_KEYS.user);
  }

  const value = {
    token,
    user,
    loading,
    isAuthenticated: Boolean(token),
    login,
    register,
    logout,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used inside AuthProvider");
  }
  return context;
}
