import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import {
  Shield, Settings, Users, Flag, ScrollText, BarChart3,
  Loader2, CheckCircle2, Trash2, Plus, Edit3,
  Lock, Globe, Palette, ToggleLeft, ToggleRight,
  Activity, Megaphone, UserCheck, DollarSign, Image, Layout, Link2,
  Sparkles, CheckCircle, XCircle, ChevronDown,
} from 'lucide-react'
import api from '@/utils/api'
import { useAuthStore } from '@/store/authStore'
import type { PlatformSettings, FeatureFlag, AuditLogEntry, AdminStats, User, FooterLink, SocialLink, LandingStatItem, PlatformFeaturesConfig, AIProvidersResponse, AIProviderInfo } from '@/types'
import { format } from 'date-fns'

// ── Overview Tab ─────────────────────────────────────────────────────────
function OverviewTab() {
  const { data: stats, isLoading } = useQuery({
    queryKey: ['admin-stats'],
    queryFn: async () => { const { data } = await api.get('/admin/stats'); return data as AdminStats },
  })

  const kpis = stats ? [
    { label: 'Total Users', value: stats.total_users, icon: Users, color: 'text-violet-400', bg: 'bg-violet-400/10' },
    { label: 'Campaigns', value: stats.total_campaigns, icon: Megaphone, color: 'text-cyan-400', bg: 'bg-cyan-400/10' },
    { label: 'Influencers', value: stats.total_influencers, icon: UserCheck, color: 'text-emerald-400', bg: 'bg-emerald-400/10' },
    { label: 'Total Revenue', value: `$${Number(stats.total_revenue ?? 0).toLocaleString()}`, icon: DollarSign, color: 'text-amber-400', bg: 'bg-amber-400/10' },
  ] : []

  return (
    <div className="space-y-6">
      {isLoading ? (
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
          {Array.from({ length: 4 }).map((_, i) => <div key={i} className="kpi-card h-24 animate-pulse" />)}
        </div>
      ) : (
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
          {kpis.map(({ label, value, icon: Icon, color, bg }) => (
            <div key={label} className="kpi-card glass-card-hover">
              <div className={`w-9 h-9 rounded-lg ${bg} flex items-center justify-center`}>
                <Icon className={`h-4 w-4 ${color}`} />
              </div>
              <div>
                <p className="text-xs text-muted-foreground">{label}</p>
                <p className="text-2xl font-bold font-heading text-foreground">{value}</p>
              </div>
            </div>
          ))}
        </div>
      )}
      {stats && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div className="glass-card p-5">
            <h3 className="text-sm font-semibold mb-4 flex items-center gap-2"><Users className="h-4 w-4 text-muted-foreground" />Users by Role</h3>
            <div className="space-y-3">
              {Object.entries(stats.users_by_role ?? {}).map(([role, count]) => (
                <div key={role} className="flex items-center gap-3">
                  <span className="text-sm capitalize w-24 text-muted-foreground">{role}</span>
                  <div className="flex-1 bg-muted/40 rounded-full h-2">
                    <div className="bg-gradient-to-r from-violet-500 to-cyan-400 h-2 rounded-full" style={{ width: `${Math.min(100, (count / (stats.total_users || 1)) * 100)}%` }} />
                  </div>
                  <span className="text-sm font-medium w-8 text-right">{count}</span>
                </div>
              ))}
            </div>
          </div>
          <div className="glass-card p-5">
            <h3 className="text-sm font-semibold mb-4 flex items-center gap-2"><Activity className="h-4 w-4 text-muted-foreground" />Campaigns by Status</h3>
            <div className="space-y-3">
              {Object.entries(stats.campaigns_by_status ?? {}).map(([status, count]) => {
                const color = { active: 'from-emerald-500 to-emerald-400', draft: 'from-slate-500 to-slate-400', planning: 'from-cyan-500 to-cyan-400', completed: 'from-violet-500 to-violet-400', cancelled: 'from-rose-500 to-rose-400', paused: 'from-amber-500 to-amber-400' }[status] ?? 'from-slate-500 to-slate-400'
                return (
                  <div key={status} className="flex items-center gap-3">
                    <span className="text-sm capitalize w-24 text-muted-foreground">{status}</span>
                    <div className="flex-1 bg-muted/40 rounded-full h-2">
                      <div className={`bg-gradient-to-r ${color} h-2 rounded-full`} style={{ width: `${Math.min(100, (count / (stats.total_campaigns || 1)) * 100)}%` }} />
                    </div>
                    <span className="text-sm font-medium w-8 text-right">{count}</span>
                  </div>
                )
              })}
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

// ── Branding Tab ─────────────────────────────────────────────────────────
function BrandingTab() {
  const qc = useQueryClient()
  const [saved, setSaved] = useState(false)

  const { data: settings, isLoading } = useQuery({
    queryKey: ['admin-settings'],
    queryFn: async () => { const { data } = await api.get('/admin/settings'); return data as PlatformSettings },
  })

  const [form, setForm] = useState<Partial<PlatformSettings>>({})

  const updateMutation = useMutation({
    mutationFn: async (payload: Partial<PlatformSettings>) => { const { data } = await api.patch('/admin/settings', payload); return data },
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['admin-settings'] })
      qc.invalidateQueries({ queryKey: ['public-settings'] })
      setSaved(true); setTimeout(() => setSaved(false), 3000)
    },
  })

  const current = { ...settings, ...form }

  if (isLoading) return <div className="glass-card p-8 animate-pulse h-64" />

  return (
    <div className="space-y-6">
      {/* Agency Identity */}
      <div className="glass-card p-6 space-y-5">
        <h3 className="text-sm font-semibold flex items-center gap-2"><Palette className="h-4 w-4 text-violet-400" />Agency Identity</h3>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div><label className="block text-xs text-muted-foreground mb-1">Agency Name</label><input className="input-field w-full" value={current.agency_name ?? ''} onChange={(e) => setForm((f) => ({ ...f, agency_name: e.target.value }))} /></div>
          <div><label className="block text-xs text-muted-foreground mb-1">Tagline</label><input className="input-field w-full" placeholder="Your tagline here..." value={current.agency_tagline ?? ''} onChange={(e) => setForm((f) => ({ ...f, agency_tagline: e.target.value }))} /></div>
          <div><label className="block text-xs text-muted-foreground mb-1">Support Email</label><input className="input-field w-full" type="email" value={current.support_email ?? ''} onChange={(e) => setForm((f) => ({ ...f, support_email: e.target.value }))} /></div>
        </div>
      </div>

      {/* Logo */}
      <div className="glass-card p-6 space-y-4">
        <h3 className="text-sm font-semibold flex items-center gap-2"><Image className="h-4 w-4 text-cyan-400" />Logo</h3>
        <div className="flex items-start gap-5">
          <div className="shrink-0">
            {current.agency_logo_url ? (
              <img
                src={current.agency_logo_url}
                alt="Agency logo"
                className="w-16 h-16 rounded-xl object-contain border border-border bg-muted/20"
                onError={(e) => { (e.target as HTMLImageElement).style.display = 'none' }}
              />
            ) : (
              <div className="w-16 h-16 rounded-xl bg-primary/15 flex items-center justify-center text-primary font-bold font-heading text-2xl border border-border">
                {(current.agency_name ?? 'O')[0].toUpperCase()}
              </div>
            )}
            <p className="text-xs text-muted-foreground mt-1.5 text-center">Preview</p>
          </div>
          <div className="flex-1">
            <label className="block text-xs text-muted-foreground mb-1">Logo URL</label>
            <input className="input-field w-full" placeholder="https://example.com/logo.png" value={current.agency_logo_url ?? ''} onChange={(e) => setForm((f) => ({ ...f, agency_logo_url: e.target.value }))} />
            <p className="text-xs text-muted-foreground/60 mt-1.5">Enter a URL for your agency logo. PNG, SVG or WebP recommended. If blank, initials will be shown.</p>
          </div>
        </div>
      </div>

      {/* Colors & Fonts */}
      <div className="glass-card p-6 space-y-5">
        <h3 className="text-sm font-semibold flex items-center gap-2"><Palette className="h-4 w-4 text-cyan-400" />Colors & Fonts</h3>
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
          {[
            { key: 'primary_color', label: 'Primary' },
            { key: 'accent_color', label: 'Accent' },
            { key: 'bg_base_color', label: 'Background' },
            { key: 'surface_color', label: 'Surface' },
          ].map(({ key, label }) => (
            <div key={key}>
              <label className="block text-xs text-muted-foreground mb-1">{label}</label>
              <div className="flex items-center gap-2">
                <input type="color" className="w-8 h-8 rounded border border-border bg-transparent cursor-pointer" value={(current as any)[key] ?? '#7C5CFC'} onChange={(e) => setForm((f) => ({ ...f, [key]: e.target.value }))} />
                <input className="input-field flex-1 text-xs" value={(current as any)[key] ?? ''} onChange={(e) => setForm((f) => ({ ...f, [key]: e.target.value }))} />
              </div>
            </div>
          ))}
        </div>
        <div className="grid grid-cols-2 gap-4">
          <div><label className="block text-xs text-muted-foreground mb-1">Heading Font</label><input className="input-field w-full" placeholder="Space Grotesk" value={current.font_heading ?? ''} onChange={(e) => setForm((f) => ({ ...f, font_heading: e.target.value }))} /></div>
          <div><label className="block text-xs text-muted-foreground mb-1">Body Font</label><input className="input-field w-full" placeholder="Inter" value={current.font_body ?? ''} onChange={(e) => setForm((f) => ({ ...f, font_body: e.target.value }))} /></div>
        </div>
      </div>

      {/* Legal Links */}
      <div className="glass-card p-6 space-y-4">
        <h3 className="text-sm font-semibold flex items-center gap-2"><Globe className="h-4 w-4 text-emerald-400" />Legal Links</h3>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div><label className="block text-xs text-muted-foreground mb-1">Terms of Service URL</label><input className="input-field w-full" placeholder="https://..." value={current.terms_url ?? ''} onChange={(e) => setForm((f) => ({ ...f, terms_url: e.target.value }))} /></div>
          <div><label className="block text-xs text-muted-foreground mb-1">Privacy Policy URL</label><input className="input-field w-full" placeholder="https://..." value={current.privacy_url ?? ''} onChange={(e) => setForm((f) => ({ ...f, privacy_url: e.target.value }))} /></div>
        </div>
      </div>

      <div className="flex items-center gap-3">
        <button className="btn-primary flex items-center gap-2 disabled:opacity-50" onClick={() => updateMutation.mutate(form)} disabled={updateMutation.isPending || Object.keys(form).length === 0}>
          {updateMutation.isPending ? <Loader2 className="h-4 w-4 animate-spin" /> : <Settings className="h-4 w-4" />}Save Changes
        </button>
        {saved && <span className="text-sm text-emerald-400 flex items-center gap-1"><CheckCircle2 className="h-4 w-4" />Saved successfully</span>}
      </div>
    </div>
  )
}

