import { type ElementType, useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { useParams, Link } from 'react-router-dom'
import { ArrowLeft, Instagram, Youtube, Globe, MapPin, Star, Sparkles, X } from 'lucide-react'
import api from '@/utils/api'
import type { Influencer } from '@/types'
import { useAuthStore } from '@/store/authStore'

const PLATFORM_ICONS: Record<string, ElementType> = {
  instagram: Instagram,
  youtube: Youtube,
}

const STATUS_OPTIONS = ['active', 'pending', 'inactive', 'suspended'] as const

export default function InfluencerDetailPage() {
  const { id } = useParams()
  const queryClient = useQueryClient()
  const { user } = useAuthStore()
  const canManage = user?.role === 'admin' || user?.role === 'manager'
  const [lightboxIdx, setLightboxIdx] = useState<number | null>(null)

  const { data: influencer, isLoading } = useQuery({
    queryKey: ['influencer', id],
    queryFn: async () => {
      const { data } = await api.get<Influencer>(`/influencers/${id}`)
      return data
    },
  })

  // Must be declared before any early returns to comply with Rules of Hooks
  const statusMutation = useMutation({
    mutationFn: (newStatus: string) => api.patch(`/influencers/${id}`, { status: newStatus }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['influencer', id] })
      queryClient.invalidateQueries({ queryKey: ['influencers'] })
      queryClient.invalidateQueries({ queryKey: ['directory-influencers'] })
    },
  })

  if (isLoading) {
    return (
      <div className="space-y-6">
        <div className="h-8 bg-muted rounded animate-pulse w-48" />
        <div className="grid grid-cols-3 gap-6">
          <div className="col-span-1 bg-card rounded-xl border border-border p-6 h-64 animate-pulse" />
          <div className="col-span-2 bg-card rounded-xl border border-border p-6 h-64 animate-pulse" />
        </div>
      </div>
    )
  }

  if (!influencer) return <div>Influencer not found</div>

  const totalFollowers = influencer.social_accounts?.reduce(
    (sum, acc) => sum + (acc.follower_count || 0), 0
  ) ?? 0

  const formatFollowers = (n: number) =>
    n >= 1_000_000 ? `${(n / 1_000_000).toFixed(1)}M`
    : n >= 1000 ? `${(n / 1000).toFixed(0)}K`
    : String(n)

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-3">
        <Link to="/app/influencers" className="p-2 rounded-lg hover:bg-muted">
          <ArrowLeft size={18} />
        </Link>
        <h1 className="text-2xl font-bold">Influencer Profile</h1>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Profile card */}
        <div className="bg-card rounded-xl border border-border p-6">
          <div className="flex flex-col items-center text-center">
            <div className="w-20 h-20 rounded-full bg-primary/20 flex items-center justify-center text-primary font-bold text-2xl mb-4">
              {String(influencer.user_id).slice(-2)}
            </div>
            {canManage ? (
              <select
                value={influencer.status}
                onChange={(e) => statusMutation.mutate(e.target.value)}
                disabled={statusMutation.isPending}
                className={`text-xs px-2.5 py-1 rounded-full font-medium mb-3 border-0 cursor-pointer appearance-none text-center disabled:opacity-60 ${
                  influencer.status === 'active' ? 'bg-emerald-400/10 text-emerald-400' :
                  influencer.status === 'pending' ? 'bg-amber-400/10 text-amber-400' :
                  influencer.status === 'suspended' ? 'bg-rose-400/10 text-rose-400' :
                  'bg-slate-400/10 text-slate-400'
                }`}
              >
                {STATUS_OPTIONS.map((s) => (
                  <option key={s} value={s} className="bg-card text-foreground capitalize">{s}</option>
                ))}
              </select>
            ) : (
              <span className={`text-xs px-2.5 py-1 rounded-full font-medium mb-3 ${
                influencer.status === 'active' ? 'bg-emerald-400/10 text-emerald-400' :
                influencer.status === 'pending' ? 'bg-amber-400/10 text-amber-400' :
                influencer.status === 'suspended' ? 'bg-rose-400/10 text-rose-400' :
                'bg-slate-400/10 text-slate-400'
              }`}>
                {influencer.status}
              </span>
            )}
            {influencer.ai_generated && (
              <span className="inline-flex items-center gap-1 text-xs px-2.5 py-1 rounded-full font-medium mb-2 bg-violet-400/10 text-violet-400">
                <Sparkles size={11} /> AI Generated
              </span>
            )}
            {influencer.location && (
              <div className="flex items-center gap-1 text-sm text-muted-foreground mb-1">
                <MapPin size={13} />
                <span>{influencer.location}</span>
              </div>
            )}
            {influencer.trust_score !== null && influencer.trust_score !== undefined && (
              <div className="flex items-center gap-1 text-sm mt-1">
                <Star size={13} className="text-yellow-500 fill-yellow-500" />
                <span className="font-medium">{influencer.trust_score}/10 trust score</span>
              </div>
            )}
          </div>

          <div className="mt-5 space-y-2">
            {influencer.niches?.map((niche) => (
              <span key={niche} className="inline-block text-xs bg-muted px-2 py-1 rounded-full capitalize mr-1">
                {niche}
              </span>
            ))}
          </div>

          {influencer.bio && (
            <p className="mt-4 text-sm text-muted-foreground leading-relaxed">{influencer.bio}</p>
          )}
        </div>

        {/* Stats & Social */}
        <div className="lg:col-span-2 space-y-5">
          {/* Aggregate stats */}
          <div className="bg-card rounded-xl border border-border p-6">
            <h2 className="font-semibold mb-4">Performance Metrics</h2>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              {[
                { label: 'Total Followers', value: formatFollowers(totalFollowers) },
                { label: 'Avg Eng. Rate', value: influencer.avg_engagement_rate ? `${(influencer.avg_engagement_rate * 100).toFixed(1)}%` : '—' },
                { label: 'Rate/Post', value: influencer.rate_per_post ? `$${influencer.rate_per_post}` : '—' },
                { label: 'Rate/Reel', value: influencer.rate_per_reel ? `$${influencer.rate_per_reel}` : '—' },
              ].map(({ label, value }) => (
                <div key={label} className="bg-muted/50 rounded-lg p-3 text-center">
                  <div className="text-lg font-bold">{value}</div>
                  <div className="text-xs text-muted-foreground mt-0.5">{label}</div>
                </div>
              ))}
            </div>
          </div>

          {/* Social Accounts */}
          <div className="bg-card rounded-xl border border-border p-6">
            <h2 className="font-semibold mb-4">Social Accounts</h2>
            <div className="space-y-3">
              {influencer.social_accounts?.map((account) => {
                const Icon = PLATFORM_ICONS[account.platform] ?? Globe
                return (
                  <div key={account.id} className="flex items-center gap-3 p-3 rounded-lg border border-border">
                    <div className="w-9 h-9 rounded-lg bg-muted flex items-center justify-center">
                      <Icon size={18} className="text-muted-foreground" />
                    </div>
                    <div className="flex-1">
                      <div className="flex items-center gap-2">
                        <span className="font-medium text-sm">@{account.username}</span>
                        <span className="text-xs text-muted-foreground capitalize">{account.platform}</span>
                        {account.is_verified && (
                          <span className="text-xs bg-blue-100 text-blue-700 px-1.5 py-0.5 rounded">verified</span>
                        )}
                      </div>
                      <div className="text-xs text-muted-foreground mt-0.5">
                        {account.follower_count ? `${formatFollowers(account.follower_count)} followers` : '—'}
                        {account.engagement_rate
                          ? ` · ${(account.engagement_rate * 100).toFixed(1)}% eng.`
                          : ''}
                      </div>
                    </div>
                    {account.profile_url && (
                      <a
                        href={account.profile_url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-xs text-primary hover:underline"
                      >
                        View Profile
                      </a>
                    )}
                  </div>
                )
              })}
              {!influencer.social_accounts?.length && (
                <p className="text-sm text-muted-foreground">No social accounts linked.</p>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Physical Attributes (AI-generated influencers) */}
      {influencer.ai_generated && influencer.physical_attributes && (
        <div className="bg-card rounded-xl border border-border p-6">
          <h2 className="font-semibold mb-4 flex items-center gap-2">
            <Sparkles size={16} className="text-violet-400" /> Physical Attributes
          </h2>
          <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-3">
            {Object.entries(influencer.physical_attributes).map(([key, val]) => (
              <div key={key} className="bg-muted/50 rounded-lg p-3">
                <div className="text-xs text-muted-foreground capitalize">{key.replace(/_/g, ' ')}</div>
                <div className="text-sm font-medium mt-0.5">{String(val) || '—'}</div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Portfolio Gallery */}
      {influencer.portfolio_images && influencer.portfolio_images.length > 0 && (
        <div className="bg-card rounded-xl border border-border p-6">
          <h2 className="font-semibold mb-4">
            Portfolio ({influencer.portfolio_images.length} images)
          </h2>
          <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-3">
            {influencer.portfolio_images.map((img, idx) => (
              <button
                key={idx}
                onClick={() => setLightboxIdx(idx)}
                className="group relative aspect-[3/4] rounded-lg overflow-hidden border border-border hover:border-primary/40 transition-colors"
              >
                <img
                  src={img.url}
                  alt={img.caption}
                  className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
                  loading="lazy"
                />
                <div className="absolute inset-x-0 bottom-0 bg-gradient-to-t from-black/70 to-transparent p-2">
                  <p className="text-xs text-white font-medium truncate">{img.caption}</p>
                  <div className="flex gap-1 mt-0.5">
                    <span className="text-[10px] px-1.5 py-0.5 rounded bg-white/20 text-white capitalize">{img.image_type}</span>
                    {img.mood && (
                      <span className="text-[10px] px-1.5 py-0.5 rounded bg-violet-400/30 text-violet-200 capitalize">{img.mood}</span>
                    )}
                  </div>
                </div>
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Lightbox */}
      {lightboxIdx !== null && influencer.portfolio_images && (
        <div
          className="fixed inset-0 z-50 bg-black/90 flex items-center justify-center p-4"
          onClick={() => setLightboxIdx(null)}
        >
          <button
            onClick={() => setLightboxIdx(null)}
            className="absolute top-4 right-4 text-white/70 hover:text-white p-2"
          >
            <X size={24} />
          </button>
          <div className="max-w-2xl w-full" onClick={(e) => e.stopPropagation()}>
            <img
              src={influencer.portfolio_images[lightboxIdx].url}
              alt={influencer.portfolio_images[lightboxIdx].caption}
              className="w-full rounded-lg"
            />
            <div className="mt-3 text-center">
              <p className="text-white font-medium">{influencer.portfolio_images[lightboxIdx].caption}</p>
              {influencer.portfolio_images[lightboxIdx].setting && (
                <p className="text-white/60 text-sm mt-1">{influencer.portfolio_images[lightboxIdx].setting}</p>
              )}
              <div className="flex justify-center gap-2 mt-2">
                <button
                  onClick={() => setLightboxIdx(Math.max(0, lightboxIdx - 1))}
                  disabled={lightboxIdx === 0}
                  className="px-3 py-1 rounded bg-white/10 text-white text-sm disabled:opacity-30 hover:bg-white/20"
                >
                  Prev
                </button>
                <span className="text-white/50 text-sm py-1">{lightboxIdx + 1} / {influencer.portfolio_images.length}</span>
                <button
                  onClick={() => setLightboxIdx(Math.min(influencer.portfolio_images!.length - 1, lightboxIdx + 1))}
                  disabled={lightboxIdx === influencer.portfolio_images.length - 1}
                  className="px-3 py-1 rounded bg-white/10 text-white text-sm disabled:opacity-30 hover:bg-white/20"
                >
                  Next
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
