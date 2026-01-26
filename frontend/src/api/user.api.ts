import { apiClient } from './client'
import type { UpdateProfileRequest, User } from '../types/api.types'

export const updateProfile = async (payload: UpdateProfileRequest) => {
  const { data } = await apiClient.patch<User>('/user/me', payload)
  return data
}

export const deleteProfile = async () => {
  const { data } = await apiClient.delete<{ ok: boolean }>('/user/me')
  return data
}
