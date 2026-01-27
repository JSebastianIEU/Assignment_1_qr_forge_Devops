import { Card } from '../../components/common/Card'
import { QRForm } from '../../components/qr/QRForm'
import { QRPreview } from '../../components/qr/QRPreview'
import { useQR } from '../../hooks/useQR'
import { Button } from '../../components/common/Button'

export const GeneratorView = () => {
  const { preview, previewMutation, createMutation } = useQR()

  const handleDownloadSvg = () => {
    if (!preview?.svg_data) return
    const element = document.createElement('a')
    element.setAttribute('href', `data:image/svg+xml;utf8,${encodeURIComponent(preview.svg_data)}`)
    element.setAttribute('download', `qr-code-${Date.now()}.svg`)
    element.style.display = 'none'
    document.body.appendChild(element)
    element.click()
    document.body.removeChild(element)
  }

  const handleDownloadPng = () => {
    if (!preview?.png_data) return
    const element = document.createElement('a')
    element.setAttribute('href', `data:image/png;base64,${preview.png_data}`)
    element.setAttribute('download', `qr-code-${Date.now()}.png`)
    element.style.display = 'none'
    document.body.appendChild(element)
    element.click()
    document.body.removeChild(element)
  }

  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 h-full min-h-0">
      {/* LEFT: Customizer (Scrollable) */}
      <div className="min-h-0 overflow-y-auto scrollbar-hide pr-2">
        <Card
          title="Customizer"
          description="Configure your QR code settings"
          className="flex flex-col"
        >
          <QRForm
            onPreview={(values) => previewMutation.mutate(values)}
            onSubmit={(values) => createMutation.mutate(values)}
            isPreviewing={previewMutation.isPending}
            isSubmitting={createMutation.isPending}
          />
        </Card>
      </div>

      {/* RIGHT: Live Canvas + Actions (Sticky) */}
      <div className="flex flex-col gap-4 h-full">
        <div className="sticky top-[120px] z-10 flex flex-col gap-4">
          {/* Live Canvas Card */}
          <Card
            title="Live Canvas"
            description="Preview your QR code in real-time"
            className="flex flex-col"
          >
            <div className="flex items-center justify-center h-64">
              <QRPreview
                svgData={preview?.svg_data}
                pngData={preview?.png_data}
              />
            </div>
          </Card>

          {/* Action Bar */}
          <div className="bg-white/70 backdrop-blur-sm rounded-2xl border border-slate-200/60 p-3 shadow-sm space-y-2">
            {/* Export Format Controls */}
            <div className="flex gap-2">
              {preview?.svg_data && (
                <button
                  onClick={handleDownloadSvg}
                  className="flex-1 px-2.5 py-1.5 text-xs font-semibold text-slate-700 bg-slate-100 hover:bg-slate-200 rounded-lg transition-colors duration-150 border border-slate-200"
                >
                  ↓ SVG
                </button>
              )}
              {preview?.png_data && (
                <button
                  onClick={handleDownloadPng}
                  className="flex-1 px-2.5 py-1.5 text-xs font-semibold text-slate-700 bg-slate-100 hover:bg-slate-200 rounded-lg transition-colors duration-150 border border-slate-200"
                >
                  ↓ PNG
                </button>
              )}
            </div>

            {/* Primary Actions */}
            <div className="flex flex-col gap-1.5">
              <Button
                className="w-full py-1.5 text-xs"
                loading={createMutation.isPending}
                onClick={() => {
                  const form = document.querySelector('form') as HTMLFormElement
                  if (form) {
                    form.dispatchEvent(new Event('submit', { bubbles: true, cancelable: true }))
                  }
                }}
              >
                Save QR
              </Button>
              <Button
                variant="secondary"
                className="w-full py-1.5 text-xs"
                loading={previewMutation.isPending}
                onClick={(e) => {
                  e.preventDefault()
                  const form = document.querySelector('form') as HTMLFormElement
                  if (form) {
                    const formData = new FormData(form)
                    const values: any = {}
                    for (const [key, value] of formData.entries()) {
                      values[key] = value
                    }
                    previewMutation.mutate(values)
                  }
                }}
              >
                View Preview
              </Button>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
