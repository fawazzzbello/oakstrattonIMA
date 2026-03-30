import { useQuery } from '@tanstack/react-query'
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  LineChart, Line, PieChart, Pie, Cell, Legend,
} from 'recharts'
import api from '@/utils/api'
import type { AgencyOverview } from '@/types'

const COLORS = ['#a855f7', '#3b82f6', '#10b981', '#f59e0b', '#ef4444']

export default function AnalyticsPage() {
  const { data: overview, isLoading } = useQuery({
    queryKey: ['analytics', 'overview'],
    queryFn: async () => {
      const { data } = await api.get<AgencyOverview>('/analytics/overview')
      return data
    },
  })

  const { data: campaigns } = useQuery({
    queryKey: ['analytics', 'campaigns'],
    queryFn: async () => {
      const { data } = await api.get('/analytics/campaigns?limit=10')
      return data as any[]
    },
  })

  const campaignStatusData = overview ? [
    { name: 'Active', value: overview.active_campaigns },
    { name: 'Completed', value: overview.completed_campaigns },
    { name: 'Other', value: overview.total_campaigns - overview.active_campaigns - overview.completed_campaigns },
  ].filter(d => d.value > 0) : []

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold">Analytics</h1>
        <p className="text-muted-foreground mt-1">Agency performance overview</p>
      </div>

      {/* Revenue vs Payouts chart */}
      <div className="bg-card rounded-xl border border-border p-6">
        <h2 className="font-semibold mb-4">Revenue vs Payouts (YTD)</h2>
        <ResponsiveContainer width="100%" height={280}>
          <BarChart data={[
            {
              name: 'This Year',
              Revenue: Number(overview?.total_revenue_ytd ?? 0),
              Payouts: Number(overview?.total_payout_ytd ?? 0),
              Net: Number(overview?.total_revenue_ytd ?? 0) - Number(overview?.total_payout_ytd ?? 0),
            },
          ]}>
            <CartesianGrid strokeDasharray="3 3" className="opacity-50" />
            <XAxis dataKey="name" />
            <YAxis tickFormatter={(v) => `$${(v / 1000).toFixed(0)}k`} />
            <Tooltip formatter={(v: number) => [`$${v.toLocaleString()}`, '']} />
            <Legend />
            <Bar dataKey="Revenue" fill="#a855f7" radius={[4, 4, 0, 0]} />
            <Bar dataKey="Payouts" fill="#3b82f6" radius={[4, 4, 0, 0]} />
            <Bar dataKey="Net" fill="#10b981" radius={[4, 4, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Campaign Status Breakdown */}
        <div className="bg-card rounded-xl border border-border p-6">
          <h2 className="font-semibold mb-4">Campaign Status</h2>
          {campaignStatusData.length > 0 ? (
            <ResponsiveContainer width="100%" height={220}>
              <PieChart>
                <Pie
                  data={campaignStatusData}
                  cx="50%"
                  cy="50%"
                  innerRadius={60}
                  outerRadius={90}
                  paddingAngle={3}
                  dataKey="value"
                >
                  {campaignStatusData.map((_, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip />
                <Legend />
              </PieChart>
            </ResponsiveContainer>
          ) : (
            <div className="h-56 flex items-center justify-center text-muted-foreground text-sm">
              No campaign data yet
            </div>
          )}
        </div>

        {/* Influencer Stats */}
        <div className="bg-card rounded-xl border border-border p-6">
          <h2 className="font-semibold mb-4">Influencer Roster</h2>
          <ResponsiveContainer width="100%" height={220}>
            <BarChart data={[
              { name: 'Total', count: overview?.total_influencers ?? 0 },
              { name: 'Active', count: overview?.active_influencers ?? 0 },
            ]}>
              <CartesianGrid strokeDasharray="3 3" className="opacity-50" />
              <XAxis dataKey="name" />
              <YAxis />
              <Tooltip />
              <Bar dataKey="count" fill="#a855f7" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Campaign Performance Table */}
      {campaigns && campaigns.length > 0 && (
        <div className="bg-card rounded-xl border border-border p-6">
          <h2 className="font-semibold mb-4">Top Campaign Performance</h2>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="text-left text-muted-foreground border-b border-border">
                  <th className="pb-3 font-medium">Campaign</th>
                  <th className="pb-3 font-medium">Status</th>
                  <th className="pb-3 font-medium">Reach</th>
                  <th className="pb-3 font-medium">Eng. Rate</th>
                  <th className="pb-3 font-medium">Spend</th>
                  <th className="pb-3 font-medium">ROAS</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-border">
                {campaigns.map((c: any) => (
                  <tr key={c.campaign_id}>
                    <td className="py-3 font-medium">{c.campaign_name}</td>
                    <td className="py-3">
                      <span className="text-xs px-2 py-0.5 rounded-full bg-muted capitalize">{c.status}</span>
                    </td>
                    <td className="py-3">{c.total_reach?.toLocaleString() ?? '—'}</td>
                    <td className="py-3">
                      {c.avg_engagement_rate ? `${(c.avg_engagement_rate * 100).toFixed(1)}%` : '—'}
                    </td>
                    <td className="py-3">
                      {c.total_spend ? `$${Number(c.total_spend).toLocaleString()}` : '—'}
                    </td>
                    <td className="py-3">{c.roas ? `${c.roas}x` : '—'}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  )
}
