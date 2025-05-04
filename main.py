from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import uvicorn
# from src.utils.auth import auth_config
from src.api.auth import router as auth_router
from src.api.progress import router as progress_router
from src.api.achievement import router as achievement_router
from src.api.profile import router as profile_router
from src.api.task import router as task_router
from src.api.rating import router as rating_router

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:9000"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(achievement_router)
app.include_router(profile_router)
app.include_router(task_router)
app.include_router(rating_router)


@app.get("/", summary="Main endpoint", tags=["Home endpoints"])
def main():
    return "Hello, stranger!"


if __name__ == '__main__':
    uvicorn.run("main:app", reload=True, port=8000) # host=0.0.0.0 for Docker
