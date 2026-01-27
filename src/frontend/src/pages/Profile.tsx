import { ProfilePanel } from '../features/profile/ProfilePanel'
import { PageHeader } from '../components/ui/PageHeader'
import { MainPanel } from '../components/layout/MainPanel'

export const Profile = () => (
  <MainPanel>
    <div className="space-y-6">
    <PageHeader
      kicker="Profile"
      title="Your account and security"
      subtitle="Update your name or password and keep your account safe."
    />
    <ProfilePanel />
    </div>
  </MainPanel>
)
