import { zodResolver } from '@hookform/resolvers/zod'
import { useForm } from 'react-hook-form'
import { Link, useLocation, useNavigate } from 'react-router-dom'

import { useAuth } from '../../hooks/useAuth'
import { ROUTES } from '../../utils/constants'
import { loginSchema, type LoginFormValues } from '../../utils/validation'
import { Button } from '../../components/common/Button'
import { Input } from '../../components/common/Input'

export const LoginForm = () => {
  const navigate = useNavigate()
  const location = useLocation()
  const { loginMutation } = useAuth()
  const redirectTo = (location.state as { from?: string } | undefined)?.from ?? ROUTES.generator

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<LoginFormValues>({
    resolver: zodResolver(loginSchema),
    defaultValues: { email: '', password: '' },
  })

  const onSubmit = (values: LoginFormValues) => {
    loginMutation.mutate(values, {
      onSuccess: () => navigate(redirectTo, { replace: true }),
    })
  }

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
      <Input label="Email" type="email" error={errors.email?.message} {...register('email')} />
      <Input label="Password" type="password" error={errors.password?.message} {...register('password')} />

      <Button type="submit" className="w-full" loading={loginMutation.isPending}>
        Sign in
      </Button>

      <p className="text-center text-sm text-slate-600">
        Need an account?{' '}
        <Link to={ROUTES.signup} className="text-[var(--brand-primary)] hover:text-[var(--brand-primary-hover)]">
          Sign up
        </Link>
      </p>
    </form>
  )
}
