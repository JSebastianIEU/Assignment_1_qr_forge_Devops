import React from 'react'

interface MainPanelProps {
  children: React.ReactNode
  className?: string
}

export const MainPanel: React.FC<MainPanelProps> = ({ children, className = '' }) => {
  return (
    <div
      className={[
        'h-full',
        'overflow-y-auto scrollbar-hide',
        'rounded-[24px] border border-white/30',
        'bg-white/65 backdrop-blur-xl',
        'shadow-[0_20px_40px_rgba(15,23,42,0.12)]',
        'p-5 sm:p-8',
        'text-slate-900',
        'z-10',
        className,
      ].join(' ')}
    >
      {children}
    </div>
  )
}
