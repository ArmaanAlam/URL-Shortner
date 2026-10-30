import time
from fastapi import FastAPI, Request, HTTPException, Depends, status
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.cache import cache
from app.core.exceptions import URLNotFoundException
from app.schemas.url import HealthCheckResponse
from app.api.deps import get_shortener_service
from app.services.shortener_service import URLShortenerService
from app.api.endpoints.url import router as url_router

def create_app() -> FastAPI:
    """Application factory: initializes routers, middlewares, and metadata."""
    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        description="Industrial-grade URL shortener engineered from first principles."
    )

    # 1. CORS Middleware (Chapter 01: HTTP & CORS)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # 2. Observability & Timing Middleware (Chapter 06 & 15)
    @app.middleware("http")
    async def process_timing_middleware(request: Request, call_next):
        start = time.time()
        response = await call_next(request)
        duration = time.time() - start
        response.headers["X-Response-Time"] = f"{duration * 1000:.2f}ms"
        return response

    # 3. Mount Routers
    app.include_router(url_router)

    # 4. Root Health Check
    @app.get("/", response_model=HealthCheckResponse, tags=["Health"])
    def health_check():
        return {
            "status": "healthy",
            "service": settings.APP_NAME,
            "cached_keys_count": cache.count()
        }

    # 5. Core Redirect Path (HTTP 302 Found)
    @app.get("/{key}", tags=["Redirect"])
    def redirect(
        key: str,
        request: Request,
        service: URLShortenerService = Depends(get_shortener_service)
    ):
        referrer = request.headers.get("referer")
        user_agent = request.headers.get("user-agent")
        try:
            target_url = service.resolve_url(key=key, referrer=referrer, user_agent=user_agent)
            return RedirectResponse(url=target_url, status_code=status.HTTP_302_FOUND)
        except URLNotFoundException as e:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

    return app

app = create_app()

if __name__ == "__main__":
    import uvicorn
    print(f"Starting server on http://{settings.HOST}:{settings.PORT} ...")
    uvicorn.run("app.main:app", host=settings.HOST, port=settings.PORT, reload=True)
