import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import axios from 'axios';

interface User {
  id: number;
  email: string;
  created_at: string;
  is_active: boolean;
}

interface AuthContextType {
  user: User | null;
  token: string | null;
  login: (email: string, password: string) => Promise<void>;
  signup: (email: string, password: string) => Promise<void>;
  logout: () => void;
  loading: boolean;
  isAuthenticated: boolean;
}

interface AuthResponse {
  access_token: string;
  user: User;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

interface AuthProviderProps {
  children: ReactNode;
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const savedToken = localStorage.getItem('auth_token');
    const savedUser = localStorage.getItem('auth_user');

    if (savedToken && savedUser) {
      try {
        setToken(savedToken);
        setUser(JSON.parse(savedUser));
        
        // Set axios default header
        axios.defaults.headers.common['Authorization'] = `Bearer ${savedToken}`;
      } catch (error) {
        console.error('Error parsing saved user data:', error);
        localStorage.removeItem('auth_token');
        localStorage.removeItem('auth_user');
      }
    }
    
    setLoading(false);
  }, []);

  const login = async (email: string, password: string): Promise<void> => {
    try {
      const response = await axios.post<AuthResponse>('http://localhost:8000/api/auth/login', {
        email,
        password
      });

      const { access_token, user: userData } = response.data;

      setToken(access_token);
      setUser(userData);

      localStorage.setItem('auth_token', access_token);
      localStorage.setItem('auth_user', JSON.stringify(userData));

      axios.defaults.headers.common['Authorization'] = `Bearer ${access_token}`;

    } catch (error: any) {
      throw new Error(
        error.response?.data?.detail || 
        'Login failed. Please check your credentials.'
      );
    }
  };

  const signup = async (email: string, password: string): Promise<void> => {
    try {
      const response = await axios.post<AuthResponse>('http://localhost:8000/api/auth/signup', {
        email,
        password
      });

      const { access_token, user: userData } = response.data;

      setToken(access_token);
      setUser(userData);

      localStorage.setItem('auth_token', access_token);
      localStorage.setItem('auth_user', JSON.stringify(userData));

      axios.defaults.headers.common['Authorization'] = `Bearer ${access_token}`;

    } catch (error: any) {
      throw new Error(
        error.response?.data?.detail || 
        'Signup failed. Please try again.'
      );
    }
  };

  const logout = (): void => {
    setUser(null);
    setToken(null);

    // Remove from localStorage
    localStorage.removeItem('auth_token');
    localStorage.removeItem('auth_user');

    // Remove axios default header
    delete axios.defaults.headers.common['Authorization'];
  };

  const isAuthenticated = !!user && !!token;

  const value: AuthContextType = {
    user,
    token,
    login,
    signup,
    logout,
    loading,
    isAuthenticated
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = (): AuthContextType => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};