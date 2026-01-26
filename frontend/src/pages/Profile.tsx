import { ProfilePanel } from '../features/profile/ProfilePanel'

export const Profile = () => (
  <div className="w-full space-y-4">
    <div>
      <h1 className="text-3xl font-bold text-slate-900">Perfil</h1>
      <p className="text-slate-600">Administra tus datos y seguridad de cuenta.</p>
    </div>
    <ProfilePanel />
  </div>
)
