from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import logging
import os

from src.database import DatabaseConnection, init_tables
from src.auth.middleware import init_auth

logger = logging.getLogger("expense_tracker.web")


def create_app() -> FastAPI:
    app = FastAPI(
        title="Smart Expense Tracker",
        description="API for Seamless Technologies expense management",
        version="1.0.0",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    db = DatabaseConnection()
    init_tables(db)
    init_auth(db)
    app.state.db = db

    from src.db.repositories.gamification import GamificationRepository
    from src.services.gamification_service import GamificationService
    gami_repo = GamificationRepository(db)
    gami_service = GamificationService(gami_repo)
    gami_service.ensure_seeded()

    base_dir = os.path.dirname(os.path.abspath(__file__))
    templates_dir = os.path.join(base_dir, "templates")
    static_dir = os.path.join(base_dir, "static")

    if os.path.isdir(templates_dir):
        app.state.templates = Jinja2Templates(directory=templates_dir)
    if os.path.isdir(static_dir):
        app.mount("/static", StaticFiles(directory=static_dir), name="static")

    from src.web.routes.pages import router as pages_router
    from src.web.routes.auth import router as auth_router
    from src.web.routes.staff import router as staff_router
    from src.web.routes.expenses import router as expenses_router
    from src.web.routes.categories import router as categories_router
    from src.web.routes.recurring import router as recurring_router
    from src.web.routes.analytics import router as analytics_router
    from src.web.routes.gamification import router as gamification_router
    from src.web.routes.settings import router as settings_router
    from src.web.routes.reports import router as reports_router
    from src.web.routes.sync import router as sync_router

    app.include_router(pages_router, tags=["Pages"])
    app.include_router(auth_router, prefix="/api/auth", tags=["Auth"])
    app.include_router(staff_router, prefix="/api/staff", tags=["Staff"])
    app.include_router(expenses_router, prefix="/api/expenses", tags=["Expenses"])
    app.include_router(categories_router, prefix="/api/categories", tags=["Categories"])
    app.include_router(recurring_router, prefix="/api/recurring", tags=["Recurring"])
    app.include_router(analytics_router, prefix="/api/analytics", tags=["Analytics"])
    app.include_router(gamification_router, prefix="/api/gamification", tags=["Gamification"])
    app.include_router(settings_router, prefix="/api/settings", tags=["Settings"])
    app.include_router(reports_router, prefix="/api/reports", tags=["Reports"])
    app.include_router(sync_router, prefix="/api/sync", tags=["Sync"])

    @app.get("/api/health")
    def health():
        return {"status": "ok"}

    @app.on_event("shutdown")
    def shutdown():
        db.close()

    return app


def start_server(host: str = "0.0.0.0", port: int = 7070):
    import uvicorn
    app = create_app()
    uvicorn.run(app, host=host, port=port, log_level="info")


def start_background_server(port: int = 7070):
    import threading
    import uvicorn
    import logging

    logging.basicConfig(level=logging.INFO)

    app = create_app()

    config = uvicorn.Config(app, host="0.0.0.0", port=port, log_level="info")
    server = uvicorn.Server(config)

    thread = threading.Thread(target=server.run, daemon=True)
    thread.start()
    logger.info("Web server started on port %d", port)
    return server
