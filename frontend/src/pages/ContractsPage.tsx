import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { useState } from 'react'
import {
  FileText, Plus, Search, ChevronDown, ChevronRight,
  Eye, Clock, CheckCircle2, Send, XCircle, AlertCircle, FileSignature, Loader2,
} from 'lucide-react'
import api from '@/utils/api'
import { format } from 'date-fns'
import Modal from '@/components/Modal'
import type { Influencer, Campaign, PaginatedResponse } from '@/types'

const FILTER_TABS = [
  { key: 'all', label: 'All' },
  { key: 'draft', label: 'Draft' },
  { key: 'sent', label: 'Sent' },
  { key: 'signed', label: 'Signed' },
  { key: 'fully_executed', label: 'Executed' },
  { key: 'expired', label: 'Expired' },
] as const

function statusBadge(status: string) {
  switch (status) {
    case 'draft': return { cls: 'status-badge bg-slate-400/10 text-slate-400', Icon: FileText, label: 'Draft' }
    case 'sent': return { cls: 'status-badge bg-cyan-400/10 text-cyan-400', Icon: Send, label: 'Sent' }
    case 'signed_influencer': return { cls: 'status-pending', Icon: Clock, label: 'Pending Agency' }
    case 'signed_agency': return { cls: 'status-pending', Icon: Clock, label: 'Pending Influencer' }
    case 'fully_executed': return { cls: 'status-active', Icon: CheckCircle2, label: 'Executed' }
    case 'voided': return { cls: 'status-cancelled', Icon: XCircle, label: 'Voided' }
    case 'expired': return { cls: 'status-cancelled', Icon: AlertCircle, label: 'Expired' }
    default: return { cls: 'status-badge bg-muted text-muted-foreground', Icon: FileText, label: status }
  }
}

const emptyForm = {
  title: '', influencer_id: '', campaign_id: '',
  total_fee: '', currency: 'USD',
  effective_date: '', expiration_date: '',
  exclusivity_clause: false,
}

