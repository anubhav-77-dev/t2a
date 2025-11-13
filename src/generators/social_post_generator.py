"""Social media post generator for different platforms."""

from typing import Dict, List, Any, Optional
import random
from datetime import datetime

from ..utils.source_tracker import SourceTracker


class SocialPostGenerator:
    """Generate platform-optimized social media posts."""
    
    # Platform character limits
    LIMITS = {
        'twitter': 280,
        'instagram': 2200,
        'facebook': 63206,  # Practical limit ~500
        'linkedin': 3000,
        'tiktok': 2200
    }
    
    # Hashtag strategies
    GENRE_HASHTAGS = {
        'Science Fiction': ['#SciFi', '#SciFiMovie', '#Space'],
        'Action': ['#ActionMovie', '#Blockbuster', '#Action'],
        'Drama': ['#Drama', '#DramaFilm'],
        'Comedy': ['#Comedy', '#Funny', '#ComingSoon'],
        'Horror': ['#Horror', '#HorrorMovie', '#Scary'],
        'Thriller': ['#Thriller', '#Suspense'],
        'Adventure': ['#Adventure', '#Epic']
    }
    
    def __init__(self, source_tracker: Optional[SourceTracker] = None):
        self.tracker = source_tracker or SourceTracker()
    
    def generate_twitter_post(
        self,
        movie_data: Dict[str, Any],
        sentiment_data: Dict[str, Any],
        include_hashtags: bool = True
    ) -> Dict[str, Any]:
        """Generate Twitter/X optimized post."""
        title = movie_data.get('title', '')
        tagline = movie_data.get('tagline', '')
        release_date = movie_data.get('release_date', '')
        
        # Short, punchy format
        if tagline:
            text = f"{tagline} 🎬 {title}"
        else:
            hook = self._get_hook(sentiment_data)
            text = f"{hook} {title}"
        
        # Add release info
        if release_date:
            try:
                date_obj = datetime.strptime(release_date, '%Y-%m-%d')
                text += f" - {date_obj.strftime('%B %d')}"
            except:
                pass
        
        # Hashtags
        if include_hashtags:
            hashtags = self._generate_hashtags(movie_data, max_count=2)
            hashtag_str = ' '.join(hashtags)
            
            # Ensure under limit
            if len(text) + len(hashtag_str) + 1 < self.LIMITS['twitter']:
                text += f" {hashtag_str}"
        
        return {
            'platform': 'Twitter/X',
            'text': text,
            'character_count': len(text),
            'optimal_time': 'Weekdays 12-3 PM, 5-6 PM',
            'post_type': 'announcement'
        }
    
    def generate_instagram_post(
        self,
        movie_data: Dict[str, Any],
        sentiment_data: Dict[str, Any],
        use_emojis: bool = True
    ) -> Dict[str, Any]:
        """Generate Instagram optimized post."""
        title = movie_data.get('title', '')
        overview = movie_data.get('overview', '')
        cast = movie_data.get('cast', [])
        
        # Instagram prefers story-driven content
        text = f"✨ {title} ✨\n\n" if use_emojis else f"{title}\n\n"
        
        # Add overview snippet
        if overview:
            snippet = overview.split('.')[0] + '.'
            text += f"{snippet}\n\n"
        
        # Cast
        if cast:
            text += f"Starring {', '.join(cast[:3])} 🌟\n\n" if use_emojis else f"Starring {', '.join(cast[:3])}\n\n"
        
        # Call to action
        text += "Tag someone who needs to see this! 👇"
        
        # Hashtags (Instagram allows many)
        hashtags = self._generate_hashtags(movie_data, max_count=10)
        text += "\n\n" + ' '.join(hashtags)
        
        return {
            'platform': 'Instagram',
            'text': text,
            'character_count': len(text),
            'optimal_time': 'Weekdays 11 AM, Wed 2 PM, Fri 9 AM',
            'post_type': 'carousel',
            'image_suggestion': 'Use poster + behind-scenes + cast photos'
        }
    
    def generate_facebook_post(
        self,
        movie_data: Dict[str, Any],
        sentiment_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate Facebook optimized post."""
        title = movie_data.get('title', '')
        overview = movie_data.get('overview', '')
        tagline = movie_data.get('tagline', '')
        cast = movie_data.get('cast', [])
        directors = movie_data.get('directors', [])
        
        # Facebook allows longer, more detailed posts
        text = ""
        
        # Hook with emotion
        hook = self._get_hook(sentiment_data)
        text += f"{hook}\n\n"
        
        # Title and tagline
        if tagline:
            text += f"🎬 {title}: {tagline}\n\n"
        else:
            text += f"🎬 {title}\n\n"
        
        # Full overview
        if overview:
            text += f"{overview}\n\n"
        
        # Credits
        if directors:
            text += f"Directed by {directors[0]}\n"
        if cast:
            text += f"Starring {', '.join(cast[:4])}\n\n"
        
        # CTA
        text += "Click below to watch the trailer and get tickets! 🎟️"
        
        return {
            'platform': 'Facebook',
            'text': text,
            'character_count': len(text),
            'optimal_time': 'Wed-Fri 1-4 PM',
            'post_type': 'link',
            'link_suggestion': 'Trailer video or ticket purchase page'
        }
    
    def generate_tiktok_caption(
        self,
        movie_data: Dict[str, Any],
        trending_sounds: List[str] = None
    ) -> Dict[str, Any]:
        """Generate TikTok optimized caption."""
        title = movie_data.get('title', '')
        
        # TikTok is very short, hook-focused
        text = f"POV: You just watched the {title} trailer 🤯\n\n"
        text += "What's your reaction? Comment below! ⬇️"
        
        # Hashtags (trending is key)
        hashtags = self._generate_hashtags(movie_data, max_count=5)
        hashtags.extend(['#MovieTok', '#FYP', '#ForYouPage'])
        text += "\n\n" + ' '.join(hashtags[:8])
        
        return {
            'platform': 'TikTok',
            'text': text,
            'character_count': len(text),
            'optimal_time': 'Tue-Thu 7-9 AM, 7-11 PM',
            'video_suggestion': 'Reaction format, trailer clips, cast interviews',
            'trending_sounds': trending_sounds or ['Use trending audio']
        }
    
    def _get_hook(self, sentiment_data: Dict[str, Any]) -> str:
        """Generate engaging hook based on sentiment."""
        overall = sentiment_data.get('overall_sentiment', 'neutral')
        
        if overall == 'positive':
            hooks = [
                "🔥 The hype is real!",
                "✨ Everyone's talking about this.",
                "🎯 This is THE event of the year.",
                "💥 Get ready for something incredible."
            ]
        else:
            hooks = [
                "🎬 Coming soon.",
                "📽️ Mark your calendars.",
                "🍿 Get ready.",
                "🎥 You've been waiting for this."
            ]
        
        return random.choice(hooks)
    
    def _generate_hashtags(
        self,
        movie_data: Dict[str, Any],
        max_count: int = 5
    ) -> List[str]:
        """Generate relevant hashtags."""
        hashtags = []
        
        # Title hashtag
        title = movie_data.get('title', '')
        if title:
            clean_title = title.replace(' ', '').replace(':', '')
            hashtags.append(f"#{clean_title}")
        
        # Genre hashtags
        genres = movie_data.get('genres', [])
        for genre in genres[:2]:
            genre_tags = self.GENRE_HASHTAGS.get(genre, [])
            hashtags.extend(genre_tags[:2])
        
        # Generic movie hashtags
        hashtags.extend(['#Movies', '#Cinema', '#ComingSoon', '#MustWatch'])
        
        # Remove duplicates and limit
        seen = set()
        unique_hashtags = []
        for tag in hashtags:
            if tag not in seen:
                seen.add(tag)
                unique_hashtags.append(tag)
        
        return unique_hashtags[:max_count]
    
    def generate_all_platforms(
        self,
        movie_data: Dict[str, Any],
        sentiment_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate posts for all major platforms."""
        return {
            'twitter': self.generate_twitter_post(movie_data, sentiment_data),
            'instagram': self.generate_instagram_post(movie_data, sentiment_data),
            'facebook': self.generate_facebook_post(movie_data, sentiment_data),
            'tiktok': self.generate_tiktok_caption(movie_data),
            'generated_at': datetime.now().isoformat()
        }


# Example usage
if __name__ == "__main__":
    generator = SocialPostGenerator()
    
    movie_data = {
        'title': 'Dune: Part Two',
        'tagline': 'Long live the fighters',
        'overview': 'Follow Paul Atreides as he unites with Chani and the Fremen.',
        'cast': ['Timothée Chalamet', 'Zendaya', 'Rebecca Ferguson'],
        'directors': ['Denis Villeneuve'],
        'genres': ['Science Fiction', 'Adventure'],
        'release_date': '2024-03-01'
    }
    
    sentiment_data = {
        'overall_sentiment': 'positive'
    }
    
    posts = generator.generate_all_platforms(movie_data, sentiment_data)
    
    for platform, post in posts.items():
        if isinstance(post, dict):
            print(f"\n📱 {post.get('platform', platform).upper()}")
            print(f"{post.get('text', '')}")
            print(f"({post.get('character_count', 0)} chars)")
