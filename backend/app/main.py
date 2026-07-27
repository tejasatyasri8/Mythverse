from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routes import chat
from app.database.database import engine
from app.database.database import Base
from app.database import models


Base.metadata.create_all(bind=engine)
app = FastAPI(
    title="MythVerse API",
    description="Backend API for MythVerse AI Chatbot",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat.router, prefix="/chat", tags=["Chat"])

@app.get("/")
def home():
    return {
        "message": "Welcome to MythVerse!"
    }