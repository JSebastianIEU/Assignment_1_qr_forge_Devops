import { Card } from '../../components/common/Card'
import { QRForm } from '../../components/qr/QRForm'
import { QRPreview } from '../../components/qr/QRPreview'
import { useQR } from '../../hooks/useQR'

export const GeneratorView = () => {
  const { preview, previewMutation, createMutation } = useQR()

  return (
    <div className="grid gap-6 lg:grid-cols-2">
      <Card
        title="Generate your QR"
        description="Set the destination, colors, and size. Use preview to verify before saving."
      >
        <QRForm
          onPreview={(values) => previewMutation.mutate(values)}
          onSubmit={(values) => createMutation.mutate(values)}
          isPreviewing={previewMutation.isPending}
          isSubmitting={createMutation.isPending}
        />
      </Card>

      <Card title="Live preview" description="See your code in high fidelity before committing.">
        <QRPreview svgData={preview?.svg_data} pngData={preview?.png_data} />
      </Card>
    </div>
  )
}
