import { createContext, useContext, useState, ReactNode } from "react";
import api from "../api";

interface User {
  name: string;
  email: string;
  username: string;
  mobile?: string;
  role: "User" | "Agent" | "Admin";
  avatar: string;
}

interface AuthContextType {
  user: User | null;
  isAuthenticated: boolean;
  signIn: (username: string, password: string) => Promise<boolean>;
  signOut: () => void;
  register: (
    username: string,
    email: string,
    password: string,
    mobile: string,
    role: "User" | "Agent" | "Admin"
  ) => Promise<boolean>;
}

const AuthContext = createContext<AuthContextType>({
  user: null,
  isAuthenticated: false,

  signIn: async (
    _username: string,
    _password: string
  ): Promise<boolean> => {
    return false;
  },

  signOut: () => {},

  register: async (
  _username: string,
  _email: string,
  _password: string,
  _mobile: string,
  _role: "User" | "Agent" | "Admin"
): Promise<boolean> => {
  return false;
},
});

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);

  const signIn = async (
    username: string,
    password: string
  ): Promise<boolean> => {
    try {
      // 1. Login and get JWT tokens
      const response = await api.post("/api/auth/login/", {
        email: username,
        password: password,
      });

      // Axios stores the response body inside response.data
      const data = response.data;

      // 2. Save JWT tokens
      localStorage.setItem("access", data.access);
      localStorage.setItem("refresh", data.refresh);

      console.log("LOGIN SUCCESS:", data);

      // 3. Ask backend who is currently logged in
      const meResponse = await api.get("/api/auth/me/");

      const meData = meResponse.data;

      console.log("ME SUCCESS:", meData);

      // 4. Store user information in React state
      setUser({
        name: meData.username,
        username: meData.username,
        email: meData.email,
        mobile: meData.mobile,
        role: meData.role,
        avatar: meData.username.charAt(0).toUpperCase(),
      });

      return true;

    } catch (error: any) {
      console.error("LOGIN ERROR:", error);

      if (error.response) {
        console.error("STATUS:", error.response.status);
        console.error("RESPONSE:", error.response.data);
      }

      return false;
    }
  };

  const register = async (
  username: string,
  email: string,
  password: string,
  mobile: string,
  role: "User" | "Agent" | "Admin"
): Promise<boolean> => {
  try {
    const response = await api.post("/api/auth/register/", {
      username,
      email,
      password,
      mobile,
      role,
    });

    const data = response.data;

    // Save the JWT tokens returned by registration
    localStorage.setItem("access", data.access);
    localStorage.setItem("refresh", data.refresh);

    console.log("REGISTER SUCCESS:", data);

    // Get the newly registered user's information
    const meResponse = await api.get("/api/auth/me/");
    const meData = meResponse.data;

    setUser({
      name: meData.username,
      username: meData.username,
      email: meData.email,
      mobile: meData.mobile,
      role: meData.role,
      avatar: meData.username.charAt(0).toUpperCase(),
    });

    return true;
  } catch (error: any) {
    console.error("REGISTER ERROR:", error);

    if (error.response) {
      console.error("STATUS:", error.response.status);
      console.error("RESPONSE:", error.response.data);
    }

    return false;
  }
};

  const signOut = () => {
    localStorage.removeItem("access");
    localStorage.removeItem("refresh");
    setUser(null);
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        isAuthenticated: !!user,
        signIn,
        signOut,
        register,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export const useAuth = () => useContext(AuthContext);