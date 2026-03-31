import { useState } from 'react'
import { useQuery, useMutation } from '@tanstack/react-query'
import {
  Sparkles, Search, Send, Bot, User, ChevronDown, ChevronUp,
  Loader2, AlertCircle, CheckCircle2, TrendingUp, Lightbulb,
  FileText, MessageSquare, RefreshCw, BarChart3,
} from 'lucide-react'
import api from '@/utils/api'
import type { Campaign, AIMatchResponse, AIInsightReport, AIChatSession, AIChatMessage, PaginatedResponse } from '@/types'
import { format } from 'date-fns'

function AIUnavailableBanner() {
  return (
    <div className="glass-card p-4 border-amber-400/30 bg-amber-400/5 flex items-center gap-3">
      <AlertCircle className="h-5 w-5 text-amber-400 shrink-0" />
      <div>
        <p className="text-sm font-medium text-amber-400">AI service not configured</p>
        <p className="text-xs text-muted-foreground mt-0.5">
          Set <code className="bg-muted px-1 rounded">ANTHROPIC_API_KEY</code> in your Railway environment variables to enable AI features.
        </p>
      </div>
    </div>
  )
}

function AIMatchingSection() {
  const [selectedCampaignId, setSelectedCampaignId] = useState<number | ''>('')
  const [results, setResults] = useState<AIMatchResponse | null>(null)
  const [aiError, setAiError] = useState<string | null>(null)

  const { data: campaigns } = useQuery({
    queryKey: ['campaigns-list-ai'],
    queryFn: async () => {
      const { data } = await api.get<PaginatedResponse<Campaign>>('/campaigns?limit=50')
      return data
    },
  })

  const matchMutation = useMutation({
    mutationFn: async () => {
      const { data } = await api.post('/ai/match-influencers', { campaign_id: selectedCampaignId, max_results: 8 })
      return data as AIMatchResponse
    },
    onSuccess: (data) => { setResults(data); setAiError(null) },
    onError: (err: any) => { setAiError(err?.response?.data?.detail ?? 'AI matching failed') },
  })

  return (
    <div className="glass-card p-6 space-y-5">
      <div className="flex items-center gap-3">
        <div className="w-9 h-9 rounded-lg bg-violet-400/10 flex items-center justify-center">
          <Search className="h-4 w-4 text-violet-400" />
        </div>
        <div>
          <h2 className="font-semibold text-foreground">AI Influencer Matching</h2>
          <p className="text-xs text-muted-foreground">Find the best influencers for your campaign</p>
        </div>
      </div>
      <div className="flex gap-3">
        <select value={selectedCampaignId} onChange={(e) => setSelectedCampaignId(e.target.value ? Number(e.target.value) : '')} className="input-field flex-1">
          <option value="">Select a campaign...</option>
          {campaigns?.items.map((c) => <option key={c.id} value={c.id}>{c.name}</option>)}
        </select>
        <button className="btn-primary flex items-center gap-2 shrink-0 disabled:opacity-50" onClick={() => matchMutation.mutate()} disabled={!selectedCampaignId || matchMutation.isPending}>
          {matchMutation.isPending ? <Loader2 className="h-4 w-4 animate-spin" /> : <Sparkles className="h-4 w-4" />}
          Find Matches
        </button>
      </div>
      {aiError && (aiError.includes('not configured') ? <AIUnavailableBanner /> : <p className="text-sm text-rose-400 flex items-center gap-2"><AlertCircle className="h-4 w-4" />{aiError}</p>)}
      {results && (
        <div className="space-y-3">
          <p className="text-xs text-muted-foreground">{results.matches.length} matches · Model: {results.model_used}</p>
          {results.matches.map((match, i) => (
            <div key={match.influencer_id} className="glass-card-hover p-4 flex gap-4">
              <div className="w-8 h-8 rounded-full bg-violet-400/10 flex items-center justify-center text-violet-400 font-bold text-sm shrink-0">#{i + 1}</div>
              <div className="flex-1 min-w-0">
                <div className="flex items-center justify-between gap-2 mb-1">
                  <span className="font-medium truncate">{match.name}</span>
                  <span className="text-sm font-bold text-violet-400 shrink-0">{Math.round(match.match_score * 100)}%</span>
                </div>
                <div className="w-full bg-muted rounded-full h-1.5 mb-2">
                  <div className="bg-gradient-to-r from-violet-500 to-cyan-400 h-1.5 rounded-full" style={{ width: `${match.match_score * 100}%` }} />
                </div>
                <p className="text-xs text-muted-foreground mb-2 line-clamp-2">{match.reasoning}</p>
                <div className="flex flex-wrap gap-1.5">
                  {match.strengths.slice(0, 3).map((s) => <span key={s} className="text-xs bg-emerald-400/10 text-emerald-400 px-2 py-0.5 rounded-full">{s}</span>)}
                  {match.concerns.slice(0, 2).map((c) => <span key={c} className="text-xs bg-amber-400/10 text-amber-400 px-2 py-0.5 rounded-full">{c}</span>)}
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

function AIBriefSection() {
  const [form, setForm] = useState({ product_name: '', product_description: '', target_audience: '', budget_range: '', campaign_type: 'brand_awareness', platforms: ['instagram'], duration_weeks: 4 })
  const [result, setResult] = useState<{ brief_markdown: string; model_used: string } | null>(null)
  const [aiError, setAiError] = useState<string | null>(null)
  const PLATFORMS = ['instagram', 'tiktok', 'youtube', 'twitter', 'facebook']

  const briefMutation = useMutation({
    mutationFn: async () => { const { data } = await api.post('/ai/generate-brief', form); return data },
    onSuccess: (data) => { setResult(data); setAiError(null) },
    onError: (err: any) => { setAiError(err?.response?.data?.detail ?? 'Brief generation failed') },
  })

  const togglePlatform = (p: string) => setForm((f) => ({ ...f, platforms: f.platforms.includes(p) ? f.platforms.filter((x) => x !== p) : [...f.platforms, p] }))

  return (
    <div className="glass-card p-6 space-y-5">
      <div className="flex items-center gap-3">
        <div className="w-9 h-9 rounded-lg bg-cyan-400/10 flex items-center justify-center"><FileText className="h-4 w-4 text-cyan-400" /></div>
        <div><h2 className="font-semibold text-foreground">AI Brief Generator</h2><p className="text-xs text-muted-foreground">Generate a complete campaign brief from minimal input</p></div>
      </div>
      {!result ? (
        <div className="space-y-4">
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div><label className="block text-xs text-muted-foreground mb-1">Product / Brand Name</label><input className="input-field w-full" placeholder="e.g. Acme Skincare" value={form.product_name} onChange={(e) => setForm((f) => ({ ...f, product_name: e.target.value }))} /></div>
            <div><label className="block text-xs text-muted-foreground mb-1">Budget Range</label><input className="input-field w-full" placeholder="e.g. $10k–$25k" value={form.budget_range} onChange={(e) => setForm((f) => ({ ...f, budget_range: e.target.value }))} /></div>
          </div>
          <div><label className="block text-xs text-muted-foreground mb-1">Product Description</label><textarea className="input-field w-full resize-none" rows={2} placeholder="Brief description of what you're promoting..." value={form.product_description} onChange={(e) => setForm((f) => ({ ...f, product_description: e.target.value }))} /></div>
          <div><label className="block text-xs text-muted-foreground mb-1">Target Audience</label><input className="input-field w-full" placeholder="e.g. Women 25–40 interested in skincare" value={form.target_audience} onChange={(e) => setForm((f) => ({ ...f, target_audience: e.target.value }))} /></div>
          <div className="grid grid-cols-2 gap-4">
            <div><label className="block text-xs text-muted-foreground mb-1">Campaign Type</label>
              <select className="input-field w-full" value={form.campaign_type} onChange={(e) => setForm((f) => ({ ...f, campaign_type: e.target.value }))}>
                {['brand_awareness', 'product_launch', 'event_promotion', 'lead_generation', 'sales', 'content_creation'].map((t) => <option key={t} value={t}>{t.replace(/_/g, ' ')}</option>)}
              </select>
            </div>
            <div><label className="block text-xs text-muted-foreground mb-1">Duration (weeks)</label><input type="number" className="input-field w-full" min={1} max={52} value={form.duration_weeks} onChange={(e) => setForm((f) => ({ ...f, duration_weeks: Number(e.target.value) }))} /></div>
          </div>
          <div>
            <label className="block text-xs text-muted-foreground mb-1.5">Platforms</label>
            <div className="flex flex-wrap gap-2">
              {PLATFORMS.map((p) => <button key={p} onClick={() => togglePlatform(p)} className={`px-3 py-1 rounded-full text-xs font-medium transition-all ${form.platforms.includes(p) ? 'bg-violet-400/20 text-violet-400 border border-violet-400/40' : 'bg-muted text-muted-foreground border border-border'}`}>{p}</button>)}
            </div>
          </div>
          {aiError && (aiError.includes('not configured') ? <AIUnavailableBanner /> : <p className="text-sm text-rose-400 flex items-center gap-2"><AlertCircle className="h-4 w-4" />{aiError}</p>)}
          <button className="btn-primary w-full flex items-center justify-center gap-2 disabled:opacity-50" onClick={() => briefMutation.mutate()} disabled={!form.product_name || briefMutation.isPending}>
            {briefMutation.isPending ? <><Loader2 className="h-4 w-4 animate-spin" />Generating brief...</> : <><Sparkles className="h-4 w-4" />Generate Campaign Brief</>}
          </button>
        </div>
      ) : (
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <span className="text-xs text-muted-foreground">Generated with {result.model_used}</span>
            <button onClick={() => setResult(null)} className="btn-ghost text-xs py-1 px-2"><RefreshCw className="h-3 w-3 mr-1 inline" />New Brief</button>
          </div>
          <div className="bg-muted/30 rounded-lg p-4 max-h-96 overflow-y-auto">
            <pre className="text-sm text-foreground whitespace-pre-wrap font-sans leading-relaxed">{result.brief_markdown}</pre>
          </div>
        </div>
      )}
    </div>
  )
}

function AIInsightsSection() {
  const [expandedId, setExpandedId] = useState<number | null>(null)
  const [aiError, setAiError] = useState<string | null>(null)

  const { data: reports, isLoading, refetch } = useQuery({
    queryKey: ['ai-insight-reports'],
    queryFn: async () => { const { data } = await api.get('/ai/insights?limit=10'); return data as { items: AIInsightReport[]; total: number } },
  })

  const generateMutation = useMutation({
    mutationFn: async () => { const { data } = await api.post('/ai/insights/generate', { report_type: 'weekly' }); return data },
    onSuccess: () => { refetch(); setAiError(null) },
    onError: (err: any) => { setAiError(err?.response?.data?.detail ?? 'Insight generation failed') },
  })

  return (
    <div className="glass-card p-6 space-y-5">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-lg bg-emerald-400/10 flex items-center justify-center"><BarChart3 className="h-4 w-4 text-emerald-400" /></div>
          <div><h2 className="font-semibold text-foreground">AI Insight Reports</h2><p className="text-xs text-muted-foreground">Weekly and monthly performance narratives</p></div>
        </div>
        <button className="btn-secondary flex items-center gap-2 text-sm disabled:opacity-50" onClick={() => generateMutation.mutate()} disabled={generateMutation.isPending}>
          {generateMutation.isPending ? <Loader2 className="h-3 w-3 animate-spin" /> : <RefreshCw className="h-3 w-3" />}Generate Report
        </button>
      </div>
      {aiError && (aiError.includes('not configured') ? <AIUnavailableBanner /> : <p className="text-sm text-rose-400 flex items-center gap-2"><AlertCircle className="h-4 w-4" />{aiError}</p>)}
      {isLoading && <div className="h-24 bg-muted/30 rounded-lg animate-pulse" />}
      {!isLoading && (!reports?.items || reports.items.length === 0) && (
        <div className="text-center py-8 text-muted-foreground">
          <Lightbulb className="h-10 w-10 mx-auto mb-3 opacity-30" />
          <p className="text-sm">No insight reports yet.</p>
          <p className="text-xs mt-1">Click "Generate Report" to create your first weekly insights.</p>
        </div>
      )}
      <div className="space-y-2">
        {reports?.items.map((report) => (
          <div key={report.id} className="glass-card-hover overflow-hidden">
            <button className="w-full flex items-center justify-between p-4 text-left" onClick={() => setExpandedId(expandedId === report.id ? null : report.id)}>
              <div className="flex items-center gap-3">
                <span className={`text-xs px-2 py-0.5 rounded-full font-medium ${report.report_type === 'weekly' ? 'bg-cyan-400/10 text-cyan-400' : 'bg-violet-400/10 text-violet-400'}`}>{report.report_type}</span>
                <span className="text-sm font-medium">{format(new Date(report.created_at), 'MMM d, yyyy')}</span>
                <span className={`text-xs flex items-center gap-1 ${report.status === 'ready' ? 'text-emerald-400' : 'text-amber-400'}`}>
                  {report.status === 'ready' ? <CheckCircle2 className="h-3 w-3" /> : <Loader2 className="h-3 w-3 animate-spin" />}{report.status}
                </span>
              </div>
              {expandedId === report.id ? <ChevronUp className="h-4 w-4 text-muted-foreground" /> : <ChevronDown className="h-4 w-4 text-muted-foreground" />}
            </button>
            {expandedId === report.id && report.report_markdown && (
              <div className="px-4 pb-4 border-t border-border/40 pt-3">
                <pre className="text-sm text-foreground whitespace-pre-wrap font-sans leading-relaxed max-h-80 overflow-y-auto">{report.report_markdown}</pre>
                {Array.isArray(report.recommendations) && report.recommendations.length > 0 && (
                  <div className="mt-4 space-y-2">
                    <p className="text-xs font-medium text-muted-foreground uppercase tracking-wider">Recommendations</p>
                    {report.recommendations.map((rec: any, i: number) => (
                      <div key={i} className="flex items-start gap-2 text-sm"><TrendingUp className="h-4 w-4 text-violet-400 shrink-0 mt-0.5" /><span>{typeof rec === 'string' ? rec : rec.text ?? JSON.stringify(rec)}</span></div>
                    ))}
                  </div>
                )}
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  )
}

function AIChatSection() {
  const [sessionId, setSessionId] = useState<number | null>(null)
  const [messages, setMessages] = useState<AIChatMessage[]>([])
  const [input, setInput] = useState('')
  const [aiError, setAiError] = useState<string | null>(null)

  const { data: sessions, refetch: refetchSessions } = useQuery({
    queryKey: ['ai-chat-sessions'],
    queryFn: async () => { const { data } = await api.get('/ai/chat/sessions?limit=5'); return data as { items: AIChatSession[] } },
  })

  const createSession = useMutation({
    mutationFn: async () => { const { data } = await api.post('/ai/chat/sessions', { session_name: `Chat ${new Date().toLocaleTimeString()}` }); return data as AIChatSession },
    onSuccess: (session) => { setSessionId(session.id); setMessages([]); refetchSessions() },
    onError: (err: any) => { setAiError(err?.response?.data?.detail ?? 'Could not start session') },
  })

  const loadSession = async (id: number) => {
    setSessionId(id)
    const { data } = await api.get(`/ai/chat/sessions/${id}/messages`)
    setMessages(data?.items ?? [])
  }

  const sendMessage = useMutation({
    mutationFn: async () => { if (!sessionId) return; const { data } = await api.post(`/ai/chat/sessions/${sessionId}/message`, { content: input }); return data },
    onSuccess: (data) => {
      if (!data) return
      setMessages((prev) => [...prev,
        { id: Date.now(), session_id: sessionId!, role: 'user', content: input, created_at: new Date().toISOString() },
        { id: Date.now() + 1, session_id: sessionId!, role: 'assistant', content: data.content, created_at: new Date().toISOString() },
      ])
      setInput(''); setAiError(null)
    },
    onError: (err: any) => { setAiError(err?.response?.data?.detail ?? 'Message failed') },
  })

  return (
    <div className="glass-card p-6 space-y-4">
      <div className="flex items-center gap-3">
        <div className="w-9 h-9 rounded-lg bg-amber-400/10 flex items-center justify-center"><MessageSquare className="h-4 w-4 text-amber-400" /></div>
        <div><h2 className="font-semibold text-foreground">AI Assistant</h2><p className="text-xs text-muted-foreground">Ask anything about your campaigns and influencers</p></div>
      </div>
      {aiError && (aiError.includes('not configured') ? <AIUnavailableBanner /> : <p className="text-sm text-rose-400 flex items-center gap-2"><AlertCircle className="h-4 w-4" />{aiError}</p>)}
      {!sessionId ? (
        <div className="space-y-3">
          {sessions?.items && sessions.items.length > 0 && (
            <div>
              <p className="text-xs text-muted-foreground mb-2">Recent conversations</p>
              {sessions.items.map((s) => (
                <button key={s.id} onClick={() => loadSession(s.id)} className="w-full text-left px-3 py-2 rounded-lg bg-muted/30 hover:bg-muted/60 text-sm mb-1 flex items-center gap-2 transition-colors">
                  <MessageSquare className="h-3.5 w-3.5 text-muted-foreground" />{s.session_name ?? `Session ${s.id}`}
                </button>
              ))}
            </div>
          )}
          <button className="btn-primary w-full flex items-center justify-center gap-2" onClick={() => createSession.mutate()} disabled={createSession.isPending}>
            {createSession.isPending ? <Loader2 className="h-4 w-4 animate-spin" /> : <MessageSquare className="h-4 w-4" />}Start New Conversation
          </button>
        </div>
      ) : (
        <div className="flex flex-col gap-3">
          <div className="bg-muted/20 rounded-lg p-3 h-64 overflow-y-auto flex flex-col gap-3">
            {messages.length === 0 && <p className="text-sm text-muted-foreground text-center mt-10">Ask about your campaigns, influencers, or get strategic advice.</p>}
            {messages.map((msg) => (
              <div key={msg.id} className={`flex items-start gap-2.5 ${msg.role === 'user' ? 'flex-row-reverse' : ''}`}>
                <div className={`w-7 h-7 rounded-full flex items-center justify-center shrink-0 ${msg.role === 'user' ? 'bg-violet-400/20' : 'bg-amber-400/20'}`}>
                  {msg.role === 'user' ? <User className="h-3.5 w-3.5 text-violet-400" /> : <Bot className="h-3.5 w-3.5 text-amber-400" />}
                </div>
                <div className={`max-w-[80%] rounded-xl px-3.5 py-2.5 text-sm leading-relaxed ${msg.role === 'user' ? 'bg-violet-400/15 text-foreground' : 'bg-muted/60 text-foreground'}`}>{msg.content}</div>
              </div>
            ))}
            {sendMessage.isPending && (
              <div className="flex items-start gap-2.5">
                <div className="w-7 h-7 rounded-full bg-amber-400/20 flex items-center justify-center"><Bot className="h-3.5 w-3.5 text-amber-400" /></div>
                <div className="bg-muted/60 rounded-xl px-4 py-3"><Loader2 className="h-4 w-4 text-muted-foreground animate-spin" /></div>
              </div>
            )}
          </div>
          <div className="flex gap-2">
            <input value={input} onChange={(e) => setInput(e.target.value)} onKeyDown={(e) => e.key === 'Enter' && !e.shiftKey && sendMessage.mutate()} placeholder="Ask anything..." className="input-field flex-1" disabled={sendMessage.isPending} />
            <button className="btn-primary px-4 shrink-0 disabled:opacity-50" onClick={() => sendMessage.mutate()} disabled={!input.trim() || sendMessage.isPending}><Send className="h-4 w-4" /></button>
          </div>
          <button className="btn-ghost text-xs text-muted-foreground" onClick={() => { setSessionId(null); setMessages([]) }}>← Back to sessions</button>
        </div>
      )}
    </div>
  )
}

export default function AIInsightsPage() {
  const tabs = [
    { id: 'matching', label: 'Influencer Matching', icon: Search },
    { id: 'brief', label: 'Brief Generator', icon: FileText },
    { id: 'insights', label: 'Insight Reports', icon: BarChart3 },
    { id: 'chat', label: 'AI Assistant', icon: MessageSquare },
  ]
  const [activeTab, setActiveTab] = useState('matching')

  return (
    <div className="page-container">
      <div className="page-header">
        <div>
          <h1 className="page-title flex items-center gap-2.5">
            <Sparkles className="h-6 w-6 text-violet-400" />
            <span className="gradient-text">AI Command Center</span>
          </h1>
          <p className="page-subtitle">Your AI-powered marketing intelligence platform</p>
        </div>
      </div>
      <div className="flex gap-1 bg-muted/30 rounded-xl p-1 w-fit flex-wrap">
        {tabs.map(({ id, label, icon: Icon }) => (
          <button key={id} onClick={() => setActiveTab(id)}
            className={`flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-all duration-200 ${activeTab === id ? 'bg-card text-foreground shadow-sm' : 'text-muted-foreground hover:text-foreground'}`}>
            <Icon className="h-3.5 w-3.5" /><span className="hidden sm:inline">{label}</span>
          </button>
        ))}
      </div>
      {activeTab === 'matching' && <AIMatchingSection />}
      {activeTab === 'brief' && <AIBriefSection />}
      {activeTab === 'insights' && <AIInsightsSection />}
      {activeTab === 'chat' && <AIChatSection />}
    </div>
  )
}
