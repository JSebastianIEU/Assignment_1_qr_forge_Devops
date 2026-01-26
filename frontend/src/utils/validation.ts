import { z } from 'zod'

const hexColor = z
  .string()
  .regex(/^#[0-9a-fA-F]{6}$/, 'Use a 6-digit hex value (e.g. #1d4ed8)')

const hexOrTransparent = z
  .string()
  .regex(/^(#[0-9a-fA-F]{6}|transparent)$/i, 'Use hex color or "transparent"')

export const loginSchema = z.object({
  email: z.string().email('Ingresa un email válido'),
  password: z.string().min(8, 'Mínimo 8 caracteres'),
})

export const signupSchema = z.object({
  email: z.string().email('Ingresa un email válido'),
  full_name: z.string().min(2, 'Nombre muy corto').max(100, 'Nombre muy largo'),
  password: z.string().min(8, 'Mínimo 8 caracteres'),
})

export const qrSchema = z.object({
  title: z.string().min(1, 'Requerido').max(200, 'Máximo 200 caracteres'),
  url: z.string().url('Debe ser una URL válida'),
  foreground_color: hexColor,
  background_color: hexOrTransparent,
  size: z.number().int().min(128).max(1024),
  padding: z.number().int().min(0).max(128),
  border_radius: z.number().int().min(0).max(120),
  overlay_text: z
    .string()
    .max(4, 'Máximo 4 caracteres')
    .optional()
    .or(z.literal('').transform(() => undefined)),
})

export const profileSchema = z.object({
  full_name: z.string().min(2, 'Muy corto').max(100, 'Muy largo').optional(),
  password: z.string().min(8, 'Mínimo 8 caracteres').optional(),
})

export type LoginFormValues = z.infer<typeof loginSchema>
export type SignupFormValues = z.infer<typeof signupSchema>
export type QRFormValues = z.infer<typeof qrSchema>
export type ProfileFormValues = z.infer<typeof profileSchema>
