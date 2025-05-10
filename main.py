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

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_URL],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True
)

app.include_router(auth_router)
app.include_router(achievement_router)
app.include_router(profile_router)
app.include_router(task_router)
app.include_router(rating_router)


async def run_server(app, port):
    config = uvicorn.Config(app, host="0.0.0.0", port=port)
    server = uvicorn.Server(config)
    await server.serve()


async def main():
    await asyncio.gather(
        run_server("admin:app", 8001),
        run_server("main:app", 8000)
    )


if __name__ == '__main__':
    asyncio.run(main())
