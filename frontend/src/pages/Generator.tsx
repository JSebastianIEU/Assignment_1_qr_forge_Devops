import { GeneratorView } from '../features/qr/GeneratorView'
import { PageHeader } from '../components/ui/PageHeader'
import { MainPanel } from '../components/layout/MainPanel'

export const Generator = () => (
  <MainPanel>
    <div className="space-y-6">
    <PageHeader
      kicker="Generator"
      title="Create and customize QR codes"
      subtitle="Preview live, save, and download in SVG or PNG."
    />
    <GeneratorView />
    </div>
  </MainPanel>
)
