import { useState } from 'react'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { useMutation } from '@tanstack/react-query'
import api from '@/utils/api'
import { useAuthStore } from '@/store/authStore'
import { CheckCircle, Loader2, Lock, User } from 'lucide-react'

const changePasswordSchema = z.object({
  current_password: z.string().min(1, 'Required'),
  new_password: z.string().min(8, 'Must be at least 8 characters'),
  confirm_password: z.string(),
}).refine((d) => d.new_password === d.confirm_password, {
  message: 'Passwords do not match',
  path: ['confirm_password'],
})
type ChangePasswordForm = z.infer<typeof changePasswordSchema>

const ROLE_LABELS: Record<string, string> = {
  admin: 'Admin',
  manager: 'Manager',
  client: 'Client',
  influencer: 'Influencer',
}

const ROLE_COLORS: Record<string, string> = {
  admin: 'bg-violet-400/10 text-violet-400',
  manager: 'bg-cyan-400/10 text-cyan-400',
  client: 'bg-emerald-400/10 text-emerald-400',
  influencer: 'bg-amber-400/10 text-amber-400',
}

export default function ProfilePage() {
  const { user } = useAuthStore()
  const [pwSuccess, setPwSuccess] = useState(false)

  const {
    register,
    handleSubmit,
    reset,
    formState: { errors },
  } = useForm<ChangePasswordForm>({ resolver: zodResolver(changePasswordSchema) })

  const changePassword = useMutation({
    mutationFn: (data: ChangePasswordForm) =>
      api.post('/auth/change-password', {
        current_password: data.current_password,
        new_password: data.new_password,
      }),
    onSuccess: () => {
      setPwSuccess(true)
      reset()
      setTimeout(() => setPwSuccess(false), 5000)
    },
  })

  const role = user?.role ?? 'client'
  const initials = user?.full_name
    ? user.full_name.split(' ').map((n) => n[0]).join('').toUpperCase().slice(0, 2)
    : 'U'

  return (
    <div className="page-container">
      <div className="page-header">
        <div>
          <h1 className="page-title">My Profile</h1>
          <p className="page-subtitle">Account details and security settings</p>
        </div>
      </div>

      <div className="grid lg:grid-cols-3 gap-6">
        {/* ── Account Info ── */}
        <div className="lg:col-span-1 glass-card p-6 flex flex-col items-center text-center gap-4">
          <div className="w-20 h-20 rounded-full bg-primary/20 glow-ring flex items-center justify-center text-primary font-bold text-2xl font-heading">
            {initials}
          </div>
          <div>
            <p className="text-lg font-semibold text-foreground font-heading">{user?.full_name}</p>
            <p className="text-sm text-muted-foreground mt-0.5">{user?.email}</p>
          </div>
          <span className={`status-badge text-xs ${ROLE_COLORS[role]}`}>
            {ROLE_LABELS[role]}
          </span>
          <div className="w-full text-left space-y-3 mt-2 border-t border-border/40 pt-4">
            <div className="flex justify-between text-sm">
              <span className="text-muted-foreground">Status</span>
              <span className={user?.is_active ? 'text-emerald-400' : 'text-rose-400'}>
                {user?.is_active ? 'Active' : 'Inactive'}
              </span>
            </div>
            <div className="flex justify-between text-sm">
              <span className="text-muted-foreground">Verified</span>
              <span className={user?.is_verified ? 'text-emerald-400' : 'text-amber-400'}>
                {user?.is_verified ? 'Yes' : 'Pending'}
              </span>
            </div>
            {user?.timezone && (
              <div className="flex justify-between text-sm">
                <span className="text-muted-foreground">Timezone</span>
                <span className="text-foreground">{user.timezone}</span>
              </div>
            )}
            {user?.created_at && (
              <div className="flex justify-between text-sm">
                <span className="text-muted-foreground">Member since</span>
                <span className="text-foreground">
                  {new Date(user.created_at).toLocaleDateString('en-US', {
                    month: 'short', year: 'numeric',
                  })}
                </span>
              </div>
            )}
          </div>
        </div>

        {/* ── Change Password ── */}
        <div className="lg:col-span-2 glass-card p-6">
          <div className="flex items-center gap-2.5 mb-6">
            <div className="w-8 h-8 rounded-lg bg-primary/10 flex items-center justify-center">
              <Lock size={16} className="text-primary" />
            </div>
            <div>
              <h2 className="font-heading font-semibold text-foreground">Change Password</h2>
              <p className="text-xs text-muted-foreground">
                You'll receive a confirmation email after changing your password.
              </p>
            </div>
          </div>

          {pwSuccess && (
            <div className="flex items-center gap-2 bg-emerald-400/10 text-emerald-400 text-sm p-3 rounded-lg border border-emerald-400/20 mb-5">
              <CheckCircle size={16} />
              Password updated successfully. A confirmation email has been sent.
            </div>
          )}

          <form
            onSubmit={handleSubmit((data) => changePassword.mutate(data))}
            className="space-y-5 max-w-sm"
          >
            <div>
              <label className="block text-sm font-medium text-foreground mb-1.5">
                Current password
              </label>
              <input
                {...register('current_password')}
                type="password"
                placeholder="••••••••"
                className="w-full input-field"
                autoComplete="current-password"
              />
              {errors.current_password && (
                <p className="text-destructive text-xs mt-1.5">{errors.current_password.message}</p>
              )}
            </div>

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

            {changePassword.error && (
              <div className="bg-destructive/10 text-destructive text-sm p-3 rounded-lg border border-destructive/20">
                {(changePassword.error as any)?.response?.data?.detail ||
                  'Failed to update password. Please try again.'}
              </div>
            )}

            <button
              type="submit"
              disabled={changePassword.isPending}
              className="btn-primary flex items-center gap-2 disabled:opacity-50"
            >
              {changePassword.isPending ? (
                <><Loader2 size={16} className="animate-spin" /> Updating...</>
              ) : (
                'Update Password'
              )}
            </button>
          </form>
        </div>
      </div>
    </div>
  )
}
