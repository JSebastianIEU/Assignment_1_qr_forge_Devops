import type { PropsWithChildren, ReactNode } from 'react'
import { twMerge } from 'tailwind-merge'

interface CardProps extends PropsWithChildren {
  title?: string
  description?: string
  actions?: ReactNode
  className?: string
}

export const Card = ({ title, description, actions, className, children }: CardProps) => (
  <div className={twMerge('card', className)}>
    {(title || description || actions) && (
      <div className="mb-4 flex items-start justify-between gap-3">
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
