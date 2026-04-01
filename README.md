# OakstrattonIMA

**AI-Powered Influence Marketing Agency (IMA) Platform**

OakstrattonIMA is a full-stack, AI-driven influencer marketing platform. It combines intelligent influencer discovery, campaign management, contract automation, payment processing, and real-time analytics — all under a sophisticated dark-theme UI designed for modern agencies.

---

## Tech Stack

| Layer | Technology |
|---|---|
| **Backend API** | Python 3.11 · FastAPI · SQLAlchemy 2.0 (async) |
| **AI Engine** | Anthropic Claude (`claude-sonnet-4-6`) via `anthropic` SDK |
| **Database** | PostgreSQL 15 (Railway managed) |
| **Cache / Queue** | Redis (Railway managed) |
| **Background Tasks** | Celery + Redis Beat |
| **Frontend** | React 18 · TypeScript · Vite · TailwindCSS |
| **Design System** | "Velvet Dark" — Space Grotesk + Inter · Glassmorphism · Aurora gradients |
| **Auth** | JWT (access + refresh tokens) · Role-based (admin/manager/client/influencer) |
| **Payments** | Stripe (client invoicing) · Stripe Connect (influencer payouts) |
| **Email** | SendGrid |
| **File Storage** | S3-compatible (AWS S3 / Cloudflare R2) |
| **Deployment** | Railway.com |

---

## Railway Deployment Guide

This is the complete step-by-step guide to deploy OakstrattonIMA on Railway.com from scratch.

### Overview

The platform runs as **four Railway services** in a single project:

| Service | Dockerfile | Purpose |
|---|---|---|
| **Backend** | `backend/Dockerfile` | FastAPI API — runs migrations on startup |
| **Worker** | `backend/Dockerfile.celery` | Celery background tasks |
| **Frontend** | `frontend/Dockerfile` | React SPA served via nginx |
| **PostgreSQL** | Railway plugin | Managed database (auto-injects `DATABASE_URL`) |
| **Redis** | Railway plugin | Broker + cache (auto-injects `REDIS_URL`) |

---

### Step 1 — Create a Railway Project

