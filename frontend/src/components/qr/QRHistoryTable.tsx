import { Download, Trash2 } from 'lucide-react'

import type { QRItem } from '../../types/api.types'
import { formatDate, truncate } from '../../utils/format'
import { Button } from '../common/Button'
import { Alert } from '../common/Alert'

interface Props {
  items?: QRItem[]
  isLoading?: boolean
  onDelete: (id: number) => void
  onDownload: (id: number) => void
  onExportCsv?: () => void
}

export const QRHistoryTable = ({ items = [], isLoading, onDelete, onDownload, onExportCsv }: Props) => {
  if (isLoading) {
    return <p className="text-sm text-slate-600">Cargando historial...</p>
  }

  if (!items.length) {
    return (
      <Alert tone="info" title="Sin registros">
        Aún no has generado códigos. Crea tu primer QR para ver el historial aquí.
      </Alert>
    )
  }

  return (
    <div className="overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-sm">
      <div className="flex items-center justify-between border-b border-slate-200 px-4 py-3">
        <p className="text-sm font-medium text-slate-700">Historial reciente</p>
        {onExportCsv && (
          <Button variant="secondary" onClick={onExportCsv}>
            Exportar CSV
          </Button>
        )}
      </div>
      <div className="overflow-x-auto">
        <table className="min-w-full text-left text-sm text-slate-700">
          <thead className="bg-slate-50 text-xs uppercase tracking-wide text-slate-500">
            <tr>
              <th className="px-4 py-3">Título</th>
              <th className="px-4 py-3">URL</th>
              <th className="px-4 py-3">Creado</th>
              <th className="px-4 py-3 text-right">Acciones</th>
            </tr>
          </thead>
          <tbody>
            {items.map((item) => (
              <tr key={item.id} className="border-t border-slate-100">
                <td className="px-4 py-3 font-medium text-slate-900">{item.title || 'Sin título'}</td>
                <td className="px-4 py-3">
                  <a href={item.url} target="_blank" rel="noreferrer" className="text-primary-600">
                    {truncate(item.url, 42)}
                  </a>
                </td>
                <td className="px-4 py-3 text-slate-600">{formatDate(item.created_at)}</td>
                <td className="px-4 py-3 text-right">
                  <div className="flex justify-end gap-2">
                    <Button variant="secondary" onClick={() => onDownload(item.id)} aria-label="Descargar">
                      <Download className="h-4 w-4" />
                    </Button>
                    <Button
                      variant="ghost"
                      className="text-red-600 hover:bg-red-50"
                      onClick={() => onDelete(item.id)}
                      aria-label="Eliminar"
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
