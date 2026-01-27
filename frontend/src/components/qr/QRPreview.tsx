interface QRPreviewProps {
  svgData?: string
  pngData?: string
}

export const QRPreview = ({ svgData, pngData }: QRPreviewProps) => {
  if (!svgData && !pngData) {
    return (
      <div className="flex h-64 items-center justify-center rounded-xl border border-dashed border-slate-300 bg-white text-slate-500">
        Preview will appear here
      </div>
    )
  }

  const svgSrc = svgData ? `data:image/svg+xml;utf8,${encodeURIComponent(svgData)}` : null
  const pngSrc = pngData ? `data:image/png;base64,${pngData}` : null

  return (
    <div className="grid gap-4 sm:grid-cols-2">
      {svgSrc && (
        <div className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm">
          <p className="mb-2 text-sm font-medium text-slate-700">SVG</p>
          <img src={svgSrc} alt="QR preview SVG" className="mx-auto h-56 w-56 object-contain" />
        </div>
      )}
      {pngSrc && (
        <div className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm">
          <p className="mb-2 text-sm font-medium text-slate-700">PNG</p>
          <img src={pngSrc} alt="QR preview PNG" className="mx-auto h-56 w-56 object-contain" />
        </div>
      )}
    </div>
  )
}
