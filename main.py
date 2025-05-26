#!/usr/bin/env python3
import asyncio
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from src.api.auth import router as auth_router
from src.api.achievement import router as achievement_router
from src.api.profile import router as profile_router
from src.api.task import router as task_router
from src.api.rating import router as rating_router
from config import settings

app = FastAPI()

# CORS configuration
origins = []

# Add configured frontend URL if set
if settings.FRONTEND_URL:
    origins.append(settings.FRONTEND_URL)
    # Allow HTTPS version if HTTP is provided
    if settings.FRONTEND_URL.startswith("http://"):
        origins.append(settings.FRONTEND_URL.replace("http://", "https://"))

# Add common Docker development URLs
origins.extend([
    "http://localhost",
    "http://localhost:80",
    "http://localhost:9000",
    "http://frontend:9000",
    "http://nginx",
    "http://nginx:80",
    "http://backend:8000"
])

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"]
)

app.include_router(auth_router)
app.include_router(achievement_router)
app.include_router(profile_router)
app.include_router(task_router)
app.include_router(rating_router)


async def run_server(app, port):
    config = uvicorn.Config(
        app,
        host="0.0.0.0",
        port=port,
        proxy_headers=True,
        forwarded_allow_ips="*"
        )
    server = uvicorn.Server(config)
    await server.serve()


async def main():
    await asyncio.gather(
        run_server("admin:app", 8001),
        run_server("main:app", 8000)
    )


if __name__ == '__main__':
    asyncio.run(main())
