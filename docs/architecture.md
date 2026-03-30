# OakstrattonIMA — Architecture Reference

## System Architecture

```
                    ┌─────────────────────────────────────┐
                    │           Railway.com                │
                    │                                      │
  User Browser ─────┤─► Frontend (React SPA / nginx)      │
                    │       ↓ /api/v1/*                    │
                    │   Backend (FastAPI)                  │
                    │       │                              │
                    │       ├── PostgreSQL (Railway)       │
                    │       ├── Redis (Railway)            │
                    │       └── S3-compatible storage      │
                    │                                      │
                    │   Celery Worker                      │
                    │       ├── Beat scheduler             │
                    │       ├── Metrics sync tasks         │
                    │       ├── Email tasks (SendGrid)     │
                    │       └── Payment tasks (Stripe)     │
                    └─────────────────────────────────────┘
```

## Data Flow

### Authentication Flow
```
Client → POST /api/v1/auth/login
       → Verify credentials in DB
       → Return access_token (24h) + refresh_token (30d)
       → Client stores in localStorage
       → Every request: Authorization: Bearer <token>
       → On 401: auto-refresh via interceptor
```

### Campaign Workflow
```
1. Manager creates Campaign (status=draft)
2. Manager adds influencers → CampaignInfluencer records (status=invited)
3. Agency negotiates fee → agreed_fee set
4. Contract generated from template → sent to influencer
5. Both parties sign → ContractStatus=fully_executed
6. CampaignInfluencer.status → contracted
7. Deliverables tracked per influencer
8. Influencer submits content → status=submitted
9. Manager approves → status=approved
10. Content published → status=published
11. Celery syncs post metrics from social APIs
12. CampaignMetrics aggregated
13. Invoice generated for client
14. Payout triggered for influencer (Stripe Connect)
```

## Database

### Connection
- Async via `asyncpg` driver
- SQLAlchemy 2.0 async sessions
- Connection pool: 10 base + 20 overflow

### Migrations
- Alembic with async support
- Auto-generate from model changes: `alembic revision --autogenerate -m "description"`
- Apply: `alembic upgrade head`
- Rollback: `alembic downgrade -1`

### Key Constraints
- All monetary values: `NUMERIC(12,2)` — no floating point for money
- All timestamps: `DateTime(timezone=True)` — always UTC
- Soft deletes: `is_active` flag, never hard-delete user data
- Audit trail: `created_at` / `updated_at` on all tables

## Security

### JWT Strategy
- Access tokens: 24-hour expiry (configurable)
- Refresh tokens: 30-day expiry, stored in localStorage
- Algorithm: HS256
- Auto-refresh: Frontend interceptor catches 401, refreshes silently

### Role-Based Access Control
| Role | Scope |
|---|---|
| admin | Full platform access |
| manager | Campaigns, influencers, clients, contracts, payments |
| client | Own campaigns and invoices only |
| influencer | Own profile, assigned campaigns, sign contracts |

### API Security
- CORS restricted to configured origins
- All financial mutations require manager+ role
- Influencers can only access their own data
- Stripe webhook signature verified before processing

## External Services

### Stripe
- Client invoicing: Payment Intents API
- Webhook confirms payment → Invoice status → PAID
- Influencer payouts: Stripe Connect transfers
- Setup: `STRIPE_SECRET_KEY`, `STRIPE_WEBHOOK_SECRET`, `STRIPE_CONNECT_CLIENT_ID`

### SendGrid
- Transactional emails: invoices, contracts, reminders
- Template-free: HTML body composed in task functions
- Setup: `SENDGRID_API_KEY`, `EMAIL_FROM`

### Social APIs

| Platform | API | Rate Limits | Auth Type |
|---|---|---|---|
| Instagram | Meta Graph API v21 | 200 req/hr/user | OAuth per-user |
| TikTok | TikTok Display API v2 | 600 req/5min | OAuth per-user |
| YouTube | Data API v3 | 10,000 quota/day | API key or OAuth |
| Twitter/X | v2 API | Tier-dependent | Bearer token |

All social API calls go through `app/tasks/metrics_sync.py` with built-in error handling.

## Celery Task Architecture

```
app/tasks/worker.py          → Celery app + Beat schedule
app/tasks/notifications.py   → Email sending tasks
app/tasks/metrics_sync.py    → Social API polling
app/tasks/payment_processing.py → Stripe payouts, invoice overdue
```

### Beat Schedule
| Task | Interval | Purpose |
|---|---|---|
| `sync_all_active_campaign_metrics` | Every 6 hours | Pull post metrics from social APIs |
| `mark_overdue_invoices` | Daily | Flip invoice status to OVERDUE |
| `send_deliverable_reminders` | Daily | Email creators with upcoming due dates |

## Frontend Architecture

### State Management
- **Auth state**: Zustand + `persist` middleware (localStorage)
- **Server state**: React Query (auto-caching, background refetch, pagination)
- **Form state**: React Hook Form + Zod validation

### API Layer
- Axios instance at `src/utils/api.ts`
- Request interceptor: auto-attach Bearer token
- Response interceptor: silent token refresh on 401, redirect to /login on failure

### Routing
- React Router v6 with nested routes
- `ProtectedRoute` wrapper checks `isAuthenticated` from auth store
- All dashboard routes nested under `/` → `DashboardLayout`

### Component Structure
```
DashboardLayout     Persistent sidebar + topbar, renders <Outlet />
  ├── DashboardPage       KPI grid, quick actions
  ├── InfluencersPage     Search/filter grid of influencer cards
  ├── InfluencerDetailPage Profile, social accounts, campaign history
  ├── CampaignsPage       Campaign list with status filters
  ├── CampaignDetailPage  Influencer pipeline, deliverables, metrics
  ├── ClientsPage         Client CRM with brand breakdown
  ├── ContractsPage       Contract list with sign/void actions
  ├── PaymentsPage        Invoice + payout management
  └── AnalyticsPage       Charts: campaign performance, revenue trends
```
