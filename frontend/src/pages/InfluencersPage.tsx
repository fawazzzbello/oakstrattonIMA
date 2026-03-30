import { useQuery } from '@tanstack/react-query'
import { useState } from 'react'
import { Search, Filter, Instagram, Youtube } from 'lucide-react'
import api from '@/utils/api'
import type { Influencer, PaginatedResponse } from '@/types'
import { Link } from 'react-router-dom'

const STATUS_COLORS = {
  active: 'bg-green-100 text-green-700',
  pending: 'bg-yellow-100 text-yellow-700',
  inactive: 'bg-gray-100 text-gray-600',
  suspended: 'bg-red-100 text-red-700',
}

function InfluencerCard({ influencer }: { influencer: Influencer }) {
  const primaryAccount = influencer.social_accounts?.[0]
  const totalFollowers = influencer.social_accounts?.reduce(
    (sum, acc) => sum + (acc.follower_count || 0), 0
  ) ?? 0

  const formatFollowers = (n: number) =>
    n >= 1_000_000 ? `${(n / 1_000_000).toFixed(1)}M` : n >= 1000 ? `${(n / 1000).toFixed(0)}K` : String(n)

  return (
    <Link
      to={`/influencers/${influencer.id}`}
      className="bg-card rounded-xl border border-border p-5 hover:shadow-md transition-shadow block"
    >
      <div className="flex items-start gap-3 mb-4">
        <div className="w-11 h-11 rounded-full bg-primary/20 flex items-center justify-center text-primary font-bold shrink-0">
          {String(influencer.user_id).slice(-2)}
        </div>
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2">
            <span className="font-medium truncate">@{primaryAccount?.username ?? `inf_${influencer.id}`}</span>
            <span className={`text-xs px-2 py-0.5 rounded-full font-medium ${STATUS_COLORS[influencer.status]}`}>
              {influencer.status}
            </span>
          </div>
          <p className="text-sm text-muted-foreground mt-0.5">
            {influencer.location ?? influencer.country_code ?? 'Unknown location'}
          </p>
        </div>
      </div>

      <div className="grid grid-cols-3 gap-3 text-center">
        <div>
          <div className="text-base font-bold">{formatFollowers(totalFollowers)}</div>
          <div className="text-xs text-muted-foreground">Followers</div>
        </div>
        <div>
          <div className="text-base font-bold">
            {influencer.avg_engagement_rate
              ? `${(influencer.avg_engagement_rate * 100).toFixed(1)}%`
              : '—'}
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
            <span key={niche} className="text-xs bg-muted px-2 py-0.5 rounded-full capitalize">
              {niche}
            </span>
          ))}
        </div>
      )}
    </Link>
  )
}

export default function InfluencersPage() {
  const [search, setSearch] = useState('')
  const [statusFilter, setStatusFilter] = useState('')

  const { data, isLoading } = useQuery({
    queryKey: ['influencers', search, statusFilter],
    queryFn: async () => {
      const params = new URLSearchParams({ limit: '50' })
      if (statusFilter) params.set('status', statusFilter)
      const { data } = await api.get<PaginatedResponse<Influencer>>(`/influencers?${params}`)
      return data
    },
  })

  const filtered = data?.items.filter((inf) => {
    if (!search) return true
    const acc = inf.social_accounts?.[0]?.username ?? ''
    return acc.toLowerCase().includes(search.toLowerCase())
  })

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">Influencers</h1>
          <p className="text-muted-foreground mt-1">
            {data?.total ?? 0} influencers in your roster
          </p>
        </div>
        <button className="bg-primary text-primary-foreground px-4 py-2 rounded-lg text-sm font-medium hover:bg-primary/90">
          + Add Influencer
        </button>
      </div>

      {/* Filters */}
      <div className="flex gap-3">
        <div className="relative flex-1 max-w-sm">
          <Search size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground" />
          <input
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search by username..."
            className="w-full pl-9 pr-3 py-2 rounded-lg border border-input bg-background text-sm focus:outline-none focus:ring-2 focus:ring-ring"
          />
        </div>
        <select
          value={statusFilter}
          onChange={(e) => setStatusFilter(e.target.value)}
          className="px-3 py-2 rounded-lg border border-input bg-background text-sm focus:outline-none focus:ring-2 focus:ring-ring"
        >
          <option value="">All Statuses</option>
          <option value="active">Active</option>
          <option value="pending">Pending</option>
          <option value="inactive">Inactive</option>
          <option value="suspended">Suspended</option>
        </select>
      </div>

      {/* Grid */}
      {isLoading ? (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-5">
          {Array.from({ length: 6 }).map((_, i) => (
            <div key={i} className="bg-card rounded-xl border border-border p-5 h-48 animate-pulse" />
          ))}
        </div>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-5">
          {(filtered ?? []).map((inf) => (
            <InfluencerCard key={inf.id} influencer={inf} />
          ))}
          {filtered?.length === 0 && (
            <div className="col-span-3 text-center py-16 text-muted-foreground">
              No influencers found. Add your first influencer to get started.
            </div>
          )}
        </div>
      )}
    </div>
  )
}
