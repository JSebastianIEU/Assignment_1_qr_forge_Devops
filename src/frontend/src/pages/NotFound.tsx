import { Link } from 'react-router-dom'

import { Button } from '../components/common/Button'
import { MainPanel } from '../components/layout/MainPanel'
import { PageHeader } from '../components/ui/PageHeader'

export const NotFound = () => (
  <MainPanel>
    <div className="space-y-4 text-center">
    <PageHeader
      kicker="404"
      title="Page not found"
      subtitle="The requested route does not exist or is no longer available."
    />
    <div className="flex justify-center">
      <Link to="/">
        <Button>Back to home</Button>
      </Link>
    </div>
    </div>
  </MainPanel>
)
