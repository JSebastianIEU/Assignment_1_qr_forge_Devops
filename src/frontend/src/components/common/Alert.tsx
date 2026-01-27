import type { ReactNode } from 'react'
import { twMerge } from 'tailwind-merge'

type Tone = 'info' | 'success' | 'warning' | 'error'

const toneClasses: Record<Tone, string> = {
  info: 'bg-blue-50 text-blue-800 border-blue-200',
  success: 'bg-green-50 text-green-800 border-green-200',
  warning: 'bg-amber-50 text-amber-800 border-amber-200',
  error: 'bg-red-50 text-red-800 border-red-200',
}

interface AlertProps {
  tone?: Tone
  title?: string
  children?: ReactNode
  className?: string
}

export const Alert = ({ tone = 'info', title, children, className }: AlertProps) => (
  <div
    className={twMerge(
      'flex gap-3 rounded-xl border px-4 py-3 text-sm leading-relaxed',
      toneClasses[tone],
      className,
    )}
  >
    <div className="flex-1">
      {title && <p className="font-semibold">{title}</p>}
      {children}
    </div>
  </div>
)
