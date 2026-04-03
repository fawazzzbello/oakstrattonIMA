import { useState, useCallback } from 'react'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { useLogin, useRegister } from '@/hooks/useAuth'
import { Navigate, Link } from 'react-router-dom'
import { useAuthStore } from '@/store/authStore'
import { Loader2, Eye, EyeOff, CheckCircle2, XCircle, Phone, User, Mail, Lock, Globe } from 'lucide-react'

// ── Schemas ────────────────────────────────────────────────────────────────────

const loginSchema = z.object({
  email: z.string().email('Invalid email address'),
  password: z.string().min(6, 'Password must be at least 6 characters'),
})

const registerSchema = z.object({
  full_name: z.string().min(2, 'Name must be at least 2 characters'),
  email: z.string().email('Invalid email address'),
  confirm_email: z.string().email('Invalid email address'),
  phone: z.string().min(7, 'Enter a valid phone number').optional().or(z.literal('')),
  timezone: z.string().optional(),
  password: z.string()
    .min(8, 'Password must be at least 8 characters')
    .regex(/[A-Z]/, 'Must contain an uppercase letter')
    .regex(/[0-9]/, 'Must contain a number'),
  confirm_password: z.string(),
}).refine((d) => d.email === d.confirm_email, {
  message: 'Emails do not match',
  path: ['confirm_email'],
}).refine((d) => d.password === d.confirm_password, {
  message: 'Passwords do not match',
  path: ['confirm_password'],
})

type LoginForm = z.infer<typeof loginSchema>
type RegisterForm = z.infer<typeof registerSchema>

// ── Password strength ──────────────────────────────────────────────────────────

function getPasswordStrength(pw: string): { score: number; label: string; color: string } {
  if (!pw) return { score: 0, label: '', color: '' }
  let score = 0
  if (pw.length >= 8) score++
  if (pw.length >= 12) score++
  if (/[A-Z]/.test(pw)) score++
  if (/[0-9]/.test(pw)) score++
  if (/[^A-Za-z0-9]/.test(pw)) score++

  if (score <= 1) return { score: 1, label: 'Weak', color: 'bg-rose-500' }
  if (score === 2) return { score: 2, label: 'Fair', color: 'bg-amber-400' }
  if (score === 3) return { score: 3, label: 'Good', color: 'bg-yellow-400' }
  if (score === 4) return { score: 4, label: 'Strong', color: 'bg-emerald-400' }
  return { score: 5, label: 'Very Strong', color: 'bg-emerald-400' }
}

// ── Common timezones ───────────────────────────────────────────────────────────

const TIMEZONES = [
  'UTC', 'America/New_York', 'America/Chicago', 'America/Denver', 'America/Los_Angeles',
  'America/Toronto', 'America/Vancouver', 'America/Sao_Paulo',
  'Europe/London', 'Europe/Paris', 'Europe/Berlin', 'Europe/Moscow',
  'Africa/Lagos', 'Africa/Johannesburg', 'Africa/Nairobi', 'Africa/Accra',
  'Asia/Dubai', 'Asia/Karachi', 'Asia/Kolkata', 'Asia/Bangkok', 'Asia/Singapore',
  'Asia/Tokyo', 'Asia/Shanghai', 'Australia/Sydney',
]

// ── Component ──────────────────────────────────────────────────────────────────

