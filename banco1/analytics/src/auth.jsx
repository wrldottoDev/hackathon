import { createContext, useContext, useEffect, useState } from "react";
import { bankRequest } from "./api";
import { BANKS, getBankById } from "./banks";

const AnalysisAuthContext = createContext(null);

const STORAGE_KEYS = {
  bankId: "analysis.bankId",
  token: "analysis.token",
  user: "analysis.user",
};

export function AnalysisAuthProvider({ children }) {
  const [bankId, setBankId] = useState(localStorage.getItem(STORAGE_KEYS.bankId) || BANKS[0].id);
  const [token, setToken] = useState(localStorage.getItem(STORAGE_KEYS.token));
  const [user, setUser] = useState(() => {
    const rawUser = localStorage.getItem(STORAGE_KEYS.user);
    return rawUser ? JSON.parse(rawUser) : null;
  });
  const [loading, setLoading] = useState(Boolean(token));

  const selectedBank = getBankById(bankId);

  useEffect(() => {
    localStorage.setItem(STORAGE_KEYS.bankId, selectedBank.id);
  }, [selectedBank.id]);

  useEffect(() => {
    if (!token) {
      setLoading(false);
      return;
    }

    let isMounted = true;
    bankRequest(selectedBank.apiUrl, "/auth/me", { token })
      .then((currentUser) => {
        if (!isMounted) {
          return;
        }
        setUser(currentUser);
        localStorage.setItem(STORAGE_KEYS.user, JSON.stringify(currentUser));
      })
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
  }, [selectedBank.apiUrl, token]);

  function saveSession(nextBankId, payload) {
    setBankId(nextBankId);
    setToken(payload.access_token);
    setUser(payload.user);
    localStorage.setItem(STORAGE_KEYS.bankId, nextBankId);
    localStorage.setItem(STORAGE_KEYS.token, payload.access_token);
    localStorage.setItem(STORAGE_KEYS.user, JSON.stringify(payload.user));
  }

  async function login({ bankId: nextBankId, email, password }) {
    const bank = getBankById(nextBankId);
    const payload = await bankRequest(bank.apiUrl, "/auth/login", {
      method: "POST",
      body: { email, password },
    });
    saveSession(bank.id, payload);
    return payload;
  }

  function logout() {
    setToken(null);
    setUser(null);
    localStorage.removeItem(STORAGE_KEYS.token);
    localStorage.removeItem(STORAGE_KEYS.user);
  }

  function changeBank(nextBankId) {
    if (nextBankId === selectedBank.id) {
      return;
    }
    logout();
    setBankId(nextBankId);
    localStorage.setItem(STORAGE_KEYS.bankId, nextBankId);
  }

  const value = {
    banks: BANKS,
    selectedBank,
    token,
    user,
    loading,
    isAuthenticated: Boolean(token),
    login,
    logout,
    changeBank,
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
