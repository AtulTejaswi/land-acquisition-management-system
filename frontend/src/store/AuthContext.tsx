import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { User, authService } from '../services/auth';

interface AuthContextType {
  user: User | null;
  token: string | null;
  login: (email: string, password: string) => Promise<void>;
  logout: () => void;
  isLoading: boolean;
}

const AuthContext = createContext<AuthContextType>({
  user: null,
  token: null,
  login: async () => {},
  logout: () => {},
  isLoading: true,
});

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const storedToken = localStorage.getItem('nlams_access_token');
    const storedUser = localStorage.getItem('nlams_user');
    if (storedToken && storedUser) {
      setToken(storedToken);
      try {
        setUser(JSON.parse(storedUser));
      } catch {}
    }
    setIsLoading(false);
  }, []);

  const login = async (email: string, password: string) => {
    const response = await authService.login(email, password);
    localStorage.setItem('nlams_access_token', response.access_token);
    localStorage.setItem('nlams_refresh_token', response.refresh_token);
    localStorage.setItem('nlams_user', JSON.stringify(response.user));
    setToken(response.access_token);
    setUser(response.user);
  };

  const logout = () => {
    authService.logout();
    setToken(null);
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{ user, token, login, logout, isLoading }}>
      {children}
    </AuthContext.Provider>
  );
}

export const useAuth = () => useContext(AuthContext);
