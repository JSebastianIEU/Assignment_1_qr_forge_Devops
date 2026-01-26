export interface Token {
  access_token: string
  token_type: 'bearer'
}

export interface User {
  id: number
  email: string
  full_name?: string | null
  created_at: string
  updated_at: string
}

export interface LoginRequest {
  email: string
  password: string
}

export interface SignupRequest {
  email: string
  full_name?: string | null
  password: string
}

export interface UpdateProfileRequest {
  full_name?: string | null
  password?: string
}

export interface QRItem {
  id: number
  user_id: number
  title?: string | null
  url: string
  foreground_color: string
  background_color: string
  size: number
  padding: number
  border_radius: number
  overlay_text?: string | null
  svg_path: string
  png_path?: string | null
  created_at: string
  updated_at: string
}

export interface QRCreateRequest {
  title: string
  url: string
  foreground_color?: string
  background_color?: string
  size?: number
  padding?: number
  border_radius?: number
  overlay_text?: string | null
}

export interface QRPreviewResponse {
  svg_data: string
  png_data: string
}

export interface ApiErrorResponse {
  detail?: string | Record<string, unknown>
  [key: string]: unknown
}
