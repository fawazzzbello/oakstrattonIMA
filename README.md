# OakstrattonIMA

**Full-stack Influencer Marketing Agency (IMA) Platform**

OakstrattonIMA streamlines every stage of influencer marketing — from creator discovery and campaign management to contract signing, payment processing, and ROI analytics — all in one platform.

---

## Tech Stack

| Layer | Technology |
|---|---|
| **Backend API** | Python 3.11 · FastAPI · SQLAlchemy 2.0 (async) |
| **Database** | PostgreSQL 15 (Railway managed) |
| **Cache / Queue** | Redis (Railway managed) |
| **Background Tasks** | Celery + Redis Beat |
| **Frontend** | React 18 · TypeScript · Vite · TailwindCSS |
| **Auth** | JWT (access + refresh tokens) · Role-based (admin/manager/client/influencer) |
| **Payments** | Stripe (client invoicing) · Stripe Connect (influencer payouts) |
| **Email** | SendGrid |
| **File Storage** | S3-compatible (AWS S3 / Cloudflare R2) |
| **Deployment** | Railway.com |

---

## Platform Features

### Influencer Discovery & CRM
- Searchable influencer roster with 50+ filter dimensions (niche, location, followers, engagement rate, tier)
- Multi-platform social accounts: Instagram, TikTok, YouTube, Twitter/X, Pinterest, LinkedIn
- Automated audience authenticity scoring (fake follower detection)
- Trust scores, internal notes, and relationship history per creator
- Influencer tiering: nano · micro · macro · mega

### Campaign Management
- Full campaign lifecycle: Draft → Planning → Active → Completed
- Campaign types: Brand Awareness, Product Launch, Sales, Affiliate, UGC, etc.
- Budget tracking per campaign with agency fee separation
- KPI targets: reach, impressions, engagement rate, clicks, conversions, ROAS
- FTC disclosure tracking baked into approval workflow

### Content Approval Workflow
- Deliverable tracking per influencer per campaign
- Multi-round review loop with revision count tracking
- Content types: IG Post/Story/Reel, TikTok Video, YouTube Video/Short, Twitter Post, Blog
- Auto-notification on submission, approval, or revision request

### Contracts & Legal
- Contract template library with `{{variable}}` substitution
- E-signature workflow with full audit trail
- Exclusivity clause tracking with date alerts
- Content usage rights management (organic + paid amplification)
- FTC / ASA compliance checkboxes

### Payments & Invoicing
- Auto-generated invoices on deliverable completion
- Client payment via Stripe (payment intents + webhook confirmation)
- Influencer payouts via Stripe Connect transfers
- Tax withholding metadata and W-9 / W-8BEN collection flags
- Milestone-based payment schedules stored per contract

### Analytics & Reporting
- Agency overview dashboard: active campaigns, revenue YTD, pending/overdue invoices
- Per-campaign metrics: reach, impressions, engagement, CPM, ROAS, conversions
- Per-influencer performance rollup across all campaigns
- Charts: bar, line, pie (powered by Recharts)

### Automation (Celery Beat)
- Social metrics sync every 6 hours (Instagram, TikTok, YouTube APIs)
- Overdue invoice detection daily
- Deliverable due-date reminders 48 hours in advance
- Automatic Stripe payout processing

---

## Quick Start

### Prerequisites
- Python 3.11+
- Node.js 20+
- PostgreSQL 15+
- Redis 7+

### 1. Clone & Configure

```bash
git clone <repo-url>
cd oakstrattonIMA
cp .env.example .env
# Edit .env with your credentials
```

### 2. Backend Setup

```bash
cd backend
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt

# Run database migrations
alembic upgrade head

# Start API server
uvicorn app.main:app --reload --port 8000
```

### 3. Celery Worker

```bash
# In a separate terminal (with venv activated)
cd backend
celery -A app.tasks.worker worker -l info

# Optional: Celery Beat scheduler
celery -A app.tasks.worker beat -l info

# Optional: Flower monitoring UI (http://localhost:5555)
celery -A app.tasks.worker flower
```

### 4. Frontend Setup

```bash
cd frontend
npm install
npm run dev   # http://localhost:5173
```

### 5. Seed Demo Data

```bash
cd backend && python ../scripts/seed.py
```

---

## API Reference

Swagger UI is available at `http://localhost:8000/docs` when `DEBUG=true`.

### Endpoints Summary

