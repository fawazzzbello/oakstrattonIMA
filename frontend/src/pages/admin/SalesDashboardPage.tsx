import { useEffect, useState } from "react";
import { BarChart, Bar, LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from "recharts";
import { TrendingUp, Users, Target, DollarSign, Calendar, FileText } from "lucide-react";
import api from "@/utils/api";

interface DashboardData {
  summary: {
    total_leads: number;
    new_leads: number;
    qualified_leads: number;
    deals_won: number;
    deals_lost: number;
    total_pipeline_value: number;
    average_lead_score: number;
    average_deal_size: number | null;
  };
  recent_leads: any[];
  upcoming_appointments: any[];
  recent_proposals: any[];
}

export default function SalesDashboardPage() {
  const [data, setData] = useState<DashboardData | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    try {
      const { data: result } = await api.get("/admin/sales/dashboard");
      setData(result);
    } catch (error) {
      console.error("Failed to fetch dashboard data:", error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <div className="page-container">Loading...</div>;
  }

  if (!data) {
    return <div className="page-container">Failed to load dashboard</div>;
  }

  const { summary, recent_leads, upcoming_appointments, recent_proposals } = data;

  // Sample data for charts
  const leadStatusData = [
    { name: "New", value: summary.new_leads, fill: "#7C5CFC" },
    { name: "Qualified", value: summary.qualified_leads, fill: "#22D3EE" },
    { name: "Won", value: summary.deals_won, fill: "#10B981" },
    { name: "Lost", value: summary.deals_lost, fill: "#EF4444" },
  ];

  const conversionRate = summary.total_leads > 0
    ? ((summary.deals_won / summary.total_leads) * 100).toFixed(1)
    : 0;

  return (
    <div className="page-container">
      <div className="page-header">
        <div>
          <h1 className="page-title">Sales Dashboard</h1>
          <p className="page-subtitle">Real-time overview of your sales pipeline and performance</p>
        </div>
        <button className="btn-primary">New Lead</button>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="kpi-card">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-xs text-muted-foreground uppercase tracking-wider">Total Leads</p>
              <p className="text-2xl font-bold mt-1">{summary.total_leads}</p>
              <p className="text-xs text-cyan-400 mt-2">+{summary.new_leads} this month</p>
            </div>
            <Users className="w-10 h-10 text-violet-400 opacity-50" />
          </div>
        </div>

        <div className="kpi-card">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-xs text-muted-foreground uppercase tracking-wider">Qualified</p>
              <p className="text-2xl font-bold mt-1">{summary.qualified_leads}</p>
              <p className="text-xs text-emerald-400 mt-2">{((summary.qualified_leads / summary.total_leads) * 100).toFixed(0)}% conversion</p>
            </div>
            <Target className="w-10 h-10 text-emerald-400 opacity-50" />
          </div>
        </div>

        <div className="kpi-card">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-xs text-muted-foreground uppercase tracking-wider">Pipeline Value</p>
              <p className="text-2xl font-bold mt-1">${(summary.total_pipeline_value / 1000).toFixed(0)}K</p>
              <p className="text-xs text-amber-400 mt-2">Avg: ${summary.average_deal_size ? (summary.average_deal_size / 1000).toFixed(0) : 0}K</p>
            </div>
            <DollarSign className="w-10 h-10 text-amber-400 opacity-50" />
          </div>
        </div>

        <div className="kpi-card">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-xs text-muted-foreground uppercase tracking-wider">Deals Won</p>
              <p className="text-2xl font-bold mt-1">{summary.deals_won}</p>
              <p className="text-xs text-pink-400 mt-2">{conversionRate}% close rate</p>
            </div>
            <TrendingUp className="w-10 h-10 text-pink-400 opacity-50" />
          </div>
        </div>
      </div>

      {/* Charts Section */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Lead Status Distribution */}
        <div className="glass-card p-6">
          <h3 className="text-sm font-semibold uppercase tracking-wider mb-4">Lead Status Distribution</h3>
          <ResponsiveContainer width="100%" height={250}>
            <PieChart>
              <Pie
                data={leadStatusData}
                cx="50%"
                cy="50%"
                innerRadius={60}
                outerRadius={90}
                paddingAngle={2}
                dataKey="value"
              >
                {leadStatusData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.fill} />
                ))}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
          <div className="mt-4 space-y-2">
            {leadStatusData.map((item) => (
              <div key={item.name} className="flex justify-between items-center text-xs">
                <span className="flex items-center gap-2">
                  <div className="w-2 h-2 rounded-full" style={{ backgroundColor: item.fill }} />
                  {item.name}
                </span>
                <span className="font-semibold">{item.value}</span>
              </div>
            ))}
          </div>
        </div>

        {/* Lead Score Distribution */}
        <div className="glass-card p-6">
          <h3 className="text-sm font-semibold uppercase tracking-wider mb-4">Average Lead Quality</h3>
          <div className="flex items-center justify-center mb-6">
            <div className="relative w-32 h-32 flex items-center justify-center">
              <svg className="w-32 h-32 transform -rotate-90" viewBox="0 0 120 120">
                <circle cx="60" cy="60" r="50" fill="none" stroke="#1e293b" strokeWidth="8" />
                <circle
                  cx="60"
                  cy="60"
                  r="50"
                  fill="none"
                  stroke="#7C5CFC"
                  strokeWidth="8"
                  strokeDasharray={`${(summary.average_lead_score / 100) * 314} 314`}
                />
              </svg>
              <div className="absolute text-center">
                <p className="text-2xl font-bold">{summary.average_lead_score.toFixed(0)}</p>
                <p className="text-xs text-muted-foreground">/ 100</p>
              </div>
            </div>
          </div>
          <p className="text-center text-sm text-muted-foreground mt-4">
            Your leads are {summary.average_lead_score > 70 ? "highly qualified" : "moderately qualified"}
          </p>
        </div>
      </div>

      {/* Recent Activity Section */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Recent Leads */}
        <div className="glass-card p-6">
          <div className="flex items-center gap-2 mb-4">
            <Users className="w-4 h-4 text-violet-400" />
            <h3 className="text-sm font-semibold uppercase tracking-wider">Recent Leads</h3>
          </div>
          <div className="space-y-3">
            {recent_leads.slice(0, 3).map((lead) => (
              <div key={lead.id} className="p-3 rounded-lg bg-card/40 border border-border/30">
                <p className="text-sm font-medium">{lead.company_name}</p>
                <p className="text-xs text-muted-foreground">{lead.contact_email}</p>
                <div className="flex items-center justify-between mt-2">
                  <span className={`text-xs px-2 py-1 rounded ${
                    lead.status === "won" ? "status-active" :
                    lead.status === "new" ? "status-pending" :
                    lead.status === "lost" ? "status-cancelled" : "status-ai"
                  }`}>
                    {lead.status}
                  </span>
                  <span className="text-xs text-muted-foreground">{lead.lead_score}/100</span>
                </div>
              </div>
            ))}
          </div>
          <button className="mt-4 text-xs text-violet-400 hover:text-violet-300">View All →</button>
        </div>

        {/* Upcoming Appointments */}
        <div className="glass-card p-6">
          <div className="flex items-center gap-2 mb-4">
            <Calendar className="w-4 h-4 text-cyan-400" />
            <h3 className="text-sm font-semibold uppercase tracking-wider">Upcoming</h3>
          </div>
          <div className="space-y-3">
            {upcoming_appointments.slice(0, 3).map((apt) => (
              <div key={apt.id} className="p-3 rounded-lg bg-card/40 border border-border/30">
                <p className="text-sm font-medium">{apt.title}</p>
                <p className="text-xs text-muted-foreground">
                  {new Date(apt.scheduled_at).toLocaleDateString()}
                </p>
                <div className="flex items-center justify-between mt-2">
                  <span className="text-xs text-cyan-400">{apt.meeting_type}</span>
                  <span className="text-xs text-muted-foreground">{apt.duration_minutes}m</span>
                </div>
              </div>
            ))}
          </div>
          <button className="mt-4 text-xs text-cyan-400 hover:text-cyan-300">View All →</button>
        </div>

        {/* Recent Proposals */}
        <div className="glass-card p-6">
          <div className="flex items-center gap-2 mb-4">
            <FileText className="w-4 h-4 text-amber-400" />
            <h3 className="text-sm font-semibold uppercase tracking-wider">Proposals</h3>
          </div>
          <div className="space-y-3">
            {recent_proposals.slice(0, 3).map((prop) => (
              <div key={prop.id} className="p-3 rounded-lg bg-card/40 border border-border/30">
                <p className="text-sm font-medium">{prop.title}</p>
                <p className="text-xs text-amber-400">${prop.total_value.toLocaleString()}</p>
                <div className="flex items-center justify-between mt-2">
                  <span className={`text-xs px-2 py-1 rounded ${
                    prop.status === "sent" ? "status-pending" :
                    prop.status === "signed" ? "status-active" :
                    prop.status === "expired" ? "status-cancelled" : "bg-slate-400/10 text-slate-400"
                  }`}>
                    {prop.status}
                  </span>
                  <span className="text-xs text-muted-foreground">{prop.view_count} views</span>
                </div>
              </div>
            ))}
          </div>
          <button className="mt-4 text-xs text-amber-400 hover:text-amber-300">View All →</button>
        </div>
      </div>
    </div>
  );
}
