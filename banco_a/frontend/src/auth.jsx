import { createContext, useCallback, useContext, useEffect, useState } from "react";
import { apiRequest } from "./api";

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [token, setToken] = useState(() => localStorage.getItem("bka_token"));
  const [user, setUser] = useState(() => {
    try {
      return JSON.parse(localStorage.getItem("bka_user"));
    } catch {
      return null;
    }
  });

  useEffect(() => {
    if (!token) return;
    apiRequest("/auth/me", {}, token)
      .then(setUser)
      .catch(() => {
        setToken(null);
        setUser(null);
        localStorage.removeItem("bka_token");
        localStorage.removeItem("bka_user");
      });
  }, []);

  const login = useCallback(async (email, password) => {
    const data = await apiRequest("/auth/login", {
      method: "POST",
      body: JSON.stringify({ email, password }),
    });
    localStorage.setItem("bka_token", data.access_token);
    localStorage.setItem("bka_user", JSON.stringify(data.user));
    setToken(data.access_token);
    setUser(data.user);
    return data;
  }, []);

  const register = useCallback(async (full_name, email, password) => {
    return apiRequest("/auth/register", {
      method: "POST",
      body: JSON.stringify({ full_name, email, password }),
    });
  }, []);

  const logout = useCallback(() => {
    localStorage.removeItem("bka_token");
    localStorage.removeItem("bka_user");
    setToken(null);
    setUser(null);
  }, []);

  return (
    <AuthContext.Provider
      value={{ token, user, isAuthenticated: !!token, login, register, logout }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  return useContext(AuthContext);
}
