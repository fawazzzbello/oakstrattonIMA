import { useQuery, useQueryClient } from '@tanstack/react-query'
import { useState } from 'react'
import {
  Building2,
  Search,
  Plus,
  X,
  Mail,
  Globe,
  Users,
  DollarSign,
  Filter,
  ExternalLink,
} from 'lucide-react'
import api from '@/utils/api'
import type { Client, PaginatedResponse } from '@/types'

const STATUS_OPTIONS = ['all', 'active', 'lead', 'paused', 'churned'] as const

function statusClass(status: string): string {
  switch (status) {
    case 'active':
      return 'status-active'
    case 'lead':
      return 'status-pending'
    case 'paused':
      return 'status-paused'
    case 'churned':
      return 'status-cancelled'
    default:
      return 'status-badge bg-muted text-muted-foreground'
  }
}

interface ClientFormData {
  company_name: string
  industry: string
  billing_email: string
  company_website: string
  monthly_budget: string
  currency: string
  status: string
  notes: string
}

const emptyForm: ClientFormData = {
  company_name: '',
  industry: '',
  billing_email: '',
  company_website: '',
  monthly_budget: '',
  currency: 'USD',
  status: 'lead',
  notes: '',
}

export default function ClientsPage() {
  const queryClient = useQueryClient()
  const [search, setSearch] = useState('')
  const [statusFilter, setStatusFilter] = useState<string>('all')
  const [showModal, setShowModal] = useState(false)
  const [formData, setFormData] = useState<ClientFormData>(emptyForm)
  const [submitError, setSubmitError] = useState('')

  const { data, isLoading, error } = useQuery({
    queryKey: ['clients'],
    queryFn: async () => {
      const { data } = await api.get<PaginatedResponse<Client>>('/clients?limit=100')
      return data
    },
  })

  const filtered = (data?.items ?? []).filter((c) => {
    const matchSearch =
      !search ||
      c.company_name.toLowerCase().includes(search.toLowerCase()) ||
      c.industry?.toLowerCase().includes(search.toLowerCase())
    const matchStatus = statusFilter === 'all' || c.status === statusFilter
    return matchSearch && matchStatus
  })

  const openAddModal = () => {
    setFormData(emptyForm)
    setShowModal(true)
  }

  const handleFormChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>
  ) => {
    setFormData((prev) => ({ ...prev, [e.target.name]: e.target.value }))
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setSubmitError('')
    try {
      await api.post('/clients', {
        company_name: formData.company_name,
        industry: formData.industry || undefined,
        billing_email: formData.billing_email || undefined,
        company_website: formData.company_website || undefined,
        monthly_budget: formData.monthly_budget ? Number(formData.monthly_budget) : undefined,
        currency: formData.currency,
        notes: formData.notes || undefined,
      })
      setShowModal(false)
      setFormData(emptyForm)
      queryClient.invalidateQueries({ queryKey: ['clients'] })
    } catch (err: any) {
      setSubmitError(err?.response?.data?.detail ?? 'Failed to create client')
    }
  }

  return (
    <div className="page-container">
      {/* Header */}
      <div className="page-header">
        <div>
          <h1 className="page-title">Clients</h1>
          <p className="page-subtitle">Manage your brand clients</p>
        </div>
        <button onClick={openAddModal} className="btn-primary flex items-center gap-2">
          <Plus size={16} />
          Add Client
        </button>
      </div>

      {/* Search & Filters */}
      <div className="flex flex-col sm:flex-row gap-3">
        <div className="relative flex-1 max-w-md">
          <Search
            size={16}
            className="absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground"
          />
          <input
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search by company or industry..."
            className="input-field w-full pl-10"
          />
        </div>
        <div className="flex items-center gap-2">
          <Filter size={14} className="text-muted-foreground" />
          {STATUS_OPTIONS.map((s) => (
            <button
              key={s}
              onClick={() => setStatusFilter(s)}
              className={`px-3 py-1.5 rounded-lg text-xs font-medium capitalize transition-colors ${
                statusFilter === s
                  ? 'bg-primary/20 text-primary border border-primary/30'
                  : 'bg-muted/50 text-muted-foreground hover:text-foreground border border-transparent'
              }`}
            >
              {s}
            </button>
          ))}
        </div>
      </div>

      {/* Error state */}
      {error && (
        <div className="glass-card p-6 text-center">
          <p className="text-rose-400">Failed to load clients. Please try again.</p>
        </div>
      )}

      {/* Loading state */}
      {isLoading && (
        <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
          {Array.from({ length: 6 }).map((_, i) => (
            <div key={i} className="glass-card p-6 space-y-4 animate-pulse">
              <div className="flex items-center gap-3">
                <div className="w-12 h-12 rounded-xl bg-muted" />
                <div className="space-y-2 flex-1">
                  <div className="h-4 w-3/4 bg-muted rounded" />
                  <div className="h-3 w-1/2 bg-muted rounded" />
                </div>
              </div>
              <div className="h-3 w-full bg-muted rounded" />
              <div className="h-3 w-2/3 bg-muted rounded" />
            </div>
          ))}
        </div>
      )}

      {/* Client Cards Grid */}
      {!isLoading && !error && (
        <>
          {filtered.length === 0 ? (
            <div className="glass-card p-12 text-center">
              <Building2 size={40} className="mx-auto text-muted-foreground mb-4" />
              <p className="text-muted-foreground">No clients found.</p>
              <p className="text-sm text-muted-foreground mt-1">
                {search || statusFilter !== 'all'
                  ? 'Try adjusting your search or filters.'
                  : 'Add your first client to get started.'}
              </p>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
              {filtered.map((client) => (
                <div key={client.id} className="glass-card-hover p-6">
                  <div className="flex items-start justify-between mb-4">
                    <div className="flex items-center gap-3">
                      <div className="w-12 h-12 rounded-xl bg-primary/10 flex items-center justify-center flex-shrink-0">
                        {client.logo_url ? (
                          <img
                            src={client.logo_url}
                            alt={client.company_name}
                            className="w-10 h-10 rounded-lg object-cover"
                          />
                        ) : (
                          <Building2 size={20} className="text-primary" />
                        )}
                      </div>
                      <div>
                        <h3 className="font-semibold text-foreground">{client.company_name}</h3>
                        <p className="text-sm text-muted-foreground">{client.industry ?? 'No industry'}</p>
                      </div>
                    </div>
                    <span className={statusClass(client.status)}>{client.status}</span>
                  </div>

                  <div className="space-y-2 mb-4">
                    {client.billing_email && (
                      <div className="flex items-center gap-2 text-sm text-muted-foreground">
                        <Mail size={13} />
                        <span className="truncate">{client.billing_email}</span>
                      </div>
                    )}
                    {client.company_website && (
                      <div className="flex items-center gap-2 text-sm text-muted-foreground">
                        <Globe size={13} />
                        <span className="truncate">{client.company_website}</span>
                      </div>
                    )}
                  </div>

                  <div className="flex items-center justify-between pt-4 border-t border-border/40">
                    <div className="flex items-center gap-4">
                      <div className="flex items-center gap-1.5 text-sm text-muted-foreground">
                        <Users size={13} />
                        <span>0 campaigns</span>
                      </div>
                      {client.monthly_budget && (
                        <div className="flex items-center gap-1.5 text-sm text-muted-foreground">
                          <DollarSign size={13} />
                          <span>
                            ${Number(client.monthly_budget).toLocaleString()}/{client.currency}
                          </span>
                        </div>
                      )}
                    </div>
                    <button className="btn-ghost text-xs flex items-center gap-1 px-2 py-1">
                      View Details <ExternalLink size={12} />
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </>
      )}

      {/* Add/Edit Client Modal */}
      {showModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm">
          <div className="glass-card p-6 w-full max-w-lg mx-4 max-h-[90vh] overflow-y-auto">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-lg font-semibold text-foreground">Add New Client</h2>
              <button
                onClick={() => setShowModal(false)}
                className="text-muted-foreground hover:text-foreground"
              >
                <X size={20} />
              </button>
            </div>

            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-muted-foreground mb-1.5">
                  Company Name *
                </label>
                <input
                  name="company_name"
                  value={formData.company_name}
                  onChange={handleFormChange}
                  required
                  className="input-field w-full"
                  placeholder="Acme Corp"
                />
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-muted-foreground mb-1.5">
                    Industry
                  </label>
                  <input
                    name="industry"
                    value={formData.industry}
                    onChange={handleFormChange}
                    className="input-field w-full"
                    placeholder="Technology"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-muted-foreground mb-1.5">
                    Status
                  </label>
                  <select
                    name="status"
                    value={formData.status}
                    onChange={handleFormChange}
                    className="input-field w-full"
                  >
                    <option value="lead">Lead</option>
                    <option value="active">Active</option>
                    <option value="paused">Paused</option>
                  </select>
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-muted-foreground mb-1.5">
                  Billing Email
                </label>
                <input
                  name="billing_email"
                  type="email"
                  value={formData.billing_email}
                  onChange={handleFormChange}
                  className="input-field w-full"
                  placeholder="billing@acme.com"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-muted-foreground mb-1.5">
                  Website
                </label>
                <input
                  name="company_website"
                  value={formData.company_website}
                  onChange={handleFormChange}
                  className="input-field w-full"
                  placeholder="https://acme.com"
                />
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-muted-foreground mb-1.5">
                    Monthly Budget
                  </label>
                  <input
                    name="monthly_budget"
                    type="number"
                    value={formData.monthly_budget}
                    onChange={handleFormChange}
                    className="input-field w-full"
                    placeholder="10000"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-muted-foreground mb-1.5">
                    Currency
                  </label>
                  <select
                    name="currency"
                    value={formData.currency}
                    onChange={handleFormChange}
                    className="input-field w-full"
                  >
                    <option value="USD">USD</option>
                    <option value="EUR">EUR</option>
                    <option value="GBP">GBP</option>
                  </select>
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-muted-foreground mb-1.5">
                  Notes
                </label>
                <textarea
                  name="notes"
                  value={formData.notes}
                  onChange={handleFormChange}
                  rows={3}
                  className="input-field w-full resize-none"
                  placeholder="Additional notes..."
                />
              </div>

              {submitError && (
                <p className="text-destructive text-sm bg-destructive/10 px-3 py-2 rounded-lg">{submitError}</p>
              )}

              <div className="flex justify-end gap-3 pt-2">
                <button type="button" onClick={() => setShowModal(false)} className="btn-secondary">
                  Cancel
                </button>
                <button type="submit" className="btn-primary">
                  Create Client
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  )
}
