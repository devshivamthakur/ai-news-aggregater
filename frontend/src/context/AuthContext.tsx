"use client";

import React, { createContext, useContext, useState, useEffect, useCallback } from "react";
import { api, User, TokenPairOut } from "@/lib/api";

interface AuthContextType {
  user: User | null;
  isLoading: boolean;
  isAuthenticated: boolean;
  isAdmin: boolean;
  login: (email: string, password: string) => Promise<void>;
  register: (email: string, password: string, name: string) => Promise<void>;
  logout: () => void;
  refreshUser: () => Promise<void>;
  updateProfile: (data: { name?: string; interests?: string[] }) => Promise<void>;
  changePassword: (currentPassword: string, newPassword: string) => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  const refreshUser = useCallback(async () => {
    if (!api.isAuthenticated()) {
      setIsLoading(false);
      return;
    }
    try {
      const userData = await api.get<User>("/me");
      setUser(userData);
    } catch {
      setUser(null);
      api.clearTokens();
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    refreshUser();
  }, [refreshUser]);

  // Keep sessions in sync across tabs: when tokens change or are cleared in
  // another tab (login/logout), reflect that here immediately.
  useEffect(() => {
    const handleStorage = (event: StorageEvent) => {
      if (event.key !== "access_token" && event.key !== "refresh_token") return;
      if (api.isAuthenticated()) {
        refreshUser();
      } else {
        setUser(null);
        setIsLoading(false);
      }
    };
    window.addEventListener("storage", handleStorage);
    return () => window.removeEventListener("storage", handleStorage);
  }, [refreshUser]);

  const login = async (email: string, password: string) => {
    const data = await api.post<TokenPairOut>("/login", { email, password });
    api.setTokens(data.access_token, data.refresh_token);
    await refreshUser();
  };

  const register = async (email: string, password: string, name: string) => {
    const data = await api.post<TokenPairOut>("/register", { email, password, name });
    api.setTokens(data.access_token, data.refresh_token);
    await refreshUser();
  };

  const logout = () => {
    api.clearTokens();
    setUser(null);
  };

  const updateProfile = async (data: { name?: string; interests?: string[] }) => {
    const updated = await api.patch<User>("/me", data);
    setUser(updated);
  };

  const changePassword = async (currentPassword: string, newPassword: string) => {
    await api.post("/me/change-password", {
      current_password: currentPassword,
      new_password: newPassword,
    });
  };

  const isAdmin = user?.role === "admin" || user?.role === "super_admin";

  return (
    <AuthContext.Provider
      value={{
        user,
        isLoading,
        isAuthenticated: !!user,
        isAdmin,
        login,
        register,
        logout,
        refreshUser,
        updateProfile,
        changePassword,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
}
