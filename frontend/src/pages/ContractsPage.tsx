import { useQuery } from '@tanstack/react-query'
import { FileText, CheckCircle, Clock, XCircle } from 'lucide-react'
import api from '@/utils/api'
import { format } from 'date-fns'

const STATUS_CONFIG: Record<string, { label: string; color: string; icon: React.ElementType }> = {
  draft: { label: 'Draft', color: 'bg-gray-100 text-gray-600', icon: FileText },
  sent: { label: 'Sent', color: 'bg-blue-100 text-blue-700', icon: Clock },
  signed_influencer: { label: 'Pending Agency', color: 'bg-yellow-100 text-yellow-700', icon: Clock },
  signed_agency: { label: 'Pending Influencer', color: 'bg-yellow-100 text-yellow-700', icon: Clock },
  fully_executed: { label: 'Fully Executed', color: 'bg-green-100 text-green-700', icon: CheckCircle },
  voided: { label: 'Voided', color: 'bg-red-100 text-red-700', icon: XCircle },
}

export default function ContractsPage() {
  const { data, isLoading } = useQuery({
    queryKey: ['contracts'],
    queryFn: async () => {
      const { data } = await api.get('/contracts?limit=100')
      return data as any
    },
  })

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">Contracts</h1>
          <p className="text-muted-foreground mt-1">{data?.total ?? 0} contracts</p>
        </div>
        <div className="flex gap-2">
          <button className="border border-border px-4 py-2 rounded-lg text-sm font-medium hover:bg-muted">
            Manage Templates
          </button>
          <button className="bg-primary text-primary-foreground px-4 py-2 rounded-lg text-sm font-medium hover:bg-primary/90">
            + New Contract
          </button>
        </div>
      </div>

      <div className="bg-card rounded-xl border border-border overflow-hidden">
        <table className="w-full text-sm">
          <thead className="bg-muted/50">
            <tr className="text-left text-muted-foreground">
              <th className="px-4 py-3 font-medium">Title</th>
              <th className="px-4 py-3 font-medium">Status</th>
              <th className="px-4 py-3 font-medium">Fee</th>
              <th className="px-4 py-3 font-medium">Effective Date</th>
              <th className="px-4 py-3 font-medium">Signed</th>
              <th className="px-4 py-3 font-medium">Actions</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-border">
            {isLoading ? (
              Array.from({ length: 4 }).map((_, i) => (
                <tr key={i}>
                  {Array.from({ length: 6 }).map((_, j) => (
                    <td key={j} className="px-4 py-3">
                      <div className="h-4 bg-muted rounded animate-pulse" />
                    </td>
                  ))}
                </tr>
              ))
            ) : (data?.items ?? []).map((contract: any) => {
              const statusCfg = STATUS_CONFIG[contract.status] ?? STATUS_CONFIG.draft
              const StatusIcon = statusCfg.icon
              return (
                <tr key={contract.id} className="hover:bg-muted/30">
                  <td className="px-4 py-3 font-medium">{contract.title}</td>
                  <td className="px-4 py-3">
                    <span className={`inline-flex items-center gap-1.5 text-xs px-2.5 py-1 rounded-full font-medium ${statusCfg.color}`}>
                      <StatusIcon size={12} />
                      {statusCfg.label}
                    </span>
                  </td>
                  <td className="px-4 py-3">
                    {contract.total_fee ? `$${Number(contract.total_fee).toLocaleString()} ${contract.currency}` : '—'}
                  </td>
                  <td className="px-4 py-3 text-muted-foreground">
                    {contract.effective_date ? format(new Date(contract.effective_date), 'MMM d, yyyy') : '—'}
                  </td>
                  <td className="px-4 py-3 text-muted-foreground">
                    {contract.influencer_signed_at ? '✓ Both' : contract.agency_signed_at ? '½ Agency' : '—'}
                  </td>
                  <td className="px-4 py-3">
                    <button className="text-primary hover:underline text-xs">View</button>
                  </td>
                </tr>
              )
            })}
            {!isLoading && !data?.items?.length && (
              <tr>
                <td colSpan={6} className="px-4 py-12 text-center text-muted-foreground">
                  No contracts yet. Create your first contract.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  )
}
