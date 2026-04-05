import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { useState } from 'react'
import { Search, Plus, Loader2, CheckCircle, Sparkles } from 'lucide-react'
import api from '@/utils/api'
import type { Influencer, PaginatedResponse, GenerateInfluencerRequest, GenerateInfluencerResponse } from '@/types'
import { Link, useNavigate } from 'react-router-dom'
import Modal from '@/components/Modal'
import { useAuthStore } from '@/store/authStore'

const STATUS_COLORS: Record<string, string> = {
  active: 'bg-emerald-400/10 text-emerald-400',
  pending: 'bg-amber-400/10 text-amber-400',
  inactive: 'bg-slate-400/10 text-slate-400',
  suspended: 'bg-rose-400/10 text-rose-400',
}

const NICHES = ['fashion', 'beauty', 'fitness', 'food', 'travel', 'tech', 'gaming', 'lifestyle', 'parenting', 'finance', 'music', 'art']
const PLATFORMS = ['instagram', 'tiktok', 'youtube', 'twitter', 'facebook', 'pinterest', 'linkedin']

function InfluencerCard({ influencer, onActivate }: { influencer: Influencer; onActivate?: () => void }) {
  const primaryAccount = influencer.social_accounts?.[0]
  const totalFollowers = influencer.social_accounts?.reduce(
    (sum, acc) => sum + (acc.follower_count || 0), 0
  ) ?? 0

  const fmt = (n: number) =>
    n >= 1_000_000 ? `${(n / 1_000_000).toFixed(1)}M` : n >= 1000 ? `${(n / 1000).toFixed(0)}K` : String(n)

  return (
    <div className="flex flex-col">
    <Link
      to={`/app/influencers/${influencer.id}`}
      className="glass-card-hover p-5 block"
    >
      <div className="flex items-start gap-3 mb-4">
        <div className="w-11 h-11 rounded-full bg-primary/20 flex items-center justify-center text-primary font-bold shrink-0 font-heading">
          {(primaryAccount?.username?.[0] ?? 'I').toUpperCase()}
        </div>
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 flex-wrap">
            <span className="font-medium truncate">@{primaryAccount?.username ?? `inf_${influencer.id}`}</span>
            <span className={`text-xs px-2 py-0.5 rounded-full font-medium ${STATUS_COLORS[influencer.status] ?? ''}`}>
              {influencer.status}
            </span>
            {influencer.ai_generated && (
              <span className="text-xs px-2 py-0.5 rounded-full font-medium bg-violet-400/10 text-violet-400 flex items-center gap-0.5">
                <Sparkles size={10} /> AI
              </span>
            )}
          </div>
          <p className="text-sm text-muted-foreground mt-0.5">
            {influencer.location ?? influencer.country_code ?? 'Unknown location'}
          </p>
        </div>
      </div>

      <div className="grid grid-cols-3 gap-3 text-center">
        <div>
          <div className="text-base font-bold">{fmt(totalFollowers)}</div>
          <div className="text-xs text-muted-foreground">Followers</div>
        </div>
        <div>
          <div className="text-base font-bold">
            {influencer.avg_engagement_rate ? `${(influencer.avg_engagement_rate * 100).toFixed(1)}%` : '—'}
          </div>
          <div className="text-xs text-muted-foreground">Eng. Rate</div>
        </div>
        <div>
          <div className="text-base font-bold">
            {influencer.rate_per_post ? `$${influencer.rate_per_post}` : '—'}
          </div>
          <div className="text-xs text-muted-foreground">Per Post</div>
        </div>
      </div>

      {influencer.niches && influencer.niches.length > 0 && (
        <div className="flex flex-wrap gap-1.5 mt-4">
          {influencer.niches.slice(0, 3).map((niche) => (
            <span key={niche} className="text-xs bg-muted px-2 py-0.5 rounded-full capitalize">{niche}</span>
          ))}
        </div>
      )}
    </Link>
    {influencer.status === 'pending' && onActivate && (
      <button
        onClick={() => onActivate()}
        className="mt-1 w-full text-xs flex items-center justify-center gap-1.5 py-1.5 rounded-lg bg-emerald-400/10 text-emerald-400 hover:bg-emerald-400/20 transition-colors font-medium"
      >
        <CheckCircle size={13} /> Activate Influencer
      </button>
    )}
    </div>
  )
}

