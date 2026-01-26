import { Card } from '../../components/common/Card'
import { QRHistoryTable } from '../../components/qr/QRHistoryTable'
import { useQR } from '../../hooks/useQR'

export const HistoryView = () => {
  const { historyQuery, deleteMutation, download, exportCsv } = useQR()

  return (
    <Card title="Historial" description="Descarga, exporta o elimina códigos previos.">
      <QRHistoryTable
        items={historyQuery.data}
        isLoading={historyQuery.isLoading}
        onDelete={(id) => deleteMutation.mutate(id)}
        onDownload={(id) => download(id)}
        onExportCsv={() => exportCsv.mutate()}
      />
    </Card>
  )
}
