"""Veyo's API. Run from backend: python -m uvicorn veyo.app:app --port 8000."""
import logging
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from .config import Settings
from .store import LocalStore
from .engine import InferenceEngine, EngineBusy
from .analysis import AnalysisService
from .middleware import RequestLimits
from . import routes_projects, routes_assets, routes_analysis, routes_adjustments, routes_comparisons


def create_app(settings: Settings | None = None, store=None, engine=None) -> FastAPI:
    settings = settings or Settings.from_env()
    application = FastAPI(title="Veyo Attention Studio", version="1.0.0", docs_url="/api/docs",
                          openapi_url="/api/openapi.json", redoc_url=None)
    if store is None:
        if settings.bucket:
            from .cloud_store import CloudStore
            store = CloudStore(settings.bucket)
        else:
            store = LocalStore(settings.storage_dir)
    application.state.settings = settings
    application.state.store = store
    application.state.engine = engine or InferenceEngine(settings)
    application.state.analysis = AnalysisService(application.state.engine)
    application.add_middleware(RequestLimits)
    application.add_middleware(CORSMiddleware, allow_origins=list(settings.allowed_origins),
                               allow_methods=["GET", "POST", "PUT", "PATCH", "OPTIONS"],
                               allow_headers=["Content-Type", "X-Workspace-Key"])

    @application.exception_handler(FileNotFoundError)
    async def missing(_request: Request, _exc):
        return JSONResponse({"detail": "This item was not found in your workspace."}, status_code=404)

    @application.exception_handler(ValueError)
    async def invalid(_request: Request, exc):
        return JSONResponse({"detail": str(exc)}, status_code=422)

    @application.exception_handler(EngineBusy)
    async def busy(_request: Request, exc):
        return JSONResponse({"detail": str(exc)}, status_code=429, headers={"Retry-After": "5"})

    @application.exception_handler(Exception)
    async def unexpected(_request: Request, exc):
        logging.getLogger("veyo").error("Request failed", exc_info=exc)
        return JSONResponse({"detail": "Something went wrong. Your saved creatives are safe; please try again."}, status_code=500)

    @application.get("/api/health")
    def health():
        return {"status": "ok", "version": "1.0.0", **application.state.engine.status,
                "storage": "cloud" if settings.bucket else "local"}

    for module in (routes_projects, routes_assets, routes_analysis, routes_adjustments, routes_comparisons):
        application.include_router(module.router)
    return application


app = create_app()
