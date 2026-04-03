import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { Link } from 'react-router-dom'
import {
  Search, Instagram, Youtube, Globe, MapPin, Users,
  Briefcase, ArrowRight, Loader2,
} from 'lucide-react'
import api from '@/utils/api'

// ── Types ─────────────────────────────────────────────────────────────────────

interface PublicSocialAccount {
  platform: string
  username: string
  follower_count?: number
  is_verified: boolean
}

interface PublicInfluencerCard {
  id: number
  full_name: string
  avatar_url?: string
  location?: string
  niches?: string[]
  bio?: string
  social_accounts: PublicSocialAccount[]
  joined_at: string
}

interface PublicTeamMember {
  id: number
  full_name: string
  avatar_url?: string
  role: string
  joined_at: string
}

// ── Helpers ───────────────────────────────────────────────────────────────────

const PLATFORM_ICONS: Record<string, React.ElementType> = {
  instagram: Instagram,
  youtube: Youtube,
}

function formatFollowers(n: number): string {
  if (n >= 1_000_000) return `${(n / 1_000_000).toFixed(1)}M`
  if (n >= 1000) return `${(n / 1000).toFixed(0)}K`
  return String(n)
}

function totalFollowers(accounts: PublicSocialAccount[]): number {
  return accounts.reduce((s, a) => s + (a.follower_count ?? 0), 0)
}

// ── Influencer Card ───────────────────────────────────────────────────────────

function InfluencerCard({ inf }: { inf: PublicInfluencerCard }) {
  const followers = totalFollowers(inf.social_accounts)
  const initials = inf.full_name.split(' ').map((w) => w[0]).join('').slice(0, 2).toUpperCase()

  return (
    <div className="glass-card-hover p-5 flex flex-col gap-4 group">
      {/* Avatar + name */}
      <div className="flex items-start gap-3">
        <div className="w-12 h-12 rounded-full bg-gradient-to-br from-violet-500/30 to-cyan-500/30 flex items-center justify-center text-foreground font-bold text-sm shrink-0 border border-border/40">
          {initials}
        </div>
        <div className="flex-1 min-w-0">
          <h3 className="font-semibold text-foreground truncate">{inf.full_name}</h3>
          {inf.location && (
            <div className="flex items-center gap-1 text-xs text-muted-foreground mt-0.5">
              <MapPin size={11} />
              <span>{inf.location}</span>
            </div>
          )}
        </div>
        {followers > 0 && (
          <div className="text-right shrink-0">
            <div className="text-sm font-bold text-foreground">{formatFollowers(followers)}</div>
            <div className="text-xs text-muted-foreground">followers</div>
          </div>
        )}
      </div>

      {/* Bio */}
      {inf.bio && (
        <p className="text-xs text-muted-foreground leading-relaxed line-clamp-2">{inf.bio}</p>
      )}

      {/* Niches */}
      {inf.niches?.length ? (
        <div className="flex flex-wrap gap-1.5">
          {inf.niches.slice(0, 4).map((niche) => (
            <span key={niche} className="text-[11px] px-2 py-0.5 rounded-full bg-violet-400/10 text-violet-400 capitalize font-medium">
              {niche}
            </span>
          ))}
          {inf.niches.length > 4 && (
            <span className="text-[11px] px-2 py-0.5 rounded-full bg-muted text-muted-foreground">
              +{inf.niches.length - 4} more
            </span>
          )}
        </div>
      ) : null}

      {/* Social platforms */}
      {inf.social_accounts.length > 0 && (
        <div className="flex items-center gap-2 pt-1 border-t border-border/40">
          {inf.social_accounts.slice(0, 4).map((acc) => {
            const Icon = PLATFORM_ICONS[acc.platform] ?? Globe
            return (
              <div key={`${acc.platform}-${acc.username}`} className="flex items-center gap-1 text-xs text-muted-foreground">
                <Icon size={13} className="shrink-0" />
                <span className="truncate max-w-[80px]">@{acc.username}</span>
                {acc.is_verified && <span className="text-cyan-400">✓</span>}
              </div>
            )
          })}
        </div>
      )}
    </div>
  )
}

