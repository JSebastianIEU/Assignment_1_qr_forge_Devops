import type { PropsWithChildren, ReactNode } from 'react'

import { GlassCard } from '../ui/GlassCard'

interface CardProps extends PropsWithChildren {
  title?: string
  description?: string
  actions?: ReactNode
  className?: string
  variant?: 'elevated' | 'subtle'
}

export const Card = ({ variant = 'subtle', ...rest }: CardProps) => <GlassCard variant={variant} {...rest} />
