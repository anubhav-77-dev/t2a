"""AI-enhanced content generation using Google Gemini."""

from typing import Dict, List, Any, Optional
import json

try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    print("⚠️  google-generativeai not installed. Install with: pip install google-generativeai")

from ..utils.config import Config


class GeminiEnhancer:
    """Enhance marketing content using Google Gemini AI."""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or Config.GEMINI_API_KEY
        self.model = None
        
        if not GEMINI_AVAILABLE:
            print("⚠️  Gemini not available. Install: pip install google-generativeai")
            return
        
        if not self.api_key:
            print("⚠️  Gemini API key not configured. Set GEMINI_API_KEY in .env")
            return
        
        try:
            genai.configure(api_key=self.api_key)
            # Use latest Gemini Flash model (free tier, fast, good quality)
            self.model = genai.GenerativeModel('gemini-2.5-flash')
            print("✅ Gemini AI initialized successfully")
        except Exception as e:
            print(f"❌ Error initializing Gemini: {e}")
    
    def is_available(self) -> bool:
        """Check if Gemini is available and configured."""
        return self.model is not None
    
    def enhance_ad_copy(
        self,
        movie_data: Dict[str, Any],
        sentiment_data: Dict[str, Any],
        existing_variants: List[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Generate enhanced ad copy using Gemini AI.
        
        Args:
            movie_data: Movie metadata
            sentiment_data: Sentiment analysis results
            existing_variants: Existing variants to improve upon
        """
        if not self.is_available():
            return []
        
        prompt = self._build_ad_copy_prompt(movie_data, sentiment_data, existing_variants)
        
        try:
            response = self.model.generate_content(prompt)
            variants = self._parse_ad_copy_response(response.text)
            return variants
        except Exception as e:
            print(f"❌ Gemini error: {e}")
            return []
    
    def _build_ad_copy_prompt(
        self,
        movie_data: Dict[str, Any],
        sentiment_data: Dict[str, Any],
        existing_variants: List[str] = None
    ) -> str:
        """Build prompt for ad copy generation."""
        title = movie_data.get('title', 'Unknown')
        tagline = movie_data.get('tagline', '')
        overview = movie_data.get('overview', '')
        
        # Handle genres - can be list of strings or list of dicts
        genres_raw = movie_data.get('genres', [])
        if genres_raw and isinstance(genres_raw[0], dict):
            genres = ', '.join([g.get('name', '') for g in genres_raw])
        else:
            genres = ', '.join(genres_raw) if genres_raw else 'Unknown'
        
        # Handle cast - can be list of strings or list of dicts
        cast_raw = movie_data.get('cast', [])[:3]
        if cast_raw and isinstance(cast_raw[0], dict):
            cast = ', '.join([c.get('name', '') for c in cast_raw])
        else:
            cast = ', '.join(cast_raw) if cast_raw else 'Unknown'
        
        sentiment = sentiment_data.get('overall_sentiment', 'neutral')
        
        prompt = f"""You are an expert movie marketing copywriter. Generate 5 compelling ad copy variants for this film:

**Movie Details:**
- Title: {title}
- Tagline: {tagline}
- Genres: {genres}
- Starring: {cast}
- Overview: {overview}

**Audience Sentiment:** {sentiment.upper()} ({sentiment_data.get('sentiment_distribution', {}).get('positive', 0):.0f}% positive)

**Requirements:**
1. Create 5 variants: 2 short (under 100 chars), 2 medium (100-200 chars), 1 long (200-280 chars)
2. Match the {sentiment} audience sentiment
3. Include compelling hooks and clear CTAs
4. Use proven marketing psychology
5. Make each variant unique and platform-appropriate

**Format your response as JSON:**
```json
[
  {{"variant": "short_1", "text": "Your ad copy here", "platform": "Twitter/Display Ads"}},
  {{"variant": "short_2", "text": "Your ad copy here", "platform": "Twitter/Display Ads"}},
  {{"variant": "medium_1", "text": "Your ad copy here", "platform": "Facebook/Instagram"}},
  {{"variant": "medium_2", "text": "Your ad copy here", "platform": "YouTube/Video"}},
  {{"variant": "long_1", "text": "Your ad copy here", "platform": "Blog/Email"}}
]
```

Generate creative, compelling copy that will drive ticket sales:"""
        
        return prompt
    
    def _parse_ad_copy_response(self, response_text: str) -> List[Dict[str, Any]]:
        """Parse Gemini's JSON response."""
        try:
            # Extract JSON from markdown code blocks if present
            if '```json' in response_text:
                json_str = response_text.split('```json')[1].split('```')[0].strip()
            elif '```' in response_text:
                json_str = response_text.split('```')[1].split('```')[0].strip()
            else:
                json_str = response_text.strip()
            
            variants = json.loads(json_str)
            
            # Standardize format and add metadata
            result = []
            for variant in variants:
                text = variant.get('text', '')
                char_count = len(text)
                
                # Determine length category
                if char_count < 100:
                    length = 'short'
                elif char_count < 200:
                    length = 'medium'
                else:
                    length = 'long'
                
                result.append({
                    'text': text,
                    'length': length,
                    'character_count': char_count,
                    'platform': variant.get('platform', 'general'),
                    'ai_generated': True
                })
            
            return result
        except Exception as e:
            print(f"⚠️  Error parsing Gemini response: {e}")
            print(f"   Response was: {response_text[:200]}...")
            return []
    
    def enhance_social_post(
        self,
        movie_data: Dict[str, Any],
        platform: str,
        sentiment_data: Dict[str, Any]
    ) -> Optional[str]:
        """Generate platform-optimized social media post."""
        if not self.is_available():
            return None
        
        title = movie_data.get('title', 'Unknown')
        tagline = movie_data.get('tagline', '')
        
        # Handle genres - can be list of strings or list of dicts
        genres_raw = movie_data.get('genres', [])
        if genres_raw and isinstance(genres_raw[0], dict):
            genres = ', '.join([g.get('name', '') for g in genres_raw])
        else:
            genres = ', '.join(genres_raw) if genres_raw else 'Unknown'
        
        platform_specs = {
            'twitter': {'limit': 280, 'style': 'concise, punchy, trending'},
            'instagram': {'limit': 2200, 'style': 'visual storytelling, emoji-rich'},
            'facebook': {'limit': 500, 'style': 'engaging, conversational'},
            'tiktok': {'limit': 2200, 'style': 'casual, meme-aware, Gen-Z'}
        }
        
        spec = platform_specs.get(platform.lower(), platform_specs['twitter'])
        
        prompt = f"""Create a {platform.upper()} post for this movie:

**Movie:** {title}
**Tagline:** {tagline}
**Genres:** {genres}

**Platform Guidelines:**
- Character limit: {spec['limit']}
- Style: {spec['style']}
- Include relevant hashtags
- Add engaging hook

Generate an attention-grabbing post that will drive engagement:"""
        
        try:
            response = self.model.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            print(f"❌ Gemini error: {e}")
            return None
    
    def generate_campaign_insights(
        self,
        campaign_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate strategic insights from campaign data."""
        if not self.is_available():
            return {}
        
        sentiment = campaign_data.get('sentiment_analysis', {})
        regional = campaign_data.get('regional_analysis', {})
        trailer = campaign_data.get('trailer_analysis', {})
        
        prompt = f"""Analyze this movie marketing campaign data and provide strategic insights:

**Trailer Performance:**
- Views: {trailer.get('stats', {}).get('view_count', 0):,}
- Engagement Rate: {trailer.get('engagement_rate', 0):.2f}%
- Days Since Published: {trailer.get('days_since_published', 0)}

**Audience Sentiment:**
- Overall: {sentiment.get('overall_sentiment', 'unknown').upper()}
- Positive: {sentiment.get('sentiment_distribution', {}).get('positive', 0):.1f}%
- Negative: {sentiment.get('sentiment_distribution', {}).get('negative', 0):.1f}%

**Top Markets:**
{self._format_regional_data(regional.get('ranked_regions', [])[:5])}

**Generate:**
1. **Key Opportunities** (3-5 bullet points)
2. **Risk Factors** (2-3 bullet points)
3. **Strategic Recommendations** (3-5 actionable items)
4. **Budget Allocation Advice** (specific percentages and reasoning)

Format as JSON:
```json
{{
  "opportunities": ["...", "...", "..."],
  "risks": ["...", "..."],
  "recommendations": ["...", "...", "..."],
  "budget_advice": "..."
}}
```"""
        
        try:
            response = self.model.generate_content(prompt)
            return self._parse_insights_response(response.text)
        except Exception as e:
            print(f"❌ Gemini error: {e}")
            return {}
    
    def _format_regional_data(self, regions: List[Dict[str, Any]]) -> str:
        """Format regional data for prompt."""
        lines = []
        for i, region in enumerate(regions, 1):
            lines.append(f"{i}. {region.get('region')} - Score: {region.get('total_score', 0)}/100 (Tier {region.get('tier', 'N/A')})")
        return '\n'.join(lines)
    
    def _parse_insights_response(self, response_text: str) -> Dict[str, Any]:
        """Parse insights JSON response."""
        try:
            # Extract JSON
            if '```json' in response_text:
                json_str = response_text.split('```json')[1].split('```')[0].strip()
            elif '```' in response_text:
                json_str = response_text.split('```')[1].split('```')[0].strip()
            else:
                json_str = response_text.strip()
            
            return json.loads(json_str)
        except Exception as e:
            print(f"⚠️  Error parsing insights: {e}")
            return {}


# Example usage
if __name__ == "__main__":
    enhancer = GeminiEnhancer()
    
    if enhancer.is_available():
        movie_data = {
            'title': 'Dune: Part Two',
            'tagline': 'Long live the fighters',
            'overview': 'Paul Atreides unites with Chani and the Fremen...',
            'genres': ['Science Fiction', 'Adventure'],
            'cast': ['Timothée Chalamet', 'Zendaya', 'Rebecca Ferguson']
        }
        
        sentiment_data = {
            'overall_sentiment': 'positive',
            'sentiment_distribution': {'positive': 82.5, 'neutral': 12.8, 'negative': 4.7}
        }
        
        print("🤖 Generating AI-enhanced ad copy...")
        variants = enhancer.enhance_ad_copy(movie_data, sentiment_data)
        
        for variant in variants:
            print(f"\n[{variant.get('variant', 'unknown').upper()}]")
            print(f"{variant.get('text', '')}")
    else:
        print("Gemini not available. Set GEMINI_API_KEY in .env file.")
