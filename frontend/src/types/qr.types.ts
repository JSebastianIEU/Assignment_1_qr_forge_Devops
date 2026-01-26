import type { QRCreateRequest, QRItem, QRPreviewResponse } from './api.types'

export type QRFormat = 'svg' | 'png'

export interface QRPreviewResult {
  svg: string
  png: string
}

export type QRHistory = QRItem[]

export type QRPreviewPayload = QRCreateRequest

export type QRGeneratePayload = QRCreateRequest

export type QRPreviewApiResponse = QRPreviewResponse
