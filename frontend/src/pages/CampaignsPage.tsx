import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { useState } from 'react'
import { Search, Calendar, DollarSign, Plus, Loader2 } from 'lucide-react'
import api from '@/utils/api'
import type { Campaign, Client, PaginatedResponse } from '@/types'
import { Link } from 'react-router-dom'
import { format } from 'date-fns'
import Modal from '@/components/Modal'

const STATUS_COLORS: Record<string, string> = {
  draft: 'bg-slate-400/10 text-slate-400',
  planning: 'bg-cyan-400/10 text-cyan-400',
  active: 'bg-emerald-400/10 text-emerald-400',
  paused: 'bg-amber-400/10 text-amber-400',
  completed: 'bg-violet-400/10 text-violet-400',
  cancelled: 'bg-rose-400/10 text-rose-400',
}

const CAMPAIGN_TYPES = [
  { value: 'brand_awareness', label: 'Brand Awareness' },
  { value: 'product_launch', label: 'Product Launch' },
  { value: 'event_promotion', label: 'Event Promotion' },
  { value: 'lead_generation', label: 'Lead Generation' },
  { value: 'app_install', label: 'App Install' },
  { value: 'sales', label: 'Sales' },
  { value: 'content_creation', label: 'Content Creation' },
  { value: 'affiliate', label: 'Affiliate' },
]

function CampaignCard({ campaign }: { campaign: Campaign }) {
  return (
    <Link to={`/app/campaigns/${campaign.id}`} className="glass-card-hover p-5 block">
      <div className="flex items-start justify-between gap-3 mb-3">
        <h3 className="font-semibold truncate">{campaign.name}</h3>
        <span className={`text-xs px-2.5 py-1 rounded-full font-medium shrink-0 ${STATUS_COLORS[campaign.status] ?? ''}`}>
          {campaign.status}
        </span>
      </div>
      <p className="text-sm text-muted-foreground capitalize mb-4">
        {campaign.campaign_type.replace(/_/g, ' ')}
      </p>
      <div className="grid grid-cols-2 gap-3 text-sm">
        {campaign.total_budget && (
          <div className="flex items-center gap-1.5 text-muted-foreground">
            <DollarSign size={14} />
            <span>${Number(campaign.total_budget).toLocaleString()} budget</span>
          </div>
        )}
        {campaign.start_date && (
          <div className="flex items-center gap-1.5 text-muted-foreground">
            <Calendar size={14} />
            <span>{format(new Date(campaign.start_date), 'MMM d, yyyy')}</span>
          </div>
        )}
      </div>
      {campaign.influencer_count !== undefined && (
        <div className="mt-3 pt-3 border-t border-border/40 text-xs text-muted-foreground">
          {campaign.influencer_count} influencer{campaign.influencer_count !== 1 ? 's' : ''} assigned
        </div>
      )}
    </Link>
  )
}

const emptyForm = {
  name: '', campaign_type: 'brand_awareness', client_id: '',
  description: '', total_budget: '', start_date: '', end_date: '',
}

