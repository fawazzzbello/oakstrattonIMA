import { useQuery } from '@tanstack/react-query'
import { useState } from 'react'
import {
  FileText,
  Plus,
  Search,
  ChevronDown,
  ChevronRight,
  Eye,
  Clock,
  CheckCircle2,
  Send,
  XCircle,
  AlertCircle,
  FileSignature,
} from 'lucide-react'
import api from '@/utils/api'
import { format } from 'date-fns'

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
    case 'draft':
      return { class: 'status-badge bg-slate-400/10 text-slate-400', icon: FileText, label: 'Draft' }
    case 'sent':
      return { class: 'status-badge bg-cyan-400/10 text-cyan-400', icon: Send, label: 'Sent' }
    case 'signed_influencer':
      return { class: 'status-pending', icon: Clock, label: 'Pending Agency' }
    case 'signed_agency':
      return { class: 'status-pending', icon: Clock, label: 'Pending Influencer' }
    case 'fully_executed':
      return { class: 'status-active', icon: CheckCircle2, label: 'Executed' }
    case 'voided':
      return { class: 'status-cancelled', icon: XCircle, label: 'Voided' }
    case 'expired':
      return { class: 'status-cancelled', icon: AlertCircle, label: 'Expired' }
    default:
      return { class: 'status-badge bg-muted text-muted-foreground', icon: FileText, label: status }
  }
}

const TEMPLATE_LIST = [
  { name: 'Standard Influencer Agreement', description: 'General-purpose contract for influencer campaigns', type: 'Standard' },
  { name: 'Content License Agreement', description: 'License for repurposing influencer-created content', type: 'License' },
  { name: 'Exclusivity Agreement', description: 'Non-compete and exclusivity terms', type: 'Exclusivity' },
  { name: 'Affiliate Partnership', description: 'Revenue-sharing affiliate arrangement', type: 'Affiliate' },
]

