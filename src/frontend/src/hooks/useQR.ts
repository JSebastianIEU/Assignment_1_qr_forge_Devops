import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'

import { createQR, deleteQR, exportHistoryCsv, fetchQRHistory, previewQR } from '../api/qr.api'
import type { QRCreateRequest, QRItem } from '../types/api.types'
import type { QRFormat } from '../types/qr.types'
import { useQRStore } from '../store/qrStore'
import { useToast } from './useToast'

const HISTORY_KEY = ['qr-history']

export const useQR = () => {
  const toast = useToast()
  const queryClient = useQueryClient()
  const { preview, setPreview, clearPreview } = useQRStore()

  const historyQuery = useQuery({
    queryKey: HISTORY_KEY,
    queryFn: fetchQRHistory,
    staleTime: 5 * 60 * 1000,
  })

  const previewMutation = useMutation({
    mutationFn: (payload: QRCreateRequest) => previewQR(payload),
    onSuccess: (data) => {
      setPreview(data)
    },
    onError: () => toast.error('No pudimos generar el preview'),
  })

  const createMutation = useMutation({
    mutationFn: (payload: QRCreateRequest) => createQR(payload),
    onSuccess: (item) => {
      clearPreview()
      toast.success('QR guardado')
      queryClient.setQueryData<QRItem[]>(HISTORY_KEY, (prev) => (prev ? [item, ...prev] : [item]))
    },
    onError: () => toast.error('No pudimos guardar el QR'),
  })

  const deleteMutation = useMutation({
    mutationFn: (id: number) => deleteQR(id),
    onSuccess: ({ id }) => {
      toast.info('QR eliminado')
      queryClient.setQueryData<QRItem[]>(HISTORY_KEY, (prev) => prev?.filter((item) => item.id !== id) ?? [])
    },
    onError: () => toast.error('No pudimos eliminar el QR'),
  })

  const exportCsv = useMutation({
    mutationFn: exportHistoryCsv,
    onSuccess: (blob) => {
      const url = URL.createObjectURL(blob)
      const anchor = document.createElement('a')
      anchor.href = url
      anchor.download = 'qr_history.csv'
      anchor.click()
      URL.revokeObjectURL(url)
      toast.success('Historial exportado')
    },
    onError: () => toast.error('No pudimos exportar el historial'),
  })

  const download = (id: number, format: QRFormat = 'svg') => {
    const url = `/api/qr/${id}/download?format=${format}`
    const anchor = document.createElement('a')
    anchor.href = url
    anchor.download = `qr-code-${id}.${format}`
    document.body.appendChild(anchor)
    anchor.click()
    document.body.removeChild(anchor)
  }

  return {
    historyQuery,
    preview,
    previewMutation,
    createMutation,
    deleteMutation,
    exportCsv,
    download,
  }
}
