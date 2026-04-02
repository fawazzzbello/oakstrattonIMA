import { useState } from 'react'
import { Link } from 'react-router-dom'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { useMutation } from '@tanstack/react-query'
import api from '@/utils/api'
import { Loader2, ArrowLeft, Mail } from 'lucide-react'

const schema = z.object({
  email: z.string().email('Invalid email address'),
})
type FormData = z.infer<typeof schema>

export default function ForgotPasswordPage() {
  const [sent, setSent] = useState(false)

  const { register, handleSubmit, formState: { errors } } = useForm<FormData>({
    resolver: zodResolver(schema),
  })

  const mutation = useMutation({
    mutationFn: (data: FormData) => api.post('/auth/forgot-password', data),
    onSuccess: () => setSent(true),
  })

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
          {sent ? (
            <div className="text-center space-y-4">
              <div className="w-14 h-14 rounded-full bg-emerald-400/10 flex items-center justify-center mx-auto">
                <Mail size={26} className="text-emerald-400" />
              </div>
              <h2 className="text-xl font-semibold font-heading text-foreground">Check your inbox</h2>
              <p className="text-muted-foreground text-sm leading-relaxed">
                If that email is registered, you'll receive a password reset link within a few minutes.
                Check your spam folder if you don't see it.
              </p>
              <Link to="/login" className="btn-primary w-full flex items-center justify-center gap-2 mt-2">
                Back to Sign In
              </Link>
            </div>
          ) : (
            <>
              <h2 className="text-xl font-semibold font-heading text-foreground mb-2">
                Forgot your password?
              </h2>
              <p className="text-muted-foreground text-sm mb-6">
                Enter your account email and we'll send you a reset link.
              </p>

              <form onSubmit={handleSubmit((data) => mutation.mutate(data))} className="space-y-5">
                <div>
                  <label className="block text-sm font-medium text-foreground mb-1.5">
                    Email address
                  </label>
                  <input
                    {...register('email')}
                    type="email"
                    placeholder="you@example.com"
                    className="w-full input-field"
                    autoComplete="email"
                  />
                  {errors.email && (
                    <p className="text-destructive text-xs mt-1.5">{errors.email.message}</p>
                  )}
                </div>

                {mutation.error && (
                  <div className="bg-destructive/10 text-destructive text-sm p-3 rounded-lg border border-destructive/20">
                    {(mutation.error as any)?.response?.data?.detail || 'Something went wrong. Please try again.'}
                  </div>
                )}

                <button
                  type="submit"
                  disabled={mutation.isPending}
                  className="w-full btn-primary flex items-center justify-center gap-2 disabled:opacity-50"
                >
                  {mutation.isPending ? (
                    <><Loader2 size={18} className="animate-spin" /> Sending...</>
                  ) : (
                    'Send Reset Link'
                  )}
                </button>
              </form>
            </>
          )}

          {!sent && (
            <p className="text-center text-sm text-muted-foreground mt-6">
              <Link to="/login" className="text-primary hover:underline inline-flex items-center gap-1">
                <ArrowLeft size={14} /> Back to Sign In
              </Link>
            </p>
          )}
        </div>
      </div>
    </div>
  )
}
