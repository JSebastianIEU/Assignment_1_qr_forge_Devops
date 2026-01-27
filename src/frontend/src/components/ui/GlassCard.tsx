import { twMerge } from 'tailwind-merge'
import type { PropsWithChildren, ReactNode } from 'react'

type Variant = 'elevated' | 'subtle'

interface GlassCardProps extends PropsWithChildren {
  title?: string
  description?: string
  actions?: ReactNode
  className?: string
  variant?: Variant
}

export const GlassCard = ({ title, description, actions, className, children, variant = 'elevated' }: GlassCardProps) => {
  const variantClasses =
    variant === 'elevated'
      ? 'shadow-[0_12px_28px_rgba(15,23,42,0.14)]'
      : 'shadow-[0_8px_18px_rgba(15,23,42,0.10)]'

  return (
    <div className={twMerge('glass-card rounded-2xl text-slate-900 p-5 md:p-6', variantClasses, className)}>
      {(title || description || actions) && (
        <div className="mb-4 flex flex-wrap items-start justify-between gap-3">
          <div>
            {title && <h3 className="text-lg font-semibold text-slate-900">{title}</h3>}
            {description && <p className="text-sm text-slate-600">{description}</p>}
          </div>
          {actions}
        </div>
      )}
      {children}
    </div>
  )
}
