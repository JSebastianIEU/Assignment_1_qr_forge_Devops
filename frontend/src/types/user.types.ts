import type { User } from './api.types'

export type AuthenticatedUser = User

export interface ProfileFormValues {
  full_name?: string | null
  password?: string
}
