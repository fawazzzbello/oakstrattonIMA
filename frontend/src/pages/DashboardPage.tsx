import { useQuery } from '@tanstack/react-query'
import {
  TrendingUp, Users, Megaphone, DollarSign,
  AlertCircle, CheckCircle2, Clock, ArrowUpRight,
} from 'lucide-react'
import api from '@/utils/api'
import type { AgencyOverview } from '@/types'

function StatCard({
  label, value, icon: Icon, trend, color = 'bg-primary/10 text-primary',
}: {
  label: string
  value: string | number
  icon: React.ElementType
  trend?: string
  color?: string
}) {
  return (
    <div className="bg-card rounded-xl border border-border p-5">
      <div className="flex items-center justify-between mb-3">
        <span className="text-sm text-muted-foreground font-medium">{label}</span>
        <div className={`w-9 h-9 rounded-lg flex items-center justify-center ${color}`}>
          <Icon size={18} />
        </div>
      </div>
      <div className="text-2xl font-bold">{value}</div>
      {trend && (
        <div className="flex items-center gap-1 mt-1 text-xs text-muted-foreground">
          <ArrowUpRight size={12} className="text-green-500" />
          <span className="text-green-600">{trend}</span>
        </div>
      )}
    </div>
  )
}

function formatCurrency(value: number) {
  return new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD', notation: 'compact' }).format(value)
}

export default function DashboardPage() {
  const { data: overview, isLoading } = useQuery({
    queryKey: ['analytics', 'overview'],
    queryFn: async () => {
      const { data } = await api.get<AgencyOverview>('/analytics/overview')
      return data
    },
  })

  if (isLoading) {
    return (
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-5">
        {Array.from({ length: 8 }).map((_, i) => (
          <div key={i} className="bg-card rounded-xl border border-border p-5 h-28 animate-pulse" />
        ))}
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold">Dashboard</h1>
        <p className="text-muted-foreground mt-1">Welcome back — here's your agency overview.</p>
      </div>

      {/* KPI Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
        <StatCard
          label="Active Campaigns"
          value={overview?.active_campaigns ?? 0}
          icon={Megaphone}
          color="bg-blue-100 text-blue-600"
        />
        <StatCard
          label="Total Influencers"
          value={overview?.total_influencers ?? 0}
          icon={Users}
          color="bg-purple-100 text-purple-600"
        />
        <StatCard
          label="Revenue YTD"
          value={formatCurrency(overview?.total_revenue_ytd ?? 0)}
          icon={DollarSign}
          color="bg-green-100 text-green-600"
        />
        <StatCard
          label="Payouts YTD"
          value={formatCurrency(overview?.total_payout_ytd ?? 0)}
          icon={TrendingUp}
          color="bg-orange-100 text-orange-600"
        />
      </div>

      {/* Secondary Stats */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
        <StatCard
          label="Completed Campaigns"
          value={overview?.completed_campaigns ?? 0}
          icon={CheckCircle2}
          color="bg-emerald-100 text-emerald-600"
        />
        <StatCard
          label="Active Influencers"
          value={overview?.active_influencers ?? 0}
          icon={Users}
          color="bg-cyan-100 text-cyan-600"
        />
        <StatCard
          label="Pending Invoices"
          value={overview?.pending_invoices ?? 0}
          icon={Clock}
          color="bg-yellow-100 text-yellow-600"
        />
        <StatCard
          label="Overdue Invoices"
          value={overview?.overdue_invoices ?? 0}
          icon={AlertCircle}
          color="bg-red-100 text-red-600"
        />
      </div>

      {/* Quick Actions */}
      <div className="bg-card rounded-xl border border-border p-6">
        <h2 className="font-semibold mb-4">Quick Actions</h2>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
          {[
            { label: 'New Campaign', href: '/campaigns', color: 'bg-blue-50 text-blue-700 hover:bg-blue-100' },
            { label: 'Add Influencer', href: '/influencers', color: 'bg-purple-50 text-purple-700 hover:bg-purple-100' },
            { label: 'Create Invoice', href: '/payments', color: 'bg-green-50 text-green-700 hover:bg-green-100' },
            { label: 'View Analytics', href: '/analytics', color: 'bg-orange-50 text-orange-700 hover:bg-orange-100' },
          ].map(({ label, href, color }) => (
            <a
              key={label}
              href={href}
              className={`flex items-center justify-center p-3 rounded-lg text-sm font-medium transition-colors ${color}`}
            >
              {label}
            </a>
          ))}
        </div>
      </div>
    </div>
  )
}
