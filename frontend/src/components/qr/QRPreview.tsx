interface QRPreviewProps {
  svgData?: string
  pngData?: string
  onDownloadSvg?: () => void
  onDownloadPng?: () => void
}

export const QRPreview = ({ svgData, pngData, onDownloadSvg, onDownloadPng }: QRPreviewProps) => {
  // Prefer PNG if both available, otherwise use SVG
  const imageSrc = pngData
    ? `data:image/png;base64,${pngData}`
    : svgData
      ? `data:image/svg+xml;utf8,${encodeURIComponent(svgData)}`
      : null

  if (!imageSrc) {
    return (
      <div className="flex flex-col items-center justify-center h-full min-h-[320px] rounded-2xl border-2 border-dashed border-slate-200 bg-gradient-to-br from-slate-50/50 to-white p-6">
        <svg
          className="w-16 h-16 text-slate-300 mb-3"
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={1.5}
            d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"
          />
        </svg>
        <p className="text-sm font-medium text-slate-500">No preview yet</p>
        <p className="text-xs text-slate-400 mt-1">Click "View Preview" to generate</p>
      </div>
    )
  }

  return (
    <div className="rounded-2xl border border-slate-200 bg-gradient-to-br from-slate-50/50 to-white p-6 shadow-sm h-full flex flex-col">
      <div className="flex-1 flex items-center justify-center bg-white rounded-xl border border-slate-100 p-6 min-h-[320px]">
        <img src={imageSrc} alt="QR code preview" className="w-full max-w-[280px] h-auto" />
      </div>

      <div className="flex flex-wrap gap-2 mt-4 pt-4 border-t border-slate-200/60">
        {svgData && onDownloadSvg && (
          <button
            onClick={onDownloadSvg}
            className="flex-1 sm:flex-initial px-4 py-2 text-xs font-semibold text-slate-700 bg-slate-100 hover:bg-slate-200 rounded-lg transition-colors duration-150"
          >
            ↓ SVG
          </button>
        )}
        {pngData && onDownloadPng && (
          <button
            onClick={onDownloadPng}
            className="flex-1 sm:flex-initial px-4 py-2 text-xs font-semibold text-slate-700 bg-slate-100 hover:bg-slate-200 rounded-lg transition-colors duration-150"
          >
            ↓ PNG
          </button>
        )}
      </div>
    </div>
  )
}