export default function ContractsPage() {
  const queryClient = useQueryClient()
  const [activeFilter, setActiveFilter] = useState('all')
  const [searchQuery, setSearchQuery] = useState('')
  const [templatesExpanded, setTemplatesExpanded] = useState(false)
  const [showModal, setShowModal] = useState(false)
  const [viewContract, setViewContract] = useState<any>(null)
  const [form, setForm] = useState(emptyForm)
  const [formError, setFormError] = useState('')

  const { data, isLoading, error } = useQuery({
    queryKey: ['contracts'],
    queryFn: async () => {
      const { data } = await api.get('/contracts?limit=100')
      return data as { items: any[]; total: number }
    },
  })

  const { data: influencers } = useQuery({
    queryKey: ['influencers-list'],
    queryFn: async () => {
      const { data } = await api.get<PaginatedResponse<Influencer>>('/influencers?limit=100')
      return data.items
    },
    enabled: showModal,
  })

  const { data: campaigns } = useQuery({
    queryKey: ['campaigns-list'],
    queryFn: async () => {
      const { data } = await api.get<PaginatedResponse<Campaign>>('/campaigns?limit=100')
      return data.items
    },
    enabled: showModal,
  })

  const createMutation = useMutation({
    mutationFn: async () => {
      const { data } = await api.post('/contracts', {
        title: form.title,
        influencer_id: Number(form.influencer_id),
        campaign_id: Number(form.campaign_id),
        total_fee: form.total_fee ? Number(form.total_fee) : undefined,
        currency: form.currency,
        effective_date: form.effective_date || undefined,
        expiration_date: form.expiration_date || undefined,
        exclusivity_clause: form.exclusivity_clause,
      })
      return data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['contracts'] })
      setShowModal(false)
      setForm(emptyForm)
      setFormError('')
    },
    onError: (e: any) => setFormError(e?.response?.data?.detail ?? 'Failed to create contract'),
  })

  const sendMutation = useMutation({
    mutationFn: (id: number) => api.post(`/contracts/${id}/sign`, { signer: 'agency' }),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['contracts'] }),
  })

  const contracts = (data?.items ?? []).filter((c: any) => {
    const matchFilter = activeFilter === 'all' ||
      c.status === activeFilter ||
      (activeFilter === 'signed' && (c.status === 'signed_influencer' || c.status === 'signed_agency'))
    const matchSearch = !searchQuery || c.title?.toLowerCase().includes(searchQuery.toLowerCase())
    return matchFilter && matchSearch
  })

  const countByStatus = (s: string) => {
    if (s === 'all') return data?.items?.length ?? 0
    if (s === 'signed') return (data?.items ?? []).filter((c: any) => c.status === 'signed_influencer' || c.status === 'signed_agency').length
    return (data?.items ?? []).filter((c: any) => c.status === s).length
  }

  const set = (k: keyof typeof emptyForm) =>
    (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) =>
      setForm(f => ({ ...f, [k]: e.target.type === 'checkbox' ? (e.target as HTMLInputElement).checked : e.target.value }))

  return (
    <div className="page-container">
      <div className="page-header">
        <div>
          <h1 className="page-title">Contracts</h1>
          <p className="page-subtitle">Track contracts and agreements</p>
        </div>
        <button onClick={() => setShowModal(true)} className="btn-primary flex items-center gap-2">
          <Plus size={16} /> New Contract
        </button>
      </div>

      <div className="flex flex-col sm:flex-row gap-3 sm:items-center sm:justify-between">
        <div className="flex gap-1 bg-muted/30 rounded-lg p-1 flex-wrap">
          {FILTER_TABS.map((tab) => (
            <button key={tab.key} onClick={() => setActiveFilter(tab.key)}
              className={`px-3 py-1.5 rounded-md text-xs font-medium transition-colors ${
                activeFilter === tab.key ? 'bg-primary/20 text-primary' : 'text-muted-foreground hover:text-foreground'
              }`}>
              {tab.label}
              <span className="ml-1.5 text-[10px] opacity-60">{countByStatus(tab.key)}</span>
            </button>
          ))}
        </div>
        <div className="relative max-w-xs w-full">
          <Search size={14} className="absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground" />
          <input value={searchQuery} onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search contracts..." className="input-field w-full pl-9 py-2 text-sm" />
        </div>
      </div>

      {error && <div className="glass-card p-6 text-center"><p className="text-rose-400">Failed to load contracts.</p></div>}

      <div className="glass-card overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="table-header border-b border-border/40">
                <th className="text-left px-5 py-3">Title</th>
                <th className="text-left px-5 py-3">Influencer</th>
                <th className="text-left px-5 py-3">Campaign</th>
                <th className="text-left px-5 py-3">Fee</th>
                <th className="text-left px-5 py-3">Status</th>
                <th className="text-left px-5 py-3">Effective</th>
                <th className="text-left px-5 py-3">Expires</th>
                <th className="text-left px-5 py-3">Actions</th>
              </tr>
            </thead>
            <tbody>
              {isLoading
                ? Array.from({ length: 5 }).map((_, i) => (
                    <tr key={i} className="table-row">
                      {Array.from({ length: 8 }).map((_, j) => (
                        <td key={j} className="px-5 py-4"><div className="h-4 bg-muted rounded animate-pulse" /></td>
                      ))}
                    </tr>
                  ))
                : contracts.map((contract: any) => {
                    const badge = statusBadge(contract.status)
                    const BadgeIcon = badge.Icon
                    return (
                      <tr key={contract.id} className="table-row">
                        <td className="px-5 py-4">
                          <div className="flex items-center gap-2">
                            <FileSignature size={14} className="text-violet-400 shrink-0" />
                            <span className="font-medium text-foreground">{contract.title}</span>
                          </div>
                        </td>
                        <td className="px-5 py-4 text-muted-foreground">#{contract.influencer_id ?? '—'}</td>
                        <td className="px-5 py-4 text-muted-foreground">#{contract.campaign_id ?? '—'}</td>
                        <td className="px-5 py-4 font-medium">
                          {contract.total_fee ? `$${Number(contract.total_fee).toLocaleString()}` : '—'}
                        </td>
                        <td className="px-5 py-4">
                          <span className={badge.cls}>
                            <BadgeIcon size={12} className="mr-1 inline" />{badge.label}
                          </span>
                        </td>
                        <td className="px-5 py-4 text-muted-foreground">
                          {contract.effective_date ? format(new Date(contract.effective_date), 'MMM d, yyyy') : '—'}
                        </td>
                        <td className="px-5 py-4 text-muted-foreground">
                          {contract.expiration_date ? format(new Date(contract.expiration_date), 'MMM d, yyyy') : '—'}
                        </td>
                        <td className="px-5 py-4">
                          <div className="flex gap-2">
                            <button onClick={() => setViewContract(contract)}
                              className="btn-ghost text-xs flex items-center gap-1 px-2 py-1">
                              <Eye size={13} /> View
                            </button>
                            {contract.status === 'draft' && (
                              <button onClick={() => sendMutation.mutate(contract.id)}
                                className="text-xs text-cyan-400 hover:underline px-2 py-1">Send</button>
                            )}
                          </div>
                        </td>
                      </tr>
                    )
                  })}
              {!isLoading && contracts.length === 0 && (
                <tr>
                  <td colSpan={8} className="px-5 py-16 text-center">
                    <FileText size={36} className="mx-auto text-muted-foreground mb-3" />
                    <p className="text-muted-foreground">No contracts found.</p>
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Templates */}
      <div className="glass-card overflow-hidden">
        <button onClick={() => setTemplatesExpanded(!templatesExpanded)}
          className="w-full flex items-center justify-between px-6 py-4 hover:bg-muted/20 transition-colors">
          <div className="flex items-center gap-3">
            <FileText size={18} className="text-violet-400" />
            <div className="text-left">
              <h3 className="font-semibold text-foreground">Contract Templates</h3>
              <p className="text-xs text-muted-foreground">Standard agreements ready to use</p>
            </div>
          </div>
          {templatesExpanded ? <ChevronDown size={18} className="text-muted-foreground" /> : <ChevronRight size={18} className="text-muted-foreground" />}
        </button>
        {templatesExpanded && (
          <div className="border-t border-border/40 px-6 py-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
              {[
                { name: 'Standard Influencer Agreement', description: 'General-purpose contract for campaigns', type: 'Standard' },
                { name: 'Content License Agreement', description: 'License for repurposing influencer content', type: 'License' },
                { name: 'Exclusivity Agreement', description: 'Non-compete and exclusivity terms', type: 'Exclusivity' },
                { name: 'Affiliate Partnership', description: 'Revenue-sharing affiliate arrangement', type: 'Affiliate' },
              ].map((t) => (
                <div key={t.name}
                  className="flex items-center justify-between p-4 rounded-lg bg-muted/20 border border-border/30 hover:border-primary/30 transition-colors cursor-pointer"
                  onClick={() => { setForm(f => ({ ...f, title: t.name })); setShowModal(true) }}>
                  <div>
                    <h4 className="text-sm font-medium">{t.name}</h4>
                    <p className="text-xs text-muted-foreground mt-0.5">{t.description}</p>
                  </div>
                  <span className="status-badge bg-violet-400/10 text-violet-400 text-[10px]">{t.type}</span>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Create Modal */}
      <Modal open={showModal} onClose={() => { setShowModal(false); setFormError('') }} title="New Contract">
        <form onSubmit={(e) => { e.preventDefault(); createMutation.mutate() }} className="space-y-4">
          <div>
            <label className="block text-sm font-medium mb-1.5">Title <span className="text-rose-400">*</span></label>
            <input value={form.title} onChange={set('title')} required placeholder="e.g. Instagram Campaign Agreement" className="input-field w-full" />
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium mb-1.5">Influencer <span className="text-rose-400">*</span></label>
              <select value={form.influencer_id} onChange={set('influencer_id')} required className="input-field w-full">
                <option value="">Select influencer...</option>
                {(influencers ?? []).map(inf => (
                  <option key={inf.id} value={inf.id}>#{inf.id} — {inf.social_accounts?.[0]?.username ?? `influencer_${inf.id}`}</option>
                ))}
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium mb-1.5">Campaign <span className="text-rose-400">*</span></label>
              <select value={form.campaign_id} onChange={set('campaign_id')} required className="input-field w-full">
                <option value="">Select campaign...</option>
                {(campaigns ?? []).map(c => <option key={c.id} value={c.id}>{c.name}</option>)}
              </select>
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium mb-1.5">Total Fee ($)</label>
              <input type="number" min="0" value={form.total_fee} onChange={set('total_fee')} placeholder="2500" className="input-field w-full" />
            </div>
            <div>
              <label className="block text-sm font-medium mb-1.5">Currency</label>
              <select value={form.currency} onChange={set('currency')} className="input-field w-full">
                {['USD', 'EUR', 'GBP', 'CAD', 'AUD'].map(c => <option key={c}>{c}</option>)}
              </select>
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium mb-1.5">Effective Date</label>
              <input type="date" value={form.effective_date} onChange={set('effective_date')} className="input-field w-full" />
            </div>
            <div>
              <label className="block text-sm font-medium mb-1.5">Expiration Date</label>
              <input type="date" value={form.expiration_date} onChange={set('expiration_date')} className="input-field w-full" />
            </div>
          </div>

          <label className="flex items-center gap-2 text-sm cursor-pointer">
            <input type="checkbox" checked={form.exclusivity_clause}
              onChange={(e) => setForm(f => ({ ...f, exclusivity_clause: e.target.checked }))}
              className="rounded" />
            Include exclusivity clause
          </label>

          {formError && <p className="text-destructive text-sm bg-destructive/10 px-3 py-2 rounded-lg">{formError}</p>}

          <div className="flex gap-3 pt-2">
            <button type="button" onClick={() => setShowModal(false)} className="btn-secondary flex-1">Cancel</button>
            <button type="submit" disabled={createMutation.isPending} className="btn-primary flex-1 flex items-center justify-center gap-2 disabled:opacity-50">
              {createMutation.isPending ? <><Loader2 size={16} className="animate-spin" /> Creating...</> : 'Create Contract'}
            </button>
          </div>
        </form>
      </Modal>

      {/* View Modal */}
      {viewContract && (
        <Modal open={!!viewContract} onClose={() => setViewContract(null)} title={viewContract.title}>
          <div className="space-y-4 text-sm">
            <div className="grid grid-cols-2 gap-4">
              <div><p className="text-muted-foreground">Status</p>
                <p className="font-medium capitalize">{viewContract.status.replace(/_/g, ' ')}</p></div>
              <div><p className="text-muted-foreground">Total Fee</p>
                <p className="font-medium">{viewContract.total_fee ? `$${Number(viewContract.total_fee).toLocaleString()} ${viewContract.currency}` : '—'}</p></div>
              <div><p className="text-muted-foreground">Influencer ID</p>
                <p className="font-medium">#{viewContract.influencer_id}</p></div>
              <div><p className="text-muted-foreground">Campaign ID</p>
                <p className="font-medium">#{viewContract.campaign_id}</p></div>
              <div><p className="text-muted-foreground">Effective Date</p>
                <p className="font-medium">{viewContract.effective_date ? format(new Date(viewContract.effective_date), 'MMM d, yyyy') : '—'}</p></div>
              <div><p className="text-muted-foreground">Expiration Date</p>
                <p className="font-medium">{viewContract.expiration_date ? format(new Date(viewContract.expiration_date), 'MMM d, yyyy') : '—'}</p></div>
              <div><p className="text-muted-foreground">Exclusivity</p>
                <p className="font-medium">{viewContract.exclusivity_clause ? 'Yes' : 'No'}</p></div>
              <div><p className="text-muted-foreground">Created</p>
                <p className="font-medium">{format(new Date(viewContract.created_at), 'MMM d, yyyy')}</p></div>
            </div>
            {viewContract.content && (
              <div>
                <p className="text-muted-foreground mb-2">Contract Content</p>
                <div className="bg-muted/30 rounded-lg p-4 text-xs whitespace-pre-wrap max-h-48 overflow-y-auto">{viewContract.content}</div>
              </div>
            )}
          </div>
        </Modal>
      )}
    </div>
  )
}
