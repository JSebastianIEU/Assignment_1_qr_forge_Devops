import { Card } from '../../components/common/Card'
import { QRHistoryTable } from '../../components/qr/QRHistoryTable'
import { useQR } from '../../hooks/useQR'
import type { QRFormat } from '../../types/qr.types'

export const HistoryView = () => {
  const { historyQuery, deleteMutation, download, exportCsv } = useQR()

  return (
    <Card title="History" description="Download, export, or delete previous QR codes.">
      <QRHistoryTable
        items={historyQuery.data}
        isLoading={historyQuery.isLoading}
        onDelete={(id) => deleteMutation.mutate(id)}
        onDownload={(id, format: QRFormat) => download(id, format)}
        onExportCsv={() => exportCsv.mutate()}
      />
    </Card>
  )
}
