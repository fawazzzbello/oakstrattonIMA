import { Link } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import type { PublicSiteSettings } from '@/types'
import api from '@/utils/api'

const DEFAULT_FEATURES = [
  {
    icon: '🤖',
    title: 'AI Influencer Matching',
    desc: 'Claude AI analyzes your campaign brief and ranks the best influencers by fit, reach, and engagement — in seconds.',
  },
  {
    icon: '📊',
    title: 'Real-Time Analytics',
    desc: 'Track impressions, clicks, conversions and ROI across every campaign and platform from a single dashboard.',
  },
  {
    icon: '📝',
    title: 'Contract Automation',
    desc: 'Generate, send, and e-sign influencer contracts automatically. No legal back-and-forth required.',
  },
  {
    icon: '💳',
    title: 'Integrated Payments',
    desc: 'Stripe-powered invoicing and influencer payouts. Automated on deliverable approval.',
  },
  {
    icon: '🎯',
    title: 'Campaign Management',
    desc: 'Full lifecycle management from brief to published content. Assign tasks, track status, approve deliverables.',
  },
  {
    icon: '🔔',
    title: 'Smart Notifications',
    desc: 'Everyone stays in the loop — managers, clients and influencers — with role-based alerts.',
  },
]

const steps = [
  {
    num: '01',
    title: 'Create a Campaign Brief',
    desc: 'Describe your brand, goals, and target audience. AI expands your brief into a full creative strategy.',
  },
  {
    num: '02',
    title: 'AI Matches Influencers',
    desc: 'Our engine scores and ranks your influencer roster against the brief, showing fit scores and reasoning.',
  },
  {
    num: '03',
    title: 'Contract, Track & Pay',
    desc: 'Send contracts, monitor live performance, approve content, and trigger payouts — all in one place.',
  },
]

const DEFAULT_STATS = [
  { value: '10×', label: 'Faster influencer matching' },
  { value: '3 min', label: 'Average contract turnaround' },
  { value: '100%', label: 'Audit-logged actions' },
  { value: 'AI', label: 'Powered by Claude' },
]

const SOCIAL_ICONS: Record<string, string> = {
  twitter: '𝕏',
  instagram: '📸',
  linkedin: '💼',
  tiktok: '🎵',
  youtube: '▶️',
  facebook: '👥',
}

