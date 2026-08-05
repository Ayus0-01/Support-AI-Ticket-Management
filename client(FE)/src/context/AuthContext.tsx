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
  signIn: (username: string, password: string) => boolean;
  signOut: () => void;
}

const DEFAULT_USER: User = {
  name: 'Lakshmipriya Gutti',
  email: 'lakshmipriya@gmail.com',
  username: 'lakshmipriya',
  role: 'Admin',
  avatar: 'L',
};

const AuthContext = createContext<AuthContextType>({
  user: null,
  isAuthenticated: false,
  signIn: () => false,
  signOut: () => {},
});

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);

  const signIn = (username: string, password: string): boolean => {
    if (
      (username === 'lakshmipriya' || username === 'lakshmipriya@gmail.com') &&
      password === 'Lakshmi@123'
    ) {
      setUser(DEFAULT_USER);
      return true;
    }
    return false;
  };

  const signOut = () => setUser(null);

  return (
    <AuthContext.Provider value={{ user, isAuthenticated: !!user, signIn, signOut }}>
      {children}
    </AuthContext.Provider>
  );
}

export const useAuth = () => useContext(AuthContext);