// ── Landing Page Tab ──────────────────────────────────────────────────────
function LandingPageTab() {
  const qc = useQueryClient()
  const [saved, setSaved] = useState(false)

  const { data: settings, isLoading } = useQuery({
    queryKey: ['admin-settings'],
    queryFn: async () => { const { data } = await api.get('/admin/settings'); return data as PlatformSettings },
  })

  const featuresConfig: PlatformFeaturesConfig = settings?.features_config ?? {}
  const landing = featuresConfig.landing ?? {}
  const footer = featuresConfig.footer ?? {}

  const [landingForm, setLandingForm] = useState<Record<string, any>>({})
  const [footerForm, setFooterForm] = useState<Record<string, any>>({})
  const [footerLinks, setFooterLinks] = useState<FooterLink[]>([])
  const [socialLinks, setSocialLinks] = useState<SocialLink[]>([])
  const [stats, setStats] = useState<{ value: string; label: string }[]>([])
  const [initialized, setInitialized] = useState(false)

  if (!isLoading && !initialized && settings) {
    const fc = settings.features_config ?? {}
    const l = fc.landing ?? {}
    const f = fc.footer ?? {}
    setLandingForm(l as Record<string, any>)
    setFooterForm({ copyright: (f as any).copyright ?? '', tagline: (f as any).tagline ?? '' })
    setFooterLinks((f as any).links ?? [])
    setSocialLinks((f as any).social ?? [])
    setStats((l as any).stats ?? [{ value: '10×', label: 'Faster influencer matching' }, { value: '3 min', label: 'Average contract turnaround' }, { value: '100%', label: 'Audit-logged actions' }, { value: 'AI', label: 'Powered by Claude' }])
    setInitialized(true)
  }

  const saveMutation = useMutation({
    mutationFn: async () => {
      const payload = {
        features_config: {
          ...featuresConfig,
          landing: { ...landingForm, stats },
          footer: { ...footerForm, links: footerLinks, social: socialLinks },
        },
      }
      const { data } = await api.patch('/admin/settings', payload)
      return data
    },
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['admin-settings'] })
      qc.invalidateQueries({ queryKey: ['public-settings'] })
      setSaved(true); setTimeout(() => setSaved(false), 3000)
    },
  })

  const addFooterLink = () => setFooterLinks((l) => [...l, { label: '', url: '' }])
  const removeFooterLink = (i: number) => setFooterLinks((l) => l.filter((_, idx) => idx !== i))
  const updateFooterLink = (i: number, field: keyof FooterLink, value: string) =>
    setFooterLinks((l) => l.map((item, idx) => idx === i ? { ...item, [field]: value } : item))

  const addSocialLink = () => setSocialLinks((l) => [...l, { platform: 'twitter', url: '' }])
  const removeSocialLink = (i: number) => setSocialLinks((l) => l.filter((_, idx) => idx !== i))
  const updateSocialLink = (i: number, field: keyof SocialLink, value: string) =>
    setSocialLinks((l) => l.map((item, idx) => idx === i ? { ...item, [field]: value } : item))

  const updateStat = (i: number, field: 'value' | 'label', val: string) =>
    setStats((s) => s.map((item, idx) => idx === i ? { ...item, [field]: val } : item))

  if (isLoading) return <div className="glass-card p-8 animate-pulse h-64" />

  return (
    <div className="space-y-6">
      {/* Hero Section */}
      <div className="glass-card p-6 space-y-4">
        <h3 className="text-sm font-semibold flex items-center gap-2"><Layout className="h-4 w-4 text-violet-400" />Hero Section</h3>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div className="sm:col-span-2">
            <label className="block text-xs text-muted-foreground mb-1">Hero Headline</label>
            <input className="input-field w-full" placeholder="Run Smarter Influencer Campaigns" value={landingForm.hero_headline ?? ''} onChange={(e) => setLandingForm((f) => ({ ...f, hero_headline: e.target.value }))} />
          </div>
          <div className="sm:col-span-2">
            <label className="block text-xs text-muted-foreground mb-1">Hero Subtitle</label>
            <textarea className="input-field w-full resize-none h-20 text-sm" placeholder="OakstrattonIMA combines AI influencer matching..." value={landingForm.hero_subtitle ?? ''} onChange={(e) => setLandingForm((f) => ({ ...f, hero_subtitle: e.target.value }))} />
          </div>
          <div>
            <label className="block text-xs text-muted-foreground mb-1">Primary CTA Text</label>
            <input className="input-field w-full" placeholder="Get Started Free" value={landingForm.cta_primary_text ?? ''} onChange={(e) => setLandingForm((f) => ({ ...f, cta_primary_text: e.target.value }))} />
          </div>
          <div>
            <label className="block text-xs text-muted-foreground mb-1">Secondary CTA Text</label>
            <input className="input-field w-full" placeholder="Browse Influencers" value={landingForm.cta_secondary_text ?? ''} onChange={(e) => setLandingForm((f) => ({ ...f, cta_secondary_text: e.target.value }))} />
          </div>
        </div>
        <div className="flex gap-4">
          <label className="flex items-center gap-2 text-sm cursor-pointer select-none">
            <input type="checkbox" className="accent-primary w-4 h-4" checked={landingForm.show_directory_cta !== false} onChange={(e) => setLandingForm((f) => ({ ...f, show_directory_cta: e.target.checked }))} />
            <span className="text-muted-foreground text-xs">Show directory CTA button</span>
          </label>
          <label className="flex items-center gap-2 text-sm cursor-pointer select-none">
            <input type="checkbox" className="accent-primary w-4 h-4" checked={landingForm.show_features !== false} onChange={(e) => setLandingForm((f) => ({ ...f, show_features: e.target.checked }))} />
            <span className="text-muted-foreground text-xs">Show features grid</span>
          </label>
        </div>
      </div>

      {/* Stats Bar */}
      <div className="glass-card p-6 space-y-4">
        <h3 className="text-sm font-semibold flex items-center gap-2"><BarChart3 className="h-4 w-4 text-cyan-400" />Stats Bar</h3>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
          {stats.map((stat, i) => (
            <div key={i} className="flex gap-2">
              <div className="flex-1">
                <label className="block text-xs text-muted-foreground mb-1">Value</label>
                <input className="input-field w-full text-sm" value={stat.value} onChange={(e) => updateStat(i, 'value', e.target.value)} />
              </div>
              <div className="flex-1">
                <label className="block text-xs text-muted-foreground mb-1">Label</label>
                <input className="input-field w-full text-sm" value={stat.label} onChange={(e) => updateStat(i, 'label', e.target.value)} />
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Footer */}
      <div className="glass-card p-6 space-y-4">
        <h3 className="text-sm font-semibold flex items-center gap-2"><Globe className="h-4 w-4 text-emerald-400" />Footer</h3>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div>
            <label className="block text-xs text-muted-foreground mb-1">Copyright Text</label>
            <input className="input-field w-full" placeholder="© 2026 OakstrattonIMA. All rights reserved." value={footerForm.copyright ?? ''} onChange={(e) => setFooterForm((f) => ({ ...f, copyright: e.target.value }))} />
          </div>
          <div>
            <label className="block text-xs text-muted-foreground mb-1">Footer Tagline</label>
            <input className="input-field w-full" placeholder="AI-Powered by Claude · Deployed on Railway" value={footerForm.tagline ?? ''} onChange={(e) => setFooterForm((f) => ({ ...f, tagline: e.target.value }))} />
          </div>
        </div>

        {/* Footer Links */}
        <div className="space-y-2">
          <div className="flex items-center justify-between">
            <label className="text-xs text-muted-foreground font-medium flex items-center gap-1"><Link2 className="h-3 w-3" />Footer Links</label>
            <button className="btn-ghost text-xs px-2 py-1 flex items-center gap-1" onClick={addFooterLink}><Plus className="h-3 w-3" />Add Link</button>
          </div>
          {footerLinks.map((link, i) => (
            <div key={i} className="flex gap-2 items-center">
              <input className="input-field flex-1 text-sm" placeholder="Label" value={link.label} onChange={(e) => updateFooterLink(i, 'label', e.target.value)} />
              <input className="input-field flex-1 text-sm" placeholder="URL" value={link.url} onChange={(e) => updateFooterLink(i, 'url', e.target.value)} />
              <button onClick={() => removeFooterLink(i)} className="p-1.5 rounded hover:bg-rose-400/10 text-muted-foreground hover:text-rose-400 transition-colors shrink-0"><Trash2 className="h-3.5 w-3.5" /></button>
            </div>
          ))}
          {footerLinks.length === 0 && <p className="text-xs text-muted-foreground/50 italic">No footer links added.</p>}
        </div>

        {/* Social Links */}
        <div className="space-y-2">
          <div className="flex items-center justify-between">
            <label className="text-xs text-muted-foreground font-medium">Social Links</label>
            <button className="btn-ghost text-xs px-2 py-1 flex items-center gap-1" onClick={addSocialLink}><Plus className="h-3 w-3" />Add Social</button>
          </div>
          {socialLinks.map((link, i) => (
            <div key={i} className="flex gap-2 items-center">
              <select className="input-field text-sm shrink-0" value={link.platform} onChange={(e) => updateSocialLink(i, 'platform', e.target.value)}>
                {['twitter', 'instagram', 'linkedin', 'tiktok', 'youtube', 'facebook'].map((p) => <option key={p} value={p}>{p}</option>)}
              </select>
              <input className="input-field flex-1 text-sm" placeholder="Profile URL" value={link.url} onChange={(e) => updateSocialLink(i, 'url', e.target.value)} />
              <button onClick={() => removeSocialLink(i)} className="p-1.5 rounded hover:bg-rose-400/10 text-muted-foreground hover:text-rose-400 transition-colors shrink-0"><Trash2 className="h-3.5 w-3.5" /></button>
            </div>
          ))}
          {socialLinks.length === 0 && <p className="text-xs text-muted-foreground/50 italic">No social links added.</p>}
        </div>
      </div>

      <div className="flex items-center gap-3">
        <button className="btn-primary flex items-center gap-2 disabled:opacity-50" onClick={() => saveMutation.mutate()} disabled={saveMutation.isPending}>
          {saveMutation.isPending ? <Loader2 className="h-4 w-4 animate-spin" /> : <Settings className="h-4 w-4" />}Save Landing & Footer
        </button>
        {saved && <span className="text-sm text-emerald-400 flex items-center gap-1"><CheckCircle2 className="h-4 w-4" />Saved successfully</span>}
      </div>
    </div>
  )
}

// ── Users Tab ────────────────────────────────────────────────────────────
function UsersTab() {
  const qc = useQueryClient()
  const [search, setSearch] = useState('')
  const [roleFilter, setRoleFilter] = useState('')
  const [showAdd, setShowAdd] = useState(false)
  const [editUser, setEditUser] = useState<User | null>(null)
  const [editForm, setEditForm] = useState<{ full_name: string; email: string; role: string; is_active: boolean; is_verified: boolean }>({ full_name: '', email: '', role: 'manager', is_active: true, is_verified: false })
  const [newUser, setNewUser] = useState({ full_name: '', email: '', password: '', role: 'manager' })

  const { data: users, isLoading } = useQuery({
    queryKey: ['admin-users', roleFilter],
    queryFn: async () => {
      const params = new URLSearchParams({ limit: '100' })
      if (roleFilter) params.set('role', roleFilter)
      const { data } = await api.get(`/admin/users?${params}`)
      return data as { items: User[]; total: number }
    },
  })

  const invalidateUserRelated = () => {
    qc.invalidateQueries({ queryKey: ['admin-users'] })
    qc.invalidateQueries({ queryKey: ['admin-stats'] })
    qc.invalidateQueries({ queryKey: ['directory-team'] })
    qc.invalidateQueries({ queryKey: ['directory-influencers'] })
  }

  const createMutation = useMutation({
    mutationFn: async () => { const { data } = await api.post('/admin/users', newUser); return data },
    onSuccess: () => { invalidateUserRelated(); setShowAdd(false); setNewUser({ full_name: '', email: '', password: '', role: 'manager' }) },
  })

  const updateMutation = useMutation({
    mutationFn: async ({ id, payload }: { id: number; payload: typeof editForm }) => {
      const { data } = await api.patch(`/admin/users/${id}`, payload)
      return data
    },
    onSuccess: () => { invalidateUserRelated(); setEditUser(null) },
  })

  const deactivateMutation = useMutation({
    mutationFn: async (userId: number) => { const { data } = await api.delete(`/admin/users/${userId}`); return data },
    onSuccess: () => invalidateUserRelated(),
  })

  const openEdit = (user: User) => {
    setEditUser(user)
    setEditForm({ full_name: user.full_name, email: user.email, role: user.role, is_active: user.is_active, is_verified: user.is_verified })
  }

  const ROLE_COLORS: Record<string, string> = {
    admin: 'bg-rose-400/10 text-rose-400',
    manager: 'bg-violet-400/10 text-violet-400',
    client: 'bg-cyan-400/10 text-cyan-400',
    influencer: 'bg-emerald-400/10 text-emerald-400',
  }

  const filtered = users?.items.filter((u) => !search || u.email.toLowerCase().includes(search.toLowerCase()) || u.full_name.toLowerCase().includes(search.toLowerCase()))

  return (
    <div className="space-y-4">
      <div className="flex gap-3 flex-wrap">
        <input className="input-field flex-1 min-w-48" placeholder="Search users..." value={search} onChange={(e) => setSearch(e.target.value)} />
        <select className="input-field" value={roleFilter} onChange={(e) => setRoleFilter(e.target.value)}>
          <option value="">All Roles</option>
          {['admin', 'manager', 'client', 'influencer'].map((r) => <option key={r} value={r} className="capitalize">{r}</option>)}
        </select>
        <button className="btn-primary flex items-center gap-2" onClick={() => { setShowAdd(!showAdd); setEditUser(null) }}><Plus className="h-4 w-4" />Add User</button>
      </div>

      {showAdd && (
        <div className="glass-card p-5 space-y-4">
          <h3 className="text-sm font-semibold">Create New User</h3>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div><label className="block text-xs text-muted-foreground mb-1">Full Name</label><input className="input-field w-full" value={newUser.full_name} onChange={(e) => setNewUser((u) => ({ ...u, full_name: e.target.value }))} /></div>
            <div><label className="block text-xs text-muted-foreground mb-1">Email</label><input className="input-field w-full" type="email" value={newUser.email} onChange={(e) => setNewUser((u) => ({ ...u, email: e.target.value }))} /></div>
            <div><label className="block text-xs text-muted-foreground mb-1">Password</label><input className="input-field w-full" type="password" value={newUser.password} onChange={(e) => setNewUser((u) => ({ ...u, password: e.target.value }))} /></div>
            <div><label className="block text-xs text-muted-foreground mb-1">Role</label>
              <select className="input-field w-full" value={newUser.role} onChange={(e) => setNewUser((u) => ({ ...u, role: e.target.value }))}>
                {['admin', 'manager', 'client', 'influencer'].map((r) => <option key={r} value={r}>{r}</option>)}
              </select>
            </div>
          </div>
          <div className="flex gap-3">
            <button className="btn-primary flex items-center gap-2 disabled:opacity-50" onClick={() => createMutation.mutate()} disabled={!newUser.email || createMutation.isPending}>
              {createMutation.isPending ? <Loader2 className="h-4 w-4 animate-spin" /> : <Plus className="h-4 w-4" />}Create User
            </button>
            <button className="btn-ghost" onClick={() => setShowAdd(false)}>Cancel</button>
          </div>
        </div>
      )}

      {editUser && (
        <div className="glass-card p-5 space-y-4 border border-violet-400/20">
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-semibold flex items-center gap-2"><Edit3 className="h-4 w-4 text-violet-400" />Edit User — {editUser.email}</h3>
            <button className="btn-ghost text-xs" onClick={() => setEditUser(null)}>✕ Close</button>
          </div>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div><label className="block text-xs text-muted-foreground mb-1">Full Name</label><input className="input-field w-full" value={editForm.full_name} onChange={(e) => setEditForm((f) => ({ ...f, full_name: e.target.value }))} /></div>
            <div><label className="block text-xs text-muted-foreground mb-1">Email</label><input className="input-field w-full" type="email" value={editForm.email} onChange={(e) => setEditForm((f) => ({ ...f, email: e.target.value }))} /></div>
            <div>
              <label className="block text-xs text-muted-foreground mb-1">Role</label>
              <select className="input-field w-full" value={editForm.role} onChange={(e) => setEditForm((f) => ({ ...f, role: e.target.value }))}>
                {['admin', 'manager', 'client', 'influencer'].map((r) => <option key={r} value={r} className="capitalize">{r}</option>)}
              </select>
            </div>
            <div className="flex flex-col gap-2 justify-center pt-4">
              <label className="flex items-center gap-2 text-sm cursor-pointer select-none">
                <input type="checkbox" className="accent-primary w-4 h-4" checked={editForm.is_active} onChange={(e) => setEditForm((f) => ({ ...f, is_active: e.target.checked }))} />
                <span className="text-muted-foreground text-xs">Account Active</span>
              </label>
              <label className="flex items-center gap-2 text-sm cursor-pointer select-none">
                <input type="checkbox" className="accent-primary w-4 h-4" checked={editForm.is_verified} onChange={(e) => setEditForm((f) => ({ ...f, is_verified: e.target.checked }))} />
                <span className="text-muted-foreground text-xs">Email Verified</span>
              </label>
            </div>
          </div>
          <div className="flex gap-3">
            <button className="btn-primary flex items-center gap-2 disabled:opacity-50 text-sm" onClick={() => updateMutation.mutate({ id: editUser.id, payload: editForm })} disabled={updateMutation.isPending}>
              {updateMutation.isPending ? <Loader2 className="h-4 w-4 animate-spin" /> : <Settings className="h-4 w-4" />}Save Changes
            </button>
            <button className="btn-ghost text-sm" onClick={() => setEditUser(null)}>Cancel</button>
          </div>
          {updateMutation.isSuccess && (
            <div className="space-y-1">
              <p className="text-xs text-emerald-400 flex items-center gap-1"><CheckCircle2 className="h-3.5 w-3.5" />User updated successfully</p>
              <p className="text-xs text-amber-400/80">Role or status changes take effect the next time the user signs in.</p>
            </div>
          )}
          {updateMutation.isError && <p className="text-xs text-rose-400">Failed to update user. Please try again.</p>}
        </div>
      )}

      <div className="glass-card overflow-hidden">
        <table className="w-full">
          <thead className="border-b border-border">
            <tr>
              <th className="table-header text-left p-4">Name</th>
              <th className="table-header text-left p-4">Email</th>
              <th className="table-header text-left p-4">Role</th>
              <th className="table-header text-left p-4">Status</th>
              <th className="table-header text-left p-4">Actions</th>
            </tr>
          </thead>
          <tbody>
            {isLoading ? Array.from({ length: 5 }).map((_, i) => (
              <tr key={i} className="table-row"><td colSpan={5} className="p-4"><div className="h-5 bg-muted/40 rounded animate-pulse" /></td></tr>
            )) : (filtered ?? []).map((user) => (
              <tr key={user.id} className={`table-row ${editUser?.id === user.id ? 'bg-violet-400/5' : ''}`}>
                <td className="p-4"><span className="font-medium text-sm">{user.full_name}</span></td>
                <td className="p-4 text-sm text-muted-foreground">{user.email}</td>
                <td className="p-4">
                  <span className={`text-xs px-2 py-0.5 rounded-full font-medium ${ROLE_COLORS[user.role] ?? 'bg-muted text-muted-foreground'}`}>{user.role}</span>
                </td>
                <td className="p-4">
                  <span className={`text-xs px-2 py-0.5 rounded-full font-medium ${user.is_active ? 'bg-emerald-400/10 text-emerald-400' : 'bg-rose-400/10 text-rose-400'}`}>
                    {user.is_active ? 'Active' : 'Inactive'}
                  </span>
                </td>
                <td className="p-4">
                  <div className="flex items-center gap-1">
                    <button onClick={() => openEdit(user)} className="p-1.5 rounded hover:bg-violet-400/10 text-muted-foreground hover:text-violet-400 transition-colors" title="Edit user">
                      <Edit3 className="h-3.5 w-3.5" />
                    </button>
                    <button onClick={() => deactivateMutation.mutate(user.id)} className="p-1.5 rounded hover:bg-rose-400/10 text-muted-foreground hover:text-rose-400 transition-colors" title="Deactivate">
                      <Trash2 className="h-3.5 w-3.5" />
                    </button>
                  </div>
                </td>
              </tr>
            ))}
            {!isLoading && filtered?.length === 0 && (
              <tr><td colSpan={5} className="p-8 text-center text-muted-foreground text-sm">No users found.</td></tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  )
}

// ── Feature Flags Tab ────────────────────────────────────────────────────
function FeatureFlagsTab() {
  const qc = useQueryClient()
  const [showCreate, setShowCreate] = useState(false)
  const [newFlag, setNewFlag] = useState({ flag_key: '', flag_name: '', description: '', is_enabled: true })

  const { data: flags, isLoading } = useQuery({
    queryKey: ['admin-feature-flags'],
    // backend returns plain array, not paginated
    queryFn: async () => { const { data } = await api.get('/admin/feature-flags'); return data as FeatureFlag[] },
  })

  const toggleMutation = useMutation({
    mutationFn: async ({ id, is_enabled }: { id: number; is_enabled: boolean }) => {
      const { data } = await api.patch(`/admin/feature-flags/${id}`, { is_enabled })
      return data
    },
    onSuccess: () => qc.invalidateQueries({ queryKey: ['admin-feature-flags'] }),
  })

  const createMutation = useMutation({
    mutationFn: async () => { const { data } = await api.post('/admin/feature-flags', newFlag); return data },
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['admin-feature-flags'] })
      setShowCreate(false)
      setNewFlag({ flag_key: '', flag_name: '', description: '', is_enabled: true })
    },
  })

  const deleteMutation = useMutation({
    mutationFn: async (id: number) => { await api.delete(`/admin/feature-flags/${id}`) },
    onSuccess: () => qc.invalidateQueries({ queryKey: ['admin-feature-flags'] }),
  })

  const rolesLabel = (roles: FeatureFlag['enabled_for_roles']) => {
    if (!roles) return null
    if (Array.isArray(roles)) return roles.join(', ')
    return Object.entries(roles).filter(([, v]) => v).map(([k]) => k).join(', ')
  }

  return (
    <div className="space-y-4">
      <div className="flex justify-end">
        <button className="btn-primary flex items-center gap-2 text-sm" onClick={() => setShowCreate(!showCreate)}>
          <Plus className="h-4 w-4" />New Flag
        </button>
      </div>

      {showCreate && (
        <div className="glass-card p-5 space-y-4">
          <h3 className="text-sm font-semibold">Create Feature Flag</h3>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div><label className="block text-xs text-muted-foreground mb-1">Flag Key</label><input className="input-field w-full font-mono text-sm" placeholder="ai_matching_enabled" value={newFlag.flag_key} onChange={(e) => setNewFlag((f) => ({ ...f, flag_key: e.target.value }))} /></div>
            <div><label className="block text-xs text-muted-foreground mb-1">Display Name</label><input className="input-field w-full text-sm" placeholder="AI Matching" value={newFlag.flag_name} onChange={(e) => setNewFlag((f) => ({ ...f, flag_name: e.target.value }))} /></div>
            <div className="sm:col-span-2"><label className="block text-xs text-muted-foreground mb-1">Description</label><input className="input-field w-full text-sm" placeholder="Optional description..." value={newFlag.description} onChange={(e) => setNewFlag((f) => ({ ...f, description: e.target.value }))} /></div>
          </div>
          <div className="flex items-center gap-3">
            <label className="flex items-center gap-2 text-sm cursor-pointer select-none">
              <input type="checkbox" className="accent-primary w-4 h-4" checked={newFlag.is_enabled} onChange={(e) => setNewFlag((f) => ({ ...f, is_enabled: e.target.checked }))} />
              <span className="text-muted-foreground text-xs">Enabled by default</span>
            </label>
          </div>
          <div className="flex gap-3">
            <button className="btn-primary flex items-center gap-2 disabled:opacity-50 text-sm" onClick={() => createMutation.mutate()} disabled={!newFlag.flag_key || !newFlag.flag_name || createMutation.isPending}>
              {createMutation.isPending ? <Loader2 className="h-4 w-4 animate-spin" /> : <Plus className="h-4 w-4" />}Create
            </button>
            <button className="btn-ghost text-sm" onClick={() => setShowCreate(false)}>Cancel</button>
          </div>
        </div>
      )}

      <div className="space-y-3">
        {isLoading && Array.from({ length: 5 }).map((_, i) => <div key={i} className="glass-card h-20 animate-pulse" />)}
        {(flags ?? []).map((flag) => (
          <div key={flag.id} className="glass-card-hover p-4 flex items-center justify-between gap-4">
            <div className="flex-1 min-w-0">
              <div className="flex items-center gap-2 mb-0.5 flex-wrap">
                <span className="font-medium text-sm">{flag.flag_name}</span>
                <code className="text-xs bg-muted px-1.5 py-0.5 rounded text-muted-foreground">{flag.flag_key}</code>
                <span className={`text-xs px-1.5 py-0.5 rounded-full font-medium ${flag.is_enabled ? 'bg-emerald-400/10 text-emerald-400' : 'bg-slate-400/10 text-slate-400'}`}>
                  {flag.is_enabled ? 'Enabled' : 'Disabled'}
                </span>
              </div>
              {flag.description && <p className="text-xs text-muted-foreground">{flag.description}</p>}
              {flag.enabled_for_roles && rolesLabel(flag.enabled_for_roles) && (
                <p className="text-xs text-muted-foreground/60 mt-0.5">Roles: {rolesLabel(flag.enabled_for_roles)}</p>
              )}
            </div>
            <div className="flex items-center gap-2 shrink-0">
              <button
                onClick={() => toggleMutation.mutate({ id: flag.id, is_enabled: !flag.is_enabled })}
                className={`transition-colors ${flag.is_enabled ? 'text-emerald-400 hover:text-emerald-300' : 'text-muted-foreground hover:text-foreground'}`}
                title={flag.is_enabled ? 'Disable' : 'Enable'}
              >
                {flag.is_enabled ? <ToggleRight className="h-7 w-7" /> : <ToggleLeft className="h-7 w-7" />}
              </button>
              <button onClick={() => deleteMutation.mutate(flag.id)} className="p-1.5 rounded hover:bg-rose-400/10 text-muted-foreground hover:text-rose-400 transition-colors" title="Delete flag">
                <Trash2 className="h-3.5 w-3.5" />
              </button>
            </div>
          </div>
        ))}
        {!isLoading && (flags ?? []).length === 0 && (
          <div className="text-center py-8 text-muted-foreground">
            <Flag className="h-10 w-10 mx-auto mb-3 opacity-30" />
            <p className="text-sm">No feature flags configured. Create one above.</p>
          </div>
        )}
      </div>
    </div>
  )
}

