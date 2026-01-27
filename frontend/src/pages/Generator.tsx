import { useMemo } from 'react'

import { Button } from '../components/common/Button'
import { Card } from '../components/common/Card'
import { QRForm } from '../components/qr/QRForm'
import { QRPreview } from '../components/qr/QRPreview'
import { MainPanel } from '../components/layout/MainPanel'
import { useQR } from '../hooks/useQR'

export const Generator = () => {
  const { preview, previewMutation, createMutation } = useQR()

  const downloadLinks = useMemo(() => {
    const links: { svg?: string; png?: string } = {}
    if (preview?.svg_data) links.svg = `data:image/svg+xml;utf8,${encodeURIComponent(preview.svg_data)}`
    if (preview?.png_data) links.png = `data:image/png;base64,${preview.png_data}`
    return links
  }, [preview])

  const triggerSvgDownload = () => {
    if (!downloadLinks.svg) return
    const a = document.createElement('a')
    a.href = downloadLinks.svg
    a.download = `qr-code-${Date.now()}.svg`
    a.click()
  }

  const triggerPngDownload = () => {
    if (!downloadLinks.png) return
    const a = document.createElement('a')
    a.href = downloadLinks.png
    a.download = `qr-code-${Date.now()}.png`
    a.click()
  }

  const submitForm = () => {
    const form = document.querySelector('form') as HTMLFormElement | null
    if (form) form.dispatchEvent(new Event('submit', { bubbles: true, cancelable: true }))
  }

  return (
    <MainPanel className="overflow-hidden">
      <div className="h-full flex flex-col min-h-0">
        {/* Mobile-only Header */}
        <div className="lg:hidden sticky top-0 z-20 -mx-5 px-5 py-3 bg-white/70 backdrop-blur-md border-b border-slate-200/60">
          <div className="space-y-1">
            <div className="text-[10px] font-semibold uppercase tracking-wider text-slate-600">Generator</div>
            <h1 className="text-xl font-bold text-slate-900">Create and customize QR codes</h1>
            <p className="text-xs text-slate-600">Preview live, save, and download in SVG or PNG.</p>
          </div>
        </div>

        {/* Content region */}
        <div className="flex-1 min-h-0 overflow-visible pt-0 lg:pt-6">
          <div className="grid grid-cols-1 lg:grid-cols-[1.8fr_1fr] gap-6 h-full min-h-0">
            {/* LEFT: Header (desktop) + Customizer (scrolls) */}
            <div className="min-h-0 overflow-y-auto scrollbar-hide px-3 lg:px-4 py-3 h-full space-y-4 [&_*]:shadow-none"
              style={{
                overflow: 'overlay',
              }}>
              {/* Desktop-only Header inside LEFT column */}
              <div className="hidden lg:block">
                <div className="space-y-1">
                  <div className="text-[11px] font-semibold uppercase tracking-wider text-slate-600">Generator</div>
                  <h1 className="text-3xl font-bold text-slate-900">Create and customize QR codes</h1>
                  <p className="text-sm text-slate-600">Preview live, save, and download in SVG or PNG.</p>
                </div>
              </div>

              <Card title="Customizer" description="Configure your QR code settings" className="flex flex-col">
                <QRForm
                  onPreview={(values) => previewMutation.mutate(values)}
                  onSubmit={(values) => createMutation.mutate(values)}
                  isPreviewing={previewMutation.isPending}
                  isSubmitting={createMutation.isPending}
                />
              </Card>
            </div>

            {/* RIGHT: Sticky preview + actions (top-aligned) */}
            <div className="min-h-0 lg:sticky lg:top-[72px] self-start space-y-2 max-h-[calc(100vh-96px)]">
              <Card title="Live Canvas" description="Real-time preview" className="flex flex-col !p-3">
                <div className="flex flex-col items-center">
                  <div className="w-full max-w-[200px] aspect-square rounded-md border border-slate-200 bg-white/70 p-1.5 flex items-center justify-center shadow-sm">
                    <div className="w-full h-full flex items-center justify-center">
                      <QRPreview svgData={preview?.svg_data} pngData={preview?.png_data} />
                    </div>
                  </div>
                </div>
              </Card>

              <div className="bg-white/80 backdrop-blur-sm rounded-lg border border-slate-200/70 p-2 shadow-sm space-y-1.5">
                <div className="flex gap-1">
                  {downloadLinks.svg && (
                    <button
                      onClick={triggerSvgDownload}
                      className="flex-1 px-1.5 py-0.5 text-[10px] font-semibold text-slate-700 bg-slate-100 hover:bg-slate-200 rounded transition-colors duration-150 border border-slate-200"
                    >
                      ↓ SVG
                    </button>
                  )}
                  {downloadLinks.png && (
                    <button
                      onClick={triggerPngDownload}
                      className="flex-1 px-1.5 py-0.5 text-[10px] font-semibold text-slate-700 bg-slate-100 hover:bg-slate-200 rounded transition-colors duration-150 border border-slate-200"
                    >
                      ↓ PNG
                    </button>
                  )}
                </div>

                <div className="flex flex-col gap-1">
                  <Button className="w-full py-1 text-[11px]" loading={createMutation.isPending} onClick={submitForm}>
                    Save QR
                  </Button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </MainPanel>
  )
}
