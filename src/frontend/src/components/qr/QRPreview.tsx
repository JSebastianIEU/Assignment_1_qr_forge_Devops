interface QRPreviewProps {
  svgData?: string
  pngData?: string
}

export const QRPreview = ({ svgData, pngData }: QRPreviewProps) => {
  // Prefer PNG if both available, otherwise use SVG
  const imageSrc = pngData
    ? `data:image/png;base64,${pngData}`
    : svgData
      ? `data:image/svg+xml;utf8,${encodeURIComponent(svgData)}`
      : null

  if (!imageSrc) {
    return (
      <div className="flex flex-col items-center justify-center h-full rounded-xl border-2 border-dashed border-slate-200 bg-gradient-to-br from-slate-50/50 to-white p-4">
        <svg
          className="w-10 h-10 text-slate-300 mb-2"
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
        <p className="text-xs font-medium text-slate-500">No preview yet</p>
        <p className="text-xs text-slate-400 mt-0.5">Click "View Preview" to generate</p>
      </div>
    )
  }

  return (
    <div className="w-full h-full flex items-center justify-center">
      <img src={imageSrc} alt="QR code preview" className="w-full max-w-[220px] h-auto" />
    </div>
  )
}
