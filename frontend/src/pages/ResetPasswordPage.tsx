import { useState } from 'react'
import { Link, useSearchParams, useNavigate } from 'react-router-dom'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { useMutation } from '@tanstack/react-query'
import api from '@/utils/api'
import { Loader2, CheckCircle, AlertCircle } from 'lucide-react'

const schema = z.object({
  new_password: z.string().min(8, 'Password must be at least 8 characters'),
  confirm_password: z.string(),
}).refine((d) => d.new_password === d.confirm_password, {
  message: 'Passwords do not match',
  path: ['confirm_password'],
})
type FormData = z.infer<typeof schema>

export default function ResetPasswordPage() {
  const [searchParams] = useSearchParams()
  const navigate = useNavigate()
  const token = searchParams.get('token')
  const [done, setDone] = useState(false)

  const { register, handleSubmit, formState: { errors } } = useForm<FormData>({
    resolver: zodResolver(schema),
  })

  const mutation = useMutation({
    mutationFn: ({ new_password }: FormData) =>
      api.post('/auth/reset-password', { token, new_password }),
    onSuccess: () => setDone(true),
  })

  // No token in URL
  if (!token) {
    return (
      <div className="min-h-screen aurora-bg flex items-center justify-center p-4">
        <div className="w-full max-w-md animate-fade-in">
          <div className="glass-card p-8 text-center space-y-4">
            <AlertCircle size={36} className="text-destructive mx-auto" />
            <h2 className="text-xl font-semibold font-heading text-foreground">Invalid Link</h2>
            <p className="text-muted-foreground text-sm">
              This password reset link is missing a token. Please request a new one.
            </p>
            <Link to="/forgot-password" className="btn-primary w-full flex items-center justify-center">
              Request New Link
            </Link>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen aurora-bg flex items-center justify-center p-4">
      <div className="w-full max-w-md animate-fade-in">
        {/* Logo */}
        <div className="text-center mb-8">
          <div className="w-12 h-12 rounded-xl bg-primary/20 glow-ring flex items-center justify-center text-primary font-bold text-xl mx-auto mb-4 font-heading">
            O
          </div>
          <h1 className="text-2xl font-bold font-heading gradient-text">OakstrattonIMA</h1>
        </div>

        <div className="glass-card p-8">
          {done ? (
            <div className="text-center space-y-4">
              <div className="w-14 h-14 rounded-full bg-emerald-400/10 flex items-center justify-center mx-auto">
                <CheckCircle size={28} className="text-emerald-400" />
              </div>
              <h2 className="text-xl font-semibold font-heading text-foreground">Password updated!</h2>
              <p className="text-muted-foreground text-sm">
                Your password has been reset successfully. You can now sign in with your new password.
              </p>
              <button
                onClick={() => navigate('/login')}
                className="btn-primary w-full"
              >
                Sign In
              </button>
            </div>
          ) : (
            <>
              <h2 className="text-xl font-semibold font-heading text-foreground mb-2">
                Set new password
              </h2>
              <p className="text-muted-foreground text-sm mb-6">
                Choose a strong password (at least 8 characters).
              </p>

              <form onSubmit={handleSubmit((data) => mutation.mutate(data))} className="space-y-5">
                <div>
                  <label className="block text-sm font-medium text-foreground mb-1.5">
                    New password
                  </label>
                  <input
                    {...register('new_password')}
                    type="password"
                    placeholder="••••••••"
                    className="w-full input-field"
                    autoComplete="new-password"
                  />
                  {errors.new_password && (
                    <p className="text-destructive text-xs mt-1.5">{errors.new_password.message}</p>
                  )}
                </div>

                <div>
                  <label className="block text-sm font-medium text-foreground mb-1.5">
                    Confirm new password
                  </label>
                  <input
                    {...register('confirm_password')}
                    type="password"
                    placeholder="••••••••"
                    className="w-full input-field"
                    autoComplete="new-password"
                  />
                  {errors.confirm_password && (
                    <p className="text-destructive text-xs mt-1.5">{errors.confirm_password.message}</p>
                  )}
                </div>

                {mutation.error && (
                  <div className="bg-destructive/10 text-destructive text-sm p-3 rounded-lg border border-destructive/20">
                    {(mutation.error as any)?.response?.data?.detail ||
                      'Reset link may have expired. Please request a new one.'}
                  </div>
                )}

                <button
                  type="submit"
                  disabled={mutation.isPending}
                  className="w-full btn-primary flex items-center justify-center gap-2 disabled:opacity-50"
                >
                  {mutation.isPending ? (
                    <><Loader2 size={18} className="animate-spin" /> Updating password...</>
                  ) : (
                    'Set New Password'
                  )}
                </button>
              </form>

              <p className="text-center text-sm text-muted-foreground mt-6">
                <Link to="/forgot-password" className="text-primary hover:underline">
                  Request a new link
                </Link>
              </p>
            </>
          )}
        </div>
      </div>
    </div>
  )
}
