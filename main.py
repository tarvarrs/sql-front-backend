from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
# from sqlalchemy import select
# from passlib.context import CryptContext
# from authx import AuthX
import uvicorn
# from src.utils.auth import auth_config
# from schemas.user import UserCreate, UserOut
# from models.user import Base, User, PasswordHash
# from database import engine, Base
from src.api.auth import router as auth_router
from src.api.progress import router as progress_router
# from src.api.achievement import router as achievement_router
from src.api.profile import router as profile_router


app = FastAPI()

# config = AuthXConfig()
# config.JWT_SECRET_KEY = "SECRET_KEY"
# config.JWT_ACCESS_COOKIE_NAME = "my_access_token"
# config.JWT_TOKEN_LOCATION = ["cookies"]

# security = AuthX(config=config)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:9000"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(progress_router)
# app.include_router(achievement_router)
app.include_router(profile_router)

@app.get("/", summary="Main endpoint", tags=["Home endpoints"])
def main():
    return "Hello"



if __name__ == '__main__':
    uvicorn.run("main:app", reload=True) # host=0.0.0.0 for Docker