import { useEffect, useState } from "react";
import { Save, AlertCircle } from "lucide-react";

interface SalesSettings {
  id: number;
  lead_score_website_visit: number;
  lead_score_email_open: number;
  lead_score_link_click: number;
  lead_score_demo_request: number;
  lead_score_proposal_view: number;
  auto_qualify_score: number;
  pipeline_stages: Record<string, any>;
  auto_send_follow_up: boolean;
  follow_up_days: number;
  demo_duration_minutes: number;
  default_timezone: string;
  from_email: string;
  from_name: string;
  proposal_validity_days: number;
  proposal_currency: string;
}

export default function SalesSettingsPage() {
  const [settings, setSettings] = useState<SalesSettings | null>(null);
  const [formData, setFormData] = useState<Partial<SalesSettings>>({});
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState<{ type: "success" | "error"; text: string } | null>(null);

  useEffect(() => {
    fetchSettings();
  }, []);

  const fetchSettings = async () => {
    try {
      const response = await fetch("/api/v1/admin/sales-settings");
      if (response.ok) {
        const data = await response.json();
        setSettings(data);
        setFormData(data);
      }
    } catch (error) {
      console.error("Failed to fetch settings:", error);
      setMessage({ type: "error", text: "Failed to load settings" });
    } finally {
      setLoading(false);
    }
  };

  const handleChange = (key: string, value: any) => {
    setFormData((prev) => ({
      ...prev,
      [key]: value,
    }));
  };

  const handleSave = async () => {
    setSaving(true);
    try {
      const response = await fetch("/api/v1/admin/sales-settings", {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(formData),
      });

      if (response.ok) {
        const updated = await response.json();
        setSettings(updated);
        setMessage({ type: "success", text: "Settings saved successfully" });
      } else {
        setMessage({ type: "error", text: "Failed to save settings" });
      }
    } catch (error) {
      console.error("Failed to save settings:", error);
      setMessage({ type: "error", text: "An error occurred while saving" });
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return <div className="page-container">Loading settings...</div>;
  }

  if (!settings) {
    return <div className="page-container">Failed to load settings</div>;
  }

  return (
    <div className="page-container">
      <div className="page-header">
        <div>
          <h1 className="page-title">Sales Configuration</h1>
          <p className="page-subtitle">Configure lead scoring, pipelines, and sales automation</p>
        </div>
      </div>

      {message && (
        <div
          className={`p-4 rounded-lg border ${
            message.type === "success"
              ? "bg-emerald-400/10 border-emerald-400/30 text-emerald-400"
              : "bg-rose-400/10 border-rose-400/30 text-rose-400"
          } flex items-center gap-3`}
        >
          <AlertCircle className="w-5 h-5 flex-shrink-0" />
          {message.text}
        </div>
      )}

      <div className="space-y-6">
        {/* Lead Scoring Configuration */}
        <div className="glass-card p-6">
          <h2 className="text-lg font-semibold mb-4">Lead Scoring Weights</h2>
          <p className="text-sm text-muted-foreground mb-4">
            Adjust how many points are awarded for different lead engagement actions
          </p>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <label className="block text-sm font-medium mb-2">Website Visit Points</label>
              <input
                type="number"
                min="0"
                max="100"
                value={formData.lead_score_website_visit || 0}
                onChange={(e) => handleChange("lead_score_website_visit", parseInt(e.target.value))}
                className="input-field w-full"
              />
            </div>

            <div>
              <label className="block text-sm font-medium mb-2">Email Open Points</label>
              <input
                type="number"
                min="0"
                max="100"
                value={formData.lead_score_email_open || 0}
                onChange={(e) => handleChange("lead_score_email_open", parseInt(e.target.value))}
                className="input-field w-full"
              />
            </div>

            <div>
              <label className="block text-sm font-medium mb-2">Link Click Points</label>
              <input
                type="number"
                min="0"
                max="100"
                value={formData.lead_score_link_click || 0}
                onChange={(e) => handleChange("lead_score_link_click", parseInt(e.target.value))}
                className="input-field w-full"
              />
            </div>

            <div>
              <label className="block text-sm font-medium mb-2">Demo Request Points</label>
              <input
                type="number"
                min="0"
                max="100"
                value={formData.lead_score_demo_request || 0}
                onChange={(e) => handleChange("lead_score_demo_request", parseInt(e.target.value))}
                className="input-field w-full"
              />
            </div>

            <div>
              <label className="block text-sm font-medium mb-2">Proposal View Points</label>
              <input
                type="number"
                min="0"
                max="100"
                value={formData.lead_score_proposal_view || 0}
                onChange={(e) => handleChange("lead_score_proposal_view", parseInt(e.target.value))}
                className="input-field w-full"
              />
            </div>

            <div>
              <label className="block text-sm font-medium mb-2">Auto-Qualify Threshold (0-100)</label>
              <input
                type="number"
                min="0"
                max="100"
                value={formData.auto_qualify_score || 0}
                onChange={(e) => handleChange("auto_qualify_score", parseInt(e.target.value))}
                className="input-field w-full"
              />
              <p className="text-xs text-muted-foreground mt-1">Leads reaching this score are auto-qualified</p>
            </div>
          </div>
        </div>

        {/* Appointment Settings */}
        <div className="glass-card p-6">
          <h2 className="text-lg font-semibold mb-4">Appointment Settings</h2>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <label className="block text-sm font-medium mb-2">Default Demo Duration (minutes)</label>
              <input
                type="number"
                min="15"
                max="480"
                value={formData.demo_duration_minutes || 30}
                onChange={(e) => handleChange("demo_duration_minutes", parseInt(e.target.value))}
                className="input-field w-full"
              />
            </div>

            <div>
              <label className="block text-sm font-medium mb-2">Default Timezone</label>
              <input
                type="text"
                placeholder="e.g., America/New_York"
                value={formData.default_timezone || "UTC"}
                onChange={(e) => handleChange("default_timezone", e.target.value)}
                className="input-field w-full"
              />
            </div>
          </div>
        </div>

        {/* Email Settings */}
        <div className="glass-card p-6">
          <h2 className="text-lg font-semibold mb-4">Email Settings</h2>

          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium mb-2">From Email Address</label>
              <input
                type="email"
                value={formData.from_email || ""}
                onChange={(e) => handleChange("from_email", e.target.value)}
                className="input-field w-full"
              />
            </div>

            <div>
              <label className="block text-sm font-medium mb-2">From Name</label>
              <input
                type="text"
                value={formData.from_name || ""}
                onChange={(e) => handleChange("from_name", e.target.value)}
                className="input-field w-full"
              />
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <label className="flex items-center gap-3 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={formData.auto_send_follow_up || false}
                    onChange={(e) => handleChange("auto_send_follow_up", e.target.checked)}
                    className="rounded border-border/60"
                  />
                  <span className="text-sm font-medium">Auto-send Follow-up Emails</span>
                </label>
              </div>

              {formData.auto_send_follow_up && (
                <div>
                  <label className="block text-sm font-medium mb-2">Follow-up After (days)</label>
                  <input
                    type="number"
                    min="1"
                    max="30"
                    value={formData.follow_up_days || 3}
                    onChange={(e) => handleChange("follow_up_days", parseInt(e.target.value))}
                    className="input-field w-full"
                  />
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Proposal Settings */}
        <div className="glass-card p-6">
          <h2 className="text-lg font-semibold mb-4">Proposal Settings</h2>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <label className="block text-sm font-medium mb-2">Proposal Validity Period (days)</label>
              <input
                type="number"
                min="1"
                max="365"
                value={formData.proposal_validity_days || 30}
                onChange={(e) => handleChange("proposal_validity_days", parseInt(e.target.value))}
                className="input-field w-full"
              />
            </div>

            <div>
              <label className="block text-sm font-medium mb-2">Default Currency</label>
              <select
                value={formData.proposal_currency || "USD"}
                onChange={(e) => handleChange("proposal_currency", e.target.value)}
                className="input-field w-full"
              >
                <option value="USD">USD ($)</option>
                <option value="EUR">EUR (€)</option>
                <option value="GBP">GBP (£)</option>
                <option value="CAD">CAD ($)</option>
                <option value="AUD">AUD ($)</option>
              </select>
            </div>
          </div>
        </div>

        {/* Pipeline Stages */}
        <div className="glass-card p-6">
          <h2 className="text-lg font-semibold mb-4">Sales Pipeline Stages</h2>
          <p className="text-sm text-muted-foreground mb-4">
            Current pipeline stages are configured in your database. Contact support to customize stages.
          </p>
          <div className="bg-card/40 rounded p-4 space-y-2">
            {settings.pipeline_stages &&
              Object.entries(settings.pipeline_stages).map(([stage, config]: [string, any]) => (
                <div key={stage} className="flex items-center justify-between p-2">
                  <div className="flex items-center gap-3">
                    <div
                      className="w-4 h-4 rounded"
                      style={{ backgroundColor: config.color || "#7C5CFC" }}
                    />
                    <span className="font-medium">{stage}</span>
                  </div>
                  <span className="text-xs text-muted-foreground">Order: {config.order || 0}</span>
                </div>
              ))}
          </div>
        </div>

        {/* Save Button */}
        <div className="flex justify-end gap-4">
          <button className="btn-secondary" onClick={fetchSettings}>
            Reset
          </button>
          <button className="btn-primary" onClick={handleSave} disabled={saving}>
            <Save className="w-4 h-4 mr-2" />
            {saving ? "Saving..." : "Save Settings"}
          </button>
        </div>
      </div>
    </div>
  );
}
