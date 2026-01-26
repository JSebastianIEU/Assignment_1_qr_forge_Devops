import type { InputHTMLAttributes } from 'react'
import { twMerge } from 'tailwind-merge'

interface InputProps extends InputHTMLAttributes<HTMLInputElement> {
  label?: string
  error?: string
  helperText?: string
}

export const Input = ({ label, error, helperText, className, ...rest }: InputProps) => (
  <label className="block space-y-1 text-sm font-medium text-slate-700">
    {label && <span>{label}</span>}
    <input className={twMerge('input', error && 'border-red-500 focus:ring-red-500', className)} {...rest} />
    {helperText && !error && <p className="text-xs text-slate-500">{helperText}</p>}
    {error && <p className="text-xs text-red-600">{error}</p>}
  </label>
)
