import { useQuery } from '@tanstack/react-query'
import { useParams, Link } from 'react-router-dom'
import { ArrowLeft, Calendar, DollarSign, Target, Users } from 'lucide-react'
import api from '@/utils/api'
import type { Campaign, CampaignMetrics, CampaignInfluencer } from '@/types'
import { format } from 'date-fns'

export default function CampaignDetailPage() {
  const { id } = useParams()

  const { data: campaign, isLoading } = useQuery({
    queryKey: ['campaign', id],
    queryFn: async () => {
      const { data } = await api.get<Campaign>(`/campaigns/${id}`)
      return data
    },
  })

  const { data: metrics } = useQuery({
    queryKey: ['campaign-metrics', id],
    queryFn: async () => {
      const { data } = await api.get<CampaignMetrics>(`/campaigns/${id}/metrics`)
      return data
    },
    enabled: !!campaign,
    retry: false,
  })

  const { data: influencers } = useQuery({
    queryKey: ['campaign-influencers', id],
    queryFn: async () => {
      const { data } = await api.get(`/campaigns/${id}/influencers?limit=50`)
      return data as any
    },
    enabled: !!campaign,
  })

  if (isLoading) {
    return (
      <div className="space-y-6">
        <div className="h-8 bg-muted rounded animate-pulse w-48" />
        <div className="h-48 bg-card rounded-xl border border-border animate-pulse" />
      </div>
    )
  }

  if (!campaign) return <div>Campaign not found</div>

  const STATUS_COLORS: Record<string, string> = {
    draft: 'bg-slate-400/10 text-slate-400',
    planning: 'bg-cyan-400/10 text-cyan-400',
    active: 'bg-emerald-400/10 text-emerald-400',
    paused: 'bg-amber-400/10 text-amber-400',
    completed: 'bg-violet-400/10 text-violet-400',
    cancelled: 'bg-rose-400/10 text-rose-400',
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-3">
        <Link to="/app/campaigns" className="p-2 rounded-lg hover:bg-muted">
          <ArrowLeft size={18} />
        </Link>
        <div className="flex-1">
          <div className="flex items-center gap-3">
            <h1 className="text-2xl font-bold">{campaign.name}</h1>
            <span className={`text-sm px-2.5 py-1 rounded-full font-medium ${STATUS_COLORS[campaign.status]}`}>
              {campaign.status}
            </span>
          </div>
          <p className="text-muted-foreground mt-0.5 capitalize">
            {campaign.campaign_type.replace(/_/g, ' ')}
          </p>
        </div>
      </div>

      {/* Overview Grid */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {[
          { icon: DollarSign, label: 'Total Budget', value: campaign.total_budget ? `$${Number(campaign.total_budget).toLocaleString()}` : '—' },
          { icon: Calendar, label: 'Start Date', value: campaign.start_date ? format(new Date(campaign.start_date), 'MMM d, yyyy') : '—' },
          { icon: Calendar, label: 'End Date', value: campaign.end_date ? format(new Date(campaign.end_date), 'MMM d, yyyy') : '—' },
          { icon: Users, label: 'Influencers', value: campaign.influencer_count ?? '0' },
        ].map(({ icon: Icon, label, value }) => (
          <div key={label} className="bg-card rounded-xl border border-border p-4">
            <div className="flex items-center gap-2 text-muted-foreground mb-1.5">
              <Icon size={14} />
              <span className="text-xs">{label}</span>
            </div>
            <div className="font-bold text-lg">{value}</div>
          </div>
        ))}
      </div>

      {/* Metrics (if available) */}
      {metrics && (
        <div className="bg-card rounded-xl border border-border p-6">
          <div className="flex items-center justify-between mb-4">
            <h2 className="font-semibold">Performance Metrics</h2>
            {metrics.last_synced_at && (
              <span className="text-xs text-muted-foreground">
                Last synced: {format(new Date(metrics.last_synced_at), 'MMM d, h:mm a')}
              </span>
            )}
          </div>
          <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-4">
            {[
              { label: 'Reach', value: metrics.total_reach?.toLocaleString() ?? '—' },
              { label: 'Impressions', value: metrics.total_impressions?.toLocaleString() ?? '—' },
              { label: 'Likes', value: metrics.total_likes?.toLocaleString() ?? '—' },
              { label: 'Comments', value: metrics.total_comments?.toLocaleString() ?? '—' },
              { label: 'Eng. Rate', value: metrics.avg_engagement_rate ? `${(metrics.avg_engagement_rate * 100).toFixed(1)}%` : '—' },
              { label: 'ROAS', value: metrics.roas ? `${metrics.roas}x` : '—' },
            ].map(({ label, value }) => (
              <div key={label} className="text-center">
                <div className="text-lg font-bold">{value}</div>
                <div className="text-xs text-muted-foreground">{label}</div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Brief */}
      {campaign.brief_text && (
        <div className="bg-card rounded-xl border border-border p-6">
          <h2 className="font-semibold mb-3">Campaign Brief</h2>
          <p className="text-sm text-muted-foreground leading-relaxed whitespace-pre-line">
            {campaign.brief_text}
          </p>
        </div>
      )}

      {/* Influencers */}
      <div className="bg-card rounded-xl border border-border p-6">
        <div className="flex items-center justify-between mb-4">
          <h2 className="font-semibold">Influencers</h2>
          <button className="text-sm text-primary hover:underline">+ Add Influencer</button>
        </div>
        {influencers?.items?.length ? (
          <div className="space-y-2">
            {influencers.items.map((ci: any) => (
              <div key={ci.id} className="flex items-center justify-between p-3 rounded-lg border border-border">
                <div>
                  <span className="font-medium text-sm">Influencer #{ci.influencer_id}</span>
                  <span className="text-xs text-muted-foreground ml-2">{ci.status}</span>
                </div>
                <div className="text-sm">
                  {ci.agreed_fee
                    ? <span className="font-medium">${ci.agreed_fee} agreed</span>
                    : ci.proposed_fee
                    ? <span className="text-muted-foreground">${ci.proposed_fee} proposed</span>
                    : '—'}
                </div>
              </div>
            ))}
          </div>
        ) : (
          <p className="text-sm text-muted-foreground">No influencers assigned yet.</p>
        )}
      </div>
    </div>
  )
}
