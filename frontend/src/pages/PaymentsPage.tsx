import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { useState } from 'react'
import { Plus, Loader2, Eye } from 'lucide-react'
import api from '@/utils/api'
import { format } from 'date-fns'
import Modal from '@/components/Modal'
import type { Client, PaginatedResponse } from '@/types'

const INVOICE_STATUS: Record<string, { color: string; label: string }> = {
  draft: { color: 'bg-slate-400/10 text-slate-400', label: 'Draft' },
  sent: { color: 'bg-cyan-400/10 text-cyan-400', label: 'Sent' },
  viewed: { color: 'bg-violet-400/10 text-violet-400', label: 'Viewed' },
  partial: { color: 'bg-amber-400/10 text-amber-400', label: 'Partial' },
  paid: { color: 'bg-emerald-400/10 text-emerald-400', label: 'Paid' },
  overdue: { color: 'bg-rose-400/10 text-rose-400', label: 'Overdue' },
  void: { color: 'bg-slate-400/10 text-slate-500', label: 'Void' },
}

const PAYOUT_STATUS: Record<string, string> = {
  pending: 'bg-amber-400/10 text-amber-400',
  approved: 'bg-cyan-400/10 text-cyan-400',
  processing: 'bg-violet-400/10 text-violet-400',
  completed: 'bg-emerald-400/10 text-emerald-400',
  failed: 'bg-rose-400/10 text-rose-400',
  cancelled: 'bg-slate-400/10 text-slate-400',
}

const today = () => new Date().toISOString().split('T')[0]
const in30 = () => {
  const d = new Date(); d.setDate(d.getDate() + 30)
  return d.toISOString().split('T')[0]
}

const emptyInv = {
  client_id: '', campaign_id: '', issue_date: today(), due_date: in30(),
  description: '', amount: '', notes: '', currency: 'USD',
}

