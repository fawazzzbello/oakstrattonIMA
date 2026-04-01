import { useState } from 'react'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { useLogin, useRegister } from '@/hooks/useAuth'
import { Navigate } from 'react-router-dom'
import { useAuthStore } from '@/store/authStore'
import { Loader2 } from 'lucide-react'

const loginSchema = z.object({
  email: z.string().email('Invalid email address'),
  password: z.string().min(6, 'Password must be at least 6 characters'),
})

const registerSchema = z.object({
  full_name: z.string().min(2, 'Name must be at least 2 characters'),
  email: z.string().email('Invalid email address'),
  password: z.string().min(6, 'Password must be at least 6 characters'),
})

type LoginForm = z.infer<typeof loginSchema>
type RegisterForm = z.infer<typeof registerSchema>

export default function LoginPage() {
  const { isAuthenticated } = useAuthStore()
  const [mode, setMode] = useState<'login' | 'register'>('login')
  const login = useLogin()
  const register = useRegister()

  const loginForm = useForm<LoginForm>({ resolver: zodResolver(loginSchema) })
  const registerForm = useForm<RegisterForm>({ resolver: zodResolver(registerSchema) })

  if (isAuthenticated) return <Navigate to="/dashboard" replace />

  const isLogin = mode === 'login'
  const isPending = login.isPending || register.isPending

  return (
    <div className="min-h-screen aurora-bg flex items-center justify-center p-4">
      <div className="w-full max-w-md animate-fade-in">
        {/* Logo / Brand */}
        <div className="text-center mb-8">
          <div className="w-14 h-14 rounded-xl bg-primary/20 glow-ring flex items-center justify-center text-primary font-bold text-2xl mx-auto mb-5 font-heading">
            O
          </div>
          <h1 className="text-3xl font-bold font-heading gradient-text">
            OakstrattonIMA
          </h1>
          <p className="text-muted-foreground mt-2 text-sm">
            AI-Powered Influence Marketing
          </p>
        </div>

        {/* Form Card */}
        <div className="glass-card p-8">
          <h2 className="text-xl font-semibold font-heading text-foreground mb-6">
            {isLogin ? 'Sign in to your account' : 'Create an account'}
          </h2>

          {isLogin ? (
            <form
              onSubmit={loginForm.handleSubmit((data) => login.mutate(data))}
              className="space-y-5"
            >
              <div>
                <label className="block text-sm font-medium text-foreground mb-1.5">
                  Email
                </label>
                <input
                  {...loginForm.register('email')}
                  type="email"
                  placeholder="you@example.com"
                  className="w-full input-field"
                  autoComplete="email"
                />
                {loginForm.formState.errors.email && (
                  <p className="text-destructive text-xs mt-1.5">
                    {loginForm.formState.errors.email.message}
                  </p>
                )}
              </div>

              <div>
                <label className="block text-sm font-medium text-foreground mb-1.5">
                  Password
                </label>
                <input
                  {...loginForm.register('password')}
                  type="password"
                  placeholder="••••••••"
                  className="w-full input-field"
                  autoComplete="current-password"
                />
                {loginForm.formState.errors.password && (
                  <p className="text-destructive text-xs mt-1.5">
                    {loginForm.formState.errors.password.message}
                  </p>
                )}
              </div>

              {login.error && (
                <div className="bg-destructive/10 text-destructive text-sm p-3 rounded-lg border border-destructive/20">
                  Invalid email or password. Please try again.
                </div>
              )}

              <button
                type="submit"
                disabled={isPending}
                className="w-full btn-primary flex items-center justify-center gap-2 disabled:opacity-50"
              >
                {login.isPending ? (
                  <>
                    <Loader2 size={18} className="animate-spin" />
                    Signing in...
                  </>
                ) : (
                  'Sign In'
                )}
              </button>
            </form>
          ) : (
            <form
              onSubmit={registerForm.handleSubmit((data) => register.mutate(data))}
              className="space-y-5"
            >
              <div>
                <label className="block text-sm font-medium text-foreground mb-1.5">
                  Full Name
                </label>
                <input
                  {...registerForm.register('full_name')}
                  type="text"
                  placeholder="Your Name"
                  className="w-full input-field"
                  autoComplete="name"
                />
                {registerForm.formState.errors.full_name && (
                  <p className="text-destructive text-xs mt-1.5">
                    {registerForm.formState.errors.full_name.message}
                  </p>
                )}
              </div>

              <div>
                <label className="block text-sm font-medium text-foreground mb-1.5">
                  Email
                </label>
                <input
                  {...registerForm.register('email')}
                  type="email"
                  placeholder="you@example.com"
                  className="w-full input-field"
                  autoComplete="email"
                />
                {registerForm.formState.errors.email && (
                  <p className="text-destructive text-xs mt-1.5">
                    {registerForm.formState.errors.email.message}
                  </p>
                )}
              </div>

              <div>
                <label className="block text-sm font-medium text-foreground mb-1.5">
                  Password
                </label>
                <input
                  {...registerForm.register('password')}
                  type="password"
                  placeholder="••••••••"
                  className="w-full input-field"
                  autoComplete="new-password"
                />
                {registerForm.formState.errors.password && (
                  <p className="text-destructive text-xs mt-1.5">
                    {registerForm.formState.errors.password.message}
                  </p>
                )}
              </div>

              {register.error && (
                <div className="bg-destructive/10 text-destructive text-sm p-3 rounded-lg border border-destructive/20">
                  Registration failed. Email may already be in use.
                </div>
              )}

              <button
                type="submit"
                disabled={isPending}
                className="w-full btn-primary flex items-center justify-center gap-2 disabled:opacity-50"
              >
                {register.isPending ? (
                  <>
                    <Loader2 size={18} className="animate-spin" />
                    Creating account...
                  </>
                ) : (
                  'Create Account'
                )}
              </button>
            </form>
          )}

          {/* Toggle */}
          <p className="text-center text-sm text-muted-foreground mt-6">
            {isLogin ? "Don't have an account?" : 'Already have an account?'}{' '}
            <button
              type="button"
              onClick={() => setMode(isLogin ? 'register' : 'login')}
              className="text-primary hover:underline font-medium"
            >
              {isLogin ? 'Register' : 'Sign In'}
            </button>
          </p>
        </div>

        {/* Footer */}
        <p className="text-center text-xs text-muted-foreground/50 mt-6">
          Powered by AI
        </p>
      </div>
    </div>
  )
}
