import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import {
  UserCheck, MapPin, Globe, Instagram, Youtube, Edit3, Save, X,
  Plus, Loader2, AlertCircle, CheckCircle2,
} from 'lucide-react'
import api from '@/utils/api'
import { useAuthStore } from '@/store/authStore'
import type { Influencer, SocialPlatform } from '@/types'
import Modal from '@/components/Modal'

const PLATFORM_ICONS: Record<string, React.ElementType> = {
  instagram: Instagram,
  youtube: Youtube,
}

const NICHE_OPTIONS = [
  'fashion', 'beauty', 'fitness', 'food', 'travel', 'tech',
  'gaming', 'lifestyle', 'business', 'education', 'entertainment',
  'health', 'parenting', 'sports', 'other',
]

const PLATFORM_OPTIONS: SocialPlatform[] = [
  'instagram', 'tiktok', 'youtube', 'twitter', 'facebook',
  'pinterest', 'linkedin', 'snapchat', 'twitch',
]

function formatFollowers(n: number) {
  if (n >= 1_000_000) return `${(n / 1_000_000).toFixed(1)}M`
  if (n >= 1000) return `${(n / 1000).toFixed(0)}K`
  return String(n)
}

export default function MyInfluencerProfilePage() {
  const { user } = useAuthStore()
  const queryClient = useQueryClient()
  const influencerId = user?.influencer_id

  const [editing, setEditing] = useState(false)
  const [showAddAccount, setShowAddAccount] = useState(false)
  const [saveSuccess, setSaveSuccess] = useState(false)
  const [formData, setFormData] = useState({ bio: '', location: '', niches: [] as string[] })
  const [newAccount, setNewAccount] = useState({ platform: 'instagram' as SocialPlatform, username: '', profile_url: '' })

  const { data: profile, isLoading, error } = useQuery({
    queryKey: ['my-influencer-profile', influencerId],
    queryFn: async () => {
      const { data } = await api.get<Influencer>(`/influencers/${influencerId}`)
      return data
    },
    enabled: !!influencerId,
  })

  const updateMutation = useMutation({
    mutationFn: async (payload: { bio?: string; location?: string; niches?: string[] }) => {
      const { data } = await api.patch(`/influencers/${influencerId}`, payload)
      return data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['my-influencer-profile', influencerId] })
      setEditing(false)
      setSaveSuccess(true)
      setTimeout(() => setSaveSuccess(false), 4000)
    },
  })

  const addAccountMutation = useMutation({
    mutationFn: async () => {
      const { data } = await api.post(`/influencers/${influencerId}/social-accounts`, {
        platform: newAccount.platform,
        username: newAccount.username,
        profile_url: newAccount.profile_url || undefined,
      })
      return data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['my-influencer-profile', influencerId] })
      setShowAddAccount(false)
      setNewAccount({ platform: 'instagram', username: '', profile_url: '' })
    },
  })

  const startEdit = () => {
    setFormData({
      bio: profile?.bio ?? '',
      location: profile?.location ?? '',
      niches: profile?.niches ?? [],
    })
    setEditing(true)
  }

  const toggleNiche = (niche: string) => {
    setFormData((f) => ({
      ...f,
      niches: f.niches.includes(niche)
        ? f.niches.filter((n) => n !== niche)
        : [...f.niches, niche],
    }))
  }

  // No influencer profile linked yet
  if (!influencerId) {
    return (
      <div className="page-container">
        <div className="glass-card p-10 text-center max-w-lg mx-auto">
          <UserCheck size={48} className="text-muted-foreground mx-auto mb-4 opacity-40" />
          <h2 className="text-lg font-semibold mb-2">No influencer profile yet</h2>
          <p className="text-sm text-muted-foreground leading-relaxed mb-6">
            Your account hasn't been linked to an influencer profile. Please contact your agency manager to get set up.
          </p>
          <a
            href="mailto:hello@oakstratton.com"
            className="btn-primary inline-flex items-center gap-2"
          >
            Contact Manager
          </a>
        </div>
      </div>
    )
  }

  if (isLoading) {
    return (
      <div className="page-container">
        <div className="h-8 w-48 bg-muted/50 rounded-lg animate-pulse" />
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="glass-card h-80 animate-pulse" />
          <div className="lg:col-span-2 glass-card h-80 animate-pulse" />
        </div>
      </div>
    )
  }

  if (error || !profile) {
    return (
      <div className="page-container">
        <div className="glass-card p-8 text-center">
          <AlertCircle size={36} className="text-destructive mx-auto mb-3" />
          <p className="text-sm text-muted-foreground">Could not load your profile. Please try refreshing.</p>
        </div>
      </div>
    )
  }

  const totalFollowers = profile.social_accounts?.reduce((s, a) => s + (a.follower_count ?? 0), 0) ?? 0

  return (
    <div className="page-container">
      {/* Header */}
      <div className="page-header">
        <div>
          <h1 className="page-title">My Profile</h1>
          <p className="page-subtitle">Manage your influencer profile and social accounts</p>
        </div>
        {!editing ? (
          <button onClick={startEdit} className="btn-secondary inline-flex items-center gap-2">
            <Edit3 size={15} />
            Edit Profile
          </button>
        ) : (
          <div className="flex gap-2">
            <button onClick={() => setEditing(false)} className="btn-ghost inline-flex items-center gap-2">
              <X size={15} />
              Cancel
            </button>
            <button
              onClick={() => updateMutation.mutate({ bio: formData.bio, location: formData.location, niches: formData.niches })}
              disabled={updateMutation.isPending}
              className="btn-primary inline-flex items-center gap-2"
            >
              {updateMutation.isPending ? <Loader2 size={15} className="animate-spin" /> : <Save size={15} />}
              Save Changes
            </button>
          </div>
        )}
      </div>

      {saveSuccess && (
        <div className="flex items-center gap-2 text-sm text-emerald-400 bg-emerald-400/10 px-4 py-2.5 rounded-lg border border-emerald-400/20">
          <CheckCircle2 size={16} />
          Profile updated successfully
        </div>
      )}

      {updateMutation.isError && (
        <div className="flex items-center gap-2 text-sm text-destructive bg-destructive/10 px-4 py-2.5 rounded-lg">
          <AlertCircle size={16} />
          {(updateMutation.error as any)?.response?.data?.detail ?? 'Failed to save changes'}
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left card — identity */}
        <div className="glass-card p-6 flex flex-col gap-5">
          <div className="flex flex-col items-center text-center">
            <div className="w-20 h-20 rounded-full bg-emerald-400/20 flex items-center justify-center text-emerald-400 font-bold text-2xl mb-3">
              {user?.full_name?.[0]?.toUpperCase() ?? 'I'}
            </div>
            <h2 className="font-semibold text-lg">{user?.full_name}</h2>
            <span className={`text-xs px-2.5 py-1 rounded-full font-medium mt-1 ${
              profile.status === 'active' ? 'bg-emerald-400/10 text-emerald-400' :
              profile.status === 'pending' ? 'bg-amber-400/10 text-amber-400' :
              'bg-slate-400/10 text-slate-400'
            }`}>
              {profile.status}
            </span>
          </div>

          {/* Location */}
          {editing ? (
            <div>
              <label className="block text-xs text-muted-foreground mb-1">Location</label>
              <input
                className="input-field w-full"
                placeholder="e.g. New York, USA"
                value={formData.location}
                onChange={(e) => setFormData((f) => ({ ...f, location: e.target.value }))}
              />
            </div>
          ) : (
            profile.location && (
              <div className="flex items-center gap-2 text-sm text-muted-foreground justify-center">
                <MapPin size={14} />
                <span>{profile.location}</span>
              </div>
            )
          )}

          {/* Stats row */}
          <div className="grid grid-cols-2 gap-3">
            <div className="bg-muted/30 rounded-lg p-3 text-center">
              <div className="font-bold text-lg">{formatFollowers(totalFollowers)}</div>
              <div className="text-xs text-muted-foreground">Total Followers</div>
            </div>
            <div className="bg-muted/30 rounded-lg p-3 text-center">
              <div className="font-bold text-lg">
                {profile.avg_engagement_rate ? `${(profile.avg_engagement_rate * 100).toFixed(1)}%` : '—'}
              </div>
              <div className="text-xs text-muted-foreground">Avg Engagement</div>
            </div>
          </div>

          {/* Rates */}
          {(profile.rate_per_post || profile.rate_per_story || profile.rate_per_reel) && (
            <div className="space-y-1.5">
              <p className="text-xs font-medium text-muted-foreground uppercase tracking-wider">Rates</p>
              {profile.rate_per_post && (
                <div className="flex justify-between text-sm">
                  <span className="text-muted-foreground">Per post</span>
                  <span className="font-medium">${profile.rate_per_post}</span>
                </div>
              )}
              {profile.rate_per_story && (
                <div className="flex justify-between text-sm">
                  <span className="text-muted-foreground">Per story</span>
                  <span className="font-medium">${profile.rate_per_story}</span>
                </div>
              )}
              {profile.rate_per_reel && (
                <div className="flex justify-between text-sm">
                  <span className="text-muted-foreground">Per reel</span>
                  <span className="font-medium">${profile.rate_per_reel}</span>
                </div>
              )}
            </div>
          )}
        </div>

        {/* Right column */}
        <div className="lg:col-span-2 space-y-5">
          {/* Bio */}
          <div className="glass-card p-6">
            <h3 className="font-semibold mb-3">Bio</h3>
            {editing ? (
              <textarea
                className="input-field w-full resize-none"
                rows={4}
                placeholder="Tell brands about yourself, your content style, and audience..."
                value={formData.bio}
                onChange={(e) => setFormData((f) => ({ ...f, bio: e.target.value }))}
              />
            ) : (
              <p className="text-sm text-muted-foreground leading-relaxed">
                {profile.bio || <span className="italic opacity-50">No bio yet. Click Edit Profile to add one.</span>}
              </p>
            )}
          </div>

          {/* Niches */}
          <div className="glass-card p-6">
            <h3 className="font-semibold mb-3">Content Niches</h3>
            {editing ? (
              <div className="flex flex-wrap gap-2">
                {NICHE_OPTIONS.map((niche) => (
                  <button
                    key={niche}
                    type="button"
                    onClick={() => toggleNiche(niche)}
                    className={`px-3 py-1.5 rounded-full text-xs font-medium transition-all capitalize ${
                      formData.niches.includes(niche)
                        ? 'bg-violet-400/20 text-violet-400 border border-violet-400/40'
                        : 'bg-muted text-muted-foreground border border-border hover:border-muted-foreground'
                    }`}
                  >
                    {niche}
                  </button>
                ))}
              </div>
            ) : (
              <div className="flex flex-wrap gap-2">
                {profile.niches?.length ? (
                  profile.niches.map((niche) => (
                    <span key={niche} className="px-3 py-1 rounded-full text-xs font-medium bg-violet-400/10 text-violet-400 capitalize">
                      {niche}
                    </span>
                  ))
                ) : (
                  <span className="text-sm text-muted-foreground italic opacity-50">No niches selected yet.</span>
                )}
              </div>
            )}
          </div>

          {/* Social Accounts */}
          <div className="glass-card p-6">
            <div className="flex items-center justify-between mb-4">
              <h3 className="font-semibold">Social Accounts</h3>
              <button
                onClick={() => setShowAddAccount(true)}
                className="btn-secondary text-xs inline-flex items-center gap-1.5 py-1.5 px-3"
              >
                <Plus size={13} />
                Add Account
              </button>
            </div>
            <div className="space-y-3">
              {profile.social_accounts?.length ? (
                profile.social_accounts.map((acc) => {
                  const Icon = PLATFORM_ICONS[acc.platform] ?? Globe
                  return (
                    <div key={acc.id} className="flex items-center gap-3 p-3 rounded-lg border border-border bg-muted/20">
                      <div className="w-9 h-9 rounded-lg bg-muted flex items-center justify-center shrink-0">
                        <Icon size={18} className="text-muted-foreground" />
                      </div>
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-2">
                          <span className="font-medium text-sm">@{acc.username}</span>
                          <span className="text-xs text-muted-foreground capitalize">{acc.platform}</span>
                          {acc.is_verified && (
                            <span className="text-xs bg-cyan-400/10 text-cyan-400 px-1.5 py-0.5 rounded">verified</span>
                          )}
                        </div>
                        <div className="text-xs text-muted-foreground mt-0.5">
                          {acc.follower_count ? `${formatFollowers(acc.follower_count)} followers` : 'Followers not synced'}
                          {acc.engagement_rate ? ` · ${(acc.engagement_rate * 100).toFixed(1)}% engagement` : ''}
                        </div>
                      </div>
                      {acc.profile_url && (
                        <a href={acc.profile_url} target="_blank" rel="noopener noreferrer" className="text-xs text-primary hover:underline shrink-0">
                          View
                        </a>
                      )}
                    </div>
                  )
                })
              ) : (
                <p className="text-sm text-muted-foreground italic text-center py-4">
                  No social accounts linked. Add your first account to get started.
                </p>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Add Social Account Modal */}
      <Modal open={showAddAccount} onClose={() => setShowAddAccount(false)} title="Add Social Account">
        <div className="space-y-4">
          <div>
            <label className="block text-xs text-muted-foreground mb-1">Platform</label>
            <select
              className="input-field w-full capitalize"
              value={newAccount.platform}
              onChange={(e) => setNewAccount((a) => ({ ...a, platform: e.target.value as SocialPlatform }))}
            >
              {PLATFORM_OPTIONS.map((p) => (
                <option key={p} value={p} className="capitalize">{p}</option>
              ))}
            </select>
          </div>
          <div>
            <label className="block text-xs text-muted-foreground mb-1">Username (without @)</label>
            <input
              className="input-field w-full"
              placeholder="e.g. your_username"
              value={newAccount.username}
              onChange={(e) => setNewAccount((a) => ({ ...a, username: e.target.value }))}
            />
          </div>
          <div>
            <label className="block text-xs text-muted-foreground mb-1">Profile URL (optional)</label>
            <input
              className="input-field w-full"
              placeholder="https://instagram.com/your_username"
              value={newAccount.profile_url}
              onChange={(e) => setNewAccount((a) => ({ ...a, profile_url: e.target.value }))}
            />
          </div>
          {addAccountMutation.isError && (
            <p className="text-sm text-destructive bg-destructive/10 px-3 py-2 rounded-lg">
              {(addAccountMutation.error as any)?.response?.data?.detail ?? 'Failed to add account'}
            </p>
          )}
          <div className="flex justify-end gap-3 pt-2">
            <button type="button" onClick={() => setShowAddAccount(false)} className="btn-secondary">Cancel</button>
            <button
              onClick={() => addAccountMutation.mutate()}
              disabled={!newAccount.username || addAccountMutation.isPending}
              className="btn-primary inline-flex items-center gap-2 disabled:opacity-50"
            >
              {addAccountMutation.isPending ? <Loader2 size={14} className="animate-spin" /> : <Plus size={14} />}
              Add Account
            </button>
          </div>
        </div>
      </Modal>
    </div>
  )
}
