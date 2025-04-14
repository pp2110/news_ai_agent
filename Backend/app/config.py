import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY")
    MODEL_NAME: str = "llama3-8b-8192"
    API_TITLE: str = "Newsroom API"
    API_DESCRIPTION: str = "API for processing and summarizing news articles"
    API_VERSION: str = "1.0.0"

settings = Settings()