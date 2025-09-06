"use client";

import {
  NEXT_PUBLIC_AUTH_SERVICE_URL,
  NEXT_PUBLIC_USER_SERVICE_URL,
} from "@/lib/constants";
import { apiClient } from "@/lib/api-client";
import React, {
  createContext,
  useContext,
  useState,
  useEffect,
  ReactNode,
} from "react";

interface User {
  id: string;
  username: string;
  type: "provider" | "submitter";
  credits?: number; // Optional for backward compatibility
}

interface AuthContextType {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  login: (username: string, password: string) => Promise<void>;
  register: (
    username: string,
    password: string,
    type: "provider" | "submitter"
  ) => Promise<void>;
  logout: () => void;
  refreshCredits: () => Promise<void>;
  loading: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
};

interface AuthProviderProps {
  children: ReactNode;
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  // Check for existing token on app load
  useEffect(() => {
    const savedToken = localStorage.getItem("token");
    const savedUser = localStorage.getItem("user");

    if (savedToken && savedUser) {
      try {
        setToken(savedToken);
        setUser(JSON.parse(savedUser));
      } catch (error) {
        console.error("Error parsing saved user data:", error);
        localStorage.removeItem("token");
        localStorage.removeItem("user");
      }
    }
    setLoading(false);
  }, []);

  const login = async (username: string, password: string) => {
    try {
      setLoading(true);

      const formData = new FormData();
      formData.append("username", username);
      formData.append("password", password);

      const response = await fetch(`${NEXT_PUBLIC_AUTH_SERVICE_URL}/login`, {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || "Login failed");
      }

      const data = await response.json();
      const { access_token } = data;

      // Get user info from data service
      const userResponse = await fetch(
        `${NEXT_PUBLIC_USER_SERVICE_URL}/users/${username}`
      );
      if (!userResponse.ok) {
        throw new Error("Failed to fetch user data");
      }

      const userData = await userResponse.json();
      const user: User = {
        id: userData.id,
        username: userData.username,
        type: userData.type,
        credits: userData.credits || 5, // Default to 5 credits for new users, fallback for existing
      };

      // Save to state and localStorage
      setToken(access_token);
      setUser(user);
      localStorage.setItem("token", access_token);
      localStorage.setItem("user", JSON.stringify(user));
      
      // Set current user in API client
      apiClient.setCurrentUser(user.username);
    } catch (error) {
      console.error("Login error:", error);
      throw error;
    } finally {
      setLoading(false);
    }
  };

  const register = async (
    username: string,
    password: string,
    type: "provider" | "submitter"
  ) => {
    try {
      setLoading(true);

      const response = await fetch(`${NEXT_PUBLIC_AUTH_SERVICE_URL}/register`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ username, password, type }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || "Registration failed");
      }

      // Auto-login after successful registration
      await login(username, password);
    } catch (error) {
      console.error("Registration error:", error);
      throw error;
    } finally {
      setLoading(false);
    }
  };

  const logout = () => {
    setUser(null);
    setToken(null);
    localStorage.removeItem("token");
    localStorage.removeItem("user");
    
    // Clear current user in API client
    apiClient.setCurrentUser("");
  };

  const refreshCredits = async () => {
    if (!user) return;
    
    try {
      const response = await fetch(`${NEXT_PUBLIC_USER_SERVICE_URL}/users/${user.username}`);
      if (response.ok) {
        const userData = await response.json();
        const updatedUser = { ...user, credits: userData.credits || user.credits || 5 };
        setUser(updatedUser);
        localStorage.setItem('user', JSON.stringify(updatedUser));
      }
    } catch (error) {
      console.error('Failed to refresh credits:', error);
    }
  };

  const value: AuthContextType = {
    user,
    token,
    isAuthenticated: !!user && !!token,
    login,
    register,
    logout,
    refreshCredits,
    loading,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};
