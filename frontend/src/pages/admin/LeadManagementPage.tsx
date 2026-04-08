import { useEffect, useState } from "react";
import { Search, Filter, Plus, Edit2, Trash2, ArrowUpRight } from "lucide-react";

interface Lead {
  id: number;
  company_name: string;
  contact_name: string;
  contact_email: string;
  status: string;
  source: string;
  lead_score: number;
  qualified: boolean;
  estimated_budget?: number;
  industry?: string;
  created_at: string;
}

export default function LeadManagementPage() {
  const [leads, setLeads] = useState<Lead[]>([]);
  const [filteredLeads, setFilteredLeads] = useState<Lead[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState("");
  const [statusFilter, setStatusFilter] = useState<string>("");
  const [showModal, setShowModal] = useState(false);
  const [editingLead, setEditingLead] = useState<Lead | null>(null);

  const statuses = ["new", "contacted", "qualified", "in_demo", "proposal_sent", "negotiating", "won", "lost", "unqualified"];
  const sources = ["website", "referral", "linkedin", "demo_request", "email_campaign", "partnership", "other"];

  useEffect(() => {
    fetchLeads();
  }, []);

  useEffect(() => {
    filterLeads();
  }, [leads, searchTerm, statusFilter]);

  const fetchLeads = async () => {
    try {
      const url = new URL("/api/v1/admin/sales/leads", window.location.origin);
      if (statusFilter) {
        url.searchParams.append("status", statusFilter);
      }
      const response = await fetch(url);
      if (response.ok) {
        const result = await response.json();
        setLeads(result.items || []);
      }
    } catch (error) {
      console.error("Failed to fetch leads:", error);
    } finally {
      setLoading(false);
    }
  };

  const filterLeads = () => {
    let filtered = leads;

    if (searchTerm) {
      filtered = filtered.filter(
        (lead) =>
          lead.company_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
          lead.contact_email.toLowerCase().includes(searchTerm.toLowerCase()) ||
          lead.contact_name.toLowerCase().includes(searchTerm.toLowerCase())
      );
    }

    if (statusFilter) {
      filtered = filtered.filter((lead) => lead.status === statusFilter);
    }

    setFilteredLeads(filtered);
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case "won":
        return "status-active";
      case "new":
      case "contacted":
        return "status-pending";
      case "lost":
      case "unqualified":
        return "status-cancelled";
      default:
        return "status-ai";
    }
  };

  const getSourceBadgeColor = (source: string) => {
    switch (source) {
      case "linkedin":
        return "bg-blue-400/10 text-blue-400";
      case "referral":
        return "bg-emerald-400/10 text-emerald-400";
      case "demo_request":
        return "bg-violet-400/10 text-violet-400";
      default:
        return "bg-slate-400/10 text-slate-400";
    }
  };

  return (
    <div className="page-container">
      <div className="page-header">
        <div>
          <h1 className="page-title">Lead Management</h1>
          <p className="page-subtitle">Track and manage your prospects through the sales pipeline</p>
        </div>
        <button className="btn-primary" onClick={() => setShowModal(true)}>
          <Plus className="w-4 h-4 mr-2" />
          New Lead
        </button>
      </div>

      {/* Filters */}
      <div className="glass-card p-6 space-y-4">
        <div className="flex items-center gap-4">
          <div className="flex-1 relative">
            <Search className="absolute left-3 top-3 w-4 h-4 text-muted-foreground" />
            <input
              type="text"
              placeholder="Search by company, email, or contact name..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="input-field pl-10 w-full"
            />
          </div>
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="input-field px-4 py-2 bg-card border-border/60"
          >
            <option value="">All Statuses</option>
            {statuses.map((status) => (
              <option key={status} value={status}>
                {status.charAt(0).toUpperCase() + status.slice(1).replace(/_/g, " ")}
              </option>
            ))}
          </select>
        </div>
      </div>

      {/* Leads Table */}
      <div className="glass-card overflow-hidden">
        {loading ? (
          <div className="p-8 text-center">Loading leads...</div>
        ) : filteredLeads.length === 0 ? (
          <div className="p-8 text-center text-muted-foreground">
            No leads found. Create your first lead to get started.
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b border-border/30 bg-card/50">
                  <th className="table-header text-left px-6 py-4">Company</th>
                  <th className="table-header text-left px-6 py-4">Contact</th>
                  <th className="table-header text-left px-6 py-4">Source</th>
                  <th className="table-header text-center px-6 py-4">Score</th>
                  <th className="table-header text-center px-6 py-4">Status</th>
                  <th className="table-header text-right px-6 py-4">Budget</th>
                  <th className="table-header text-center px-6 py-4">Actions</th>
                </tr>
              </thead>
              <tbody>
                {filteredLeads.map((lead) => (
                  <tr key={lead.id} className="table-row hover:bg-card/40 transition-colors">
                    <td className="px-6 py-4">
                      <div>
                        <p className="font-medium">{lead.company_name}</p>
                        {lead.industry && <p className="text-xs text-muted-foreground">{lead.industry}</p>}
                      </div>
                    </td>
                    <td className="px-6 py-4">
                      <div>
                        <p className="text-sm">{lead.contact_name}</p>
                        <p className="text-xs text-muted-foreground">{lead.contact_email}</p>
                      </div>
                    </td>
                    <td className="px-6 py-4">
                      <span className={`text-xs px-2 py-1 rounded-full ${getSourceBadgeColor(lead.source)}`}>
                        {lead.source.replace(/_/g, " ")}
                      </span>
                    </td>
                    <td className="px-6 py-4 text-center">
                      <div className="flex items-center justify-center gap-2">
                        <span className="text-sm font-semibold">{lead.lead_score}</span>
                        {lead.lead_score >= 70 && <ArrowUpRight className="w-4 h-4 text-emerald-400" />}
                      </div>
                    </td>
                    <td className="px-6 py-4 text-center">
                      <span className={`text-xs px-2 py-1 rounded-full ${getStatusColor(lead.status)}`}>
                        {lead.status.replace(/_/g, " ")}
                      </span>
                      {lead.qualified && (
                        <div className="text-xs text-emerald-400 mt-1">✓ Qualified</div>
                      )}
                    </td>
                    <td className="px-6 py-4 text-right">
                      {lead.estimated_budget ? (
                        <span className="text-sm font-medium">${(lead.estimated_budget / 1000).toFixed(0)}K</span>
                      ) : (
                        <span className="text-xs text-muted-foreground">-</span>
                      )}
                    </td>
                    <td className="px-6 py-4 text-center">
                      <div className="flex items-center justify-center gap-2">
                        <button
                          onClick={() => setEditingLead(lead)}
                          className="p-2 hover:bg-card/60 rounded-lg transition-colors"
                          title="Edit"
                        >
                          <Edit2 className="w-4 h-4 text-cyan-400" />
                        </button>
                        <button
                          className="p-2 hover:bg-card/60 rounded-lg transition-colors"
                          title="Delete"
                        >
                          <Trash2 className="w-4 h-4 text-rose-400" />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Stats Summary */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-6">
        <div className="glass-card p-4 text-center">
          <p className="text-2xl font-bold">{leads.length}</p>
          <p className="text-xs text-muted-foreground uppercase mt-2">Total Leads</p>
        </div>
        <div className="glass-card p-4 text-center">
          <p className="text-2xl font-bold text-emerald-400">{leads.filter((l) => l.qualified).length}</p>
          <p className="text-xs text-muted-foreground uppercase mt-2">Qualified</p>
        </div>
        <div className="glass-card p-4 text-center">
          <p className="text-2xl font-bold text-violet-400">{leads.filter((l) => l.status === "won").length}</p>
          <p className="text-xs text-muted-foreground uppercase mt-2">Won</p>
        </div>
        <div className="glass-card p-4 text-center">
          <p className="text-2xl font-bold text-amber-400">
            {(leads.reduce((sum, l) => sum + l.lead_score, 0) / leads.length).toFixed(0)}
          </p>
          <p className="text-xs text-muted-foreground uppercase mt-2">Avg Score</p>
        </div>
      </div>
    </div>
  );
}
