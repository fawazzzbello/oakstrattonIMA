# OakstrattonIMA — Claude Code Instructions

## Project Overview
OakstrattonIMA is an **AI-powered Influence Marketing Agency (IMA) platform**. It combines intelligent influencer discovery, campaign management, contract automation, payment processing, and real-time analytics — all under a futuristic "Velvet Dark" UI. The platform is deployed on Railway.com and integrates Anthropic Claude for AI features.

## Architecture
- **Backend**: Python 3.11 + FastAPI + SQLAlchemy 2.0 (async) + Alembic
- **AI Engine**: Anthropic Claude (`claude-sonnet-4-6`) via `anthropic==0.40.0` SDK
- **Frontend**: React 18 + TypeScript + Vite + TailwindCSS ("Velvet Dark" design system)
- **Database**: PostgreSQL 15 (Railway managed)
- **Cache/Queue**: Redis (Railway managed)
- **Task Queue**: Celery + Redis
- **Deployment**: Railway.com only (no local dev — deploy directly to Railway)

## Repository Layout
```
oakstrattonIMA/
├── backend/
│   ├── app/
│   │   ├── api/v1/endpoints/
│   │   │   ├── auth.py, influencers.py, campaigns.py, clients.py
│   │   │   ├── analytics.py, payments.py, contracts.py, notifications.py
│   │   │   ├── ai.py          ← AI features: matching, brief, content, insights, chat
│   │   │   └── admin.py       ← Super admin: settings, users, flags, audit logs
│   │   ├── core/              # config, security, deps, exceptions
│   │   ├── db/                # session.py, base.py (imports all models for Alembic)
│   │   ├── models/
│   │   │   ├── user.py, influencer.py, campaign.py, client.py
│   │   │   ├── contract.py, payment.py, social_account.py, notification.py
│   │   │   ├── platform_settings.py  ← PlatformSettings, FeatureFlag, AuditLog
│   │   │   └── ai_result.py          ← AIAnalysis, AIInsightReport, AIChatSession/Message
│   │   ├── schemas/
│   │   │   ├── auth.py, user.py, influencer.py, campaign.py, common.py
│   │   │   ├── admin.py       ← Admin schemas
│   │   │   └── ai.py          ← AI request/response schemas
│   │   ├── services/
│   │   │   ├── ai/
│   │   │   │   ├── client.py          ← Shared AsyncAnthropic wrapper (ai_client singleton)
│   │   │   │   ├── matching.py        ← match_influencers()
│   │   │   │   ├── brief_generator.py ← generate_brief()
│   │   │   │   ├── content_analyzer.py← analyze_content()
│   │   │   │   └── insights.py        ← generate_insights_report()
│   │   │   └── audit.py               ← log_action() helper
│   │   ├── tasks/             # Celery worker + beat schedule
│   │   └── main.py
│   ├── migrations/versions/
│   │   ├── 0001_initial_schema.py        ← All core tables + enums
│   │   └── 0002_ai_and_admin_tables.py   ← AI/admin tables + seed data
│   ├── Dockerfile
│   ├── Dockerfile.celery
│   └── requirements.txt
├── frontend/
│   └── src/
│       ├── components/layout/DashboardLayout.tsx  ← Futuristic sidebar
│       ├── pages/
│       │   ├── LoginPage.tsx, DashboardPage.tsx
│       │   ├── InfluencersPage.tsx, InfluencerDetailPage.tsx
│       │   ├── CampaignsPage.tsx, CampaignDetailPage.tsx
│       │   ├── ClientsPage.tsx, ContractsPage.tsx
│       │   ├── PaymentsPage.tsx, AnalyticsPage.tsx
│       │   ├── AIInsightsPage.tsx   ← AI Command Center
│       │   └── AdminPage.tsx        ← Super Admin Dashboard
│       ├── store/authStore.ts
│       ├── types/index.ts
│       └── utils/api.ts
├── railway.toml
└── .env.example
```

## Development Commands

### Backend
```bash
cd backend
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
alembic upgrade head                          # Run migrations (0001 + 0002)
uvicorn app.main:app --reload                 # Dev server (port 8000)
celery -A app.tasks.worker worker -l info     # Celery worker
pytest tests/ -v                             # Run tests
```

### Frontend
```bash
cd frontend
npm install
npm run dev        # Dev server (port 5173)
npm run build      # Production build
npm run lint       # ESLint check
```

## Core Directives (Read Before Any Change)

1. **Never expose secrets** — All credentials in `.env`. Never hardcode API keys.
2. **API versioning** — All routes prefixed `/api/v1/`. Do not break existing endpoints.
3. **DB migrations** — Every model change needs an Alembic migration: `alembic revision --autogenerate -m "description"`. Import new models in `app/db/base.py`.
4. **Auth** — JWT tokens via `/api/v1/auth/`. Roles: `admin`, `manager`, `client`, `influencer`. Use `require_admin` / `require_manager` dependencies from `app/core/deps.py`.
5. **AI endpoints** — Always check `ai_client.is_available` before calling Claude. Return `503 {"detail": "AI service not configured"}` if `ANTHROPIC_API_KEY` is missing.
6. **Admin endpoints** — All `/api/v1/admin/*` routes require `Depends(require_admin)`. Call `log_action()` from `app/services/audit.py` for every mutating operation.
7. **Pagination** — All list endpoints support `?skip=0&limit=50` and return `{"items": [...], "total": N}`.
8. **Async first** — Use `async def` for all FastAPI handlers and SQLAlchemy async sessions.
9. **Financial data** — Monetary values as `NUMERIC(12,2)` (e.g. `1500.00` = $1,500.00).
10. **File uploads** — Store in Railway Volume or S3-compatible bucket. Never store blobs in Postgres.
11. **Error handling** — Use `app/core/exceptions.py`. Always return `{"detail": "..."}`.

