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
      <div className="flex flex-col items-center justify-center h-full w-full rounded-xl border-2 border-dashed border-slate-200 bg-gradient-to-br from-slate-50/50 to-white p-4">
        <svg
          className="w-20 h-20 text-slate-300 mb-2"
          fill="currentColor"
          viewBox="0 0 24 24"
        >
          <path d="M3 3h7v7H3V3zm2 2v3h3V5H5zM3 14h7v7H3v-7zm2 2v3h3v-3H5zM14 3h7v7h-7V3zm2 2v3h3V5h-3zM14 14h3v3h-3v-3zm5 0h2v2h-2v-2zm0 3h2v2h-2v-2zm-3 2h2v2h-2v-2z"/>
        </svg>
        <p className="text-[10px] text-slate-400 text-center leading-tight">
          QR preview<br />will appear here
        </p>
      </div>
    )
  }

  return (
    <div className="w-full h-full flex items-center justify-center">
      <img src={imageSrc} alt="QR code preview" className="w-full max-w-[220px] h-auto" />
    </div>
  )
}
