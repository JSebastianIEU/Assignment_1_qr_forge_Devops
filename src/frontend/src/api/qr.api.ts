import { apiClient } from './client'
import type { QRCreateRequest, QRItem, QRPreviewResponse } from '../types/api.types'
import type { QRFormat } from '../types/qr.types'

export const previewQR = async (payload: QRCreateRequest) => {
  const { data } = await apiClient.post<QRPreviewResponse>('/qr/preview', payload)
  return data
}

export const createQR = async (payload: QRCreateRequest) => {
  const { data } = await apiClient.post<QRItem>('/qr', payload)
  return data
}

export const fetchQRHistory = async () => {
  const { data } = await apiClient.get<QRItem[]>('/qr/history')
  return data
}

export const deleteQR = async (id: number) => {
  await apiClient.delete(`/qr/${id}`)
  return { id }
}

export const downloadQR = async (id: number, format: QRFormat = 'svg') => {
  const { data } = await apiClient.get<Blob>(`/qr/${id}/download`, {
    params: { format },
    responseType: 'blob',
  })
  return data
}

export const exportHistoryCsv = async () => {
  const { data } = await apiClient.get<Blob>('/export/csv', { responseType: 'blob' })
  return data
}
