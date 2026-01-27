import { HistoryView } from '../features/qr/HistoryView'
import { PageHeader } from '../components/ui/PageHeader'
import { MainPanel } from '../components/layout/MainPanel'

export const History = () => (
  <MainPanel>
    <div className="space-y-6">
    <PageHeader
      kicker="History"
      title="Saved QR codes"
      subtitle="Download, export, or delete the codes you already generated."
    />
    <HistoryView />
    </div>
  </MainPanel>
)
