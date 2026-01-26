interface SpinnerProps {
  size?: 'sm' | 'md'
}

export const Spinner = ({ size = 'md' }: SpinnerProps) => {
  const dimension = size === 'sm' ? 'h-4 w-4' : 'h-6 w-6'
  return (
    <span
      className={`inline-block ${dimension} animate-spin rounded-full border-2 border-slate-300 border-t-primary-600`}
      role="status"
      aria-live="polite"
    />
  )
}
