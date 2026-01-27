import { Download, Link2, Trash2 } from 'lucide-react'
import { useState } from 'react'

import type { QRItem } from '../../types/api.types'
import { formatDate } from '../../utils/format'
import { Button } from '../common/Button'
import { Alert } from '../common/Alert'
import { useToast } from '../../hooks/useToast'

interface Props {
  items?: QRItem[]
  isLoading?: boolean
  onDelete: (id: number) => void
  onDownload: (id: number) => void
  onExportCsv?: () => void
}

const URLLinkButton = ({ url }: { url: string }) => {
  const [hoveredUrl, setHoveredUrl] = useState<string | null>(null)
  const toast = useToast()

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(url)
      toast.success('Link copied to clipboard')
    } catch {
      toast.error('Failed to copy link')
    }
  }

  return (
    <div className="relative inline-block">
      <button
        onClick={handleCopy}
        onMouseEnter={() => setHoveredUrl(url)}
        onMouseLeave={() => setHoveredUrl(null)}
        className="inline-flex items-center justify-center w-8 h-8 text-slate-600 hover:text-blue-600 transition-colors duration-150 rounded hover:bg-blue-50"
        title="Copy URL"
      >
        <Link2 className="w-4 h-4" />
      </button>

      {hoveredUrl && (
        <div className="absolute bottom-full left-1/2 -translate-x-1/2 mb-2 z-50 pointer-events-none">
          <div className="bg-slate-900 text-white text-xs rounded px-3 py-2 max-w-xs break-words whitespace-normal">
            {url}
            <div className="absolute top-full left-1/2 -translate-x-1/2 w-2 h-2 bg-slate-900 transform rotate-45" />
          </div>
        </div>
      )}
    </div>
  )
}

export const QRHistoryTable = ({ items = [], isLoading, onDelete, onDownload, onExportCsv }: Props) => {
  if (isLoading) {
    return <p className="text-sm text-slate-600">Loading history...</p>
  }

  if (!items.length) {
    return (
      <Alert tone="info" title="No records">
        You have not generated any QR codes yet. Create your first QR to see them here.
      </Alert>
    )
  }

  return (
    <div className="overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-sm">
      <div className="flex items-center justify-between border-b border-slate-200 px-4 py-3">
        <p className="text-sm font-medium text-slate-700">Recent history</p>
        {onExportCsv && (
          <Button variant="secondary" onClick={onExportCsv}>
            Export CSV
          </Button>
        )}
      </div>
      <div className="overflow-x-auto">
        <table className="min-w-full text-left text-sm text-slate-700">
          <thead className="bg-slate-50 text-xs uppercase tracking-wide text-slate-500">
            <tr>
              <th className="px-4 py-3">Title</th>
              <th className="px-4 py-3">URL</th>
              <th className="px-4 py-3">Created</th>
              <th className="px-4 py-3 text-right">Actions</th>
            </tr>
          </thead>
          <tbody>
            {items.map((item) => (
              <tr key={item.id} className="border-t border-slate-100">
                <td className="px-4 py-3 font-medium text-slate-900">{item.title || 'Untitled'}</td>
                <td className="px-4 py-3">
                  <URLLinkButton url={item.url} />
                </td>
                <td className="px-4 py-3 text-slate-600">{formatDate(item.created_at)}</td>
                <td className="px-4 py-3 text-right">
                  <div className="flex justify-end gap-2">
                    <Button variant="secondary" onClick={() => onDownload(item.id)} aria-label="Download">
                      <Download className="h-4 w-4" />
                    </Button>
                    <Button
                      variant="ghost"
                      className="text-red-600 hover:bg-red-50"
                      onClick={() => onDelete(item.id)}
                      aria-label="Delete"
                    >
                      <Trash2 className="h-4 w-4" />
                    </Button>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}