export default function PaymentsPage() {
  const queryClient = useQueryClient()
  const [tab, setTab] = useState<'invoices' | 'payouts'>('invoices')
  const [showModal, setShowModal] = useState(false)
  const [viewInvoice, setViewInvoice] = useState<any>(null)
  const [form, setForm] = useState(emptyInv)
  const [formError, setFormError] = useState('')

  const { data: invoices, isLoading: loadingInv } = useQuery({
    queryKey: ['invoices'],
    queryFn: async () => { const { data } = await api.get('/payments/invoices?limit=50'); return data as any },
    enabled: tab === 'invoices',
  })

  const { data: payouts, isLoading: loadingPay } = useQuery({
    queryKey: ['payouts'],
    queryFn: async () => { const { data } = await api.get('/payments/payouts?limit=50'); return data as any },
    enabled: tab === 'payouts',
  })

  const { data: clients } = useQuery({
    queryKey: ['clients-list'],
    queryFn: async () => { const { data } = await api.get<PaginatedResponse<Client>>('/clients?limit=100'); return data.items },
    enabled: showModal,
  })

  const createMutation = useMutation({
    mutationFn: async () => {
      const { data } = await api.post('/payments/invoices', {
        client_id: Number(form.client_id),
        campaign_id: form.campaign_id ? Number(form.campaign_id) : undefined,
        issue_date: form.issue_date,
        due_date: form.due_date,
        currency: form.currency,
        notes: form.notes || undefined,
        line_items: [{
          description: form.description || 'Campaign services',
          quantity: 1,
          unit_price: Number(form.amount),
        }],
      })
      return data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['invoices'] })
      setShowModal(false)
      setForm(emptyInv)
      setFormError('')
    },
    onError: (e: any) => setFormError(e?.response?.data?.detail ?? 'Failed to create invoice'),
  })

  const sendMutation = useMutation({
    mutationFn: (id: number) => api.post(`/payments/invoices/${id}/send`),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['invoices'] }),
  })

  const set = (k: keyof typeof emptyInv) =>
    (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>) =>
      setForm(f => ({ ...f, [k]: e.target.value }))

  return (
    <div className="page-container">
      <div className="page-header">
        <div>
          <h1 className="page-title">Payments</h1>
          <p className="page-subtitle">Invoices and influencer payouts</p>
        </div>
        {tab === 'invoices' && (
          <button onClick={() => setShowModal(true)} className="btn-primary flex items-center gap-2">
            <Plus size={16} /> Create Invoice
          </button>
        )}
      </div>

      <div className="flex gap-1 bg-muted/40 rounded-lg p-1 w-fit">
        {(['invoices', 'payouts'] as const).map((t) => (
          <button key={t} onClick={() => setTab(t)}
            className={`px-4 py-1.5 rounded-md text-sm font-medium transition-colors capitalize ${
              tab === t ? 'bg-card shadow-sm text-foreground' : 'text-muted-foreground hover:text-foreground'
            }`}>{t}</button>
        ))}
      </div>

      {/* Invoices */}
      {tab === 'invoices' && (
        <div className="glass-card overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="table-header border-b border-border/40">
                  <th className="text-left px-5 py-3">Invoice #</th>
                  <th className="text-left px-5 py-3">Status</th>
                  <th className="text-left px-5 py-3">Amount</th>
                  <th className="text-left px-5 py-3">Paid</th>
                  <th className="text-left px-5 py-3">Due Date</th>
                  <th className="text-left px-5 py-3">Actions</th>
                </tr>
              </thead>
              <tbody>
                {loadingInv
                  ? Array.from({ length: 4 }).map((_, i) => (
                      <tr key={i} className="table-row">
                        {Array.from({ length: 6 }).map((_, j) => (
                          <td key={j} className="px-5 py-3"><div className="h-4 bg-muted rounded animate-pulse" /></td>
                        ))}
                      </tr>
                    ))
                  : (invoices?.items ?? []).map((inv: any) => {
                      const cfg = INVOICE_STATUS[inv.status] ?? INVOICE_STATUS.draft
                      return (
                        <tr key={inv.id} className="table-row">
                          <td className="px-5 py-3 font-medium font-mono">{inv.invoice_number}</td>
                          <td className="px-5 py-3">
                            <span className={`status-badge ${cfg.color}`}>{cfg.label}</span>
                          </td>
                          <td className="px-5 py-3 font-medium">
                            ${Number(inv.total_amount).toLocaleString()} {inv.currency}
                          </td>
                          <td className="px-5 py-3 text-muted-foreground">
                            ${Number(inv.amount_paid).toLocaleString()}
                          </td>
                          <td className="px-5 py-3 text-muted-foreground">
                            {format(new Date(inv.due_date), 'MMM d, yyyy')}
                          </td>
                          <td className="px-5 py-3">
                            <div className="flex gap-2">
                              <button onClick={() => setViewInvoice(inv)}
                                className="btn-ghost text-xs flex items-center gap-1 px-2 py-1">
                                <Eye size={13} /> View
                              </button>
                              {inv.status === 'draft' && (
                                <button onClick={() => sendMutation.mutate(inv.id)}
                                  disabled={sendMutation.isPending}
                                  className="text-xs text-cyan-400 hover:underline px-2 py-1 disabled:opacity-50">
                                  Send
                                </button>
                              )}
                            </div>
                          </td>
                        </tr>
                      )
                    })}
                {!loadingInv && !invoices?.items?.length && (
                  <tr>
                    <td colSpan={6} className="px-5 py-16 text-center text-muted-foreground">
                      No invoices yet. Create your first invoice.
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Payouts */}
      {tab === 'payouts' && (
        <div className="glass-card overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="table-header border-b border-border/40">
                  <th className="text-left px-5 py-3">Influencer</th>
                  <th className="text-left px-5 py-3">Status</th>
                  <th className="text-left px-5 py-3">Amount</th>
                  <th className="text-left px-5 py-3">Net Amount</th>
                  <th className="text-left px-5 py-3">Scheduled</th>
                  <th className="text-left px-5 py-3">Description</th>
                </tr>
              </thead>
              <tbody>
                {loadingPay
                  ? Array.from({ length: 4 }).map((_, i) => (
                      <tr key={i} className="table-row">
                        {Array.from({ length: 6 }).map((_, j) => (
                          <td key={j} className="px-5 py-3"><div className="h-4 bg-muted rounded animate-pulse" /></td>
                        ))}
                      </tr>
                    ))
                  : (payouts?.items ?? []).map((p: any) => (
                      <tr key={p.id} className="table-row">
                        <td className="px-5 py-3 font-medium">Influencer #{p.influencer_id}</td>
                        <td className="px-5 py-3">
                          <span className={`status-badge ${PAYOUT_STATUS[p.status] ?? 'bg-muted text-muted-foreground'}`}>
                            {p.status}
                          </span>
                        </td>
                        <td className="px-5 py-3">${Number(p.amount).toLocaleString()} {p.currency}</td>
                        <td className="px-5 py-3">{p.net_amount ? `$${Number(p.net_amount).toLocaleString()}` : '—'}</td>
                        <td className="px-5 py-3 text-muted-foreground">
                          {p.scheduled_date ? format(new Date(p.scheduled_date), 'MMM d, yyyy') : '—'}
                        </td>
                        <td className="px-5 py-3 text-muted-foreground">{p.description ?? '—'}</td>
                      </tr>
                    ))}
                {!loadingPay && !payouts?.items?.length && (
                  <tr>
                    <td colSpan={6} className="px-5 py-16 text-center text-muted-foreground">No payouts yet.</td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Create Invoice Modal */}
      <Modal open={showModal} onClose={() => { setShowModal(false); setFormError('') }} title="Create Invoice">
        <form onSubmit={(e) => { e.preventDefault(); createMutation.mutate() }} className="space-y-4">
          <div>
            <label className="block text-sm font-medium mb-1.5">Client <span className="text-rose-400">*</span></label>
            <select value={form.client_id} onChange={set('client_id')} required className="input-field w-full">
              <option value="">Select client...</option>
              {(clients ?? []).map(c => <option key={c.id} value={c.id}>{c.company_name}</option>)}
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium mb-1.5">Service Description <span className="text-rose-400">*</span></label>
            <input value={form.description} onChange={set('description')} required
              placeholder="e.g. Instagram Campaign — June 2026" className="input-field w-full" />
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium mb-1.5">Amount ($) <span className="text-rose-400">*</span></label>
              <input type="number" min="0" step="0.01" value={form.amount} onChange={set('amount')} required
                placeholder="5000" className="input-field w-full" />
            </div>
            <div>
              <label className="block text-sm font-medium mb-1.5">Currency</label>
              <select value={form.currency} onChange={set('currency')} className="input-field w-full">
                {['USD', 'EUR', 'GBP', 'CAD', 'AUD'].map(c => <option key={c}>{c}</option>)}
              </select>
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium mb-1.5">Issue Date <span className="text-rose-400">*</span></label>
              <input type="date" value={form.issue_date} onChange={set('issue_date')} required className="input-field w-full" />
            </div>
            <div>
              <label className="block text-sm font-medium mb-1.5">Due Date <span className="text-rose-400">*</span></label>
              <input type="date" value={form.due_date} onChange={set('due_date')} required className="input-field w-full" />
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium mb-1.5">Notes</label>
            <textarea value={form.notes} onChange={set('notes')} rows={2}
              placeholder="Payment terms, additional info..." className="input-field w-full resize-none" />
          </div>

          {formError && <p className="text-destructive text-sm bg-destructive/10 px-3 py-2 rounded-lg">{formError}</p>}

          <div className="flex gap-3 pt-2">
            <button type="button" onClick={() => setShowModal(false)} className="btn-secondary flex-1">Cancel</button>
            <button type="submit" disabled={createMutation.isPending} className="btn-primary flex-1 flex items-center justify-center gap-2 disabled:opacity-50">
              {createMutation.isPending ? <><Loader2 size={16} className="animate-spin" /> Creating...</> : 'Create Invoice'}
            </button>
          </div>
        </form>
      </Modal>

      {/* View Invoice Modal */}
      {viewInvoice && (
        <Modal open={!!viewInvoice} onClose={() => setViewInvoice(null)} title={`Invoice ${viewInvoice.invoice_number}`}>
          <div className="space-y-4 text-sm">
            <div className="grid grid-cols-2 gap-4">
              <div><p className="text-muted-foreground">Status</p>
                <p className="font-medium">{INVOICE_STATUS[viewInvoice.status]?.label ?? viewInvoice.status}</p></div>
              <div><p className="text-muted-foreground">Total Amount</p>
                <p className="font-medium">${Number(viewInvoice.total_amount).toLocaleString()} {viewInvoice.currency}</p></div>
              <div><p className="text-muted-foreground">Amount Paid</p>
                <p className="font-medium">${Number(viewInvoice.amount_paid).toLocaleString()}</p></div>
              <div><p className="text-muted-foreground">Due Date</p>
                <p className="font-medium">{format(new Date(viewInvoice.due_date), 'MMM d, yyyy')}</p></div>
            </div>
            {viewInvoice.line_items?.length > 0 && (
              <div>
                <p className="text-muted-foreground mb-2">Line Items</p>
                <div className="space-y-2">
                  {viewInvoice.line_items.map((item: any, i: number) => (
                    <div key={i} className="flex justify-between bg-muted/20 px-3 py-2 rounded-lg text-xs">
                      <span>{item.description}</span>
                      <span className="font-medium">${(item.quantity * item.unit_price).toLocaleString()}</span>
                    </div>
                  ))}
                </div>
              </div>
            )}
            {viewInvoice.notes && (
              <div><p className="text-muted-foreground mb-1">Notes</p>
                <p className="text-xs bg-muted/20 px-3 py-2 rounded-lg">{viewInvoice.notes}</p></div>
            )}
          </div>
        </Modal>
      )}
    </div>
  )
}
