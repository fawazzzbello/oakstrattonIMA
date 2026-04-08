import { useEffect, useState } from "react";
import { DollarSign, Copy, CheckCircle, Clock, XCircle, Link2, Download } from "lucide-react";
import api from "@/utils/api";

interface ProposalPayment {
  id: number;
  proposal_id: number;
  amount: number;
  currency: string;
  status: string;
  stripe_payment_intent_id?: string;
  payment_method?: string;
  paid_at?: string;
  due_date?: string;
  refunded_at?: string;
  refund_amount?: number;
  created_at: string;
}

interface PaymentLink {
  id: number;
  proposal_id: number;
  payment_link_url: string;
  is_active: boolean;
  expires_at?: string;
  link_clicks: number;
  last_clicked_at?: string;
}

interface Proposal {
  id: number;
  proposal_number: string;
  title: string;
  total_value: number;
  status: string;
  created_at: string;
}

export default function PaymentTrackingPage() {
  const [proposals, setProposals] = useState<Proposal[]>([]);
  const [payments, setPayments] = useState<ProposalPayment[]>([]);
  const [paymentLinks, setPaymentLinks] = useState<PaymentLink[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedStatus, setSelectedStatus] = useState<string>("");
  const [copiedLink, setCopiedLink] = useState<number | null>(null);

  useEffect(() => {
    Promise.all([fetchProposals(), fetchPayments()]).finally(() => setLoading(false));
  }, []);

  const fetchProposals = async () => {
    try {
      const { data } = await api.get("/admin/sales/proposals");
      setProposals(data.items || []);
    } catch (error) {
      console.error("Failed to fetch proposals:", error);
    }
  };

  const fetchPayments = async () => {
    try {
      const { data } = await api.get("/admin/sales/payments");
      setPayments(data);
    } catch (error) {
      console.error("Failed to fetch payments:", error);
    }
  };

  const getProposalTitle = (proposalId: number) => {
    return proposals.find((p) => p.id === proposalId)?.title || "Unknown";
  };

  const getProposalNumber = (proposalId: number) => {
    return proposals.find((p) => p.id === proposalId)?.proposal_number || "-";
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case "completed":
      case "paid":
        return "status-active";
      case "pending":
        return "status-pending";
      case "failed":
        return "status-cancelled";
      case "processing":
        return "status-ai";
      default:
        return "bg-slate-400/10 text-slate-400";
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case "completed":
      case "paid":
        return <CheckCircle className="w-5 h-5 text-emerald-400" />;
      case "pending":
        return <Clock className="w-5 h-5 text-amber-400" />;
      case "failed":
        return <XCircle className="w-5 h-5 text-rose-400" />;
      default:
        return <Clock className="w-5 h-5 text-muted-foreground" />;
    }
  };

  const copyToClipboard = (link: string, id: number) => {
    navigator.clipboard.writeText(link);
    setCopiedLink(id);
    setTimeout(() => setCopiedLink(null), 2000);
  };

  const filteredPayments = selectedStatus
    ? payments.filter((p) => p.status === selectedStatus)
    : payments;

  const totalValue = filteredPayments.reduce((sum, p) => sum + p.amount, 0);
  const paidValue = filteredPayments
    .filter((p) => p.status === "completed" || p.status === "paid")
    .reduce((sum, p) => sum + p.amount, 0);
  const pendingValue = filteredPayments
    .filter((p) => p.status === "pending")
    .reduce((sum, p) => sum + p.amount, 0);

  if (loading) {
    return <div className="page-container">Loading payment data...</div>;
  }

  return (
    <div className="page-container">
      <div className="page-header">
        <div>
          <h1 className="page-title">Payment Tracking</h1>
          <p className="page-subtitle">Monitor proposal payments and payment links</p>
        </div>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="kpi-card">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-xs text-muted-foreground uppercase tracking-wider">Total Value</p>
              <p className="text-2xl font-bold mt-1">${(totalValue / 1000).toFixed(1)}K</p>
              <p className="text-xs text-muted-foreground mt-2">{filteredPayments.length} invoices</p>
            </div>
            <DollarSign className="w-10 h-10 text-violet-400 opacity-50" />
          </div>
        </div>

        <div className="kpi-card">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-xs text-muted-foreground uppercase tracking-wider">Paid</p>
              <p className="text-2xl font-bold mt-1 text-emerald-400">${(paidValue / 1000).toFixed(1)}K</p>
              <p className="text-xs text-emerald-400 mt-2">
                {((paidValue / totalValue) * 100).toFixed(0)}% collected
              </p>
            </div>
            <CheckCircle className="w-10 h-10 text-emerald-400 opacity-50" />
          </div>
        </div>

        <div className="kpi-card">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-xs text-muted-foreground uppercase tracking-wider">Pending</p>
              <p className="text-2xl font-bold mt-1 text-amber-400">${(pendingValue / 1000).toFixed(1)}K</p>
              <p className="text-xs text-amber-400 mt-2">
                {filteredPayments.filter((p) => p.status === "pending").length} awaiting payment
              </p>
            </div>
            <Clock className="w-10 h-10 text-amber-400 opacity-50" />
          </div>
        </div>
      </div>

      {/* Filter */}
      <div className="glass-card p-4">
        <select
          value={selectedStatus}
          onChange={(e) => setSelectedStatus(e.target.value)}
          className="input-field w-full md:w-64"
        >
          <option value="">All Payment Statuses</option>
          <option value="pending">Pending</option>
          <option value="processing">Processing</option>
          <option value="paid">Paid / Completed</option>
          <option value="failed">Failed</option>
          <option value="refunded">Refunded</option>
        </select>
      </div>

      {/* Payments Table */}
      {filteredPayments.length === 0 ? (
        <div className="glass-card p-8 text-center">
          <DollarSign className="w-12 h-12 mx-auto text-muted-foreground opacity-50 mb-4" />
          <p className="text-muted-foreground">No payments found</p>
        </div>
      ) : (
        <div className="glass-card overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b border-border/30 bg-card/50">
                  <th className="table-header text-left px-6 py-4">Proposal</th>
                  <th className="table-header text-left px-6 py-4">Amount</th>
                  <th className="table-header text-center px-6 py-4">Status</th>
                  <th className="table-header text-left px-6 py-4">Payment Method</th>
                  <th className="table-header text-left px-6 py-4">Due Date</th>
                  <th className="table-header text-right px-6 py-4">Actions</th>
                </tr>
              </thead>
              <tbody>
                {filteredPayments.map((payment) => (
                  <tr key={payment.id} className="table-row hover:bg-card/40 transition-colors">
                    <td className="px-6 py-4">
                      <div>
                        <p className="font-medium">{getProposalTitle(payment.proposal_id)}</p>
                        <p className="text-xs text-muted-foreground">{getProposalNumber(payment.proposal_id)}</p>
                      </div>
                    </td>
                    <td className="px-6 py-4">
                      <span className="font-semibold">
                        {payment.currency} ${payment.amount.toLocaleString()}
                      </span>
                    </td>
                    <td className="px-6 py-4 text-center">
                      <div className="flex items-center justify-center gap-2">
                        {getStatusIcon(payment.status)}
                        <span className={`text-xs px-2 py-1 rounded ${getStatusColor(payment.status)}`}>
                          {payment.status.charAt(0).toUpperCase() + payment.status.slice(1)}
                        </span>
                      </div>
                    </td>
                    <td className="px-6 py-4">
                      {payment.payment_method ? (
                        <span className="text-sm capitalize">{payment.payment_method.replace(/_/g, " ")}</span>
                      ) : (
                        <span className="text-xs text-muted-foreground">-</span>
                      )}
                    </td>
                    <td className="px-6 py-4">
                      {payment.due_date ? (
                        <span className="text-sm">
                          {new Date(payment.due_date).toLocaleDateString()}
                        </span>
                      ) : (
                        <span className="text-xs text-muted-foreground">-</span>
                      )}
                    </td>
                    <td className="px-6 py-4 text-right">
                      <button className="p-2 hover:bg-card/60 rounded transition-colors">
                        <Download className="w-4 h-4 text-cyan-400" />
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Payment Links Section */}
      <div className="mt-8">
        <h2 className="text-lg font-semibold mb-4">Shareable Payment Links</h2>
        <div className="space-y-4">
          {paymentLinks.slice(0, 10).map((link) => (
            <div key={link.id} className="glass-card p-4">
              <div className="flex items-center justify-between">
                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-2">
                    <Link2 className="w-4 h-4 text-violet-400" />
                    <p className="font-medium">Proposal #{link.proposal_id}</p>
                    {link.is_active ? (
                      <span className="status-active text-xs px-2 py-1">Active</span>
                    ) : (
                      <span className="status-paused text-xs px-2 py-1">Expired</span>
                    )}
                  </div>
                  <p className="text-sm text-muted-foreground break-all">{link.payment_link_url}</p>
                  <div className="flex gap-4 mt-2 text-xs text-muted-foreground">
                    <span>{link.link_clicks} clicks</span>
                    {link.last_clicked_at && (
                      <span>Last clicked: {new Date(link.last_clicked_at).toLocaleDateString()}</span>
                    )}
                  </div>
                </div>
                <button
                  onClick={() => copyToClipboard(link.payment_link_url, link.id)}
                  className="ml-4 px-4 py-2 bg-card/60 hover:bg-card/80 rounded transition-colors text-sm"
                >
                  {copiedLink === link.id ? "Copied!" : "Copy"}
                </button>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