## AI Services Reference

### `app/services/ai/client.py`
```python
from app.services.ai.client import ai_client

# Check availability before use
if not ai_client.is_available:
    raise HTTPException(503, detail="AI service not configured")

# Generate text response
result = await ai_client.generate(system_prompt, user_message)
# result = {"content": "...", "model": "...", "input_tokens": N, "output_tokens": N}

# Generate and auto-parse JSON response
result = await ai_client.generate_json(system_prompt, user_message)
# result["parsed"] = the parsed dict
```

### AI Model
Default: `claude-sonnet-4-6` (set via `AI_MODEL` env var). Overridable per-platform in `platform_settings.ai_model_override`.

## Design System: "Velvet Dark"

The frontend uses a custom dark theme. Follow these conventions in all new components:

### CSS Utility Classes (defined in `src/index.css`)
```
.glass-card          → bg-card/80 backdrop-blur-xl border border-border/60 rounded-xl
.glass-card-hover    → glass-card + hover:border-primary/30 + hover:glow
.gradient-text       → bg-gradient-to-r from-violet-400 to-cyan-400 bg-clip-text text-transparent
.btn-primary         → solid violet button
.btn-secondary       → muted bordered button
.btn-ghost           → transparent hover button
.input-field         → dark input with focus ring
.table-header        → uppercase muted table heading
.table-row           → border-bottom hover row
.page-container      → p-6 space-y-6 animate-fade-in
.kpi-card            → glass-card p-5 flex flex-col gap-2
.status-active       → emerald pill badge
.status-pending      → amber pill badge
.status-paused       → slate pill badge
.status-cancelled    → rose pill badge
.status-ai           → violet pill badge
```

### Status Badge Colors
```
active/published/completed  → bg-emerald-400/10 text-emerald-400
pending/draft               → bg-amber-400/10 text-amber-400
paused/inactive             → bg-slate-400/10 text-slate-400
cancelled/rejected/overdue  → bg-rose-400/10 text-rose-400
planning/sent/viewed        → bg-cyan-400/10 text-cyan-400
AI-related                  → bg-violet-400/10 text-violet-400
```

### Typography
- Page titles (`h1`): `font-heading` (Space Grotesk)
- Body text: `font-sans` (Inter, default)
- Muted text: `text-muted-foreground`

### Page Structure Pattern
```tsx
<div className="page-container">
  <div className="page-header">
    <div>
      <h1 className="page-title">Page Title</h1>
      <p className="page-subtitle">Description</p>
    </div>
    <button className="btn-primary">Action</button>
  </div>
  <div className="glass-card p-6">
    {/* content */}
  </div>
</div>
```

## Key Workflows

### AI Influencer Matching
1. Manager selects campaign in `/ai-insights` → AI Matching tab
2. POST `/api/v1/ai/match-influencers` with `{campaign_id, max_results}`
3. `services/ai/matching.py` fetches campaign + influencers from DB → builds prompt → calls Claude
4. Returns ranked list with scores, reasoning, strengths, concerns

### Campaign Lifecycle
1. Client creates brief → agency uses AI Brief Generator to expand it
2. Agency uses AI Matching to find best influencers
3. Influencers contracted → content submitted → approved → published
4. Metrics synced via Celery → AI generates insight report
5. Campaign closed → invoice generated → payment processed

### Platform Customization (Admin)
1. Admin visits `/admin` → Branding tab
2. Updates agency name, colors, fonts → PATCH `/api/v1/admin/settings`
3. PlatformSettings (singleton id=1) updated in DB
4. Feature flags toggle AI capabilities per role

### Payment Flow
1. Deliverable approved → invoice auto-generated
2. Invoice sent to client → Stripe payment intent created
3. Client pays → Stripe webhook confirms → influencer payout triggered
4. All steps logged in `transactions` table + `audit_logs`

## Railway Deployment
- Backend: `railway.toml` → `backend/Dockerfile` → runs `alembic upgrade head` then uvicorn
- Frontend: Separate Railway service → `frontend/Dockerfile` → nginx SPA with `/api` proxy
- Worker: Separate Railway service → `backend/Dockerfile.celery`
- **Required env vars**: `SECRET_KEY`, `ANTHROPIC_API_KEY`, `AI_MODEL`, `SENDGRID_API_KEY`, `STRIPE_SECRET_KEY`, `STRIPE_WEBHOOK_SECRET`, `FRONTEND_URL`, `CORS_ORIGINS`
- **Auto-injected by Railway**: `DATABASE_URL`, `REDIS_URL`

## Testing Standards
- Backend: `pytest` with `pytest-asyncio`; 80%+ coverage target
- Frontend: Vitest + React Testing Library
- Integration tests in `backend/tests/integration/`

## Code Style
- Python: `ruff check . --fix && ruff format .`
- TypeScript: `npm run lint && npm run format`
- Commits: Conventional Commits (`feat:`, `fix:`, `chore:`, `docs:`)
