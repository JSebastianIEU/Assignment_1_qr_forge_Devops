import axios, { AxiosError, AxiosHeaders, type InternalAxiosRequestConfig } from 'axios'

import type { ApiErrorResponse, Token } from '../types/api.types'

const API_BASE_URL = import.meta.env.VITE_API_URL || '/api'
const REFRESH_ENABLED = import.meta.env.VITE_ENABLE_REFRESH !== 'false'
const ACCESS_TOKEN_KEY = 'access_token'

const getAccessToken = () =>
  typeof window !== 'undefined' ? localStorage.getItem(ACCESS_TOKEN_KEY) : null

const setAccessToken = (token: string) => {
  if (typeof window !== 'undefined') {
    localStorage.setItem(ACCESS_TOKEN_KEY, token)
  }
}

const clearAccessToken = () => {
  if (typeof window !== 'undefined') {
    localStorage.removeItem(ACCESS_TOKEN_KEY)
  }
}

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  withCredentials: true,
  headers: { 'Content-Type': 'application/json' },
})

apiClient.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    const token = getAccessToken()
    if (token && config.headers) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => Promise.reject(error),
)

apiClient.interceptors.response.use(
  (response) => response,
  async (error: AxiosError<ApiErrorResponse>) => {
    const originalRequest = error.config as (InternalAxiosRequestConfig & { _retry?: boolean }) | undefined
    const status = error.response?.status

    if (status === 401 && originalRequest && !originalRequest._retry) {
      originalRequest._retry = true

      if (REFRESH_ENABLED) {
        try {
          const { data } = await axios.post<Token>(
            `${API_BASE_URL}/auth/refresh`,
            {},
            { withCredentials: true },
          )
          setAccessToken(data.access_token)
          const headers = new AxiosHeaders(originalRequest.headers)
          headers.set('Authorization', `Bearer ${data.access_token}`)
          originalRequest.headers = headers
          return apiClient(originalRequest)
        } catch (refreshError) {
          clearAccessToken()
          if (typeof window !== 'undefined') {
            window.location.href = '/login'
          }
          return Promise.reject(refreshError)
        }
      }

      clearAccessToken()
      if (typeof window !== 'undefined') {
        window.location.href = '/login'
      }
    }

    return Promise.reject(error)
  },
)

export class ApiError extends Error {
  status: number
  data?: unknown

  constructor(status: number, message: string, data?: unknown) {
    super(message)
    this.status = status
    this.data = data
  }
}

export const tokenStorage = {
  get: getAccessToken,
  set: setAccessToken,
  clear: clearAccessToken,
}
