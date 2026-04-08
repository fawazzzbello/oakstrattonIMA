import { useEffect, useState } from "react";
import { Plus, Edit2, Trash2, Mail, Phone, Briefcase, Users } from "lucide-react";

interface Contact {
  id: number;
  lead_id: number;
  full_name: string;
  email: string;
  phone?: string;
  title?: string;
  department?: string;
  is_primary_contact: boolean;
  decision_maker: boolean;
  influencer: boolean;
  email_opens: number;
  email_clicks: number;
  last_contact_at?: string;
  engagement_score: number;
  calendar_synced: boolean;
  created_at: string;
}

interface Lead {
  id: number;
  company_name: string;
}

export default function ContactManagementPage() {
  const [contacts, setContacts] = useState<Contact[]>([]);
  const [leads, setLeads] = useState<Lead[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedLeadId, setSelectedLeadId] = useState<number | null>(null);
  const [showModal, setShowModal] = useState(false);
  const [editingContact, setEditingContact] = useState<Contact | null>(null);

  useEffect(() => {
    Promise.all([fetchContacts(), fetchLeads()]).finally(() => setLoading(false));
  }, []);

  const fetchContacts = async () => {
    try {
      const response = await fetch("/api/v1/admin/sales/contacts");
      if (response.ok) {
        const data = await response.json();
        setContacts(data);
      }
    } catch (error) {
      console.error("Failed to fetch contacts:", error);
    }
  };

  const fetchLeads = async () => {
    try {
      const response = await fetch("/api/v1/admin/sales/leads?limit=1000");
      if (response.ok) {
        const result = await response.json();
        setLeads(result.items || []);
      }
    } catch (error) {
      console.error("Failed to fetch leads:", error);
    }
  };

  const filteredContacts = selectedLeadId
    ? contacts.filter((c) => c.lead_id === selectedLeadId)
    : contacts;

  const getLeadName = (leadId: number) => {
    return leads.find((l) => l.id === leadId)?.company_name || "Unknown";
  };

  return (
    <div className="page-container">
      <div className="page-header">
        <div>
          <h1 className="page-title">Contact Management</h1>
          <p className="page-subtitle">Manage decision makers and influencers at prospect companies</p>
        </div>
        <button className="btn-primary" onClick={() => setShowModal(true)}>
          <Plus className="w-4 h-4 mr-2" />
          New Contact
        </button>
      </div>

      {/* Filter by Lead */}
      <div className="glass-card p-4">
        <label className="text-sm font-medium mb-2 block">Filter by Company</label>
        <select
          value={selectedLeadId || ""}
          onChange={(e) => setSelectedLeadId(e.target.value ? parseInt(e.target.value) : null)}
          className="input-field w-full"
        >
          <option value="">All Companies</option>
          {leads.map((lead) => (
            <option key={lead.id} value={lead.id}>
              {lead.company_name}
            </option>
          ))}
        </select>
      </div>

      {/* Contacts Grid */}
      {loading ? (
        <div className="glass-card p-8 text-center">Loading contacts...</div>
      ) : filteredContacts.length === 0 ? (
        <div className="glass-card p-8 text-center">
          <Users className="w-12 h-12 mx-auto text-muted-foreground opacity-50 mb-4" />
          <p className="text-muted-foreground">No contacts found</p>
          <button className="btn-primary mt-4" onClick={() => setShowModal(true)}>
            <Plus className="w-4 h-4 mr-2" />
            Add First Contact
          </button>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {filteredContacts.map((contact) => (
            <div key={contact.id} className="glass-card p-6 hover:border-primary/30 transition-colors">
              <div className="flex items-start justify-between mb-4">
                <div>
                  <h3 className="text-lg font-semibold">{contact.full_name}</h3>
                  <p className="text-sm text-muted-foreground">{getLeadName(contact.lead_id)}</p>
                </div>
                <div className="flex gap-2">
                  <button
                    onClick={() => setEditingContact(contact)}
                    className="p-2 hover:bg-card/60 rounded transition-colors"
                  >
                    <Edit2 className="w-4 h-4 text-cyan-400" />
                  </button>
                  <button className="p-2 hover:bg-card/60 rounded transition-colors">
                    <Trash2 className="w-4 h-4 text-rose-400" />
                  </button>
                </div>
              </div>

              {/* Role Badges */}
              <div className="flex flex-wrap gap-2 mb-4">
                {contact.decision_maker && (
                  <span className="status-active text-xs px-2 py-1">Decision Maker</span>
                )}
                {contact.is_primary_contact && (
                  <span className="status-ai text-xs px-2 py-1">Primary</span>
                )}
                {contact.influencer && (
                  <span className="bg-amber-400/10 text-amber-400 text-xs px-2 py-1 rounded">
                    Influencer
                  </span>
                )}
              </div>

              {/* Contact Info */}
              <div className="space-y-2 mb-4">
                <div className="flex items-center gap-2 text-sm">
                  <Mail className="w-4 h-4 text-muted-foreground" />
                  <a href={`mailto:${contact.email}`} className="text-cyan-400 hover:underline">
                    {contact.email}
                  </a>
                </div>
                {contact.phone && (
                  <div className="flex items-center gap-2 text-sm">
                    <Phone className="w-4 h-4 text-muted-foreground" />
                    <span>{contact.phone}</span>
                  </div>
                )}
                {contact.title && (
                  <div className="flex items-center gap-2 text-sm">
                    <Briefcase className="w-4 h-4 text-muted-foreground" />
                    <span>{contact.title}</span>
                  </div>
                )}
              </div>

              {/* Engagement Metrics */}
              <div className="border-t border-border/30 pt-4">
                <div className="grid grid-cols-3 gap-4">
                  <div>
                    <p className="text-xs text-muted-foreground uppercase">Email Score</p>
                    <p className="text-lg font-semibold text-cyan-400">{contact.engagement_score}</p>
                  </div>
                  <div>
                    <p className="text-xs text-muted-foreground uppercase">Opens</p>
                    <p className="text-lg font-semibold">{contact.email_opens}</p>
                  </div>
                  <div>
                    <p className="text-xs text-muted-foreground uppercase">Clicks</p>
                    <p className="text-lg font-semibold">{contact.email_clicks}</p>
                  </div>
                </div>
              </div>

              {/* Calendar Status */}
              {contact.calendar_synced && (
                <div className="mt-4 p-2 bg-emerald-400/10 border border-emerald-400/30 rounded text-xs text-emerald-400">
                  ✓ Calendar synced
                </div>
              )}
            </div>
          ))}
        </div>
      )}

      {/* Stats Summary */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-6">
        <div className="glass-card p-4 text-center">
          <p className="text-2xl font-bold">{filteredContacts.length}</p>
          <p className="text-xs text-muted-foreground uppercase mt-2">Total Contacts</p>
        </div>
        <div className="glass-card p-4 text-center">
          <p className="text-2xl font-bold text-emerald-400">
            {filteredContacts.filter((c) => c.decision_maker).length}
          </p>
          <p className="text-xs text-muted-foreground uppercase mt-2">Decision Makers</p>
        </div>
        <div className="glass-card p-4 text-center">
          <p className="text-2xl font-bold text-cyan-400">
            {filteredContacts.filter((c) => c.calendar_synced).length}
          </p>
          <p className="text-xs text-muted-foreground uppercase mt-2">Calendar Synced</p>
        </div>
        <div className="glass-card p-4 text-center">
          <p className="text-2xl font-bold text-amber-400">
            {(
              filteredContacts.reduce((sum, c) => sum + c.engagement_score, 0) / filteredContacts.length
            ).toFixed(0)}
          </p>
          <p className="text-xs text-muted-foreground uppercase mt-2">Avg Engagement</p>
        </div>
      </div>
    </div>
  );
}
