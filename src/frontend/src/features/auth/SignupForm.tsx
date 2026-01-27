import { zodResolver } from '@hookform/resolvers/zod'
import { useForm } from 'react-hook-form'
import { Link, useNavigate } from 'react-router-dom'

import { useAuth } from '../../hooks/useAuth'
import { ROUTES } from '../../utils/constants'
import { signupSchema, type SignupFormValues } from '../../utils/validation'
import { Button } from '../../components/common/Button'
import { Input } from '../../components/common/Input'

export const SignupForm = () => {
  const navigate = useNavigate()
  const { signupMutation } = useAuth()

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<SignupFormValues>({
    resolver: zodResolver(signupSchema),
    defaultValues: { email: '', full_name: '', password: '' },
  })

  const onSubmit = (values: SignupFormValues) => {
    signupMutation.mutate(values, {
      onSuccess: () => navigate(ROUTES.login, { replace: true }),
    })
  }

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
      <Input label="Full name" error={errors.full_name?.message} {...register('full_name')} />
      <Input label="Email" type="email" error={errors.email?.message} {...register('email')} />
      <Input label="Password" type="password" error={errors.password?.message} {...register('password')} />

      <Button type="submit" className="w-full" loading={signupMutation.isPending}>
        Create account
      </Button>

      <p className="text-center text-sm text-slate-600">
        Already have an account?{' '}
        <Link to={ROUTES.login} className="text-[var(--brand-primary)] hover:text-[var(--brand-primary-hover)]">
          Sign in
        </Link>
      </p>
    </form>
  )
}
