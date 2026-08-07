import { createContext, useContext, useState, ReactNode } from 'react';
import { apiFetch } from "../api";

interface User {
  name: string;
  email: string;
  username: string;
  role: string;
  avatar: string;
}

interface AuthContextType {
  user: User | null;
  isAuthenticated: boolean;
  signIn: (username: string, password: string) => Promise<boolean>;
  signOut: () => void;
}

const AuthContext = createContext<AuthContextType>({
  user: null,
  isAuthenticated: false,
  signIn: async () => false,
  signOut: () => {},
});

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);

  const signIn = async (username: string, password: string): Promise<boolean> => {
  try {
    const response = await fetch(
      "https://support-ai-ticket-management-team-18k9.onrender.com/api/auth/login/",
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          email: username,
          password,
        }),
      }
    );

    const data = await response.json();

    if (!response.ok) {
      console.log(data.message);
      return false;
    }

    localStorage.setItem("access", data.access);
    localStorage.setItem("refresh", data.refresh);

    const meResponse = await apiFetch("/api/auth/me/");
    const meData = await meResponse.json();

    if (!meResponse.ok) {
      console.log("ME API error:", meData.message);
      return false;
    }

    setUser({
      name: meData.username,
      username: meData.username,
      email: meData.email,
      role: "User",
      avatar: meData.username.charAt(0).toUpperCase(),
    });

    return true;

  } catch (error) {
    console.error("Login error:", error);
    return false;
  }
};

  const signOut = () => {
  localStorage.removeItem("access");
  localStorage.removeItem("refresh");
  setUser(null);
};

  return (
    <AuthContext.Provider value={{ user, isAuthenticated: !!user, signIn, signOut }}>
      {children}
    </AuthContext.Provider>
  );
}

export const useAuth = () => useContext(AuthContext);
