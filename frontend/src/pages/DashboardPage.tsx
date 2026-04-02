import { useQuery } from '@tanstack/react-query'
import { Link } from 'react-router-dom'
import {
  Megaphone, Users, DollarSign, TrendingUp,
  Sparkles, ArrowUpRight, ArrowDownRight,
  Bell, CheckCircle2, UserPlus, FileText,
  ChevronRight, Calendar,
} from 'lucide-react'
import {
  AreaChart, Area, XAxis, YAxis, CartesianGrid,
  Tooltip, ResponsiveContainer,
} from 'recharts'
import api from '@/utils/api'
import { useAuthStore } from '@/store/authStore'
import type { AgencyOverview, Notification } from '@/types'

// ── Fallback data ─────────────────────────────────────────
const SAMPLE_INSIGHTS = [
  {
    id: 1,
    title: 'High-performing influencer detected',
    description:
      'Sarah Chen has 3x above-average engagement this month. Consider expanding her campaign scope.',
    link: '/app/influencers',
  },
  {
    id: 2,
    title: 'Campaign budget optimization',
    description:
      'The "Summer Launch" campaign is under-spending by 22%. Reallocate budget to maximize ROI.',
    link: '/app/campaigns',
  },
  {
    id: 3,
    title: 'Trending niche opportunity',
    description:
      'Wellness & self-care content is surging +45% this quarter. 12 influencers in your roster match.',
    link: '/app/influencers',
  },
  {
    id: 4,
    title: 'Content approval bottleneck',
    description:
      '7 deliverables are awaiting review for more than 48 hours. Approve them to keep timelines on track.',
    link: '/app/campaigns',
  },
]

const SAMPLE_CHART_DATA = [
  { month: 'Jul', performance: 4200 },
  { month: 'Aug', performance: 5800 },
  { month: 'Sep', performance: 4900 },
  { month: 'Oct', performance: 7200 },
  { month: 'Nov', performance: 6800 },
  { month: 'Dec', performance: 8100 },
  { month: 'Jan', performance: 7400 },
  { month: 'Feb', performance: 9200 },
  { month: 'Mar', performance: 8800 },
]

const SAMPLE_ACTIVITY = [
  { id: 1, icon: CheckCircle2, text: 'Campaign "Spring Collection" marked as completed', time: '2 hours ago' },
  { id: 2, icon: UserPlus, text: 'New influencer application from @lifestyle_maya', time: '4 hours ago' },
  { id: 3, icon: FileText, text: 'Invoice #INV-0042 paid by Luxe Beauty Co.', time: '6 hours ago' },
  { id: 4, icon: Megaphone, text: 'Campaign "Tech Summit 2026" moved to active', time: '1 day ago' },
  { id: 5, icon: Bell, text: 'Deliverable approved for @fitnessguru on "Wellness Week"', time: '1 day ago' },
  { id: 6, icon: DollarSign, text: 'Payout of $2,400 sent to @travel_adventures', time: '2 days ago' },
  { id: 7, icon: UserPlus, text: 'Influencer @foodie_delights joined the roster', time: '3 days ago' },
  { id: 8, icon: Calendar, text: 'Campaign "Holiday Gift Guide" scheduled for Dec 1', time: '3 days ago' },
]

// ── Helpers ────────────────────────────────────────────────
function formatCurrency(value: number) {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
    notation: 'compact',
    maximumFractionDigits: 1,
  }).format(value)
}

function formatDate() {
  return new Intl.DateTimeFormat('en-US', {
    weekday: 'long',
    year: 'numeric',
    month: 'long',
    day: 'numeric',
  }).format(new Date())
}

function formatRelativeTime(isoString: string): string {
  const diff = Date.now() - new Date(isoString).getTime()
  const minutes = Math.floor(diff / 60000)
  if (minutes < 60) return `${minutes}m ago`
  const hours = Math.floor(minutes / 60)
  if (hours < 24) return `${hours}h ago`
  const days = Math.floor(hours / 24)
  return `${days}d ago`
}

