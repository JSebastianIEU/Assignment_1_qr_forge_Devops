const locale = 'en-US'

export const formatDate = (value?: string | number | Date) => {
  if (!value) return ''
  const date = typeof value === 'string' || typeof value === 'number' ? new Date(value) : value
  return new Intl.DateTimeFormat(locale, {
    year: 'numeric',
    month: 'short',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
  }).format(date)
}

export const formatRelative = (value?: string | number | Date) => {
  if (!value) return ''
  const date = typeof value === 'string' || typeof value === 'number' ? new Date(value) : value
  const diff = Date.now() - date.getTime()
  const minutes = Math.round(diff / 60000)
  if (minutes < 1) return 'just now'
  if (minutes < 60) return `${minutes}m ago`
  const hours = Math.round(minutes / 60)
  if (hours < 24) return `${hours}h ago`
  const days = Math.round(hours / 24)
  return `${days}d ago`
}

export const truncate = (value: string, length = 48) =>
  value.length > length ? `${value.slice(0, length)}…` : value