// ── Team Member Card ──────────────────────────────────────────────────────────

function TeamCard({ member }: { member: PublicTeamMember }) {
  const initials = member.full_name.split(' ').map((w) => w[0]).join('').slice(0, 2).toUpperCase()

  return (
    <div className="glass-card-hover p-5 flex flex-col items-center text-center gap-3">
      <div className="w-16 h-16 rounded-full bg-gradient-to-br from-violet-500/20 to-cyan-500/20 flex items-center justify-center text-foreground font-bold text-lg border border-border/40">
        {initials}
      </div>
      <div>
        <h3 className="font-semibold text-foreground">{member.full_name}</h3>
        <span className="inline-flex items-center gap-1 text-xs px-2.5 py-0.5 rounded-full font-medium mt-1.5 bg-violet-400/10 text-violet-400">
          <Briefcase size={10} />
          Manager
        </span>
      </div>
      <p className="text-xs text-muted-foreground">
        Joined {new Date(member.joined_at).toLocaleDateString('en-US', { month: 'short', year: 'numeric' })}
      </p>
    </div>
  )
}

// ── Main Page ─────────────────────────────────────────────────────────────────

export default function DirectoryPage() {
  const [activeTab, setActiveTab] = useState<'influencers' | 'team'>('influencers')
  const [search, setSearch] = useState('')
  const [nicheFilter, setNicheFilter] = useState('')

  const { data: influencers, isLoading: infLoading } = useQuery({
    queryKey: ['directory-influencers', search, nicheFilter],
    queryFn: async () => {
      const params = new URLSearchParams({ limit: '60' })
      if (search) params.set('search', search)
      if (nicheFilter) params.set('niche', nicheFilter)
      const { data } = await api.get<{ items: PublicInfluencerCard[]; total: number }>(
        `/directory/influencers?${params}`
      )
      return data
    },
    refetchInterval: 30_000,  // refresh every 30s for live updates
  })

  const { data: team, isLoading: teamLoading } = useQuery({
    queryKey: ['directory-team'],
    queryFn: async () => {
      const { data } = await api.get<{ items: PublicTeamMember[]; total: number }>('/directory/team')
      return data
    },
    refetchInterval: 60_000,
  })

  const NICHE_OPTIONS = [
    'fashion', 'beauty', 'fitness', 'food', 'travel', 'tech',
    'gaming', 'lifestyle', 'business', 'education',
  ]

  return (
    <div className="min-h-screen bg-[#070814]">
      {/* ── Header bar ── */}
      <header className="sticky top-0 z-30 bg-[#070814]/90 backdrop-blur-xl border-b border-border/30">
        <div className="max-w-6xl mx-auto px-4 sm:px-6 h-16 flex items-center justify-between gap-4">
          <Link to="/" className="flex items-center gap-2.5 shrink-0">
            <div className="w-8 h-8 rounded-lg bg-primary flex items-center justify-center text-white font-bold text-sm">
              O
            </div>
            <span className="gradient-text font-heading font-bold text-lg hidden sm:block">OakstrattonIMA</span>
          </Link>
          <Link
            to="/login"
            className="btn-primary text-sm inline-flex items-center gap-2 shrink-0"
          >
            Login / Register
            <ArrowRight size={14} />
          </Link>
        </div>
      </header>

      {/* ── Hero ── */}
      <section className="relative overflow-hidden py-16 sm:py-24 text-center px-4">
        <div className="absolute inset-0 bg-gradient-to-b from-violet-600/8 via-transparent to-transparent pointer-events-none" />
        <div className="relative max-w-2xl mx-auto">
          <div className="inline-flex items-center gap-2 bg-violet-400/10 border border-violet-400/20 rounded-full px-4 py-1.5 text-xs text-violet-400 font-medium mb-6">
            <Users size={13} />
            Live Roster — {influencers?.total ?? '…'} Influencers
          </div>
          <h1 className="text-3xl sm:text-4xl lg:text-5xl font-heading font-bold text-foreground leading-tight mb-4">
            Meet Our{' '}
            <span className="gradient-text">Influencer Roster</span>
          </h1>
          <p className="text-muted-foreground text-base sm:text-lg leading-relaxed mb-8 max-w-xl mx-auto">
            Browse our curated network of creators and the agency team behind OakstrattonIMA's campaigns.
          </p>
          <Link to="/login" className="btn-primary inline-flex items-center gap-2 text-sm">
            Join Our Roster <ArrowRight size={14} />
          </Link>
        </div>
      </section>

      {/* ── Content ── */}
      <div className="max-w-6xl mx-auto px-4 sm:px-6 pb-20">
        {/* Tabs */}
        <div className="flex gap-1 bg-muted/20 rounded-xl p-1 w-fit mb-8 border border-border/30">
          <button
            onClick={() => setActiveTab('influencers')}
            className={`flex items-center gap-2 px-5 py-2 rounded-lg text-sm font-medium transition-all ${
              activeTab === 'influencers' ? 'bg-card text-foreground shadow-sm' : 'text-muted-foreground hover:text-foreground'
            }`}
          >
            <Users size={15} />
            Influencers
            {influencers && (
              <span className="ml-1 text-xs bg-violet-400/20 text-violet-400 px-1.5 py-0.5 rounded-full">
                {influencers.total}
              </span>
            )}
          </button>
          <button
            onClick={() => setActiveTab('team')}
            className={`flex items-center gap-2 px-5 py-2 rounded-lg text-sm font-medium transition-all ${
              activeTab === 'team' ? 'bg-card text-foreground shadow-sm' : 'text-muted-foreground hover:text-foreground'
            }`}
          >
            <Briefcase size={15} />
            Agency Team
            {team && (
              <span className="ml-1 text-xs bg-amber-400/20 text-amber-400 px-1.5 py-0.5 rounded-full">
                {team.total}
              </span>
            )}
          </button>
        </div>

        {/* Influencers tab */}
        {activeTab === 'influencers' && (
          <div className="space-y-6">
            {/* Filters */}
            <div className="flex flex-col sm:flex-row gap-3">
              <div className="flex items-center gap-2 bg-card border border-border/50 rounded-lg px-3 py-2 flex-1">
                <Search size={15} className="text-muted-foreground shrink-0" />
                <input
                  type="text"
                  placeholder="Search by name or niche..."
                  value={search}
                  onChange={(e) => setSearch(e.target.value)}
                  className="bg-transparent text-sm text-foreground placeholder:text-muted-foreground focus:outline-none w-full"
                />
              </div>
              <select
                value={nicheFilter}
                onChange={(e) => setNicheFilter(e.target.value)}
                className="input-field sm:w-44 capitalize"
              >
                <option value="">All niches</option>
                {NICHE_OPTIONS.map((n) => (
                  <option key={n} value={n} className="capitalize">{n}</option>
                ))}
              </select>
            </div>

            {infLoading ? (
              <div className="flex items-center justify-center py-20">
                <Loader2 size={28} className="animate-spin text-muted-foreground" />
              </div>
            ) : influencers?.items.length ? (
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
                {influencers.items.map((inf) => (
                  <InfluencerCard key={inf.id} inf={inf} />
                ))}
              </div>
            ) : (
              <div className="text-center py-20 text-muted-foreground">
                <Users size={40} className="mx-auto mb-3 opacity-30" />
                <p className="text-sm">No influencers found{search ? ` for "${search}"` : ''}.</p>
              </div>
            )}
          </div>
        )}

        {/* Team tab */}
        {activeTab === 'team' && (
          <div>
            {teamLoading ? (
              <div className="flex items-center justify-center py-20">
                <Loader2 size={28} className="animate-spin text-muted-foreground" />
              </div>
            ) : team?.items.length ? (
              <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-4">
                {team.items.map((member) => (
                  <TeamCard key={member.id} member={member} />
                ))}
              </div>
            ) : (
              <div className="text-center py-20 text-muted-foreground">
                <Briefcase size={40} className="mx-auto mb-3 opacity-30" />
                <p className="text-sm">No team members listed yet.</p>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  )
}
