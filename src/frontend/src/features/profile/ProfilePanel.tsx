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
      toast.success('Profile updated')
    },
    onError: () => toast.error('Unable to update profile'),
  })

  const deleteMutation = useMutation({
    mutationFn: deleteProfile,
    onSuccess: () => {
      toast.info('Account deleted')
      logoutMutation.mutate()
    },
    onError: () => toast.error('Unable to delete your account'),
  })

  const onSubmit = (values: ProfileFormValues) => {
    updateMutation.mutate(values)
  }

  return (
    <div className="space-y-6">
      <Card title="Profile" description="Update your name or password.">
        <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
          <Input label="Full name" error={errors.full_name?.message} {...register('full_name')} />
          <Input
            label="New password"
            type="password"
            error={errors.password?.message}
            {...register('password')}
            placeholder="••••••••"
            helperText="Leave blank to keep the current password"
          />
          <Button type="submit" loading={updateMutation.isPending}>
            Save changes
          </Button>
        </form>
      </Card>

      <Card
        title="Danger zone"
        description="Deleting your account removes all generated QR codes."
        actions={
          <Button
            variant="secondary"
            className="border-red-200 text-red-700 hover:bg-red-50"
            onClick={() => deleteMutation.mutate()}
            loading={deleteMutation.isPending}
          >
            Delete account
          </Button>
        }
      >
        <Alert tone="warning">
          This action is irreversible. Export your QR codes before you continue.
        </Alert>
      </Card>
    </div>
  )
}
