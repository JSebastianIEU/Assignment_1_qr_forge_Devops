import { Navigate, Outlet, useLocation } from 'react-router-dom'

import { useAuthStore } from '../../store/authStore'
import { Spinner } from '../common/Spinner'

export const ProtectedRoute = () => {
  const location = useLocation()
  const { isAuthenticated, isLoading } = useAuthStore()

  if (isLoading) {
    return (
      <div className="flex w-full items-center justify-center py-10">
        <Spinner />
      </div>
    )
  }

  return isAuthenticated ? <Outlet /> : <Navigate to="/login" state={{ from: location.pathname }} replace />
}
