import { create } from 'zustand';
import type { User } from '@/types';

interface AuthState {
  accessToken: string | null;
  user: User | null;
  setAuth: (token: string, user?: User | null) => void;
  setUser: (user: User | null) => void;
  logout: () => void;
}

// Access token is kept in memory (zustand) rather than localStorage to reduce
// XSS exposure. It's rehydrated on load via a silent refresh call in a real
// deployment; for now the login flow populates it directly.
export const useAuthStore = create<AuthState>((set) => ({
  accessToken: null,
  user: null,
  setAuth: (token, user = null) => set({ accessToken: token, user }),
  setUser: (user) => set({ user }),
  logout: () => set({ accessToken: null, user: null }),
}));