1. Go to [railway.app](https://railway.app) and sign in.
2. Click **New Project**.
3. Choose **Empty Project**.

---

### Step 2 — Add PostgreSQL and Redis Plugins

Inside your new project:

1. Click **+ New** → **Database** → **Add PostgreSQL**. Railway creates the database and auto-injects `DATABASE_URL` into any service you link it to.
2. Click **+ New** → **Database** → **Add Redis**. Railway auto-injects `REDIS_URL`.

---

### Step 3 — Deploy the Backend Service

1. Click **+ New** → **GitHub Repo** → connect and select your fork of this repository.
2. Railway will auto-detect the build. Override the settings:
   - **Root Directory:** *(leave blank — build context is repo root)*
   - **Dockerfile Path:** `backend/Dockerfile`
3. Go to the service **Variables** tab and add the following:

#### Backend Environment Variables

| Variable | Value | Notes |
|---|---|---|
| `SECRET_KEY` | `$(openssl rand -hex 32)` | Run that command locally to generate |
| `ENVIRONMENT` | `production` | |
| `DEBUG` | `false` | |
| `FRONTEND_URL` | `https://your-frontend.up.railway.app` | Set after frontend is deployed |
| `CORS_ORIGINS` | `https://your-frontend.up.railway.app` | Comma-separated; no JSON brackets needed |
| `ANTHROPIC_API_KEY` | `sk-ant-...` | Required for all AI features |
| `AI_MODEL` | `claude-sonnet-4-6` | |
| `SENDGRID_API_KEY` | `SG.xxxx` | Required for email notifications |
| `EMAIL_FROM` | `noreply@youragency.com` | |
| `STRIPE_SECRET_KEY` | `sk_live_xxxx` | Required for payments |
| `STRIPE_WEBHOOK_SECRET` | `whsec_xxxx` | From Stripe dashboard → Webhooks |
| `CELERY_BROKER_URL` | `redis://...` | Copy from your Railway Redis service variables |
| `CELERY_RESULT_BACKEND` | `redis://...` | Same Redis URL |

> `DATABASE_URL` and `REDIS_URL` are **auto-injected** by Railway — do not set these manually.

4. Go to **Settings** → **Networking** → **Generate Domain** to get your backend public URL (e.g. `https://oakstratton-backend.up.railway.app`).

5. The backend runs `alembic upgrade head` on every startup. On first deploy this creates all tables and seeds default platform settings and feature flags.

6. Confirm the deployment is healthy:
   - Check deploy logs — you should see `Application startup complete.`
   - Visit `https://your-backend.up.railway.app/health` — should return `{"status":"ok"}`
   - Visit `https://your-backend.up.railway.app/docs` (with `DEBUG=true`) for the interactive API docs.

---

### Step 4 — Deploy the Celery Worker Service

1. Click **+ New** → **GitHub Repo** → same repository.
2. Override the settings:
   - **Dockerfile Path:** `backend/Dockerfile.celery`
3. Go to **Variables** and add the **same environment variables as the Backend** (the worker needs access to the database, Redis, Stripe, etc.).
4. The worker does **not** need a public domain — it only connects outbound.

---

### Step 5 — Deploy the Frontend Service

1. Click **+ New** → **GitHub Repo** → same repository.
2. Override the settings:
   - **Dockerfile Path:** `frontend/Dockerfile`
3. Go to **Variables** and add:

#### Frontend Environment Variables

| Variable | Value | Notes |
|---|---|---|
| `BACKEND_URL` | `https://your-backend.up.railway.app` | Your backend Railway URL from Step 3 |

> `BACKEND_URL` is injected into the nginx config at container startup. It tells nginx where to proxy `/api/` requests.

4. Go to **Settings** → **Networking** → **Generate Domain** to get your frontend URL.

5. Go back to the **Backend** service and update `FRONTEND_URL` and `CORS_ORIGINS` with the frontend URL from this step, then redeploy the backend.

---

### Step 6 — Configure Stripe Webhooks

1. In the [Stripe Dashboard](https://dashboard.stripe.com/webhooks), add a new endpoint:
   - **URL:** `https://your-backend.up.railway.app/api/v1/payments/webhook`
   - **Events to listen for:** `payment_intent.succeeded`, `payment_intent.payment_failed`, `invoice.paid`
2. Copy the **Signing Secret** and set it as `STRIPE_WEBHOOK_SECRET` on the Backend service.

---

### Step 7 — Create the First Admin User

The database starts empty. Create your first admin user via the API:

```bash
curl -X POST https://your-backend.up.railway.app/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@youragency.com","password":"yourpassword","full_name":"Your Name"}'
```

Then promote them to admin directly in the Railway PostgreSQL console:

```sql
UPDATE users SET role = 'admin' WHERE email = 'admin@youragency.com';
```

Access the Railway PostgreSQL console via your project → PostgreSQL service → **Data** tab.

---

### Complete Environment Variables Reference

Below is the full list of environment variables. Required ones are marked.

```bash
# ── Core ─────────────────────────────────────────────────────────────
APP_NAME=OakstrattonIMA
ENVIRONMENT=production           # development | production
DEBUG=false                      # true enables /docs Swagger UI
SECRET_KEY=                      # REQUIRED — openssl rand -hex 32

# ── Database & Cache (auto-injected by Railway plugins) ──────────────
DATABASE_URL=                    # Auto-injected by Railway PostgreSQL plugin
REDIS_URL=                       # Auto-injected by Railway Redis plugin
CELERY_BROKER_URL=               # REQUIRED — copy from Redis plugin variable
CELERY_RESULT_BACKEND=           # REQUIRED — copy from Redis plugin variable
DATABASE_POOL_SIZE=10
DATABASE_MAX_OVERFLOW=20

# ── CORS & Frontend ──────────────────────────────────────────────────
FRONTEND_URL=                    # REQUIRED — https://your-frontend.up.railway.app
CORS_ORIGINS=                    # REQUIRED — https://your-frontend.up.railway.app
                                 # Comma-separated for multiple origins

# ── AI (Anthropic Claude) ────────────────────────────────────────────
ANTHROPIC_API_KEY=               # REQUIRED for AI features — sk-ant-...
AI_MODEL=claude-sonnet-4-6
AI_MAX_TOKENS=4096

# ── Email (SendGrid) ─────────────────────────────────────────────────
SENDGRID_API_KEY=                # REQUIRED for notifications — SG.xxxx
EMAIL_FROM=noreply@youragency.com
EMAIL_FROM_NAME=OakstrattonIMA

# ── Payments (Stripe) ────────────────────────────────────────────────
STRIPE_SECRET_KEY=               # REQUIRED — sk_live_xxxx or sk_test_xxxx
STRIPE_WEBHOOK_SECRET=           # REQUIRED — whsec_xxxx (from Stripe dashboard)
STRIPE_CONNECT_CLIENT_ID=        # For influencer payouts — ca_xxxx

# ── Social Media APIs (optional — for metric sync) ───────────────────
INSTAGRAM_APP_ID=
INSTAGRAM_APP_SECRET=
TIKTOK_CLIENT_KEY=
TIKTOK_CLIENT_SECRET=
YOUTUBE_API_KEY=
TWITTER_BEARER_TOKEN=

# ── File Storage (S3-compatible) ─────────────────────────────────────
S3_BUCKET_NAME=oakstratton-ima-media
S3_ENDPOINT_URL=                 # Leave blank for AWS S3; set for Cloudflare R2
AWS_ACCESS_KEY_ID=
AWS_SECRET_ACCESS_KEY=
AWS_REGION=us-east-1
```

---

### Redeployment & Migrations

- Every backend deploy automatically runs `alembic upgrade head` before starting uvicorn.
- If you add new models, generate a migration: `alembic revision --autogenerate -m "description"` and commit it — it runs automatically on next deploy.
- To force a clean redeploy (clear Railway build cache), push a new commit or click **Redeploy** in the Railway dashboard.

---

### Troubleshooting

| Symptom | Cause | Fix |
|---|---|---|
| `DATABASE_URL is not set` | PostgreSQL plugin not linked to service | Add the PostgreSQL plugin to the service in Railway dashboard |
| `AI service not configured (503)` | Missing `ANTHROPIC_API_KEY` | Add the variable to the Backend service |
| Frontend API calls fail (CORS) | `CORS_ORIGINS` doesn't match frontend URL | Update `CORS_ORIGINS` on the Backend service and redeploy |
| Frontend shows blank page on `/api/` | `BACKEND_URL` not set on Frontend service | Set `BACKEND_URL` to the backend Railway URL |
| Celery tasks not running | `CELERY_BROKER_URL` not set on Worker | Copy the Redis URL and set it on the Worker service |
| Migrations fail on startup | New migration references missing model | Check that the model is imported in `app/models/__init__.py` |

---

## Platform Features

### AI Command Center (`/ai-insights`)
- **AI Influencer Matching** — Claude analyzes campaigns against your influencer roster and returns ranked match scores (0–100) with reasoning, strengths, and concerns
- **AI Brief Generator** — Generate comprehensive campaign briefs from minimal input (product, audience, budget, platforms)
- **AI Insight Reports** — Weekly/monthly narrative performance reports auto-generated by Claude with key metrics and actionable recommendations
- **AI Chat Assistant** — Conversational assistant with persistent session history, contextual platform awareness

### Super Admin Dashboard (`/admin`, admin role only)
- **Platform Overview** — Live stats: users by role, campaigns by status, total revenue
- **Branding & White-label** — Agency name, tagline, logo URL, primary/accent/background colors, heading/body fonts, legal links
- **User Management** — Full CRUD for all users; assign any role; soft-delete
- **Feature Flags** — Toggle any AI or platform feature on/off; restrict by role
- **Audit Logs** — Immutable, searchable log of every user action across the platform

### Influencer Discovery & CRM
- Searchable roster with filter by status, platform, niche
- Multi-platform social accounts: Instagram, TikTok, YouTube, Twitter/X, Pinterest, LinkedIn
- Audience authenticity scoring, trust scores, internal notes
- AI match scores displayed on influencer cards and detail pages

### Campaign Management
- Full lifecycle: Draft → Planning → Active → Completed
- Campaign types: Brand Awareness, Product Launch, Sales, Affiliate, UGC, and more
- Budget tracking with agency fee separation
- KPI targets: reach, impressions, engagement rate, clicks, conversions, ROAS
- AI Brief panel embedded in campaign detail view

### Content Approval Workflow
- Deliverable tracking per influencer per campaign
- Multi-round review with revision count tracking
- Content types: IG Post/Story/Reel, TikTok Video, YouTube Video/Short, Twitter Post, Blog
- Auto-notification on submission, approval, or revision request

### Contracts & Legal
- Contract template library with `{{variable}}` substitution
- E-signature workflow with full audit trail
- Exclusivity clause tracking, content usage rights management
- FTC / ASA compliance checkboxes

### Payments & Invoicing
- Auto-generated invoices on deliverable completion
- Client payment via Stripe (payment intents + webhook)
- Influencer payouts via Stripe Connect
- Tax withholding metadata, W-9 / W-8BEN flags, milestone schedules

### Analytics
- Agency overview dashboard with KPI cards
- Per-campaign metrics: reach, impressions, engagement, CPM, ROAS, conversions
- Gradient-fill charts powered by Recharts

### Automation (Celery Beat)
- Social metrics sync every 6 hours
- Overdue invoice detection daily
- Deliverable due-date reminders 48 hours in advance
- Automatic Stripe payout processing

---

## API Reference

Swagger UI available at `https://your-backend.railway.app/docs` when `DEBUG=true`.

### Endpoint Summary

| Method | Path | Auth | Description |
|---|---|---|---|
| `POST` | `/api/v1/auth/login` | — | Get JWT tokens |
| `POST` | `/api/v1/auth/register` | — | Register new user |
| `GET` | `/api/v1/auth/me` | Any | Current user profile |
| `GET` | `/api/v1/influencers` | Any | List influencers |
| `GET` | `/api/v1/campaigns` | Any | List campaigns |
| `GET` | `/api/v1/clients` | Manager+ | List clients |
| `GET` | `/api/v1/contracts` | Any | List contracts |
| `GET` | `/api/v1/payments/invoices` | Manager+ | List invoices |
| `GET` | `/api/v1/analytics/overview` | Manager+ | Agency KPIs |
| `POST` | `/api/v1/ai/match-influencers` | Manager+ | AI influencer matching |
| `POST` | `/api/v1/ai/generate-brief` | Manager+ | AI campaign brief |
| `POST` | `/api/v1/ai/analyze-content` | Manager+ | AI content scoring |
| `GET` | `/api/v1/ai/insights` | Manager+ | AI insight reports |
| `POST` | `/api/v1/ai/chat/sessions` | Manager+ | Start AI chat session |
| `GET` | `/api/v1/admin/settings` | Admin | Platform settings |
| `PATCH` | `/api/v1/admin/settings` | Admin | Update platform settings |
| `GET` | `/api/v1/admin/users` | Admin | All users |
| `GET` | `/api/v1/admin/feature-flags` | Admin | Feature flags |
| `GET` | `/api/v1/admin/audit-logs` | Admin | Audit log |
| `GET` | `/api/v1/admin/stats` | Admin | Platform statistics |

### Roles

| Role | Access |
|---|---|
| `admin` | Full access including `/admin/*` routes |
| `manager` | Campaigns, influencers, clients, contracts, payments, AI features |
| `client` | Own campaigns and invoices (read) |
| `influencer` | Own profile, assigned campaigns, contract signing |

---

## Project Structure

```
oakstrattonIMA/
├── backend/
│   ├── app/
│   │   ├── api/v1/endpoints/
│   │   │   ├── auth.py, influencers.py, campaigns.py
│   │   │   ├── clients.py, contracts.py, payments.py
│   │   │   ├── analytics.py, notifications.py
│   │   │   ├── ai.py          ← AI features API
│   │   │   └── admin.py       ← Super admin API
│   │   ├── core/              # config, security, deps, exceptions
│   │   ├── db/                # session, base
│   │   ├── models/
│   │   │   ├── user.py, influencer.py, campaign.py, client.py
│   │   │   ├── contract.py, payment.py, social_account.py, notification.py
│   │   │   ├── platform_settings.py  ← PlatformSettings, FeatureFlag, AuditLog
│   │   │   └── ai_result.py          ← AIAnalysis, AIInsightReport, AIChatSession/Message
│   │   ├── schemas/
│   │   │   ├── auth.py, user.py, influencer.py, campaign.py, common.py
│   │   │   ├── admin.py       ← Admin request/response schemas
│   │   │   └── ai.py          ← AI request/response schemas
│   │   ├── services/
│   │   │   ├── ai/
│   │   │   │   ├── client.py          ← Shared Anthropic AsyncAnthropic client
│   │   │   │   ├── matching.py        ← Influencer-campaign matching
│   │   │   │   ├── brief_generator.py ← Campaign brief generation
│   │   │   │   ├── content_analyzer.py← Content safety/quality scoring
│   │   │   │   └── insights.py        ← Weekly/monthly insight reports
│   │   │   └── audit.py       ← log_action() helper for audit trail
│   │   ├── tasks/             # Celery: notifications, metrics_sync, payments
│   │   └── main.py
│   ├── migrations/
│   │   └── versions/
│   │       ├── 0001_initial_schema.py   ← All core tables
│   │       └── 0002_ai_and_admin_tables.py ← AI + admin tables + seed data
│   ├── start.sh               ← Validates DATABASE_URL, runs migrations, starts uvicorn
│   ├── Dockerfile
│   ├── Dockerfile.celery
│   └── requirements.txt
├── frontend/
│   └── src/
│       ├── components/layout/
│       │   └── DashboardLayout.tsx  ← Sidebar with AI + Admin sections
│       ├── pages/
│       │   ├── LoginPage.tsx
│       │   ├── DashboardPage.tsx
│       │   ├── InfluencersPage.tsx
│       │   ├── InfluencerDetailPage.tsx
│       │   ├── CampaignsPage.tsx
│       │   ├── CampaignDetailPage.tsx
│       │   ├── ClientsPage.tsx
│       │   ├── ContractsPage.tsx
│       │   ├── PaymentsPage.tsx
│       │   ├── AnalyticsPage.tsx
│       │   ├── AIInsightsPage.tsx   ← AI Command Center (4 tabs)
│       │   └── AdminPage.tsx        ← Super Admin Dashboard (5 tabs)
│       ├── store/authStore.ts
│       ├── types/index.ts
│       └── utils/api.ts             ← Axios + JWT auto-refresh
├── railway.toml                 ← Backend build/deploy config
├── .env.example                 ← All env var reference with comments
└── CLAUDE.md
```

---

## Database Schema

```
users
  ├── influencers ──► social_accounts
  │       └── campaign_influencers ──► deliverables
  │                   ├── contracts
  │                   └── payouts
  ├── clients ──► brands
  │       └── campaigns ──► campaign_influencers
  │               └── campaign_metrics
  │               └── invoices ──► transactions
  ├── notifications
  ├── ai_chat_sessions ──► ai_chat_messages
  └── [referenced by]
        ├── audit_logs
        ├── ai_analyses
        └── ai_insight_reports

platform_settings   (singleton, id=1 — agency branding & config)
feature_flags       (per-feature enable/disable with role restrictions)
```

---

## Testing

```bash
cd backend
pytest tests/ -v --cov=app --cov-report=term-missing
```

80%+ coverage target. Async tests use `pytest-asyncio`.

---

## License

Proprietary — OakstrattonIMA. All rights reserved.