// ── Audit Logs Tab ───────────────────────────────────────────────────────
function AuditLogsTab() {
  const [actionFilter, setActionFilter] = useState('')

  const { data: logs, isLoading } = useQuery({
    queryKey: ['admin-audit-logs', actionFilter],
    queryFn: async () => {
      const params = new URLSearchParams({ limit: '50' })
      if (actionFilter) params.set('action', actionFilter)
      const { data } = await api.get(`/admin/audit-logs?${params}`)
      return data as { items: AuditLogEntry[]; total: number }
    },
  })

  return (
    <div className="space-y-4">
      <div className="flex gap-3">
        <input className="input-field flex-1" placeholder="Filter by action (e.g. user.created)..." value={actionFilter} onChange={(e) => setActionFilter(e.target.value)} />
      </div>
      <div className="glass-card overflow-hidden">
        <table className="w-full">
          <thead className="border-b border-border">
            <tr>
              <th className="table-header text-left p-4">Timestamp</th>
              <th className="table-header text-left p-4">User</th>
              <th className="table-header text-left p-4">Action</th>
              <th className="table-header text-left p-4">Resource</th>
              <th className="table-header text-left p-4">IP</th>
            </tr>
          </thead>
          <tbody>
            {isLoading ? Array.from({ length: 8 }).map((_, i) => (
              <tr key={i} className="table-row"><td colSpan={5} className="p-4"><div className="h-4 bg-muted/40 rounded animate-pulse" /></td></tr>
            )) : (logs?.items ?? []).map((log) => (
              <tr key={log.id} className="table-row text-sm">
                <td className="p-4 text-muted-foreground text-xs">{format(new Date(log.created_at), 'MMM d, HH:mm')}</td>
                <td className="p-4 text-foreground truncate max-w-36">{log.user_email}</td>
                <td className="p-4"><code className="text-xs bg-muted px-1.5 py-0.5 rounded text-violet-400">{log.action}</code></td>
                <td className="p-4 text-muted-foreground text-xs">{log.resource_type}{log.resource_id ? ` #${log.resource_id}` : ''}</td>
                <td className="p-4 text-muted-foreground text-xs">{log.ip_address ?? '—'}</td>
              </tr>
            ))}
            {!isLoading && logs?.items.length === 0 && (
              <tr><td colSpan={5} className="p-8 text-center text-muted-foreground text-sm">No audit logs yet.</td></tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  )
}

// ── Main Page ────────────────────────────────────────────────────────────
// ── AI Engine Tab ─────────────────────────────────────────────────────────
function AIEngineTab() {
  const qc = useQueryClient()
  const [saved, setSaved] = useState(false)
  const [selectedProvider, setSelectedProvider] = useState<string>('')
  const [selectedModel, setSelectedModel] = useState<string>('')
  const [initialized, setInitialized] = useState(false)

  const { data, isLoading } = useQuery({
    queryKey: ['admin-ai-providers'],
    queryFn: async () => {
      const { data } = await api.get<AIProvidersResponse>('/admin/ai-providers')
      return data
    },
  })

  // Initialize local state from server data once
  if (!isLoading && !initialized && data) {
    setSelectedProvider(data.active_provider)
    setSelectedModel(data.active_model)
    setInitialized(true)
  }

  const activeProviderInfo = data?.providers.find(p => p.id === selectedProvider)

  const saveMutation = useMutation({
    mutationFn: async () => {
      const { data: result } = await api.patch('/admin/settings', {
        ai_provider_override: selectedProvider,
        ai_model_override: selectedModel,
      })
      return result
    },
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['admin-ai-providers'] })
      qc.invalidateQueries({ queryKey: ['admin-settings'] })
      setSaved(true)
      setTimeout(() => setSaved(false), 3000)
    },
  })

  const handleProviderChange = (pid: string) => {
    setSelectedProvider(pid)
    const info = data?.providers.find(p => p.id === pid)
    if (info) setSelectedModel(info.default_model)
  }

  const PROVIDER_ICONS: Record<string, string> = {
    claude: '🧠',
    gemini: '♊',
    openai: '🤖',
  }

  const PROVIDER_COLORS: Record<string, string> = {
    claude: 'border-violet-500/40 bg-violet-500/10',
    gemini: 'border-cyan-500/40 bg-cyan-500/10',
    openai: 'border-emerald-500/40 bg-emerald-500/10',
  }

  const PROVIDER_TEXT: Record<string, string> = {
    claude: 'text-violet-400',
    gemini: 'text-cyan-400',
    openai: 'text-emerald-400',
  }

  if (isLoading) return <div className="glass-card p-8 animate-pulse h-64" />

  return (
    <div className="space-y-6">
      {/* Provider Cards */}
      <div className="glass-card p-6 space-y-5">
        <h3 className="text-sm font-semibold flex items-center gap-2">
          <Sparkles className="h-4 w-4 text-violet-400" /> AI Engine Selection
        </h3>
        <p className="text-sm text-muted-foreground">
          Choose which AI provider powers all platform features — influencer matching, brief generation, content analysis, and AI-generated profiles.
        </p>

        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
          {data?.providers.map((provider: AIProviderInfo) => {
            const isSelected = selectedProvider === provider.id
            const icon = PROVIDER_ICONS[provider.id] ?? '🤖'
            const colorBorder = isSelected ? PROVIDER_COLORS[provider.id] : 'border-border bg-muted/20'
            const textColor = PROVIDER_TEXT[provider.id] ?? 'text-foreground'

            return (
              <button
                key={provider.id}
                onClick={() => provider.is_configured && handleProviderChange(provider.id)}
                disabled={!provider.is_configured}
                className={`relative text-left p-4 rounded-xl border-2 transition-all duration-200 ${colorBorder} ${
                  provider.is_configured ? 'cursor-pointer hover:border-opacity-70' : 'opacity-50 cursor-not-allowed'
                } ${isSelected ? 'ring-2 ring-offset-2 ring-offset-background ring-primary/30' : ''}`}
              >
                {isSelected && (
                  <span className="absolute top-2 right-2 text-xs bg-primary/20 text-primary px-2 py-0.5 rounded-full font-medium">
                    Active
                  </span>
                )}
                <div className="text-2xl mb-2">{icon}</div>
                <div className={`font-semibold text-sm ${isSelected ? textColor : 'text-foreground'}`}>
                  {provider.name}
                </div>
                <div className="flex items-center gap-1.5 mt-2">
                  {provider.is_configured ? (
                    <><CheckCircle className="h-3.5 w-3.5 text-emerald-400" /><span className="text-xs text-emerald-400">Configured</span></>
                  ) : (
                    <><XCircle className="h-3.5 w-3.5 text-rose-400" /><span className="text-xs text-rose-400">No API key</span></>
                  )}
                </div>
                <div className="text-xs text-muted-foreground mt-1">
                  {provider.models.length} model{provider.models.length !== 1 ? 's' : ''} available
                </div>
              </button>
            )
          })}
        </div>
      </div>

      {/* Model Selection */}
      {activeProviderInfo && (
        <div className="glass-card p-6 space-y-4">
          <h3 className="text-sm font-semibold flex items-center gap-2">
            <ChevronDown className="h-4 w-4 text-cyan-400" /> Model Version
          </h3>
          <p className="text-sm text-muted-foreground">
            Select the specific model version for <span className="text-foreground font-medium">{activeProviderInfo.name}</span>.
            More capable models produce better results but may be slower or more expensive.
          </p>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
            {activeProviderInfo.models.map((m: string) => (
              <button
                key={m}
                onClick={() => setSelectedModel(m)}
                className={`text-left p-3 rounded-lg border transition-colors ${
                  selectedModel === m
                    ? 'border-primary/50 bg-primary/10 text-primary'
                    : 'border-border bg-muted/20 text-muted-foreground hover:border-primary/20 hover:text-foreground'
                }`}
              >
                <div className="font-mono text-xs font-medium">{m}</div>
                {m === activeProviderInfo.default_model && (
                  <div className="text-[10px] mt-1 text-muted-foreground">Recommended</div>
                )}
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Daily Limit */}
      <div className="glass-card p-6 space-y-4">
        <h3 className="text-sm font-semibold">Active Configuration</h3>
        <div className="grid grid-cols-2 gap-4 text-sm">
          <div className="bg-muted/40 rounded-lg p-3">
            <div className="text-xs text-muted-foreground mb-1">Provider</div>
            <div className="font-medium capitalize">{selectedProvider || '—'}</div>
          </div>
          <div className="bg-muted/40 rounded-lg p-3">
            <div className="text-xs text-muted-foreground mb-1">Model</div>
            <div className="font-mono text-xs font-medium truncate">{selectedModel || '—'}</div>
          </div>
        </div>
        <p className="text-xs text-muted-foreground">
          Changes apply immediately on the current server process. On multi-worker deployments, all workers reload the config from the database on their next startup.
        </p>
      </div>

      <div className="flex items-center gap-3">
        <button
          className="btn-primary flex items-center gap-2 disabled:opacity-50"
          onClick={() => saveMutation.mutate()}
          disabled={saveMutation.isPending || !selectedProvider || !selectedModel}
        >
          {saveMutation.isPending ? <Loader2 className="h-4 w-4 animate-spin" /> : <Sparkles className="h-4 w-4" />}
          Save AI Engine
        </button>
        {saved && (
          <span className="text-sm text-emerald-400 flex items-center gap-1">
            <CheckCircle2 className="h-4 w-4" /> AI engine updated
          </span>
        )}
        {saveMutation.isError && (
          <span className="text-sm text-rose-400">Failed to save. Please try again.</span>
        )}
      </div>
    </div>
  )
}

export default function AdminPage() {
  const { user } = useAuthStore()
  const [activeTab, setActiveTab] = useState('overview')

  if (user?.role !== 'admin') {
    return (
      <div className="page-container">
        <div className="glass-card p-12 text-center">
          <Lock className="h-12 w-12 mx-auto mb-4 text-rose-400/60" />
          <h2 className="text-xl font-semibold mb-2">Access Denied</h2>
          <p className="text-muted-foreground">You need admin privileges to access this section.</p>
        </div>
      </div>
    )
  }

  const tabs = [
    { id: 'overview', label: 'Overview', icon: BarChart3 },
    { id: 'branding', label: 'Branding', icon: Palette },
    { id: 'landing', label: 'Landing Page', icon: Layout },
    { id: 'ai-engine', label: 'AI Engine', icon: Sparkles },
    { id: 'users', label: 'Users', icon: Users },
    { id: 'flags', label: 'Feature Flags', icon: Flag },
    { id: 'audit', label: 'Audit Logs', icon: ScrollText },
  ]

  return (
    <div className="page-container">
      <div className="page-header">
        <div>
          <h1 className="page-title flex items-center gap-2.5">
            <Shield className="h-6 w-6 text-rose-400" />
            <span className="gradient-text">Platform Administration</span>
          </h1>
          <p className="page-subtitle">Configure and manage your platform settings</p>
        </div>
      </div>

      <div className="flex gap-1 bg-muted/30 rounded-xl p-1 w-fit flex-wrap">
        {tabs.map(({ id, label, icon: Icon }) => (
          <button key={id} onClick={() => setActiveTab(id)}
            className={`flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-all duration-200 ${activeTab === id ? 'bg-card text-foreground shadow-sm' : 'text-muted-foreground hover:text-foreground'}`}>
            <Icon className="h-3.5 w-3.5" /><span className="hidden sm:inline">{label}</span>
          </button>
        ))}
      </div>

      {activeTab === 'overview' && <OverviewTab />}
      {activeTab === 'branding' && <BrandingTab />}
      {activeTab === 'landing' && <LandingPageTab />}
      {activeTab === 'ai-engine' && <AIEngineTab />}
      {activeTab === 'users' && <UsersTab />}
      {activeTab === 'flags' && <FeatureFlagsTab />}
      {activeTab === 'audit' && <AuditLogsTab />}
    </div>
  )
}
