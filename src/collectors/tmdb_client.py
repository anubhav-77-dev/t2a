"""TMDb (The Movie Database) API client."""

import requests
from typing import Dict, List, Optional, Any
from datetime import datetime
import time

from ..utils.config import Config


class TMDbClient:
    """Client for interacting with The Movie Database API."""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or Config.TMDB_API_KEY
        self.base_url = Config.TMDB_BASE_URL
        self.image_base = Config.TMDB_IMAGE_BASE
        
        if not (self.api_key or Config.TMDB_BEARER_TOKEN):
            raise ValueError("TMDb API auth required. Set TMDB_API_KEY or TMDB_BEARER_TOKEN in .env file.")
    
    def _make_request(self, endpoint: str, params: Optional[Dict] = None, max_retries: int = 3) -> Dict[str, Any]:
        """Make a request to the TMDb API with retry logic."""
        params = params or {}
        # Use v3 api_key when available; with v4 bearer we can also call v3 using Authorization header
        if self.api_key:
            params['api_key'] = self.api_key
        
        headers = {}
        if Config.TMDB_BEARER_TOKEN:
            headers['Authorization'] = f"Bearer {Config.TMDB_BEARER_TOKEN}"
        
        url = f"{self.base_url}/{endpoint}"
        
        for attempt in range(max_retries):
            try:
                response = requests.get(url, params=params, headers=headers, timeout=15)
                response.raise_for_status()
                return response.json()
            except requests.exceptions.ConnectionError as e:
                if attempt < max_retries - 1:
                    wait_time = 2 ** attempt  # Exponential backoff: 1s, 2s, 4s
                    print(f"⚠️  Connection error (attempt {attempt + 1}/{max_retries}), retrying in {wait_time}s...")
                    time.sleep(wait_time)
                else:
                    print(f"❌ TMDb API connection failed after {max_retries} attempts: {e}")
                    print(f"💡 Tip: Check your internet connection or try again later")
                    return {}
            except requests.exceptions.RequestException as e:
                print(f"❌ TMDb API error: {e}")
                return {}
        
        return {}
    
    def search_movie(self, title: str, year: Optional[int] = None) -> List[Dict[str, Any]]:
        """Search for movies by title."""
        params = {'query': title}
        if year:
            params['year'] = year
        
        data = self._make_request('search/movie', params)
        return data.get('results', [])
    
    def get_movie_details(self, movie_id: int) -> Dict[str, Any]:
        """Get detailed information about a movie."""
        endpoint = f'movie/{movie_id}'
        params = {'append_to_response': 'videos,credits,keywords,release_dates,images'}
        return self._make_request(endpoint, params)
    
    def get_movie_videos(self, movie_id: int) -> List[Dict[str, Any]]:
        """Get videos (trailers, teasers) for a movie."""
        data = self._make_request(f'movie/{movie_id}/videos')
        return data.get('results', [])
    
    def get_movie_credits(self, movie_id: int) -> Dict[str, Any]:
        """Get cast and crew information."""
        return self._make_request(f'movie/{movie_id}/credits')
    
    def get_movie_keywords(self, movie_id: int) -> List[Dict[str, Any]]:
        """Get keywords associated with the movie."""
        data = self._make_request(f'movie/{movie_id}/keywords')
        return data.get('keywords', [])
    
    def extract_marketing_metadata(self, movie_id: int) -> Dict[str, Any]:
        """
        Extract marketing-relevant metadata from a movie.
        
        Returns a structured dict with:
        - Basic info (title, tagline, overview, genres)
        - Cast & crew highlights
        - Keywords for targeting
        - Visual assets (posters, backdrops)
        - Release information
        """
        details = self.get_movie_details(movie_id)
        
        if not details:
            return {}
        
        # Extract top cast (limit to top 5 for marketing)
        cast = details.get('credits', {}).get('cast', [])[:5]
        cast_names = [person['name'] for person in cast]
        
        # Extract director
        crew = details.get('credits', {}).get('crew', [])
        directors = [person['name'] for person in crew if person.get('job') == 'Director']
        
        # Extract genres
        genres = [g['name'] for g in details.get('genres', [])]
        
        # Extract keywords
        keywords = [kw['name'] for kw in details.get('keywords', {}).get('keywords', [])]
        
        # Get poster and backdrop URLs
        poster_path = details.get('poster_path')
        backdrop_path = details.get('backdrop_path')
        
        poster_url = f"{self.image_base}{poster_path}" if poster_path else None
        backdrop_url = f"{self.image_base}{backdrop_path}" if backdrop_path else None
        
        # Extract release date and status
        release_date = details.get('release_date', '')
        status = details.get('status', '')
        
        # Get trailers
        videos = details.get('videos', {}).get('results', [])
        trailers = [
            {
                'name': v['name'],
                'key': v['key'],
                'site': v['site'],
                'type': v['type'],
                'url': f"https://www.youtube.com/watch?v={v['key']}" if v['site'] == 'YouTube' else None
            }
            for v in videos if v['type'] in ['Trailer', 'Teaser']
        ]
        
        return {
            'movie_id': movie_id,
            'title': details.get('title', ''),
            'original_title': details.get('original_title', ''),
            'tagline': details.get('tagline', ''),
            'overview': details.get('overview', ''),
            'genres': genres,
            'cast': cast_names,
            'directors': directors,
            'keywords': keywords,
            'poster_url': poster_url,
            'backdrop_url': backdrop_url,
            'release_date': release_date,
            'status': status,
            'runtime': details.get('runtime'),
            'budget': details.get('budget'),
            'revenue': details.get('revenue'),
            'vote_average': details.get('vote_average'),
            'vote_count': details.get('vote_count'),
            'popularity': details.get('popularity'),
            'trailers': trailers,
            'homepage': details.get('homepage'),
            'imdb_id': details.get('imdb_id'),
        }
    
    def get_similar_movies(self, movie_id: int, limit: int = 5) -> List[Dict[str, Any]]:
        """Get similar movies for competitive analysis."""
        data = self._make_request(f'movie/{movie_id}/similar')
        results = data.get('results', [])[:limit]
        return [
            {
                'id': m['id'],
                'title': m['title'],
                'popularity': m.get('popularity'),
                'vote_average': m.get('vote_average')
            }
            for m in results
        ]


# Example usage
if __name__ == "__main__":
    client = TMDbClient()
    
    # Search for a movie
    results = client.search_movie("Dune Part Two", year=2024)
    if results:
        movie_id = results[0]['id']
        print(f"Found: {results[0]['title']} (ID: {movie_id})")
        
        # Get marketing metadata
        metadata = client.extract_marketing_metadata(movie_id)
        print(f"\n📊 Marketing Metadata:")
        print(f"Title: {metadata['title']}")
        print(f"Tagline: {metadata['tagline']}")
        print(f"Genres: {', '.join(metadata['genres'])}")
        print(f"Cast: {', '.join(metadata['cast'][:3])}")
        print(f"Keywords: {', '.join(metadata['keywords'][:5])}")
