"""Ad copy generator with source tracing."""

from typing import Dict, List, Any, Optional
import random

from ..utils.source_tracker import SourceTracker, SourceType


class AdCopyGenerator:
    """Generate advertising copy grounded in data sources."""
    
    # Copy templates by length
    SHORT_TEMPLATES = [
        "{hook} {title} - {cta}",
        "{emotion} {title}. {cta}",
        "{title}: {tagline} {cta}",
        "{quote} - {title}",
    ]
    
    MEDIUM_TEMPLATES = [
        "{hook} {title} {description} {cast_mention} {cta}",
        "{emotion} {overview} {title} - {date_mention} {cta}",
        "{tagline} Experience {title}, {genre_mention} {cast_mention} {cta}",
    ]
    
    LONG_TEMPLATES = [
        "{hook} {overview} Starring {cast}, {title} {genre_mention} {date_mention} {social_proof} {cta}",
        "{emotion} {description} From {director}, {title} brings {tagline} {cast_mention} {date_mention} {cta}",
    ]
    
    # Dynamic components
    HOOKS = [
        "Get ready.",
        "Mark your calendars.",
        "The wait is over.",
        "Coming soon.",
        "Don't miss",
        "Experience",
        "Witness",
    ]
    
    EMOTION_WORDS = [
        "Epic.", "Breathtaking.", "Unforgettable.", "Stunning.",
        "Mind-blowing.", "Spectacular.", "Legendary.", "Iconic."
    ]
    
    CTAS = [
        "Watch now",
        "In theaters now",
        "Get tickets",
        "Book your seats",
        "Don't miss it",
        "Experience it in theaters",
        "Coming soon",
        "Available now"
    ]
    
    def __init__(self, source_tracker: Optional[SourceTracker] = None):
        self.tracker = source_tracker or SourceTracker()
    
    def generate_variants(
        self,
        movie_data: Dict[str, Any],
        sentiment_data: Dict[str, Any],
        trending_phrases: List[str] = None,
        count: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Generate multiple ad copy variants.
        
        Returns list of variants with source citations.
        """
        variants = []
        
        # Extract key elements
        title = movie_data.get('title', 'This Film')
        tagline = movie_data.get('tagline', '')
        overview = movie_data.get('overview', '')
        cast = movie_data.get('cast', [])
        directors = movie_data.get('directors', [])
        genres = movie_data.get('genres', [])
        release_date = movie_data.get('release_date', '')
        
        # Add TMDb sources
        if tagline:
            self.tracker.add_tmdb_metadata('tagline', tagline, movie_data.get('movie_id', 0))
        if overview:
            self.tracker.add_tmdb_metadata('overview', overview[:100], movie_data.get('movie_id', 0))
        
        # Sentiment-based emotion selection
        overall_sentiment = sentiment_data.get('overall_sentiment', 'neutral')
        if overall_sentiment == 'positive':
            emotions = ["Breathtaking", "Epic", "Spectacular", "Incredible"]
        else:
            emotions = ["Witness", "Experience", "Discover", "See"]
        
        # Generate short variants
        for i in range(min(2, count)):
            short_copy = self._generate_short(
                title, tagline, release_date, emotions, trending_phrases
            )
            if short_copy:
                variants.append({
                    'variant': f'short_{i+1}',
                    'length': 'short',
                    'text': short_copy,
                    'character_count': len(short_copy),
                    'platform': 'Twitter/X, Display Ads',
                    'sources': [s.source_id for s in self.tracker.sources[-2:]],
                })
        
        # Generate medium variants
        for i in range(min(2, count - 2)):
            medium_copy = self._generate_medium(
                title, tagline, overview, cast, genres, release_date, emotions
            )
            if medium_copy:
                variants.append({
                    'variant': f'medium_{i+1}',
                    'length': 'medium',
                    'text': medium_copy,
                    'character_count': len(medium_copy),
                    'platform': 'Facebook, Instagram, YouTube',
                    'sources': [s.source_id for s in self.tracker.sources[-3:]],
                })
        
        # Generate long variant
        if count > 4:
            long_copy = self._generate_long(
                title, tagline, overview, cast, directors, genres,
                release_date, sentiment_data
            )
            if long_copy:
                variants.append({
                    'variant': 'long_1',
                    'length': 'long',
                    'text': long_copy,
                    'character_count': len(long_copy),
                    'platform': 'Video pre-roll, Blog posts',
                    'sources': [s.source_id for s in self.tracker.sources[-4:]],
                })
        
        return variants
    
    def _generate_short(
        self,
        title: str,
        tagline: str,
        release_date: str,
        emotions: List[str],
        trending_phrases: Optional[List[str]] = None
    ) -> str:
        """Generate short ad copy (< 100 chars)."""
        cta = self._get_cta(release_date)
        
        # Use trending phrase if available
        if trending_phrases and random.random() > 0.5:
            hook = trending_phrases[0]
        else:
            hook = random.choice(self.HOOKS)
        
        # Simple format
        if tagline and len(f"{title}: {tagline} {cta}") < 100:
            return f"{title}: {tagline} {cta}"
        else:
            return f"{hook} {title}. {cta}"
    
    def _generate_medium(
        self,
        title: str,
        tagline: str,
        overview: str,
        cast: List[str],
        genres: List[str],
        release_date: str,
        emotions: List[str]
    ) -> str:
        """Generate medium ad copy (100-200 chars)."""
        cta = self._get_cta(release_date)
        emotion = random.choice(emotions) if emotions else ""
        
        # Shorten overview
        description = overview.split('.')[0] if overview else ""
        if len(description) > 80:
            description = description[:77] + "..."
        
        # Cast mention
        cast_str = ""
        if cast:
            cast_str = f"Starring {', '.join(cast[:2])}"
        
        # Genre mention
        genre_str = ""
        if genres:
            genre_str = f"({genres[0]})"
        
        parts = [emotion, description, title, genre_str, cast_str, cta]
        copy = ' '.join(p for p in parts if p)
        
        # Trim if too long
        if len(copy) > 200:
            parts = [emotion, title, genre_str, cast_str, cta]
            copy = ' '.join(p for p in parts if p)
        
        return copy
    
    def _generate_long(
        self,
        title: str,
        tagline: str,
        overview: str,
        cast: List[str],
        directors: List[str],
        genres: List[str],
        release_date: str,
        sentiment_data: Dict[str, Any]
    ) -> str:
        """Generate long ad copy (200-300 chars)."""
        cta = self._get_cta(release_date)
        
        # Start with hook or emotion
        emotion = self._select_emotion_from_sentiment(sentiment_data)
        
        # Build narrative
        description = overview.split('.')[0] if overview else ""
        if len(description) > 100:
            description = description[:97] + "..."
        
        # Add credibility
        director_str = ""
        if directors:
            director_str = f"From director {directors[0]}"
        
        cast_str = ""
        if cast and len(cast) >= 2:
            cast_str = f"Starring {cast[0]} and {cast[1]}"
        elif cast:
            cast_str = f"Starring {cast[0]}"
        
        # Social proof
        social_proof = ""
        if sentiment_data.get('overall_sentiment') == 'positive':
            positive_pct = sentiment_data.get('sentiment_distribution', {}).get('positive', 0)
            if positive_pct > 70:
                social_proof = "Critics and fans are raving."
        
        # Assemble
        parts = [emotion, description, director_str, cast_str, title, social_proof, cta]
        copy = ' '.join(p for p in parts if p).strip()
        
        return copy
    
    def _get_cta(self, release_date: str) -> str:
        """Determine appropriate CTA based on release date."""
        if not release_date:
            return "Coming soon"
        
        # Parse date (simplified)
        try:
            from datetime import datetime
            release = datetime.strptime(release_date, '%Y-%m-%d')
            now = datetime.now()
            
            if release <= now:
                return random.choice([
                    "Watch now",
                    "In theaters now",
                    "Get tickets"
                ])
            elif (release - now).days <= 14:
                return "Book your seats today"
            else:
                return f"Coming {release.strftime('%B %d')}"
        except:
            return "Coming soon"
    
    def _select_emotion_from_sentiment(self, sentiment_data: Dict[str, Any]) -> str:
        """Select emotion word based on sentiment analysis."""
        overall = sentiment_data.get('overall_sentiment', 'neutral')
        
        if overall == 'positive':
            emotions = sentiment_data.get('emotion_totals', {})
            if emotions.get('anticipation', 0) > 10:
                return "The wait is over."
            else:
                return random.choice([
                    "Epic.", "Breathtaking.", "Spectacular.", "Unforgettable."
                ])
        else:
            return "Experience"
    
    def generate_with_sources(
        self,
        movie_data: Dict[str, Any],
        sentiment_data: Dict[str, Any],
        trending_phrases: List[str] = None,
        count: int = 5
    ) -> Dict[str, Any]:
        """Generate ad copy with full source tracing."""
        self.tracker.clear()
        
        variants = self.generate_variants(
            movie_data, sentiment_data, trending_phrases, count
        )
        
        return {
            'variants': variants,
            'total_variants': len(variants),
            'sources': self.tracker.to_citation_list(),
            'source_details': self.tracker.to_json()
        }


# Example usage
if __name__ == "__main__":
    generator = AdCopyGenerator()
    
    # Sample data
    movie_data = {
        'movie_id': 693134,
        'title': 'Dune: Part Two',
        'tagline': 'Long live the fighters',
        'overview': 'Follow the mythic journey of Paul Atreides as he unites with Chani and the Fremen...',
        'cast': ['Timothée Chalamet', 'Zendaya', 'Rebecca Ferguson'],
        'directors': ['Denis Villeneuve'],
        'genres': ['Science Fiction', 'Adventure'],
        'release_date': '2024-03-01'
    }
    
    sentiment_data = {
        'overall_sentiment': 'positive',
        'sentiment_distribution': {'positive': 82, 'neutral': 13, 'negative': 5},
        'emotion_totals': {'anticipation': 45, 'positive_signals': 120}
    }
    
    result = generator.generate_with_sources(movie_data, sentiment_data, count=5)
    
    print("📝 Generated Ad Copy Variants:\n")
    for variant in result['variants']:
        print(f"[{variant['variant'].upper()}] ({variant['character_count']} chars)")
        print(f"{variant['text']}")
        print(f"Platform: {variant['platform']}\n")