export default function LoginPage() {
  const { isAuthenticated } = useAuthStore()
  const [mode, setMode] = useState<'login' | 'register'>('login')
  const [showPw, setShowPw] = useState(false)
  const [showConfirmPw, setShowConfirmPw] = useState(false)
  const [pwValue, setPwValue] = useState('')
  const login = useLogin()
  const register = useRegister()

  const loginForm = useForm<LoginForm>({ resolver: zodResolver(loginSchema) })
  const registerForm = useForm<RegisterForm>({
    resolver: zodResolver(registerSchema),
    mode: 'onChange',
  })

  const watchEmail = registerForm.watch('email', '')
  const watchConfirmEmail = registerForm.watch('confirm_email', '')
  const watchConfirmPw = registerForm.watch('confirm_password', '')

  const emailsMatch = watchEmail && watchConfirmEmail && watchEmail === watchConfirmEmail
  const emailsMismatch = watchConfirmEmail && watchEmail !== watchConfirmEmail
  const pwsMatch = pwValue && watchConfirmPw && pwValue === watchConfirmPw
  const pwsMismatch = watchConfirmPw && pwValue !== watchConfirmPw

  const strength = getPasswordStrength(pwValue)

  if (isAuthenticated) return <Navigate to="/app/dashboard" replace />

  const isLogin = mode === 'login'
  const isPending = login.isPending || register.isPending

  const handleRegisterSubmit = useCallback((data: RegisterForm) => {
    // Strip confirm fields before sending to backend
    const { confirm_email, confirm_password, ...payload } = data
    register.mutate({ ...payload, phone: payload.phone || undefined } as any)
  }, [register])

  return (
    <div className="min-h-screen aurora-bg flex items-center justify-center p-4">
      <div className="w-full max-w-md animate-fade-in">

        {/* Brand */}
        <div className="text-center mb-8">
          <div className="w-14 h-14 rounded-xl bg-primary/20 glow-ring flex items-center justify-center text-primary font-bold text-2xl mx-auto mb-5 font-heading">
            O
          </div>
          <h1 className="text-3xl font-bold font-heading gradient-text">OakstrattonIMA</h1>
          <p className="text-muted-foreground mt-2 text-sm">AI-Powered Influence Marketing</p>
        </div>

        <div className="glass-card p-8">
          <h2 className="text-xl font-semibold font-heading text-foreground mb-6">
            {isLogin ? 'Sign in to your account' : 'Create your account'}
          </h2>

          {/* ── LOGIN FORM ── */}
          {isLogin ? (
            <form onSubmit={loginForm.handleSubmit((data) => login.mutate(data))} className="space-y-5">
              <div>
                <label className="block text-sm font-medium text-foreground mb-1.5">Email</label>
                <div className="relative">
                  <Mail size={15} className="absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground pointer-events-none" />
                  <input {...loginForm.register('email')} type="email" placeholder="you@example.com" className="w-full input-field pl-9" autoComplete="email" />
                </div>
                {loginForm.formState.errors.email && <p className="text-destructive text-xs mt-1.5">{loginForm.formState.errors.email.message}</p>}
              </div>

              <div>
                <label className="block text-sm font-medium text-foreground mb-1.5">Password</label>
                <div className="relative">
                  <Lock size={15} className="absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground pointer-events-none" />
                  <input {...loginForm.register('password')} type={showPw ? 'text' : 'password'} placeholder="••••••••" className="w-full input-field pl-9 pr-10" autoComplete="current-password" />
                  <button type="button" onClick={() => setShowPw((v) => !v)} className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground transition-colors">
                    {showPw ? <EyeOff size={15} /> : <Eye size={15} />}
                  </button>
                </div>
                {loginForm.formState.errors.password && <p className="text-destructive text-xs mt-1.5">{loginForm.formState.errors.password.message}</p>}
              </div>

              {login.error && (
                <div className="bg-destructive/10 text-destructive text-sm p-3 rounded-lg border border-destructive/20">
                  {(login.error as any)?.response?.data?.detail || 'Invalid email or password.'}
                </div>
              )}

              <div className="flex justify-end">
                <Link to="/forgot-password" className="text-xs text-muted-foreground hover:text-primary transition-colors">Forgot password?</Link>
              </div>

              <button type="submit" disabled={isPending} className="w-full btn-primary flex items-center justify-center gap-2 disabled:opacity-50">
                {login.isPending ? <><Loader2 size={18} className="animate-spin" />Signing in...</> : 'Sign In'}
              </button>
            </form>

          ) : (
            // ── REGISTER FORM ──
            <form onSubmit={registerForm.handleSubmit(handleRegisterSubmit)} className="space-y-4">

              {/* Full Name */}
              <div>
                <label className="block text-sm font-medium text-foreground mb-1.5">Full Name <span className="text-rose-400">*</span></label>
                <div className="relative">
                  <User size={15} className="absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground pointer-events-none" />
                  <input {...registerForm.register('full_name')} type="text" placeholder="Jane Smith" className="w-full input-field pl-9" autoComplete="name" />
                </div>
                {registerForm.formState.errors.full_name && <p className="text-destructive text-xs mt-1">{registerForm.formState.errors.full_name.message}</p>}
              </div>

              {/* Email */}
              <div>
                <label className="block text-sm font-medium text-foreground mb-1.5">Email <span className="text-rose-400">*</span></label>
                <div className="relative">
                  <Mail size={15} className="absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground pointer-events-none" />
                  <input {...registerForm.register('email')} type="email" placeholder="you@example.com" className="w-full input-field pl-9" autoComplete="email" />
                </div>
                {registerForm.formState.errors.email && <p className="text-destructive text-xs mt-1">{registerForm.formState.errors.email.message}</p>}
              </div>

              {/* Confirm Email */}
              <div>
                <label className="block text-sm font-medium text-foreground mb-1.5">Confirm Email <span className="text-rose-400">*</span></label>
                <div className="relative">
                  <Mail size={15} className="absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground pointer-events-none" />
                  <input {...registerForm.register('confirm_email')} type="email" placeholder="you@example.com" className={`w-full input-field pl-9 pr-9 ${emailsMatch ? 'border-emerald-500/50' : emailsMismatch ? 'border-rose-500/50' : ''}`} autoComplete="email" />
                  {emailsMatch && <CheckCircle2 size={15} className="absolute right-3 top-1/2 -translate-y-1/2 text-emerald-400" />}
                  {emailsMismatch && <XCircle size={15} className="absolute right-3 top-1/2 -translate-y-1/2 text-rose-400" />}
                </div>
                {emailsMismatch && !registerForm.formState.errors.confirm_email && (
                  <p className="text-rose-400 text-xs mt-1 flex items-center gap-1"><XCircle size={11} />Emails do not match</p>
                )}
                {emailsMatch && <p className="text-emerald-400 text-xs mt-1 flex items-center gap-1"><CheckCircle2 size={11} />Emails match</p>}
                {registerForm.formState.errors.confirm_email && <p className="text-destructive text-xs mt-1">{registerForm.formState.errors.confirm_email.message}</p>}
              </div>

              {/* Phone */}
              <div>
                <label className="block text-sm font-medium text-foreground mb-1.5">Phone Number <span className="text-muted-foreground font-normal text-xs">(optional)</span></label>
                <div className="relative">
                  <Phone size={15} className="absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground pointer-events-none" />
                  <input {...registerForm.register('phone')} type="tel" placeholder="+1 555 000 0000" className="w-full input-field pl-9" autoComplete="tel" />
                </div>
                {registerForm.formState.errors.phone && <p className="text-destructive text-xs mt-1">{registerForm.formState.errors.phone.message}</p>}
              </div>

              {/* Timezone */}
              <div>
                <label className="block text-sm font-medium text-foreground mb-1.5">Timezone <span className="text-muted-foreground font-normal text-xs">(optional)</span></label>
                <div className="relative">
                  <Globe size={15} className="absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground pointer-events-none" />
                  <select {...registerForm.register('timezone')} className="w-full input-field pl-9 appearance-none">
                    {TIMEZONES.map((tz) => <option key={tz} value={tz}>{tz.replace('_', ' ')}</option>)}
                  </select>
                </div>
              </div>

              {/* Password */}
              <div>
                <label className="block text-sm font-medium text-foreground mb-1.5">Password <span className="text-rose-400">*</span></label>
                <div className="relative">
                  <Lock size={15} className="absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground pointer-events-none" />
                  <input
                    {...registerForm.register('password')}
                    type={showPw ? 'text' : 'password'}
                    placeholder="Min 8 chars, 1 uppercase, 1 number"
                    className="w-full input-field pl-9 pr-10"
                    autoComplete="new-password"
                    onChange={(e) => {
                      registerForm.register('password').onChange(e)
                      setPwValue(e.target.value)
                    }}
                  />
                  <button type="button" onClick={() => setShowPw((v) => !v)} className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground transition-colors">
                    {showPw ? <EyeOff size={15} /> : <Eye size={15} />}
                  </button>
                </div>
                {/* Strength bar */}
                {pwValue && (
                  <div className="mt-2 space-y-1">
                    <div className="flex gap-1">
                      {[1, 2, 3, 4, 5].map((i) => (
                        <div key={i} className={`h-1 flex-1 rounded-full transition-all duration-300 ${i <= strength.score ? strength.color : 'bg-muted/40'}`} />
                      ))}
                    </div>
                    <p className={`text-xs font-medium ${strength.score <= 1 ? 'text-rose-400' : strength.score <= 2 ? 'text-amber-400' : strength.score <= 3 ? 'text-yellow-400' : 'text-emerald-400'}`}>
                      {strength.label}
                    </p>
                  </div>
                )}
                {registerForm.formState.errors.password && <p className="text-destructive text-xs mt-1">{registerForm.formState.errors.password.message}</p>}
              </div>

              {/* Confirm Password */}
              <div>
                <label className="block text-sm font-medium text-foreground mb-1.5">Confirm Password <span className="text-rose-400">*</span></label>
                <div className="relative">
                  <Lock size={15} className="absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground pointer-events-none" />
                  <input
                    {...registerForm.register('confirm_password')}
                    type={showConfirmPw ? 'text' : 'password'}
                    placeholder="Re-enter your password"
                    className={`w-full input-field pl-9 pr-10 ${pwsMatch ? 'border-emerald-500/50' : pwsMismatch ? 'border-rose-500/50' : ''}`}
                    autoComplete="new-password"
                  />
                  <button type="button" onClick={() => setShowConfirmPw((v) => !v)} className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground transition-colors">
                    {showConfirmPw ? <EyeOff size={15} /> : <Eye size={15} />}
                  </button>
                </div>
                {pwsMismatch && !registerForm.formState.errors.confirm_password && (
                  <p className="text-rose-400 text-xs mt-1 flex items-center gap-1"><XCircle size={11} />Passwords do not match</p>
                )}
                {pwsMatch && <p className="text-emerald-400 text-xs mt-1 flex items-center gap-1"><CheckCircle2 size={11} />Passwords match</p>}
                {registerForm.formState.errors.confirm_password && <p className="text-destructive text-xs mt-1">{registerForm.formState.errors.confirm_password.message}</p>}
              </div>

              {register.error && (
                <div className="bg-destructive/10 text-destructive text-sm p-3 rounded-lg border border-destructive/20">
                  {(register.error as any)?.response?.data?.detail || (register.error as any)?.message || 'Registration failed. Please try again.'}
                </div>
              )}

              <button type="submit" disabled={isPending} className="w-full btn-primary flex items-center justify-center gap-2 disabled:opacity-50 mt-2">
                {register.isPending ? <><Loader2 size={18} className="animate-spin" />Creating account...</> : 'Create Account'}
              </button>

              <p className="text-xs text-muted-foreground/50 text-center">By registering you agree to our terms of service.</p>
            </form>
          )}

          {/* Toggle */}
          <p className="text-center text-sm text-muted-foreground mt-6">
            {isLogin ? "Don't have an account?" : 'Already have an account?'}{' '}
            <button type="button" onClick={() => { setMode(isLogin ? 'register' : 'login'); setPwValue('') }} className="text-primary hover:underline font-medium">
              {isLogin ? 'Register' : 'Sign In'}
            </button>
          </p>
        </div>

        <p className="text-center text-xs text-muted-foreground/50 mt-6">Powered by AI</p>
      </div>
    </div>
  )
}
