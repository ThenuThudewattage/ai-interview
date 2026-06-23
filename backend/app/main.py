"""FastAPI application entry point."""
import logging

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.router import api_router
from app.config import settings
from app.core.exceptions import AppException
from app.db.database import create_all_tables

logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
logger = logging.getLogger(__name__)

# ── App initialization ─────────────────────────────────────────

app = FastAPI(
    title="AI Interview Intelligence Platform",
    description=(
        "Production-grade agentic AI interview platform with multi-agent orchestration, "
        "RAG-powered question retrieval, and personalized learning paths."
    ),
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# ── CORS ──────────────────────────────────────────────────────

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Exception handlers ─────────────────────────────────────────

@app.exception_handler(AppException)
async def app_exception_handler(request: Request, exc: AppException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.message, "status_code": exc.status_code},
    )


@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error", "status_code": 500},
    )

# ── Startup / Shutdown ─────────────────────────────────────────

@app.on_event("startup")
async def startup():
    logger.info("🚀 AI Interview Platform starting...")
    if settings.APP_ENV == "development":
        logger.info("📊 Dev mode: creating tables if not exist...")
        await create_all_tables()
    logger.info("✅ Server ready!")


@app.on_event("shutdown")
async def shutdown():
    logger.info("👋 Server shutting down...")

# ── Routes ────────────────────────────────────────────────────

app.include_router(api_router)


@app.get("/health", tags=["Health"])
async def health_check():
    return {
        "status": "healthy",
        "version": "1.0.0",
        "environment": settings.APP_ENV,
    }


@app.get("/", tags=["Root"])
async def root():
    return {
        "message": "AI Interview Intelligence Platform API",
        "docs": "/docs",
        "version": "1.0.0",
    }