// ── Component ─────────────────────────────────────────────
export default function DashboardPage() {
  const user = useAuthStore((s) => s.user)
  const role = user?.role ?? 'client'
  const isAgencyUser = role === 'admin' || role === 'manager'

  // Agency overview KPIs — only for admin/manager (endpoint requires manager role)
  const { data: overview, isLoading } = useQuery({
    queryKey: ['analytics', 'overview'],
    queryFn: async () => {
      const { data } = await api.get<AgencyOverview>('/analytics/overview')
      return data
    },
    enabled: isAgencyUser,
    retry: false,
  })

  // Notifications for activity feed
  const { data: notifications } = useQuery({
    queryKey: ['notifications'],
    queryFn: async () => {
      const { data } = await api.get<{ items: Notification[] }>('/notifications?limit=8')
      return data.items
    },
    retry: false,
  })

  // AI insights — only for admin/manager
  const { data: aiInsights } = useQuery({
    queryKey: ['ai-insights'],
    queryFn: async () => {
      const { data } = await api.get('/ai/insights')
      return data
    },
    enabled: isAgencyUser,
    retry: false,
  })

  const insights =
    (aiInsights as any)?.items?.length ? (aiInsights as any).items : SAMPLE_INSIGHTS

  const activityItems = notifications?.length
    ? notifications.map((n) => ({
        id: n.id,
        icon: Bell,
        text: n.title,
        time: formatRelativeTime(n.created_at),
      }))
    : SAMPLE_ACTIVITY

  // ── Loading skeleton (only shown for agency users waiting for overview) ──
  if (isAgencyUser && isLoading) {
    return (
      <div className="page-container">
        <div className="h-10 w-72 bg-muted/50 rounded-lg animate-pulse" />
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
          {Array.from({ length: 4 }).map((_, i) => (
            <div key={i} className="glass-card p-5 h-28 animate-pulse" />
          ))}
        </div>
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div className="glass-card p-6 h-80 animate-pulse" />
          <div className="glass-card p-6 h-80 animate-pulse" />
        </div>
        <div className="glass-card p-6 h-64 animate-pulse" />
      </div>
    )
  }

  const kpis = [
    {
      label: 'Active Campaigns',
      value: overview?.active_campaigns ?? 0,
      icon: Megaphone,
      iconBg: 'bg-violet-500/20',
      iconColor: 'text-violet-400',
      change: '+12%',
      up: true,
    },
    {
      label: 'Total Influencers',
      value: overview?.total_influencers ?? 0,
      icon: Users,
      iconBg: 'bg-cyan-500/20',
      iconColor: 'text-cyan-400',
      change: '+8%',
      up: true,
    },
    {
      label: 'Revenue This Month',
      value: formatCurrency(overview?.total_revenue_ytd ?? 0),
      icon: DollarSign,
      iconBg: 'bg-emerald-500/20',
      iconColor: 'text-emerald-400',
      change: '+23%',
      up: true,
    },
    {
      label: 'Avg. Engagement Rate',
      value: overview?.avg_campaign_roi ? `${overview.avg_campaign_roi}%` : '4.2%',
      icon: TrendingUp,
      iconBg: 'bg-amber-500/20',
      iconColor: 'text-amber-400',
      change: '-2%',
      up: false,
    },
  ]

  return (
    <div className="page-container">
      {/* ── Header ── */}
      <div className="page-header">
        <h1 className="text-2xl font-heading font-bold">
          Welcome back,{' '}
          <span className="gradient-text">{user?.full_name ?? 'Team'}</span>
        </h1>
        <p className="page-subtitle mt-1">{formatDate()}</p>
      </div>

      {/* ── KPI Cards (agency users only) ── */}
      {isAgencyUser && (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
          {kpis.map((kpi) => {
            const Icon = kpi.icon
            return (
              <div key={kpi.label} className="glass-card-hover p-5">
                <div className="flex items-center justify-between mb-3">
                  <span className="text-sm text-muted-foreground">{kpi.label}</span>
                  <div
                    className={`w-9 h-9 rounded-lg flex items-center justify-center ${kpi.iconBg}`}
                  >
                    <Icon size={18} className={kpi.iconColor} />
                  </div>
                </div>
                <div className="text-2xl font-bold font-heading">{kpi.value}</div>
                <div className="flex items-center gap-1 mt-1.5 text-xs">
                  {kpi.up ? (
                    <ArrowUpRight size={14} className="text-emerald-400" />
                  ) : (
                    <ArrowDownRight size={14} className="text-rose-400" />
                  )}
                  <span className={kpi.up ? 'text-emerald-400' : 'text-rose-400'}>
                    {kpi.change}
                  </span>
                  <span className="text-muted-foreground ml-0.5">vs last month</span>
                </div>
              </div>
            )
          })}
        </div>
      )}

      {/* ── AI Insights + Campaign Performance Chart (agency only) ── */}
      {isAgencyUser && <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* AI Insights Panel */}
        <div className="glass-card p-6">
          <div className="flex items-center gap-2 mb-5">
            <Sparkles size={18} className="text-violet-400" />
            <h2 className="font-heading font-semibold text-lg">AI Insights</h2>
            <span className="status-ai">Beta</span>
          </div>

          {insights.length > 0 ? (
            <div className="space-y-4">
              {insights.map((insight: any) => (
                <div key={insight.id} className="flex gap-3">
                  <div className="mt-1.5 w-2 h-2 rounded-full bg-violet-400 shrink-0" />
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium text-foreground">{insight.title}</p>
                    <p className="text-xs text-muted-foreground mt-0.5 leading-relaxed">
                      {insight.description}
                    </p>
                    <Link
                      to={insight.link ?? '#'}
                      className="text-xs text-violet-400 hover:text-violet-300 mt-1 inline-flex items-center gap-1"
                    >
                      View Details <ChevronRight size={12} />
                    </Link>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center py-8">
              <Sparkles size={32} className="text-muted-foreground mx-auto mb-3" />
              <p className="text-sm text-muted-foreground">
                No AI insights yet. Generate your first report.
              </p>
            </div>
          )}
        </div>

        {/* Campaign Performance Chart */}
        <div className="glass-card p-6">
          <h2 className="font-heading font-semibold text-lg mb-5">Campaign Performance</h2>
          <ResponsiveContainer width="100%" height={260}>
            <AreaChart data={SAMPLE_CHART_DATA}>
              <defs>
                <linearGradient id="perfGradient" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0%" stopColor="#7C5CFC" stopOpacity={0.3} />
                  <stop offset="100%" stopColor="#7C5CFC" stopOpacity={0} />
                </linearGradient>
              </defs>
              <CartesianGrid
                strokeDasharray="3 3"
                stroke="#1A2540"
                vertical={false}
              />
              <XAxis
                dataKey="month"
                tick={{ fill: '#7E8FA8', fontSize: 12 }}
                axisLine={{ stroke: '#1A2540' }}
                tickLine={false}
              />
              <YAxis
                tick={{ fill: '#7E8FA8', fontSize: 12 }}
                axisLine={false}
                tickLine={false}
                width={45}
              />
              <Tooltip
                contentStyle={{
                  backgroundColor: '#0E1117',
                  border: '1px solid #1A2540',
                  borderRadius: '8px',
                  color: '#E4EBF8',
                  fontSize: 12,
                }}
              />
              <Area
                type="monotone"
                dataKey="performance"
                stroke="#7C5CFC"
                strokeWidth={2}
                fill="url(#perfGradient)"
              />
            </AreaChart>
          </ResponsiveContainer>
        </div>
      </div>}

      {/* ── Recent Activity ── */}
      <div className="glass-card p-6">
        <h2 className="font-heading font-semibold text-lg mb-4">Recent Activity</h2>
        <div className="space-y-1">
          {activityItems.slice(0, 8).map((item) => {
            const Icon = item.icon
            return (
              <div
                key={item.id}
                className="flex items-start gap-3 py-2.5 border-b border-border/50 last:border-0"
              >
                <div className="w-8 h-8 rounded-lg bg-muted flex items-center justify-center shrink-0 mt-0.5">
                  <Icon size={14} className="text-muted-foreground" />
                </div>
                <div className="flex-1 min-w-0">
                  <p className="text-sm text-foreground">{item.text}</p>
                  <p className="text-xs text-muted-foreground mt-0.5">{item.time}</p>
                </div>
              </div>
            )
          })}
        </div>
      </div>

      {/* ── Quick Actions (role-gated) ── */}
      <div className="flex flex-wrap gap-3">
        {isAgencyUser && (
          <>
            <Link to="/app/campaigns" className="btn-primary inline-flex items-center gap-2">
              <Megaphone size={16} />
              Create Campaign
            </Link>
            <Link to="/app/influencers" className="btn-secondary inline-flex items-center gap-2">
              <Users size={16} />
              Find Influencers
            </Link>
            <Link to="/app/ai-insights" className="btn-secondary inline-flex items-center gap-2">
              <Sparkles size={16} className="text-violet-400" />
              Generate AI Report
            </Link>
          </>
        )}
        {role === 'client' && (
          <Link to="/app/campaigns" className="btn-primary inline-flex items-center gap-2">
            <Megaphone size={16} />
            View My Campaigns
          </Link>
        )}
        {role === 'influencer' && (
          <Link to="/app/my-profile" className="btn-primary inline-flex items-center gap-2">
            <Users size={16} />
            Update My Profile
          </Link>
        )}
        <Link to="/app/contracts" className="btn-secondary inline-flex items-center gap-2">
          <FileText size={16} />
          {isAgencyUser ? 'Contracts' : 'My Contracts'}
        </Link>
      </div>
    </div>
  )
}
