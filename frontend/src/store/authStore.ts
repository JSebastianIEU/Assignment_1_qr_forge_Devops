import { create } from 'zustand'
import { persist } from 'zustand/middleware'

import { tokenStorage } from '../api/client'
import type { User } from '../types/api.types'

interface AuthState {
  user: User | null
  isAuthenticated: boolean
  isLoading: boolean
  login: (user: User, token: string) => void
  logout: () => void
  setUser: (user: User | null) => void
  setLoading: (loading: boolean) => void
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      user: null,
      isAuthenticated: false,
      isLoading: false,
      login: (user, token) => {
        tokenStorage.set(token)
        set({ user, isAuthenticated: true, isLoading: false })
      },
      logout: () => {
        tokenStorage.clear()
        set({ user: null, isAuthenticated: false, isLoading: false })
      },
      setUser: (user) => set({ user, isAuthenticated: Boolean(user) }),
      setLoading: (loading) => set({ isLoading: loading }),
    }),
    {
      name: 'auth-storage',
      partialize: (state) => ({ user: state.user, isAuthenticated: state.isAuthenticated }),
    },
  ),
)
