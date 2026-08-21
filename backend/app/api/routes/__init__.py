from fastapi import APIRouter

from app.api.routes import admin, categories, health, jobs, news, sources, admin_routes

router = APIRouter()
router.include_router(admin.router, tags=["admin"])
router.include_router(admin_routes.router, tags=["admin_routes"])
router.include_router(categories.router, tags=["categories"])
router.include_router(health.router, tags=["health"])
router.include_router(jobs.router, tags=["jobs"])
router.include_router(news.router,  tags=["news"])
router.include_router(sources.router, tags=["sources"])

