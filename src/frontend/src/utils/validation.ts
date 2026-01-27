import { z } from 'zod'

const hexColor = z
  .string()
  .regex(/^#[0-9a-fA-F]{6}$/, 'Use a 6-digit hex value (e.g. #1d4ed8)')

const hexOrTransparent = z
  .string()
  .regex(/^(#[0-9a-fA-F]{6}|transparent)$/i, 'Use a hex color or "transparent"')

export const loginSchema = z.object({
  email: z.string().email('Enter a valid email'),
  password: z.string().min(8, 'Minimum 8 characters'),
})

export const signupSchema = z.object({
  email: z.string().email('Enter a valid email'),
  full_name: z.string().min(2, 'Name is too short').max(100, 'Name is too long'),
  password: z.string().min(8, 'Minimum 8 characters'),
})

export const qrSchema = z.object({
  title: z.string().min(1, 'Required').max(200, 'Maximum 200 characters'),
  url: z.string().url('Must be a valid URL'),
  foreground_color: hexColor,
  background_color: hexOrTransparent,
  size: z.number().int().min(128, 'Minimum 128').max(1024, 'Maximum 1024'),
  padding: z.number().int().min(0, 'Minimum 0').max(128, 'Maximum 128'),
  border_radius: z.number().int().min(0, 'Minimum 0').max(120, 'Maximum 120'),
  overlay_text: z
    .string()
    .max(4, 'Maximum 4 characters')
    .optional()
    .or(z.literal('').transform(() => undefined)),
})

export const profileSchema = z.object({
  full_name: z.string().min(2, 'Too short').max(100, 'Too long').optional(),
  password: z.string().min(8, 'Minimum 8 characters').optional(),
})

export type LoginFormValues = z.infer<typeof loginSchema>
export type SignupFormValues = z.infer<typeof signupSchema>
export type QRFormValues = z.infer<typeof qrSchema>
export type ProfileFormValues = z.infer<typeof profileSchema>
