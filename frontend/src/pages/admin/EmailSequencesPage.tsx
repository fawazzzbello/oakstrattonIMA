import { useEffect, useState } from "react";
import { Plus, Edit2, Trash2, Mail, ToggleRight, ToggleLeft } from "lucide-react";
import api from "@/utils/api";

interface EmailSequence {
  id: number;
  name: string;
  description?: string;
  trigger: string;
  is_active: boolean;
  emails: any[];
  total_sent: number;
  active_sequences: number;
  created_at: string;
}

export default function EmailSequencesPage() {
  const [sequences, setSequences] = useState<EmailSequence[]>([]);
  const [loading, setLoading] = useState(true);

  const triggers = [
    { value: "new_lead", label: "New Lead Captured" },
    { value: "qualified", label: "Lead Qualified" },
    { value: "demo_completed", label: "Demo Completed" },
    { value: "proposal_sent", label: "Proposal Sent" },
    { value: "manual", label: "Manual Trigger" },
  ];

  useEffect(() => {
    fetchSequences();
  }, []);

  const fetchSequences = async () => {
    try {
      const { data } = await api.get("/admin/sales/email-sequences");
      setSequences(data);
    } catch (error) {
      console.error("Failed to fetch sequences:", error);
    } finally {
      setLoading(false);
    }
  };

  const getTriggerLabel = (trigger: string) => {
    return triggers.find((t) => t.value === trigger)?.label || trigger;
  };

  return (
    <div className="page-container">
      <div className="page-header">
        <div>
          <h1 className="page-title">Email Sequences</h1>
          <p className="page-subtitle">Manage automated email campaigns for lead nurturing</p>
        </div>
        <button className="btn-primary">
          <Plus className="w-4 h-4 mr-2" />
          New Sequence
        </button>
      </div>

      {/* Info Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
        <div className="glass-card p-4">
          <div className="flex items-center gap-3">
            <Mail className="w-5 h-5 text-violet-400" />
            <div>
              <p className="text-xs text-muted-foreground uppercase">Total Sequences</p>
              <p className="text-2xl font-bold">{sequences.length}</p>
            </div>
          </div>
        </div>

        <div className="glass-card p-4">
          <div className="flex items-center gap-3">
            <Mail className="w-5 h-5 text-emerald-400" />
            <div>
              <p className="text-xs text-muted-foreground uppercase">Active</p>
              <p className="text-2xl font-bold">{sequences.filter((s) => s.is_active).length}</p>
            </div>
          </div>
        </div>

        <div className="glass-card p-4">
          <div className="flex items-center gap-3">
            <Mail className="w-5 h-5 text-amber-400" />
            <div>
              <p className="text-xs text-muted-foreground uppercase">Total Sent</p>
              <p className="text-2xl font-bold">{sequences.reduce((sum, s) => sum + s.total_sent, 0)}</p>
            </div>
          </div>
        </div>
      </div>

      {/* Sequences List */}
      {loading ? (
        <div className="glass-card p-8 text-center">Loading sequences...</div>
      ) : sequences.length === 0 ? (
        <div className="glass-card p-8 text-center">
          <Mail className="w-12 h-12 mx-auto text-muted-foreground opacity-50 mb-4" />
          <p className="text-muted-foreground">No email sequences created yet</p>
          <button className="btn-primary mt-4">
            <Plus className="w-4 h-4 mr-2" />
            Create First Sequence
          </button>
        </div>
      ) : (
        <div className="space-y-4">
          {sequences.map((sequence) => (
            <div key={sequence.id} className="glass-card p-6 hover:border-primary/30 transition-colors">
              <div className="flex items-start justify-between gap-4">
                <div className="flex-1">
                  <div className="flex items-center gap-3 mb-2">
                    <h3 className="text-lg font-semibold">{sequence.name}</h3>
                    {sequence.is_active ? (
                      <span className="status-active text-xs px-2 py-1">Active</span>
                    ) : (
                      <span className="status-paused text-xs px-2 py-1">Inactive</span>
                    )}
                  </div>

                  {sequence.description && (
                    <p className="text-sm text-muted-foreground mb-3">{sequence.description}</p>
                  )}

                  <div className="flex flex-wrap gap-4 text-sm">
                    <div>
                      <p className="text-xs text-muted-foreground uppercase tracking-wider">Trigger</p>
                      <p className="text-sm font-medium text-cyan-400">{getTriggerLabel(sequence.trigger)}</p>
                    </div>

                    <div>
                      <p className="text-xs text-muted-foreground uppercase tracking-wider">Emails</p>
                      <p className="text-sm font-medium">
                        {Array.isArray(sequence.emails) ? sequence.emails.length : 0} steps
                      </p>
                    </div>

                    <div>
                      <p className="text-xs text-muted-foreground uppercase tracking-wider">Total Sent</p>
                      <p className="text-sm font-medium text-amber-400">{sequence.total_sent}</p>
                    </div>

                    <div>
                      <p className="text-xs text-muted-foreground uppercase tracking-wider">Active Sequences</p>
                      <p className="text-sm font-medium text-emerald-400">{sequence.active_sequences}</p>
                    </div>
                  </div>
                </div>

                {/* Email Steps Preview */}
                <div className="min-w-max">
                  <p className="text-xs text-muted-foreground uppercase tracking-wider mb-2">Email Steps</p>
                  <div className="space-y-1 max-w-xs">
                    {Array.isArray(sequence.emails) && sequence.emails.slice(0, 3).map((email, idx) => (
                      <div
                        key={idx}
                        className="text-xs bg-card/40 rounded px-2 py-1 border border-border/30 truncate"
                        title={email.subject}
                      >
                        {idx + 1}. {email.subject}
                      </div>
                    ))}
                    {Array.isArray(sequence.emails) && sequence.emails.length > 3 && (
                      <div className="text-xs text-muted-foreground px-2">+{sequence.emails.length - 3} more</div>
                    )}
                  </div>
                </div>

                {/* Actions */}
                <div className="flex items-center gap-2 flex-shrink-0">
                  <button
                    className="p-2 hover:bg-card/60 rounded-lg transition-colors"
                    title={sequence.is_active ? "Deactivate" : "Activate"}
                  >
                    {sequence.is_active ? (
                      <ToggleRight className="w-5 h-5 text-emerald-400" />
                    ) : (
                      <ToggleLeft className="w-5 h-5 text-muted-foreground" />
                    )}
                  </button>

                  <button
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
              </div>

              {/* Progress Bar */}
              <div className="mt-4 pt-4 border-t border-border/30">
                <div className="flex items-center justify-between mb-2">
                  <p className="text-xs text-muted-foreground">Usage Status</p>
                  <p className="text-xs font-medium">
                    {sequence.active_sequences} / {sequence.total_sent} active
                  </p>
                </div>
                <div className="w-full bg-card/40 rounded-full h-2 overflow-hidden">
                  <div
                    className="bg-gradient-to-r from-violet-400 to-cyan-400 h-full transition-all"
                    style={{
                      width: `${sequence.total_sent > 0 ? (sequence.active_sequences / sequence.total_sent) * 100 : 0}%`,
                    }}
                  />
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Help Section */}
      <div className="glass-card p-6 mt-6 bg-violet-400/5 border-violet-400/30">
        <h3 className="text-sm font-semibold mb-3">💡 Email Sequence Tips</h3>
        <ul className="text-sm text-muted-foreground space-y-2">
          <li>• Create sequences triggered by specific lead actions (qualification, demo request, proposal sent)</li>
          <li>• Space out emails over several days to avoid overwhelming prospects</li>
          <li>• Personalize emails with lead name, company, and relevant context</li>
          <li>• Track opens and clicks to understand prospect engagement</li>
          <li>• A/B test different subject lines and content to optimize open rates</li>
        </ul>
      </div>
    </div>
  );
}
