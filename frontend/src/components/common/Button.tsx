import { forwardRef, type ButtonHTMLAttributes } from 'react'
import { twMerge } from 'tailwind-merge'

type Variant = 'primary' | 'secondary' | 'ghost'

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: Variant
  loading?: boolean
}

const baseStyles: Record<Variant, string> = {
  primary: 'btn-primary',
  secondary: 'btn-secondary',
  ghost:
    'inline-flex items-center justify-center rounded-lg px-4 py-2 text-sm font-semibold text-slate-700 hover:bg-slate-100 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary-500 focus-visible:ring-offset-2',
}

export const Button = forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant = 'primary', loading, disabled, children, ...rest }, ref) => {
    const composed = twMerge(baseStyles[variant], className)
    return (
      <button ref={ref} className={composed} disabled={disabled || loading} {...rest}>
        {loading ? 'Cargando...' : children}
      </button>
    )
  },
)

Button.displayName = 'Button'