export default function CampaignsPage() {
  const queryClient = useQueryClient()
  const [search, setSearch] = useState('')
  const [statusFilter, setStatusFilter] = useState('')
  const [showModal, setShowModal] = useState(false)
  const [form, setForm] = useState(emptyForm)
  const [formError, setFormError] = useState('')

  const { data, isLoading } = useQuery({
    queryKey: ['campaigns', statusFilter],
    queryFn: async () => {
      const params = new URLSearchParams({ limit: '50' })
      if (statusFilter) params.set('status', statusFilter)
      const { data } = await api.get<PaginatedResponse<Campaign>>(`/campaigns?${params}`)
      return data
    },
  })

  const { data: clients } = useQuery({
    queryKey: ['clients-list'],
    queryFn: async () => {
      const { data } = await api.get<PaginatedResponse<Client>>('/clients?limit=100')
      return data.items
    },
    enabled: showModal,
  })

  const createMutation = useMutation({
    mutationFn: async () => {
      const { data } = await api.post('/campaigns', {
        name: form.name,
        campaign_type: form.campaign_type,
        client_id: Number(form.client_id),
        description: form.description || undefined,
        total_budget: form.total_budget ? Number(form.total_budget) : undefined,
        start_date: form.start_date || undefined,
        end_date: form.end_date || undefined,
      })
      return data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['campaigns'] })
      setShowModal(false)
      setForm(emptyForm)
      setFormError('')
    },
    onError: (e: any) => setFormError(e?.response?.data?.detail ?? 'Failed to create campaign'),
  })

  const filtered = data?.items.filter((c) =>
    !search || c.name.toLowerCase().includes(search.toLowerCase())
  )

  const set = (k: keyof typeof emptyForm) => (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>) =>
    setForm(f => ({ ...f, [k]: e.target.value }))

  return (
    <div className="page-container">
      <div className="page-header">
        <div>
          <h1 className="page-title">Campaigns</h1>
          <p className="page-subtitle">{data?.total ?? 0} campaigns total</p>
        </div>
        <button onClick={() => setShowModal(true)} className="btn-primary flex items-center gap-2">
          <Plus size={16} /> New Campaign
        </button>
      </div>

      <div className="flex gap-3 flex-wrap">
        <div className="relative flex-1 min-w-[180px] max-w-sm">
          <Search size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground" />
          <input value={search} onChange={(e) => setSearch(e.target.value)}
            placeholder="Search campaigns..." className="input-field w-full pl-9" />
        </div>
        <select value={statusFilter} onChange={(e) => setStatusFilter(e.target.value)} className="input-field">
          <option value="">All Statuses</option>
          {['draft', 'planning', 'active', 'paused', 'completed', 'cancelled'].map((s) => (
            <option key={s} value={s} className="capitalize">{s}</option>
          ))}
        </select>
      </div>

      {isLoading ? (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-5">
          {Array.from({ length: 6 }).map((_, i) => (
            <div key={i} className="glass-card p-5 h-40 animate-pulse" />
          ))}
        </div>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-5">
          {(filtered ?? []).map((c) => <CampaignCard key={c.id} campaign={c} />)}
          {filtered?.length === 0 && (
            <div className="col-span-3 text-center py-16 text-muted-foreground">
              No campaigns found. Create your first campaign to get started.
            </div>
          )}
        </div>
      )}

      <Modal open={showModal} onClose={() => { setShowModal(false); setFormError('') }} title="New Campaign">
        <form onSubmit={(e) => { e.preventDefault(); createMutation.mutate() }} className="space-y-4">
          <div>
            <label className="block text-sm font-medium mb-1.5">Campaign Name <span className="text-rose-400">*</span></label>
            <input value={form.name} onChange={set('name')} required placeholder="e.g. Summer Launch 2026" className="input-field w-full" />
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium mb-1.5">Type <span className="text-rose-400">*</span></label>
              <select value={form.campaign_type} onChange={set('campaign_type')} className="input-field w-full" required>
                {CAMPAIGN_TYPES.map(t => <option key={t.value} value={t.value}>{t.label}</option>)}
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium mb-1.5">Client <span className="text-rose-400">*</span></label>
              <select value={form.client_id} onChange={set('client_id')} className="input-field w-full" required>
                <option value="">Select client...</option>
                {(clients ?? []).map(c => <option key={c.id} value={c.id}>{c.company_name}</option>)}
              </select>
              {!clients?.length && showModal && (
                <p className="text-xs text-amber-400 mt-1">No clients yet — add a client first.</p>
              )}
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium mb-1.5">Description</label>
            <textarea value={form.description} onChange={set('description')} rows={2}
              placeholder="Campaign goals and brief..." className="input-field w-full resize-none" />
          </div>

          <div>
            <label className="block text-sm font-medium mb-1.5">Total Budget ($)</label>
            <input type="number" min="0" value={form.total_budget} onChange={set('total_budget')}
              placeholder="10000" className="input-field w-full" />
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium mb-1.5">Start Date</label>
              <input type="date" value={form.start_date} onChange={set('start_date')} className="input-field w-full" />
            </div>
            <div>
              <label className="block text-sm font-medium mb-1.5">End Date</label>
              <input type="date" value={form.end_date} onChange={set('end_date')} className="input-field w-full" />
            </div>
          </div>

          {formError && <p className="text-destructive text-sm bg-destructive/10 px-3 py-2 rounded-lg">{formError}</p>}

          <div className="flex gap-3 pt-2">
            <button type="button" onClick={() => setShowModal(false)} className="btn-secondary flex-1">Cancel</button>
            <button type="submit" disabled={createMutation.isPending} className="btn-primary flex-1 flex items-center justify-center gap-2 disabled:opacity-50">
              {createMutation.isPending ? <><Loader2 size={16} className="animate-spin" /> Creating...</> : 'Create Campaign'}
            </button>
          </div>
        </form>
      </Modal>
    </div>
  )
}
