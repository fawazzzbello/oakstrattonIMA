import { useQuery } from '@tanstack/react-query'
import { useState } from 'react'
import { CreditCard, AlertCircle, CheckCircle, Clock } from 'lucide-react'
import api from '@/utils/api'
import { format } from 'date-fns'

const INVOICE_STATUS_CONFIG: Record<string, { color: string; label: string }> = {
  draft: { color: 'bg-gray-100 text-gray-600', label: 'Draft' },
  sent: { color: 'bg-blue-100 text-blue-700', label: 'Sent' },
  viewed: { color: 'bg-indigo-100 text-indigo-700', label: 'Viewed' },
  partial: { color: 'bg-yellow-100 text-yellow-700', label: 'Partial' },
  paid: { color: 'bg-green-100 text-green-700', label: 'Paid' },
  overdue: { color: 'bg-red-100 text-red-700', label: 'Overdue' },
  void: { color: 'bg-gray-100 text-gray-500', label: 'Void' },
}

export default function PaymentsPage() {
  const [tab, setTab] = useState<'invoices' | 'payouts'>('invoices')

  const { data: invoices, isLoading: loadingInvoices } = useQuery({
    queryKey: ['invoices'],
    queryFn: async () => {
      const { data } = await api.get('/payments/invoices?limit=50')
      return data as any
    },
    enabled: tab === 'invoices',
  })

  const { data: payouts, isLoading: loadingPayouts } = useQuery({
    queryKey: ['payouts'],
    queryFn: async () => {
      const { data } = await api.get('/payments/payouts?limit=50')
      return data as any
    },
    enabled: tab === 'payouts',
  })

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">Payments</h1>
          <p className="text-muted-foreground mt-1">Invoices and influencer payouts</p>
        </div>
        <button className="bg-primary text-primary-foreground px-4 py-2 rounded-lg text-sm font-medium hover:bg-primary/90">
          + Create Invoice
        </button>
      </div>

      {/* Tabs */}
      <div className="flex gap-1 bg-muted rounded-lg p-1 w-fit">
        {(['invoices', 'payouts'] as const).map((t) => (
          <button
            key={t}
            onClick={() => setTab(t)}
            className={`px-4 py-1.5 rounded-md text-sm font-medium transition-colors capitalize ${
              tab === t ? 'bg-card shadow-sm text-foreground' : 'text-muted-foreground hover:text-foreground'
            }`}
          >
            {t}
          </button>
        ))}
      </div>

      {/* Invoices Table */}
      {tab === 'invoices' && (
        <div className="bg-card rounded-xl border border-border overflow-hidden">
          <table className="w-full text-sm">
            <thead className="bg-muted/50">
              <tr className="text-left text-muted-foreground">
                <th className="px-4 py-3 font-medium">Invoice #</th>
                <th className="px-4 py-3 font-medium">Status</th>
                <th className="px-4 py-3 font-medium">Amount</th>
                <th className="px-4 py-3 font-medium">Paid</th>
                <th className="px-4 py-3 font-medium">Due Date</th>
                <th className="px-4 py-3 font-medium">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-border">
              {loadingInvoices ? (
                Array.from({ length: 4 }).map((_, i) => (
                  <tr key={i}>
                    {Array.from({ length: 6 }).map((_, j) => (
                      <td key={j} className="px-4 py-3">
                        <div className="h-4 bg-muted rounded animate-pulse" />
                      </td>
                    ))}
                  </tr>
                ))
              ) : (invoices?.items ?? []).map((inv: any) => {
                const cfg = INVOICE_STATUS_CONFIG[inv.status] ?? INVOICE_STATUS_CONFIG.draft
                return (
                  <tr key={inv.id} className="hover:bg-muted/30">
                    <td className="px-4 py-3 font-medium font-mono">{inv.invoice_number}</td>
                    <td className="px-4 py-3">
                      <span className={`text-xs px-2.5 py-1 rounded-full font-medium ${cfg.color}`}>
                        {cfg.label}
                      </span>
                    </td>
                    <td className="px-4 py-3 font-medium">
                      ${Number(inv.total_amount).toLocaleString()} {inv.currency}
                    </td>
                    <td className="px-4 py-3 text-muted-foreground">
                      ${Number(inv.amount_paid).toLocaleString()}
                    </td>
                    <td className="px-4 py-3 text-muted-foreground">
                      {format(new Date(inv.due_date), 'MMM d, yyyy')}
                    </td>
                    <td className="px-4 py-3 flex gap-2">
                      <button className="text-primary hover:underline text-xs">View</button>
                      {inv.status === 'draft' && (
                        <button className="text-muted-foreground hover:underline text-xs">Send</button>
                      )}
                    </td>
                  </tr>
                )
              })}
              {!loadingInvoices && !invoices?.items?.length && (
                <tr>
                  <td colSpan={6} className="px-4 py-12 text-center text-muted-foreground">
                    No invoices yet.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      )}

      {/* Payouts Table */}
      {tab === 'payouts' && (
        <div className="bg-card rounded-xl border border-border overflow-hidden">
          <table className="w-full text-sm">
            <thead className="bg-muted/50">
              <tr className="text-left text-muted-foreground">
                <th className="px-4 py-3 font-medium">Influencer</th>
                <th className="px-4 py-3 font-medium">Status</th>
                <th className="px-4 py-3 font-medium">Amount</th>
                <th className="px-4 py-3 font-medium">Net Amount</th>
                <th className="px-4 py-3 font-medium">Scheduled</th>
                <th className="px-4 py-3 font-medium">Description</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-border">
              {loadingPayouts ? (
                Array.from({ length: 4 }).map((_, i) => (
                  <tr key={i}>
                    {Array.from({ length: 6 }).map((_, j) => (
                      <td key={j} className="px-4 py-3">
                        <div className="h-4 bg-muted rounded animate-pulse" />
                      </td>
                    ))}
                  </tr>
                ))
              ) : (payouts?.items ?? []).map((payout: any) => (
                <tr key={payout.id} className="hover:bg-muted/30">
                  <td className="px-4 py-3 font-medium">#{payout.influencer_id}</td>
                  <td className="px-4 py-3">
                    <span className="text-xs px-2.5 py-1 rounded-full font-medium bg-muted capitalize">
                      {payout.status}
                    </span>
                  </td>
                  <td className="px-4 py-3">${Number(payout.amount).toLocaleString()} {payout.currency}</td>
                  <td className="px-4 py-3">{payout.net_amount ? `$${Number(payout.net_amount).toLocaleString()}` : '—'}</td>
                  <td className="px-4 py-3 text-muted-foreground">
                    {payout.scheduled_date ? format(new Date(payout.scheduled_date), 'MMM d, yyyy') : '—'}
                  </td>
                  <td className="px-4 py-3 text-muted-foreground">{payout.description ?? '—'}</td>
                </tr>
              ))}
              {!loadingPayouts && !payouts?.items?.length && (
                <tr>
                  <td colSpan={6} className="px-4 py-12 text-center text-muted-foreground">
                    No payouts yet.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
}
