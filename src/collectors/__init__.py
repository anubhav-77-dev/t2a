"""Collector package initialization."""

from .tmdb_client import TMDbClient
from .youtube_client import YouTubeClient
from .wikipedia_client import WikipediaClient
from .trends_client import TrendsClient
from .weather_client import WeatherClient, MAJOR_CITIES

__all__ = [
    'TMDbClient',
    'YouTubeClient',
    'WikipediaClient',
    'TrendsClient',
    'WeatherClient',
    'MAJOR_CITIES'
]
