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
    <div className="grid gap-5 lg:grid-cols-[420px_1fr] h-full">
      {/* Customizer Panel */}
      <div className="flex flex-col h-full">
        <Card
          title="Customizer"
          description="Configure your QR code settings"
          className="flex flex-col h-full"
        >
          <QRForm
            onPreview={(values) => previewMutation.mutate(values)}
            onSubmit={(values) => createMutation.mutate(values)}
            isPreviewing={previewMutation.isPending}
            isSubmitting={createMutation.isPending}
          />
        </Card>
      </div>

      {/* Preview Canvas - Sticky */}
      <div className="flex flex-col h-full gap-5 overflow-hidden">
        <div className="sticky top-0 z-10">
          <Card
            title="Live Canvas"
            description="Preview your QR code in real-time"
            className="flex flex-col"
          >
            <div className="flex items-center justify-center min-h-[400px]">
              <QRPreview
                svgData={preview?.svg_data}
                pngData={preview?.png_data}
                onDownloadSvg={handleDownloadSvg}
                onDownloadPng={handleDownloadPng}
              />
            </div>
          </Card>
        </div>

        {/* Sticky Action Bar */}
        <div className="sticky top-[calc(400px+144px)] bg-white/95 backdrop-blur-sm rounded-2xl border border-slate-200/60 p-5 shadow-sm space-y-3">
          <div className="flex flex-col gap-2">
            <Button
              className="w-full"
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
              className="w-full"
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
  )
}
