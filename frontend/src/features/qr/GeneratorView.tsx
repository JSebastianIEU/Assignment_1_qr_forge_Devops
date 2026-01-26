import { Card } from '../../components/common/Card'
import { QRForm } from '../../components/qr/QRForm'
import { QRPreview } from '../../components/qr/QRPreview'
import { useQR } from '../../hooks/useQR'

export const GeneratorView = () => {
  const { preview, previewMutation, createMutation } = useQR()

  return (
    <div className="grid gap-6 lg:grid-cols-2">
      <Card
        title="Genera tu QR"
        description="Configura el destino, colores y tamaño. Usa preview para validar antes de guardar."
      >
        <QRForm
          onPreview={(values) => previewMutation.mutate(values)}
          onSubmit={(values) => createMutation.mutate(values)}
          isPreviewing={previewMutation.isPending}
          isSubmitting={createMutation.isPending}
        />
      </Card>

      <Card title="Preview en vivo" description="Así se verá tu código en alta definición">
        <QRPreview svgData={preview?.svg_data} pngData={preview?.png_data} />
      </Card>
    </div>
  )
}
