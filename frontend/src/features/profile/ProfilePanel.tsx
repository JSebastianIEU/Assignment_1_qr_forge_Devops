import { zodResolver } from '@hookform/resolvers/zod'
import { useMutation } from '@tanstack/react-query'
import { useEffect } from 'react'
import { useForm } from 'react-hook-form'

import { deleteProfile, updateProfile } from '../../api/user.api'
import { useAuth } from '../../hooks/useAuth'
import { useToast } from '../../hooks/useToast'
import { profileSchema, type ProfileFormValues } from '../../utils/validation'
import { Button } from '../../components/common/Button'
import { Card } from '../../components/common/Card'
import { Input } from '../../components/common/Input'
import { Alert } from '../../components/common/Alert'
import { useAuthStore } from '../../store/authStore'

export const ProfilePanel = () => {
  const toast = useToast()
  const { user, logoutMutation } = useAuth()
  const { setUser } = useAuthStore()

  const {
    register,
    handleSubmit,
    formState: { errors },
    reset,
  } = useForm<ProfileFormValues>({
    resolver: zodResolver(profileSchema),
    defaultValues: { full_name: user?.full_name ?? '', password: '' },
  })

  useEffect(() => {
    reset({ full_name: user?.full_name ?? '', password: '' })
  }, [user, reset])

  const updateMutation = useMutation({
    mutationFn: (values: ProfileFormValues) => updateProfile(values),
    onSuccess: (updated) => {
      setUser(updated)
      reset({ full_name: updated.full_name ?? '', password: '' })
      toast.success('Perfil actualizado')
    },
    onError: () => toast.error('No pudimos actualizar el perfil'),
  })

  const deleteMutation = useMutation({
    mutationFn: deleteProfile,
    onSuccess: () => {
      toast.info('Cuenta eliminada')
      logoutMutation.mutate()
    },
    onError: () => toast.error('No pudimos eliminar la cuenta'),
  })

  const onSubmit = (values: ProfileFormValues) => {
    updateMutation.mutate(values)
  }

  return (
    <div className="space-y-6">
      <Card title="Perfil" description="Actualiza tu nombre o contraseña.">
        <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
          <Input label="Nombre completo" error={errors.full_name?.message} {...register('full_name')} />
          <Input
            label="Nueva contraseña"
            type="password"
            error={errors.password?.message}
            {...register('password')}
            placeholder="••••••••"
            helperText="Déjalo en blanco para mantener la actual"
          />
          <Button type="submit" loading={updateMutation.isPending}>
            Guardar cambios
          </Button>
        </form>
      </Card>

      <Card
        title="Zona de riesgo"
        description="Eliminar tu cuenta borrará todos los QR generados."
        actions={
          <Button
            variant="secondary"
            className="border-red-200 text-red-700 hover:bg-red-50"
            onClick={() => deleteMutation.mutate()}
            loading={deleteMutation.isPending}
          >
            Eliminar cuenta
          </Button>
        }
      >
        <Alert tone="warning">
          Esta acción es irreversible. Asegúrate de haber exportado tus QR antes de continuar.
        </Alert>
      </Card>
    </div>
  )
}