| Method | Path | Description |
|---|---|---|
| `POST` | `/api/v1/auth/login` | Get JWT tokens |
| `POST` | `/api/v1/auth/register` | Register new user |
| `POST` | `/api/v1/auth/refresh` | Refresh access token |
| `GET` | `/api/v1/auth/me` | Current user profile |
| `GET` | `/api/v1/influencers` | List influencers (filterable) |
| `POST` | `/api/v1/influencers` | Create influencer profile |
| `GET` | `/api/v1/influencers/:id` | Influencer detail |
| `PATCH` | `/api/v1/influencers/:id` | Update influencer |
| `POST` | `/api/v1/influencers/:id/social-accounts` | Add social account |
| `GET` | `/api/v1/campaigns` | List campaigns |
| `POST` | `/api/v1/campaigns` | Create campaign |
| `PATCH` | `/api/v1/campaigns/:id` | Update campaign |
| `POST` | `/api/v1/campaigns/:id/influencers` | Add influencer to campaign |
| `PATCH` | `/api/v1/campaigns/:id/influencers/:ci_id` | Update campaign influencer |
| `PATCH` | `/api/v1/campaigns/:id/deliverables/:d_id` | Update deliverable |
| `GET` | `/api/v1/campaigns/:id/metrics` | Campaign performance |
| `GET` | `/api/v1/clients` | List clients |
| `POST` | `/api/v1/clients` | Create client |
| `POST` | `/api/v1/clients/:id/brands` | Add brand |
| `GET` | `/api/v1/contracts` | List contracts |
| `POST` | `/api/v1/contracts` | Create contract |
| `POST` | `/api/v1/contracts/:id/sign` | Sign contract |
| `GET` | `/api/v1/contracts/templates` | List templates |
| `GET` | `/api/v1/payments/invoices` | List invoices |
| `POST` | `/api/v1/payments/invoices` | Create invoice |
| `POST` | `/api/v1/payments/invoices/:id/send` | Send invoice to client |
| `POST` | `/api/v1/payments/payouts` | Create payout |
| `POST` | `/api/v1/payments/stripe/webhook` | Stripe webhook handler |
| `GET` | `/api/v1/analytics/overview` | Agency overview KPIs |
| `GET` | `/api/v1/analytics/campaigns` | Campaign performance table |
| `GET` | `/api/v1/analytics/influencer/:id/performance` | Influencer stats |
| `GET` | `/api/v1/notifications` | User notifications |
| `POST` | `/api/v1/notifications/:id/read` | Mark notification read |

### Authentication

All protected routes require:
```
Authorization: Bearer <access_token>
```

### Roles & Permissions

| Role | Access |
|---|---|
| `admin` | Full access to everything |
| `manager` | Read/write campaigns, influencers, clients, contracts, payments |
| `client` | Read own campaigns and invoices |
| `influencer` | Read own profile, campaigns they're in, sign contracts |

---

## Deployment (Railway.com)

### Services Required
1. **Backend** — FastAPI API server
2. **Worker** — Celery worker (background tasks)
3. **Frontend** — React SPA (served via nginx)
4. **PostgreSQL** — Railway Postgres plugin
5. **Redis** — Railway Redis plugin

### Deploy

```bash
# Install Railway CLI
npm install -g @railway/cli

# Login and link project
railway login
railway link

# Deploy all services
railway up
```

### Required Environment Variables (Railway Dashboard)

```
SECRET_KEY=<random 32-byte hex>
DATABASE_URL=<auto-injected by Railway Postgres plugin>
REDIS_URL=<auto-injected by Railway Redis plugin>
SENDGRID_API_KEY=<your sendgrid key>
STRIPE_SECRET_KEY=<your stripe key>
STRIPE_WEBHOOK_SECRET=<your stripe webhook secret>
FRONTEND_URL=<your deployed frontend URL>
CORS_ORIGINS=["https://your-frontend.railway.app"]
```

See `.env.example` for the full list.

---

## Project Structure

```
oakstrattonIMA/
├── backend/
│   ├── app/
│   │   ├── api/v1/endpoints/   # auth, influencers, campaigns, clients,
│   │   │                       # analytics, payments, contracts, notifications
│   │   ├── core/               # config, security, deps, exceptions
│   │   ├── db/                 # session, base
│   │   ├── models/             # SQLAlchemy ORM models
│   │   ├── schemas/            # Pydantic request/response schemas
│   │   ├── tasks/              # Celery: notifications, metrics_sync, payments
│   │   └── main.py             # FastAPI app entrypoint
│   ├── migrations/             # Alembic migration files
│   ├── tests/                  # Pytest test suite
│   ├── Dockerfile              # API server image
│   ├── Dockerfile.celery       # Celery worker image
│   ├── alembic.ini
│   └── requirements.txt
├── frontend/
│   └── src/
│       ├── components/
│       │   └── layout/         # DashboardLayout, sidebar, topbar
│       ├── pages/              # Dashboard, Influencers, Campaigns,
│       │                       # Clients, Contracts, Payments, Analytics
│       ├── hooks/              # useAuth, React Query hooks
│       ├── store/              # Zustand: authStore
│       ├── types/              # TypeScript interfaces (mirrors backend models)
│       └── utils/              # api.ts (axios + auto-refresh), cn.ts
├── scripts/
│   ├── setup.sh                # One-time local setup
│   ├── dev.sh                  # Start all services locally
│   ├── migrate.sh              # Run Alembic migrations
│   ├── deploy.sh               # Railway deployment helper
│   └── seed.py                 # Demo data seeder
├── docs/
├── railway.toml                # Railway multi-service config
├── .env.example                # Environment variable template
├── .gitignore
└── CLAUDE.md                   # Claude Code instructions
```

---

## Database Schema

Core entities and relationships:

```
users ──────────────────────────────────────────────────────┐
  │                                                          │
  ├─► influencers ──► social_accounts                       │
  │       │                                                  │
  │       └─► campaign_influencers ──► deliverables         │
  │                   │                                      │
  │                   └─► contracts                         │
  │                   └─► payouts                           │
  │                                                          │
  └─► clients ──► brands                                    │
          │                                                  │
          └─► campaigns ──► campaign_influencers            │
          │       │                                          │
          │       └─► campaign_metrics                      │
          │                                                  │
          └─► invoices ──► transactions                     │
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