export default function ContractsPage() {
  const [activeFilter, setActiveFilter] = useState('all')
  const [searchQuery, setSearchQuery] = useState('')
  const [templatesExpanded, setTemplatesExpanded] = useState(false)

  const { data, isLoading, error } = useQuery({
    queryKey: ['contracts'],
    queryFn: async () => {
      const { data } = await api.get('/contracts?limit=100')
      return data as { items: any[]; total: number }
    },
  })

  const contracts = (data?.items ?? []).filter((c: any) => {
    const matchFilter =
      activeFilter === 'all' ||
      c.status === activeFilter ||
      (activeFilter === 'signed' && (c.status === 'signed_influencer' || c.status === 'signed_agency'))
    const matchSearch =
      !searchQuery || c.title?.toLowerCase().includes(searchQuery.toLowerCase())
    return matchFilter && matchSearch
  })

  const countByStatus = (status: string) => {
    if (status === 'all') return data?.items?.length ?? 0
    if (status === 'signed')
      return (data?.items ?? []).filter(
        (c: any) => c.status === 'signed_influencer' || c.status === 'signed_agency'
      ).length
    return (data?.items ?? []).filter((c: any) => c.status === status).length
  }

  return (
    <div className="page-container">
      {/* Header */}
      <div className="page-header">
        <div>
          <h1 className="page-title">Contracts</h1>
          <p className="page-subtitle">Track contracts and agreements</p>
        </div>
        <button className="btn-primary flex items-center gap-2">
          <Plus size={16} />
          New Contract
        </button>
      </div>

      {/* Filter Tabs */}
      <div className="flex flex-col sm:flex-row gap-3 sm:items-center sm:justify-between">
        <div className="flex gap-1 bg-muted/30 rounded-lg p-1 flex-wrap">
          {FILTER_TABS.map((tab) => (
            <button
              key={tab.key}
              onClick={() => setActiveFilter(tab.key)}
              className={`px-3 py-1.5 rounded-md text-xs font-medium transition-colors ${
                activeFilter === tab.key
                  ? 'bg-primary/20 text-primary'
                  : 'text-muted-foreground hover:text-foreground'
              }`}
            >
              {tab.label}
              <span className="ml-1.5 text-[10px] opacity-60">{countByStatus(tab.key)}</span>
            </button>
          ))}
        </div>

        <div className="relative max-w-xs w-full">
          <Search
            size={14}
            className="absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground"
          />
          <input
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search contracts..."
            className="input-field w-full pl-9 py-2 text-sm"
          />
        </div>
      </div>

      {/* Error */}
      {error && (
        <div className="glass-card p-6 text-center">
          <p className="text-rose-400">Failed to load contracts.</p>
        </div>
      )}

      {/* Contracts Table */}
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
                <th className="text-left px-5 py-3">Effective Date</th>
                <th className="text-left px-5 py-3">Expiry</th>
                <th className="text-left px-5 py-3">Actions</th>
              </tr>
            </thead>
            <tbody>
              {isLoading
                ? Array.from({ length: 5 }).map((_, i) => (
                    <tr key={i} className="table-row">
                      {Array.from({ length: 8 }).map((_, j) => (
                        <td key={j} className="px-5 py-4">
                          <div className="h-4 bg-muted rounded animate-pulse" />
                        </td>
                      ))}
                    </tr>
                  ))
                : contracts.map((contract: any) => {
                    const badge = statusBadge(contract.status)
                    const BadgeIcon = badge.icon
                    return (
                      <tr key={contract.id} className="table-row">
                        <td className="px-5 py-4">
                          <div className="flex items-center gap-2">
                            <FileSignature size={14} className="text-violet-400 flex-shrink-0" />
                            <span className="font-medium text-foreground">{contract.title}</span>
                          </div>
                        </td>
                        <td className="px-5 py-4 text-muted-foreground">
                          {contract.influencer_name ?? `#${contract.influencer_id ?? '—'}`}
                        </td>
                        <td className="px-5 py-4 text-muted-foreground">
                          {contract.campaign_name ?? `#${contract.campaign_id ?? '—'}`}
                        </td>
                        <td className="px-5 py-4 font-medium">
                          {contract.total_fee
                            ? `$${Number(contract.total_fee).toLocaleString()}`
                            : '—'}
                        </td>
                        <td className="px-5 py-4">
                          <span className={badge.class}>
                            <BadgeIcon size={12} className="mr-1" />
                            {badge.label}
                          </span>
                        </td>
                        <td className="px-5 py-4 text-muted-foreground">
                          {contract.effective_date
                            ? format(new Date(contract.effective_date), 'MMM d, yyyy')
                            : '—'}
                        </td>
                        <td className="px-5 py-4 text-muted-foreground">
                          {contract.expiry_date
                            ? format(new Date(contract.expiry_date), 'MMM d, yyyy')
                            : '—'}
                        </td>
                        <td className="px-5 py-4">
                          <button className="btn-ghost text-xs flex items-center gap-1 px-2 py-1">
                            <Eye size={13} />
                            View
                          </button>
                        </td>
                      </tr>
                    )
                  })}
              {!isLoading && contracts.length === 0 && (
                <tr>
                  <td colSpan={8} className="px-5 py-16 text-center">
                    <FileText size={36} className="mx-auto text-muted-foreground mb-3" />
                    <p className="text-muted-foreground">No contracts found.</p>
                    <p className="text-sm text-muted-foreground mt-1">
                      Create your first contract to get started.
                    </p>
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Contract Templates Section */}
      <div className="glass-card overflow-hidden">
        <button
          onClick={() => setTemplatesExpanded(!templatesExpanded)}
          className="w-full flex items-center justify-between px-6 py-4 hover:bg-muted/20 transition-colors"
        >
          <div className="flex items-center gap-3">
            <FileText size={18} className="text-violet-400" />
            <div className="text-left">
              <h3 className="font-semibold text-foreground">Contract Templates</h3>
              <p className="text-xs text-muted-foreground">
                {TEMPLATE_LIST.length} templates available
              </p>
            </div>
          </div>
          {templatesExpanded ? (
            <ChevronDown size={18} className="text-muted-foreground" />
          ) : (
            <ChevronRight size={18} className="text-muted-foreground" />
          )}
        </button>

        {templatesExpanded && (
          <div className="border-t border-border/40 px-6 py-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
              {TEMPLATE_LIST.map((template) => (
                <div
                  key={template.name}
                  className="flex items-center justify-between p-4 rounded-lg bg-muted/20 border border-border/30 hover:border-primary/30 transition-colors"
                >
                  <div>
                    <h4 className="text-sm font-medium text-foreground">{template.name}</h4>
                    <p className="text-xs text-muted-foreground mt-0.5">{template.description}</p>
                  </div>
                  <span className="status-badge bg-violet-400/10 text-violet-400 text-[10px]">
                    {template.type}
                  </span>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