const emptyForm = {
  bio: '', location: '', country_code: '', niches: [] as string[],
  platform: 'instagram', username: '',
  rate_per_post: '', rate_per_story: '', currency: 'USD',
}

const GENDERS = ['male', 'female', 'non-binary']
const AGE_RANGES = ['18-25', '25-35', '35-45']
const AI_NICHES = ['fashion', 'beauty', 'fitness', 'food', 'travel', 'tech', 'gaming', 'lifestyle', 'business', 'education', 'entertainment', 'health', 'sports']

const emptyAIForm: GenerateInfluencerRequest = {
  gender: undefined,
  age_range: undefined,
  niche: undefined,
  ethnicity: undefined,
  extra_instructions: undefined,
}

export default function InfluencersPage() {
  const queryClient = useQueryClient()
  const navigate = useNavigate()
  const { user } = useAuthStore()
  const isAdmin = user?.role === 'admin'
  const canManage = isAdmin || user?.role === 'manager'
  const [search, setSearch] = useState('')
  const [statusFilter, setStatusFilter] = useState('')
  const [showModal, setShowModal] = useState(false)
  const [showAIModal, setShowAIModal] = useState(false)
  const [aiForm, setAIForm] = useState(emptyAIForm)
  const [aiError, setAIError] = useState('')
  const [form, setForm] = useState(emptyForm)
  const [formError, setFormError] = useState('')

  const activateMutation = useMutation({
    mutationFn: (infId: number) => api.patch(`/influencers/${infId}`, { status: 'active' }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['influencers'] })
      queryClient.invalidateQueries({ queryKey: ['directory-influencers'] })
    },
  })

  const aiGenerateMutation = useMutation({
    mutationFn: async (req: GenerateInfluencerRequest) => {
      const { data } = await api.post<GenerateInfluencerResponse>('/ai/generate-influencer', req)
      return data
    },
    onSuccess: (result) => {
      queryClient.invalidateQueries({ queryKey: ['influencers'] })
      queryClient.invalidateQueries({ queryKey: ['directory-influencers'] })
      setShowAIModal(false)
      setAIForm(emptyAIForm)
      setAIError('')
      navigate(`/app/influencers/${result.influencer_id}`)
    },
    onError: (e: any) => setAIError(e?.response?.data?.detail ?? 'AI generation failed. Please try again.'),
  })

  const { data, isLoading } = useQuery({
    queryKey: ['influencers', statusFilter],
    queryFn: async () => {
      const params = new URLSearchParams({ limit: '50' })
      if (statusFilter) params.set('status', statusFilter)
      const { data } = await api.get<PaginatedResponse<Influencer>>(`/influencers?${params}`)
      return data
    },
  })

  const createMutation = useMutation({
    mutationFn: async () => {
      // 1. Create influencer profile
      const { data: inf } = await api.post('/influencers', {
        bio: form.bio || undefined,
        location: form.location || undefined,
        country_code: form.country_code || undefined,
        niches: form.niches.length ? form.niches : undefined,
        rate_per_post: form.rate_per_post ? Number(form.rate_per_post) : undefined,
        rate_per_story: form.rate_per_story ? Number(form.rate_per_story) : undefined,
        currency: form.currency,
      })
      // 2. Add social account if username provided
      if (form.username) {
        await api.post(`/influencers/${inf.id}/social-accounts`, {
          platform: form.platform,
          username: form.username,
        })
      }
      return inf
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['influencers'] })
      setShowModal(false)
      setForm(emptyForm)
      setFormError('')
    },
    onError: (e: any) => setFormError(e?.response?.data?.detail ?? 'Failed to create influencer'),
  })

  const filtered = data?.items.filter((inf) => {
    if (!search) return true
    const acc = inf.social_accounts?.[0]?.username ?? ''
    return acc.toLowerCase().includes(search.toLowerCase()) ||
      inf.location?.toLowerCase().includes(search.toLowerCase())
  })

  const toggleNiche = (n: string) =>
    setForm((f) => ({
      ...f, niches: f.niches.includes(n) ? f.niches.filter((x) => x !== n) : [...f.niches, n],
    }))

  return (
    <div className="page-container">
      <div className="page-header">
        <div>
          <h1 className="page-title">Influencers</h1>
          <p className="page-subtitle">{data?.total ?? 0} influencers in your roster</p>
        </div>
        <div className="flex gap-2">
          {isAdmin && (
            <button onClick={() => setShowAIModal(true)} className="flex items-center gap-2 px-4 py-2 rounded-lg bg-violet-500/20 text-violet-400 border border-violet-500/30 hover:bg-violet-500/30 transition-colors font-medium text-sm">
              <Sparkles size={16} /> AI Generate
            </button>
          )}
          <button onClick={() => setShowModal(true)} className="btn-primary flex items-center gap-2">
            <Plus size={16} /> Add Influencer
          </button>
        </div>
      </div>

      <div className="flex gap-3 flex-wrap">
        <div className="relative flex-1 min-w-[180px] max-w-sm">
          <Search size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground" />
          <input value={search} onChange={(e) => setSearch(e.target.value)}
            placeholder="Search by username or location..."
            className="input-field w-full pl-9" />
        </div>
        <select value={statusFilter} onChange={(e) => setStatusFilter(e.target.value)} className="input-field">
          <option value="">All Statuses</option>
          <option value="active">Active</option>
          <option value="pending">Pending</option>
          <option value="inactive">Inactive</option>
          <option value="suspended">Suspended</option>
        </select>
      </div>

      {isLoading ? (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-5">
          {Array.from({ length: 6 }).map((_, i) => (
            <div key={i} className="glass-card p-5 h-48 animate-pulse" />
          ))}
        </div>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-5">
          {(filtered ?? []).map((inf) => (
            <InfluencerCard
              key={inf.id}
              influencer={inf}
              onActivate={canManage ? () => activateMutation.mutate(inf.id) : undefined}
            />
          ))}
          {filtered?.length === 0 && (
            <div className="col-span-3 text-center py-16 text-muted-foreground">
              No influencers found. Add your first influencer to get started.
            </div>
          )}
        </div>
      )}

      {/* AI Generate Modal */}
      <Modal open={showAIModal} onClose={() => { setShowAIModal(false); setAIError('') }} title="Generate AI Influencer">
        <form onSubmit={(e) => { e.preventDefault(); aiGenerateMutation.mutate(aiForm) }} className="space-y-4">
          <p className="text-sm text-muted-foreground">
            Generate a complete AI influencer profile with social accounts, portfolio images, and demographics. Optionally specify preferences below.
          </p>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium mb-1.5">Gender</label>
              <select value={aiForm.gender ?? ''} onChange={(e) => setAIForm(f => ({ ...f, gender: e.target.value || undefined }))} className="input-field w-full">
                <option value="">Any</option>
                {GENDERS.map(g => <option key={g} value={g} className="capitalize">{g}</option>)}
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium mb-1.5">Age Range</label>
              <select value={aiForm.age_range ?? ''} onChange={(e) => setAIForm(f => ({ ...f, age_range: e.target.value || undefined }))} className="input-field w-full">
                <option value="">Any</option>
                {AGE_RANGES.map(r => <option key={r} value={r}>{r}</option>)}
              </select>
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium mb-1.5">Primary Niche</label>
            <select value={aiForm.niche ?? ''} onChange={(e) => setAIForm(f => ({ ...f, niche: e.target.value || undefined }))} className="input-field w-full">
              <option value="">Any</option>
              {AI_NICHES.map(n => <option key={n} value={n} className="capitalize">{n}</option>)}
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium mb-1.5">Ethnicity (optional)</label>
            <input
              value={aiForm.ethnicity ?? ''}
              onChange={(e) => setAIForm(f => ({ ...f, ethnicity: e.target.value || undefined }))}
              placeholder="e.g. East Asian, Scandinavian..."
              className="input-field w-full"
            />
          </div>

          <div>
            <label className="block text-sm font-medium mb-1.5">Extra Creative Direction (optional)</label>
            <textarea
              value={aiForm.extra_instructions ?? ''}
              onChange={(e) => setAIForm(f => ({ ...f, extra_instructions: e.target.value || undefined }))}
              rows={2}
              placeholder="e.g. edgy street style, luxury aesthetic, outdoorsy..."
              className="input-field w-full resize-none"
            />
          </div>

          {aiError && (
            <p className="text-destructive text-sm bg-destructive/10 px-3 py-2 rounded-lg">{aiError}</p>
          )}

          <div className="flex gap-3 pt-2">
            <button type="button" onClick={() => setShowAIModal(false)} className="btn-secondary flex-1">Cancel</button>
            <button type="submit" disabled={aiGenerateMutation.isPending} className="flex-1 flex items-center justify-center gap-2 px-4 py-2 rounded-lg bg-violet-500 text-white hover:bg-violet-600 transition-colors font-medium text-sm disabled:opacity-50">
              {aiGenerateMutation.isPending ? <><Loader2 size={16} className="animate-spin" /> Generating...</> : <><Sparkles size={16} /> Generate Influencer</>}
            </button>
          </div>
        </form>
      </Modal>

      <Modal open={showModal} onClose={() => { setShowModal(false); setFormError('') }} title="Add Influencer">
        <form onSubmit={(e) => { e.preventDefault(); createMutation.mutate() }} className="space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium mb-1.5">Primary Platform</label>
              <select value={form.platform} onChange={(e) => setForm(f => ({ ...f, platform: e.target.value }))} className="input-field w-full">
                {PLATFORMS.map(p => <option key={p} value={p} className="capitalize">{p}</option>)}
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium mb-1.5">Username <span className="text-rose-400">*</span></label>
              <input value={form.username} onChange={(e) => setForm(f => ({ ...f, username: e.target.value }))}
                placeholder="@handle" className="input-field w-full" required />
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium mb-1.5">Location</label>
              <input value={form.location} onChange={(e) => setForm(f => ({ ...f, location: e.target.value }))}
                placeholder="New York, USA" className="input-field w-full" />
            </div>
            <div>
              <label className="block text-sm font-medium mb-1.5">Country Code</label>
              <input value={form.country_code} onChange={(e) => setForm(f => ({ ...f, country_code: e.target.value.toUpperCase() }))}
                placeholder="US" maxLength={2} className="input-field w-full" />
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium mb-2">Niches</label>
            <div className="flex flex-wrap gap-2">
              {NICHES.map(n => (
                <button key={n} type="button"
                  onClick={() => toggleNiche(n)}
                  className={`text-xs px-3 py-1 rounded-full border transition-colors capitalize ${
                    form.niches.includes(n) ? 'bg-primary/20 border-primary/50 text-primary' : 'border-border text-muted-foreground hover:border-primary/30'
                  }`}>{n}</button>
              ))}
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium mb-1.5">Rate / Post ($)</label>
              <input type="number" min="0" value={form.rate_per_post}
                onChange={(e) => setForm(f => ({ ...f, rate_per_post: e.target.value }))}
                placeholder="500" className="input-field w-full" />
            </div>
            <div>
              <label className="block text-sm font-medium mb-1.5">Rate / Story ($)</label>
              <input type="number" min="0" value={form.rate_per_story}
                onChange={(e) => setForm(f => ({ ...f, rate_per_story: e.target.value }))}
                placeholder="200" className="input-field w-full" />
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium mb-1.5">Bio</label>
            <textarea value={form.bio} onChange={(e) => setForm(f => ({ ...f, bio: e.target.value }))}
              rows={2} placeholder="Short bio about the influencer..." className="input-field w-full resize-none" />
          </div>

          {formError && (
            <p className="text-destructive text-sm bg-destructive/10 px-3 py-2 rounded-lg">{formError}</p>
          )}

          <div className="flex gap-3 pt-2">
            <button type="button" onClick={() => setShowModal(false)} className="btn-secondary flex-1">Cancel</button>
            <button type="submit" disabled={createMutation.isPending} className="btn-primary flex-1 flex items-center justify-center gap-2 disabled:opacity-50">
              {createMutation.isPending ? <><Loader2 size={16} className="animate-spin" /> Adding...</> : 'Add Influencer'}
            </button>
          </div>
        </form>
      </Modal>
    </div>
  )
}
