import { apiClient, tokenStorage } from './client'
import type { LoginRequest, SignupRequest, Token, User } from '../types/api.types'

export const login = async (payload: LoginRequest) => {
  const { data } = await apiClient.post<Token>('/auth/login', payload)
  tokenStorage.set(data.access_token)
  const user = await getCurrentUser(data.access_token)
  return { token: data.access_token, user }
}

export const signup = async (payload: SignupRequest) => {
  const { data } = await apiClient.post<User>('/auth/signup', payload)
  return data
}

export const logout = async () => {
  try {
    await apiClient.post('/auth/logout')
  } finally {
    tokenStorage.clear()
  }
}

export const getCurrentUser = async (token?: string) => {
  const { data } = await apiClient.get<User>('/user/me', {
    headers: token ? { Authorization: `Bearer ${token}` } : undefined,
  })
  return data
}
