# OakstrattonIMA — Claude Code Instructions

## Project Overview
OakstrattonIMA is a full-stack Influencer Marketing Agency (IMA) platform. It streamlines influencer discovery, campaign management, contracts, payments, and analytics for the agency and its brand clients.

## Architecture
- **Backend**: Python 3.11 + FastAPI + SQLAlchemy 2.0 + Alembic
- **Frontend**: React 18 + TypeScript + Vite + TailwindCSS + shadcn/ui
- **Database**: PostgreSQL 15 (Railway managed)
- **Cache/Queue**: Redis (Railway managed)
- **Task Queue**: Celery + Redis
- **Deployment**: Railway.com (backend + frontend + postgres + redis services)

## Repository Layout
```
oakstrattonIMA/
├── backend/           # FastAPI application
│   ├── app/
│   │   ├── api/v1/endpoints/   # Route handlers
│   │   ├── core/               # Config, security, deps
│   │   ├── db/                 # Database session, base
│   │   ├── models/             # SQLAlchemy ORM models
│   │   ├── schemas/            # Pydantic request/response schemas
│   │   ├── services/           # Business logic layer
│   │   ├── tasks/              # Celery async tasks
│   │   └── utils/              # Helpers (email, social APIs, etc.)
│   ├── migrations/             # Alembic migration files
│   └── tests/                  # Pytest test suite
├── frontend/          # React + Vite SPA
│   └── src/
│       ├── components/         # Reusable UI components
│       ├── pages/              # Route-level page components
│       ├── hooks/              # Custom React hooks
│       ├── store/              # Zustand global state
│       └── types/              # TypeScript type definitions
├── scripts/           # Dev/deploy helper scripts
└── docs/              # Architecture docs, API references
```

## Development Commands

### Backend
```bash
cd backend
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
alembic upgrade head                    # Run migrations
uvicorn app.main:app --reload           # Dev server (port 8000)
celery -A app.tasks.worker worker -l info   # Celery worker
pytest tests/ -v                        # Run tests
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

1. **Never expose secrets** — All credentials go in `.env`, never hardcoded.
2. **API versioning** — All routes are prefixed `/api/v1/`. Do not break existing endpoints.
3. **DB migrations** — Every model change requires an Alembic migration. Run `alembic revision --autogenerate -m "description"`.
4. **Auth** — JWT tokens via `/api/v1/auth/`. Role-based access: `admin`, `manager`, `client`, `influencer`.
5. **Pagination** — All list endpoints must support `?skip=0&limit=50` with a `total` count in response.
6. **Async first** — Use `async def` for all FastAPI route handlers and SQLAlchemy async sessions.
7. **Social API rate limits** — All social platform API calls go through `app/utils/social/` with built-in rate limit handling and caching.
8. **Financial data** — All monetary values stored as `NUMERIC(12,2)` in cents-free format (e.g. 1500.00 = $1,500.00).
9. **File uploads** — Media/documents stored in Railway Volume or S3-compatible bucket. Never store blobs in Postgres.
10. **Error handling** — Use `app/core/exceptions.py` custom exceptions. Always return structured `{"detail": "..."}` error responses.

## Key Workflows

### Influencer Onboarding
1. Influencer submits application via `/apply` public page
2. Agency reviews → approves/rejects in dashboard
3. On approval: contract template auto-sent, social handles verified via APIs
4. Influencer added to discoverable roster

### Campaign Lifecycle
1. Client creates campaign brief (goals, budget, timeline, content requirements)
2. Agency discovers & pitches influencers → sends proposals
3. Influencers accept/negotiate → countersign contracts
4. Content submitted for approval → feedback loop
5. Published content tracked → metrics pulled from social APIs
6. Campaign closes → final report generated → payment released

### Payment Flow
1. Deliverable marked complete by agency
2. Invoice auto-generated → sent to client
3. Client payment processed (Stripe)
4. Influencer payout triggered (Stripe Connect or bank transfer)
5. All transactions logged with tax metadata

## Railway Deployment
- Backend: `railway up` from `/backend` — Dockerfile provided
- Frontend: Static site deploy or Railway static service from `/frontend/dist`
- Database: Railway Postgres — connection via `DATABASE_URL` env var
- Redis: Railway Redis — connection via `REDIS_URL` env var
- Environment variables: Set in Railway dashboard, mirror `.env.example`

## Testing Standards
- Backend: `pytest` with `pytest-asyncio` for async tests; 80%+ coverage target
- Frontend: Vitest + React Testing Library for component tests
- Integration tests in `backend/tests/integration/` use a test PostgreSQL database

## Code Style
- Python: `ruff` for linting + formatting (`ruff check . --fix && ruff format .`)
- TypeScript: ESLint + Prettier (`npm run lint && npm run format`)
- Commit messages: Conventional Commits (`feat:`, `fix:`, `chore:`, `docs:`)
