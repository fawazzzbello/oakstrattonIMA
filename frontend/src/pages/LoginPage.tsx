import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { useLogin } from '@/hooks/useAuth'
import { Navigate } from 'react-router-dom'
import { useAuthStore } from '@/store/authStore'

const loginSchema = z.object({
  email: z.string().email('Invalid email address'),
  password: z.string().min(6, 'Password must be at least 6 characters'),
})

type LoginForm = z.infer<typeof loginSchema>

export default function LoginPage() {
  const { isAuthenticated } = useAuthStore()
  const login = useLogin()

  const { register, handleSubmit, formState: { errors } } = useForm<LoginForm>({
    resolver: zodResolver(loginSchema),
  })

  if (isAuthenticated) return <Navigate to="/dashboard" replace />

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-brand-50 to-background p-4">
      <div className="w-full max-w-md">
        {/* Logo */}
        <div className="text-center mb-8">
          <div className="w-16 h-16 rounded-2xl bg-primary flex items-center justify-center text-primary-foreground font-bold text-2xl mx-auto mb-4">
            O
          </div>
          <h1 className="text-2xl font-bold text-foreground">OakstrattonIMA</h1>
          <p className="text-muted-foreground mt-1">Influencer Marketing Platform</p>
        </div>

        {/* Form Card */}
        <div className="bg-card rounded-2xl border border-border p-8 shadow-sm">
          <h2 className="text-xl font-semibold mb-6">Sign in to your account</h2>

          <form onSubmit={handleSubmit((data) => login.mutate(data))} className="space-y-4">
            <div>
              <label className="block text-sm font-medium mb-1.5">Email</label>
              <input
                {...register('email')}
                type="email"
                placeholder="you@example.com"
                className="w-full px-3 py-2 rounded-lg border border-input bg-background text-sm focus:outline-none focus:ring-2 focus:ring-ring"
              />
              {errors.email && (
                <p className="text-destructive text-xs mt-1">{errors.email.message}</p>
              )}
            </div>

            <div>
              <label className="block text-sm font-medium mb-1.5">Password</label>
              <input
                {...register('password')}
                type="password"
                placeholder="••••••••"
                className="w-full px-3 py-2 rounded-lg border border-input bg-background text-sm focus:outline-none focus:ring-2 focus:ring-ring"
              />
              {errors.password && (
                <p className="text-destructive text-xs mt-1">{errors.password.message}</p>
              )}
            </div>

            {login.error && (
              <div className="bg-destructive/10 text-destructive text-sm p-3 rounded-lg">
                Invalid email or password. Please try again.
              </div>
            )}

            <button
              type="submit"
              disabled={login.isPending}
              className="w-full bg-primary text-primary-foreground py-2.5 rounded-lg font-medium hover:bg-primary/90 disabled:opacity-50 transition-colors"
            >
              {login.isPending ? 'Signing in...' : 'Sign In'}
            </button>
          </form>
        </div>
      </div>
    </div>
  )
}
