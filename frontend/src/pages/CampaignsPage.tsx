import { useQuery } from '@tanstack/react-query'
import { useState } from 'react'
import { Search, Calendar, DollarSign } from 'lucide-react'
import api from '@/utils/api'
import type { Campaign, PaginatedResponse } from '@/types'
import { Link } from 'react-router-dom'
import { format } from 'date-fns'

const STATUS_COLORS: Record<string, string> = {
  draft: 'bg-slate-400/10 text-slate-400',
  planning: 'bg-cyan-400/10 text-cyan-400',
  active: 'bg-emerald-400/10 text-emerald-400',
  paused: 'bg-amber-400/10 text-amber-400',
  completed: 'bg-violet-400/10 text-violet-400',
  cancelled: 'bg-rose-400/10 text-rose-400',
}

function CampaignCard({ campaign }: { campaign: Campaign }) {
  return (
    <Link
      to={`/campaigns/${campaign.id}`}
      className="bg-card rounded-xl border border-border p-5 hover:shadow-md transition-shadow block"
    >
      <div className="flex items-start justify-between gap-3 mb-3">
        <h3 className="font-semibold truncate">{campaign.name}</h3>
        <span className={`text-xs px-2.5 py-1 rounded-full font-medium shrink-0 ${STATUS_COLORS[campaign.status]}`}>
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
        <div className="mt-3 pt-3 border-t border-border text-xs text-muted-foreground">
          {campaign.influencer_count} influencer{campaign.influencer_count !== 1 ? 's' : ''} assigned
        </div>
      )}
    </Link>
  )
}

export default function CampaignsPage() {
  const [search, setSearch] = useState('')
  const [statusFilter, setStatusFilter] = useState('')

  const { data, isLoading } = useQuery({
    queryKey: ['campaigns', statusFilter],
    queryFn: async () => {
      const params = new URLSearchParams({ limit: '50' })
      if (statusFilter) params.set('status', statusFilter)
      const { data } = await api.get<PaginatedResponse<Campaign>>(`/campaigns?${params}`)
      return data
    },
  })

  const filtered = data?.items.filter((c) =>
    !search || c.name.toLowerCase().includes(search.toLowerCase())
  )

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">Campaigns</h1>
          <p className="text-muted-foreground mt-1">{data?.total ?? 0} campaigns total</p>
        </div>
        <button className="bg-primary text-primary-foreground px-4 py-2 rounded-lg text-sm font-medium hover:bg-primary/90">
          + New Campaign
        </button>
      </div>

      <div className="flex gap-3">
        <div className="relative flex-1 max-w-sm">
          <Search size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground" />
          <input
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search campaigns..."
            className="w-full pl-9 pr-3 py-2 rounded-lg border border-input bg-background text-sm focus:outline-none focus:ring-2 focus:ring-ring"
          />
        </div>
        <select
          value={statusFilter}
          onChange={(e) => setStatusFilter(e.target.value)}
          className="px-3 py-2 rounded-lg border border-input bg-background text-sm focus:outline-none"
        >
          <option value="">All Statuses</option>
          {['draft', 'planning', 'active', 'paused', 'completed', 'cancelled'].map((s) => (
            <option key={s} value={s} className="capitalize">{s}</option>
          ))}
        </select>
      </div>

      {isLoading ? (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-5">
          {Array.from({ length: 6 }).map((_, i) => (
            <div key={i} className="bg-card rounded-xl border border-border p-5 h-40 animate-pulse" />
          ))}
        </div>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-5">
          {(filtered ?? []).map((c) => (
            <CampaignCard key={c.id} campaign={c} />
          ))}
          {filtered?.length === 0 && (
            <div className="col-span-3 text-center py-16 text-muted-foreground">
              No campaigns found. Create your first campaign to get started.
            </div>
          )}
        </div>
      )}
    </div>
  )
}