export default function LandingPage() {
  const { data: siteSettings } = useQuery<PublicSiteSettings>({
    queryKey: ['public-settings'],
    queryFn: async () => {
      const { data } = await api.get('/directory/public-settings')
      return data
    },
    staleTime: 60_000,
  })

  const agencyName = siteSettings?.agency_name ?? 'OakstrattonIMA'
  const agencyLogo = siteSettings?.agency_logo_url
  const agencyTagline = siteSettings?.agency_tagline
  const landing = siteSettings?.landing_config ?? {}
  const footer = siteSettings?.footer_config ?? {}

  const heroHeadline = (landing as any).hero_headline ?? 'Run Smarter\nInfluencer Campaigns'
  const heroSubtitle = (landing as any).hero_subtitle ?? `${agencyName} combines AI influencer matching, contract automation, real-time analytics and integrated payments into one sleek platform built for modern marketing agencies.`
  const ctaPrimary = (landing as any).cta_primary_text ?? 'Get Started Free'
  const ctaSecondary = (landing as any).cta_secondary_text ?? 'Browse Influencers'
  const showDirectoryCta = (landing as any).show_directory_cta !== false
  const showFeatures = (landing as any).show_features !== false
  const statsData: { value: string; label: string }[] = (landing as any).stats?.length ? (landing as any).stats : DEFAULT_STATS

  const footerCopyright = (footer as any).copyright ?? `© ${new Date().getFullYear()} ${agencyName}. All rights reserved.`
  const footerTagline = (footer as any).tagline ?? 'AI-Powered by Claude · Deployed on Railway'
  const footerLinks: { label: string; url: string }[] = (footer as any).links ?? []
  const socialLinks: { platform: string; url: string }[] = (footer as any).social ?? []

  return (
    <div className="min-h-screen bg-background text-foreground overflow-x-hidden">

      {/* ── Sticky Nav ── */}
      <header className="sticky top-0 z-50 border-b border-border/40 bg-background/80 backdrop-blur-xl">
        <div className="mx-auto max-w-6xl px-4 sm:px-6 flex h-14 items-center justify-between">
          <div className="flex items-center gap-2.5">
            {agencyLogo ? (
              <img src={agencyLogo} alt={agencyName} className="w-7 h-7 rounded-lg object-contain" />
            ) : (
              <div className="w-7 h-7 rounded-lg bg-primary/20 glow-ring flex items-center justify-center text-primary font-bold text-sm font-heading">
                {agencyName[0].toUpperCase()}
              </div>
            )}
            <span className="font-heading font-semibold text-foreground text-sm">
              {agencyName}
            </span>
          </div>
          <Link to="/login" className="btn-primary text-sm px-5 py-2">
            Sign In
          </Link>
        </div>
      </header>

      {/* ── Hero ── */}
      <section className="relative aurora-bg px-4 sm:px-6 pt-20 pb-24 text-center overflow-hidden">
        <div className="pointer-events-none absolute -top-32 left-1/2 -translate-x-1/2 w-[600px] h-[600px] rounded-full bg-primary/5 blur-[120px]" />
        <div className="pointer-events-none absolute top-20 -right-20 w-72 h-72 rounded-full bg-cyan-500/5 blur-[80px]" />

        <div className="relative mx-auto max-w-3xl">
          <div className="inline-flex items-center gap-2 rounded-full bg-primary/10 border border-primary/20 px-4 py-1.5 text-xs text-primary font-medium mb-6">
            <span className="w-1.5 h-1.5 rounded-full bg-primary animate-pulse" />
            AI-Powered Influence Marketing Platform
          </div>

          <h1 className="font-heading text-4xl sm:text-5xl md:text-6xl font-bold leading-tight mb-6">
            {heroHeadline.includes('\n') ? (
              <>
                {heroHeadline.split('\n')[0]}
                <br />
                <span className="gradient-text">{heroHeadline.split('\n')[1]}</span>
              </>
            ) : (
              <span className="gradient-text">{heroHeadline}</span>
            )}
          </h1>

          <p className="text-muted-foreground text-base sm:text-lg max-w-xl mx-auto mb-10 leading-relaxed">
            {heroSubtitle}
          </p>

          <div className="flex flex-col sm:flex-row gap-3 justify-center">
            <Link
              to="/login"
              className="btn-primary text-base px-8 py-3 rounded-xl shadow-[0_0_30px_rgba(124,92,252,0.25)] hover:shadow-[0_0_40px_rgba(124,92,252,0.35)] transition-shadow"
            >
              {ctaPrimary}
            </Link>
            {showDirectoryCta && (
              <Link to="/directory" className="btn-secondary text-base px-8 py-3 rounded-xl">
                {ctaSecondary}
              </Link>
            )}
          </div>
        </div>
      </section>

      {/* ── Stats bar ── */}
      <section className="border-y border-border/40 bg-card/30">
        <div className="mx-auto max-w-6xl px-4 sm:px-6 py-8 grid grid-cols-2 md:grid-cols-4 gap-6 text-center">
          {statsData.map((s) => (
            <div key={s.label}>
              <div className="font-heading text-2xl sm:text-3xl font-bold gradient-text">{s.value}</div>
              <div className="text-xs text-muted-foreground mt-1">{s.label}</div>
            </div>
          ))}
        </div>
      </section>

      {/* ── Features ── */}
      {showFeatures && (
        <section className="px-4 sm:px-6 py-20">
          <div className="mx-auto max-w-6xl">
            <div className="text-center mb-12">
              <h2 className="font-heading text-2xl sm:text-3xl font-bold mb-3">
                Everything your agency needs
              </h2>
              <p className="text-muted-foreground text-sm sm:text-base max-w-xl mx-auto">
                One platform, zero spreadsheets. From discovery to payment — fully automated.
              </p>
            </div>

            <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-4">
              {DEFAULT_FEATURES.map((f) => (
                <div key={f.title} className="glass-card-hover p-5 group">
                  <div className="w-10 h-10 rounded-lg bg-primary/10 flex items-center justify-center text-xl mb-4 group-hover:bg-primary/15 transition-colors">
                    {f.icon}
                  </div>
                  <h3 className="font-heading font-semibold text-foreground mb-2">{f.title}</h3>
                  <p className="text-muted-foreground text-sm leading-relaxed">{f.desc}</p>
                </div>
              ))}
            </div>
          </div>
        </section>
      )}

      {/* ── How it works ── */}
      <section className="px-4 sm:px-6 py-20 bg-card/20 border-y border-border/40">
        <div className="mx-auto max-w-4xl">
          <div className="text-center mb-12">
            <h2 className="font-heading text-2xl sm:text-3xl font-bold mb-3">
              From brief to results in 3 steps
            </h2>
            <p className="text-muted-foreground text-sm sm:text-base">
              The fastest way to run a campaign — start to finish.
            </p>
          </div>

          <div className="grid md:grid-cols-3 gap-6 relative">
            <div className="hidden md:block absolute top-8 left-[calc(16.66%+1.5rem)] right-[calc(16.66%+1.5rem)] h-px bg-gradient-to-r from-primary/20 via-primary/50 to-primary/20" />
            {steps.map((s) => (
              <div key={s.num} className="glass-card p-6 relative">
                <div className="w-10 h-10 rounded-full bg-primary/15 glow-ring flex items-center justify-center text-primary font-heading font-bold text-sm mb-4 relative z-10">
                  {s.num}
                </div>
                <h3 className="font-heading font-semibold text-foreground mb-2">{s.title}</h3>
                <p className="text-muted-foreground text-sm leading-relaxed">{s.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ── Role callout ── */}
      <section className="px-4 sm:px-6 py-20">
        <div className="mx-auto max-w-5xl">
          <div className="text-center mb-10">
            <h2 className="font-heading text-2xl sm:text-3xl font-bold mb-3">
              Built for every stakeholder
            </h2>
            <p className="text-muted-foreground text-sm sm:text-base max-w-lg mx-auto">
              Role-based access means every user sees exactly what they need.
            </p>
          </div>

          <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-4">
            {[
              { role: 'Admin', color: 'violet', desc: 'Platform control, settings, audit logs, feature flags.', icon: '🛡️' },
              { role: 'Manager', color: 'cyan', desc: 'Campaign operations, AI tools, influencer matching.', icon: '🎬' },
              { role: 'Client', color: 'emerald', desc: 'Campaign visibility, approvals, invoice management.', icon: '🏢' },
              { role: 'Influencer', color: 'amber', desc: 'Brief access, content submission, payment tracking.', icon: '⭐' },
            ].map((r) => (
              <div key={r.role} className="glass-card p-5 text-center">
                <div className="text-2xl mb-3">{r.icon}</div>
                <div className={`status-badge mb-2 ${
                  r.color === 'violet' ? 'bg-violet-400/10 text-violet-400' :
                  r.color === 'cyan' ? 'bg-cyan-400/10 text-cyan-400' :
                  r.color === 'emerald' ? 'bg-emerald-400/10 text-emerald-400' :
                  'bg-amber-400/10 text-amber-400'
                }`}>
                  {r.role}
                </div>
                <p className="text-muted-foreground text-xs leading-relaxed mt-2">{r.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ── CTA ── */}
      <section className="px-4 sm:px-6 py-20 aurora-bg border-t border-border/40">
        <div className="mx-auto max-w-2xl text-center">
          <div className="glass-card p-8 sm:p-12 relative overflow-hidden">
            <div className="pointer-events-none absolute inset-0 bg-gradient-to-br from-primary/5 to-cyan-500/5 rounded-xl" />
            <div className="relative">
              <h2 className="font-heading text-2xl sm:text-3xl font-bold mb-4">
                Ready to launch your
                <span className="gradient-text"> next campaign?</span>
              </h2>
              <p className="text-muted-foreground text-sm sm:text-base mb-8 max-w-md mx-auto">
                Register for free and get your agency running on the most intelligent
                influencer marketing platform available.
              </p>
              <div className="flex flex-col sm:flex-row gap-3 justify-center">
                <Link
                  to="/login"
                  className="btn-primary text-base px-8 py-3 rounded-xl shadow-[0_0_30px_rgba(124,92,252,0.3)]"
                >
                  {ctaPrimary}
                </Link>
                {showDirectoryCta && (
                  <Link to="/directory" className="btn-secondary text-base px-8 py-3 rounded-xl">
                    View Influencer Directory
                  </Link>
                )}
              </div>
              <p className="text-xs text-muted-foreground/60 mt-5">
                Default admin: <code className="font-mono text-muted-foreground">admin@oakstrattonima.com</code>
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* ── Footer ── */}
      <footer className="border-t border-border/40 px-4 sm:px-6 py-8">
        <div className="mx-auto max-w-6xl flex flex-col gap-5">
          <div className="flex flex-col sm:flex-row items-center justify-between gap-4">
            <div className="flex items-center gap-2">
              {agencyLogo ? (
                <img src={agencyLogo} alt={agencyName} className="w-5 h-5 rounded object-contain" />
              ) : (
                <div className="w-5 h-5 rounded bg-primary/20 flex items-center justify-center text-primary font-bold font-heading text-xs">
                  {agencyName[0].toUpperCase()}
                </div>
              )}
              <span className="text-xs text-muted-foreground/50">{agencyName}</span>
            </div>

            {footerLinks.length > 0 && (
              <div className="flex flex-wrap gap-4 justify-center">
                {footerLinks.map((link, i) => (
                  <a key={i} href={link.url} target="_blank" rel="noopener noreferrer" className="text-xs text-muted-foreground/50 hover:text-primary transition-colors">
                    {link.label}
                  </a>
                ))}
              </div>
            )}

            {socialLinks.length > 0 ? (
              <div className="flex gap-3">
                {socialLinks.map((link, i) => (
                  <a key={i} href={link.url} target="_blank" rel="noopener noreferrer" className="text-muted-foreground/40 hover:text-primary transition-colors text-sm" title={link.platform}>
                    {SOCIAL_ICONS[link.platform] ?? link.platform}
                  </a>
                ))}
              </div>
            ) : (
              <Link to="/login" className="text-xs text-primary/60 hover:text-primary transition-colors">
                Sign In →
              </Link>
            )}
          </div>
          <div className="flex flex-col sm:flex-row items-center justify-between gap-2 text-xs text-muted-foreground/40 border-t border-border/20 pt-4">
            <span>{footerCopyright}</span>
            <span>{footerTagline}</span>
          </div>
        </div>
      </footer>
    </div>
  )
}
