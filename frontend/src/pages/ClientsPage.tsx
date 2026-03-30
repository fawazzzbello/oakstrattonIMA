import { useQuery } from '@tanstack/react-query'
import { useState } from 'react'
import { Building2, Search } from 'lucide-react'
import api from '@/utils/api'
import type { Client, PaginatedResponse } from '@/types'

const STATUS_COLORS: Record<string, string> = {
  lead: 'bg-blue-100 text-blue-700',
  active: 'bg-green-100 text-green-700',
  paused: 'bg-yellow-100 text-yellow-700',
  churned: 'bg-gray-100 text-gray-600',
}

export default function ClientsPage() {
  const [search, setSearch] = useState('')

  const { data, isLoading } = useQuery({
    queryKey: ['clients'],
    queryFn: async () => {
      const { data } = await api.get<PaginatedResponse<Client>>('/clients?limit=100')
      return data
    },
  })

  const filtered = data?.items.filter((c) =>
    !search || c.company_name.toLowerCase().includes(search.toLowerCase())
  )

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">Clients</h1>
          <p className="text-muted-foreground mt-1">{data?.total ?? 0} clients</p>
        </div>
        <button className="bg-primary text-primary-foreground px-4 py-2 rounded-lg text-sm font-medium hover:bg-primary/90">
          + Add Client
        </button>
      </div>

      <div className="relative max-w-sm">
        <Search size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground" />
        <input
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          placeholder="Search clients..."
          className="w-full pl-9 pr-3 py-2 rounded-lg border border-input bg-background text-sm focus:outline-none focus:ring-2 focus:ring-ring"
        />
      </div>

      <div className="bg-card rounded-xl border border-border overflow-hidden">
        <table className="w-full text-sm">
          <thead className="bg-muted/50">
            <tr className="text-left text-muted-foreground">
              <th className="px-4 py-3 font-medium">Company</th>
              <th className="px-4 py-3 font-medium">Industry</th>
              <th className="px-4 py-3 font-medium">Status</th>
              <th className="px-4 py-3 font-medium">Monthly Budget</th>
              <th className="px-4 py-3 font-medium">Billing Email</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-border">
            {isLoading
              ? Array.from({ length: 5 }).map((_, i) => (
                  <tr key={i}>
                    {Array.from({ length: 5 }).map((_, j) => (
                      <td key={j} className="px-4 py-3">
                        <div className="h-4 bg-muted rounded animate-pulse" />
                      </td>
                    ))}
                  </tr>
                ))
              : (filtered ?? []).map((client) => (
                  <tr key={client.id} className="hover:bg-muted/30 transition-colors">
                    <td className="px-4 py-3">
                      <div className="flex items-center gap-2.5">
                        <div className="w-8 h-8 rounded-lg bg-primary/10 flex items-center justify-center">
                          <Building2 size={14} className="text-primary" />
                        </div>
                        <span className="font-medium">{client.company_name}</span>
                      </div>
                    </td>
                    <td className="px-4 py-3 text-muted-foreground">{client.industry ?? '—'}</td>
                    <td className="px-4 py-3">
                      <span className={`text-xs px-2.5 py-1 rounded-full font-medium ${STATUS_COLORS[client.status]}`}>
                        {client.status}
                      </span>
                    </td>
                    <td className="px-4 py-3">
                      {client.monthly_budget
                        ? `$${Number(client.monthly_budget).toLocaleString()} ${client.currency}`
                        : '—'}
                    </td>
                    <td className="px-4 py-3 text-muted-foreground">{client.billing_email ?? '—'}</td>
                  </tr>
                ))}
            {!isLoading && filtered?.length === 0 && (
              <tr>
                <td colSpan={5} className="px-4 py-12 text-center text-muted-foreground">
                  No clients found.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  )
}
