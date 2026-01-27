import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { useEffect } from 'react'

import { getCurrentUser, login as loginApi, logout as logoutApi, signup as signupApi } from '../api/auth.api'
import { tokenStorage } from '../api/client'
import type { LoginRequest, SignupRequest, User } from '../types/api.types'
import { useAuthStore } from '../store/authStore'
import { useToast } from './useToast'

const AUTH_QUERY_KEY = ['auth', 'me']

export const useAuth = () => {
  const toast = useToast()
  const queryClient = useQueryClient()
  const { user, isAuthenticated, isLoading, login, logout, setUser, setLoading } = useAuthStore()
  const hasToken = Boolean(tokenStorage.get())

  const profileQuery = useQuery<User>({
    queryKey: AUTH_QUERY_KEY,
    queryFn: () => getCurrentUser(),
    enabled: hasToken && !user,
    staleTime: 5 * 60 * 1000,
    retry: false,
  })

  useEffect(() => {
    if (profileQuery.data) {
      setUser(profileQuery.data)
    }
  }, [profileQuery.data, setUser])

  useEffect(() => {
    if (profileQuery.isError) {
      logout()
    }
  }, [profileQuery.isError, logout])

  const loginMutation = useMutation({
    mutationFn: (payload: LoginRequest) => loginApi(payload),
    onMutate: () => setLoading(true),
    onSuccess: ({ user: userData, token }) => {
      login(userData, token)
      queryClient.setQueryData<User>(AUTH_QUERY_KEY, userData)
      toast.success('Session started')
    },
    onError: () => toast.error('Failed to sign in'),
    onSettled: () => setLoading(false),
  })

  const signupMutation = useMutation({
    mutationFn: (payload: SignupRequest) => signupApi(payload),
    onMutate: () => setLoading(true),
    onSuccess: () => toast.success('Account created, now sign in'),
    onError: () => toast.error('Failed to create account'),
    onSettled: () => setLoading(false),
  })

  const logoutMutation = useMutation({
    mutationFn: logoutApi,
    onSuccess: () => {
      logout()
      queryClient.removeQueries({ queryKey: AUTH_QUERY_KEY })
      toast.info('Session ended')
    },
    onError: () => toast.error('Failed to sign out'),
  })

  const resolvedUser: User | null = user ?? profileQuery.data ?? null

  return {
    user: resolvedUser,
    isAuthenticated,
    isLoading: isLoading || profileQuery.isFetching,
    loginMutation,
    signupMutation,
    logoutMutation,
  }
}
