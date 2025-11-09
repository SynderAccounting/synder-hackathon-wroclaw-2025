import { createContext, useContext, useEffect, useState, useCallback } from 'react';
import type { User, LoginCredentials, RegisterCredentials, AuthState } from '@/features/user/types';
import { authApi, tokenStorage, userStorage } from '@/features/user/api';

interface AuthContextType extends AuthState {
  login: (credentials: LoginCredentials) => Promise<void>;
  register: (credentials: RegisterCredentials) => Promise<void>;
  logout: () => void;
  refreshUser: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [state, setState] = useState<AuthState>({
    user: null,
    token: null,
    isAuthenticated: false,
    isLoading: true,
  });

  // Initialize auth state from localStorage
  useEffect(() => {
    const initAuth = async () => {
      const token = tokenStorage.getToken();
      const user = userStorage.getUser();

      if (token && user) {
        // Verify token is still valid by fetching user
        try {
          const freshUser = await authApi.getUser(token);
          userStorage.setUser(freshUser);
          setState({
            user: freshUser,
            token,
            isAuthenticated: true,
            isLoading: false,
          });
        } catch (error) {
          // Token invalid, clear storage
          tokenStorage.removeToken();
          userStorage.removeUser();
          setState({
            user: null,
            token: null,
            isAuthenticated: false,
            isLoading: false,
          });
        }
      } else {
        setState({
          user: null,
          token: null,
          isAuthenticated: false,
          isLoading: false,
        });
      }
    };

    initAuth();
  }, []);

  const login = useCallback(async (credentials: LoginCredentials) => {
    setState((prev) => ({ ...prev, isLoading: true }));

    try {
      // Get token from login
      const { token } = await authApi.login(credentials);
      tokenStorage.setToken(token);

      // Fetch user data with token
      const user = await authApi.getUser(token);
      userStorage.setUser(user);

      setState({
        user,
        token,
        isAuthenticated: true,
        isLoading: false,
      });
    } catch (error) {
      setState({
        user: null,
        token: null,
        isAuthenticated: false,
        isLoading: false,
      });
      throw error;
    }
  }, []);

  const register = useCallback(async (credentials: RegisterCredentials) => {
    setState((prev) => ({ ...prev, isLoading: true }));

    try {
      // Register user - wait for response
      await authApi.register(credentials);

      // Reset loading state
      setState((prev) => ({ ...prev, isLoading: false }));
    } catch (error) {
      setState((prev) => ({ ...prev, isLoading: false }));
      throw error;
    }
  }, []);

  const logout = useCallback(() => {
    tokenStorage.removeToken();
    userStorage.removeUser();
    setState({
      user: null,
      token: null,
      isAuthenticated: false,
      isLoading: false,
    });
  }, []);

  const refreshUser = useCallback(async () => {
    const token = tokenStorage.getToken();
    if (!token) return;

    try {
      const user = await authApi.getUser(token);
      userStorage.setUser(user);
      setState((prev) => ({ ...prev, user }));
    } catch (error) {
      // If refresh fails, logout
      logout();
      throw error;
    }
  }, [logout]);

  return (
    <AuthContext.Provider
      value={{
        ...state,
        login,
        register,
        logout,
        refreshUser,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}
