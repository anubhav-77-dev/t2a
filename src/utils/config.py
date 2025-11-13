"""Configuration management for the Trailer-to-Campaign Autopilot."""

import os
from pathlib import Path
from dotenv import load_dotenv
from typing import List

# Project paths
PROJECT_ROOT = Path(__file__).parent.parent.parent

# Load environment variables from project root
load_dotenv(PROJECT_ROOT / '.env')

CACHE_DIR = PROJECT_ROOT / "cache"
OUTPUT_DIR = PROJECT_ROOT / "outputs"

# Create directories if they don't exist
CACHE_DIR.mkdir(exist_ok=True)
OUTPUT_DIR.mkdir(exist_ok=True)


class Config:
    """Application configuration."""
    
    # API Keys
    TMDB_API_KEY: str = os.getenv("TMDB_API_KEY", "")
    # TMDb v4 Read Access Token (Bearer)
    TMDB_BEARER_TOKEN: str = os.getenv("TMDB_BEARER_TOKEN", "")
    YOUTUBE_API_KEY: str = os.getenv("YOUTUBE_API_KEY", "")
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    
    # API Endpoints
    TMDB_BASE_URL: str = "https://api.themoviedb.org/3"
    TMDB_IMAGE_BASE: str = "https://image.tmdb.org/t/p/original"
    WIKIPEDIA_PAGEVIEWS_URL: str = "https://wikimedia.org/api/rest_v1/metrics/pageviews"
    OPEN_METEO_URL: str = "https://api.open-meteo.com/v1/forecast"
    
    # Default settings
    DEFAULT_REGIONS: List[str] = os.getenv("DEFAULT_REGIONS", "US,UK,CA,AU,IN").split(",")
    MAX_COMMENTS_ANALYZE: int = int(os.getenv("MAX_COMMENTS_ANALYZE", "500"))
    SENTIMENT_THRESHOLD: float = float(os.getenv("SENTIMENT_THRESHOLD", "0.6"))
    
    # Cache settings
    CACHE_EXPIRY_HOURS: int = 24
    ENABLE_CACHE: bool = True
    
    # Content generation
    AD_COPY_VARIANTS: int = 5
    SOCIAL_POST_VARIANTS: int = 3
    EMAIL_SUBJECT_VARIANTS: int = 4
    
    @classmethod
    def validate(cls) -> bool:
        """Validate that required API keys are present."""
        missing = []
        if not (cls.TMDB_API_KEY or cls.TMDB_BEARER_TOKEN):
            missing.append("TMDB_API_KEY or TMDB_BEARER_TOKEN")
        if not cls.YOUTUBE_API_KEY:
            missing.append("YOUTUBE_API_KEY")
        
        if missing:
            print(f"⚠️  Warning: Missing required API keys: {', '.join(missing)}")
            print("Please set them in your .env file. See .env.example for reference.")
            return False
        return True
    
    @classmethod
    def has_gemini(cls) -> bool:
        """Check if Gemini API key is configured."""
        return bool(cls.GEMINI_API_KEY)
    
    @classmethod
    def has_openai(cls) -> bool:
        """Check if OpenAI API key is configured."""
        return bool(cls.OPENAI_API_KEY)
    
    @classmethod
    def has_ai_api(cls) -> bool:
        """Check if any AI API is configured."""
        return cls.has_gemini() or cls.has_openai()


# Validate configuration on import
Config.validate()
