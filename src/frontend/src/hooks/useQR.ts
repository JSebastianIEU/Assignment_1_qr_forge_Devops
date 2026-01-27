import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'

import { createQR, deleteQR, downloadQR, exportHistoryCsv, fetchQRHistory, previewQR } from '../api/qr.api'
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
    onError: () => toast.error('Failed to generate preview'),
  })

  const createMutation = useMutation({
    mutationFn: (payload: QRCreateRequest) => createQR(payload),
    onSuccess: (item) => {
      clearPreview()
      toast.success('QR saved')
      queryClient.setQueryData<QRItem[]>(HISTORY_KEY, (prev) => (prev ? [item, ...prev] : [item]))
    },
    onError: () => toast.error('Failed to save QR'),
  })

  const deleteMutation = useMutation({
    mutationFn: (id: number) => deleteQR(id),
    onSuccess: ({ id }) => {
      toast.info('QR deleted')
      queryClient.setQueryData<QRItem[]>(HISTORY_KEY, (prev) => prev?.filter((item) => item.id !== id) ?? [])
    },
    onError: () => toast.error('Failed to delete QR'),
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
      toast.success('History exported')
    },
    onError: () => toast.error('Failed to export history'),
  })

  const download = async (id: number, format: QRFormat = 'svg') => {
    try {
      const blob = await downloadQR(id, format)
      const url = URL.createObjectURL(blob)
      const anchor = document.createElement('a')
      anchor.href = url
      anchor.download = `qr-code-${id}.${format}`
      document.body.appendChild(anchor)
      anchor.click()
      document.body.removeChild(anchor)
      URL.revokeObjectURL(url)
      toast.success('QR downloaded')
    } catch (error) {
      toast.error('Failed to download QR')
    }
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
