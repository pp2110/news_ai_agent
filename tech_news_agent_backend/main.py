from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import router
import uvicorn
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(
    title="News Agent API",
    description="AI-powered news summarization service"
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix="/api/v1")

if __name__ == "__main__":
    uvicorn.run(
        "main:app", 
        host="0.0.0.0", 
        port=8000, 
        reload=True
    )