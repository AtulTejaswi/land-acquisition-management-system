import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { User, authService } from '../services/auth';

interface AuthContextType {
  user: User | null;
  login: (email: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
  switchRole: (roleName: string) => void;
  isLoading: boolean;
}

const AuthContext = createContext<AuthContextType>({
  user: null,
  login: async () => {},
  logout: async () => {},
  switchRole: () => {},
  isLoading: true,
});

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const justLoggedIn = React.useRef(false);

  useEffect(() => {
    // If user was just set by login(), trust it and skip the /auth/me probe
    if (justLoggedIn.current) {
      justLoggedIn.current = false;
      setIsLoading(false);
      return;
    }

    // On mount, try to fetch user via cookie-based /auth/me
    const storedUser = localStorage.getItem('nlams_user');
    if (storedUser) {
      // Optimistic: show cached user immediately, then verify with server
      try {
        setUser(JSON.parse(storedUser));
      } catch { /* ignore */ }
    }

    authService
      .getMe()
      .then((u) => {
        setUser(u);
        localStorage.setItem('nlams_user', JSON.stringify(u));
      })
      .catch(() => {
        // No valid cookie — clear cached user
        setUser(null);
        localStorage.removeItem('nlams_user');
      })
      .finally(() => setIsLoading(false));
  }, []);

  const login = async (email: string, password: string) => {
    const response = await authService.login(email, password);
    // Server sets httpOnly cookies; we only store the user object for UI
    localStorage.setItem('nlams_user', JSON.stringify(response.user));
    setUser(response.user);
    justLoggedIn.current = true;
  };

  const logout = async () => {
    await authService.logout();
    setUser(null);
  };

  const switchRole = (roleName: string) => {
    if (user) {
      const updatedUser = { ...user, role_name: roleName };
      setUser(updatedUser);
      localStorage.setItem('nlams_user', JSON.stringify(updatedUser));
    }
  };

  return (
    <AuthContext.Provider value={{ user, login, logout, switchRole, isLoading }}>
      {children}
    </AuthContext.Provider>
  );
}

export const useAuth = () => useContext(AuthContext);
