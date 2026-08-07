import { createContext, useContext, useState, ReactNode } from 'react';

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

    if (response.ok) {
      localStorage.setItem("access", data.access);
      localStorage.setItem("refresh", data.refresh);

      setUser({
        name: username,
        username: username,
        email: "",
        role: "User",
        avatar: username.charAt(0).toUpperCase(),
      });

      return true;
    }

    console.log(data.message);
    return false;
  } catch (error) {
    console.error(error);
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
