from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from app.core.config import settings
from app.api.v1.router import api_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: verify DB connection + apply platform AI config
    from app.db.session import engine, AsyncSessionLocal
    async with engine.begin() as conn:
        pass  # tables managed by Alembic migrations

    # Load platform AI provider/model overrides so ai_client uses DB settings
    try:
        from sqlalchemy import select
        from app.models.platform_settings import PlatformSettings
        from app.services.ai.client import ai_client
        async with AsyncSessionLocal() as session:
            result = await session.execute(select(PlatformSettings).where(PlatformSettings.id == 1))
            ps = result.scalar_one_or_none()
            if ps and (ps.ai_provider_override or ps.ai_model_override):
                provider = ps.ai_provider_override or ai_client.active_provider
                model = ps.ai_model_override or ai_client.active_model
                try:
                    ai_client.configure(provider, model)
                except ValueError:
                    pass
    except Exception:
        pass  # DB may not be ready yet on first deploy; migrations run first

    yield
    # Shutdown: close DB pool
    await engine.dispose()


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="OakstrattonIMA — Influencer Marketing Agency Platform API",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routes
app.include_router(api_router)


@app.get("/health")
async def health_check():
    return {"status": "ok", "version": settings.APP_VERSION}


@app.get("/")
async def root():
    return {"app": settings.APP_NAME, "version": settings.APP_VERSION}
