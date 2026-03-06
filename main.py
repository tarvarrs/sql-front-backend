#!/usr/bin/env python3
import asyncio

# from prometheus_client import make_asgi_app, Counter, Histogram
import time

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config import settings
from src.api.achievement import router as achievement_router
from src.api.analytics import router as analytics_router
from src.api.auth import router as auth_router
from src.api.profile import router as profile_router
from src.api.rating import router as rating_router
from src.api.task import router as task_router
from src.api.user_activity import router as activity_router

app = FastAPI()

# # Добавьте Prometheus middleware
# metrics_app = make_asgi_app()
# app.mount("/metrics", metrics_app)

# # Создайте метрики
# REQUEST_COUNT = Counter(
#     'request_count', 'App Request Count',
#     ['method', 'endpoint', 'http_status']
# )
# REQUEST_LATENCY = Histogram(
#     'request_latency_seconds', 'Request latency',
#     ['method', 'endpoint']
# )

# @app.middleware("http")
# async def monitor_requests(request, call_next):
#     start_time = time.time()
#     method = request.method
#     endpoint = request.url.path

#     try:
#         response = await call_next(request)
#     except Exception:
#         REQUEST_COUNT.labels(method, endpoint, 500).inc()
#         raise

#     latency = time.time() - start_time
#     REQUEST_LATENCY.labels(method, endpoint).observe(latency)
#     REQUEST_COUNT.labels(method, endpoint, response.status_code).inc()

#     return response

# CORS configuration
origins = []

# Add configured frontend URL if set
if settings.FRONTEND_URL:
    origins.append(settings.FRONTEND_URL)
    # Allow HTTPS version if HTTP is provided
    if settings.FRONTEND_URL.startswith("http://"):
        origins.append(settings.FRONTEND_URL.replace("http://", "https://"))

# Add common Docker development URLs
origins.extend(
    [
        "http://localhost",
        "http://localhost:80",
        "http://localhost:9000",
        "http://frontend:9000",
        "http://nginx",
        "http://nginx:80",
        "http://backend:8000",
        "http://192.168.146.1:9000",
        "http://localhost:9000",
    ]
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

app.include_router(auth_router)
app.include_router(achievement_router)
app.include_router(profile_router)
app.include_router(task_router)
app.include_router(rating_router)
app.include_router(analytics_router)
app.include_router(activity_router)


async def run_server(app, port):
    config = uvicorn.Config(
        app, host="0.0.0.0", port=port, proxy_headers=True, forwarded_allow_ips="*"
    )
    server = uvicorn.Server(config)
    await server.serve()


async def main():
    await asyncio.gather(run_server("admin:app", 8001), run_server("main:app", 8000))


if __name__ == "__main__":
    asyncio.run(main())
