"""Google Trends client using pytrends."""

from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import time
import random

try:
    from pytrends.request import TrendReq
except ImportError:
    print("⚠️  pytrends not installed. Google Trends features will be unavailable.")
    TrendReq = None


class TrendsClient:
    """Client for Google Trends data using pytrends."""
    
    def __init__(self, language: str = 'en-US', timezone: int = 360):
        """
        Initialize Trends client.
        
        Args:
            language: Language code (e.g., 'en-US', 'fr-FR')
            timezone: Timezone offset in minutes from UTC
        """
        if TrendReq is None:
            self.pytrends = None
            print("⚠️  TrendsClient not initialized. Install pytrends.")
            return
        
        self.pytrends = TrendReq(hl=language, tz=timezone)
        self.request_delay = 2.0  # Increased base delay between requests
        self.max_retries = 1  # Only 1 retry - fail fast on rate limits
    
    def _retry_with_backoff(self, func, *args, max_retries=None, **kwargs):
        """Execute function with exponential backoff on rate limit errors."""
        max_retries = max_retries or self.max_retries
        
        for attempt in range(max_retries):
            try:
                # Add progressive delay
                if attempt > 0:
                    delay = 5 + random.uniform(0, 2)  # Fixed 5-7s delay on retry
                    time.sleep(delay)
                else:
                    time.sleep(self.request_delay)
                
                return func(*args, **kwargs)
            
            except Exception as e:
                error_msg = str(e).lower()
                
                # Check if it's a rate limit error
                if '429' in error_msg or 'rate' in error_msg or 'quota' in error_msg or '400' in error_msg:
                    # Don't retry on rate limits - just skip
                    return None
                
                # For other errors, fail immediately
                return None
        
        return None
    
    def get_interest_over_time(
        self,
        keywords: List[str],
        timeframe: str = 'today 3-m',
        geo: str = ''
    ) -> Dict[str, Any]:
        """
        Get interest over time for keywords.
        
        Args:
            keywords: List of search terms (max 5)
            timeframe: Time range ('today 3-m', 'today 12-m', 'all', etc.)
            geo: Geographic region (e.g., 'US', 'GB', '')
        """
        if not self.pytrends:
            return {}
        
        def _fetch():
            self.pytrends.build_payload(keywords, timeframe=timeframe, geo=geo)
            return self.pytrends.interest_over_time()
        
        try:
            data = self._retry_with_backoff(_fetch)
            
            if data is None or data.empty:
                return {'keywords': keywords, 'data': []}
            
            # Convert to JSON-serializable format
            results = []
            for date, row in data.iterrows():
                entry = {'date': date.strftime('%Y-%m-%d')}
                for keyword in keywords:
                    if keyword in row:
                        entry[keyword] = int(row[keyword])
                results.append(entry)
            
            # Calculate summary statistics
            summary = {}
            for keyword in keywords:
                if keyword in data.columns:
                    values = data[keyword].tolist()
                    summary[keyword] = {
                        'avg': round(sum(values) / len(values), 2) if values else 0,
                        'max': int(max(values)) if values else 0,
                        'min': int(min(values)) if values else 0,
                        'latest': int(values[-1]) if values else 0
                    }
            
            return {
                'keywords': keywords,
                'timeframe': timeframe,
                'geo': geo or 'Worldwide',
                'data': results,
                'summary': summary
            }
        
        except Exception as e:
            print(f"❌ Trends API error: {e}")
            return {}
    
    def get_interest_by_region(
        self,
        keyword: str,
        resolution: str = 'COUNTRY'
    ) -> Dict[str, Any]:
        """
        Get interest by geographic region.
        
        Args:
            keyword: Search term
            resolution: 'COUNTRY', 'REGION' (state/province), or 'CITY'
        """
        if not self.pytrends:
            return {}
        
        def _fetch():
            self.pytrends.build_payload([keyword])
            return self.pytrends.interest_by_region(resolution=resolution)
        
        try:
            data = self._retry_with_backoff(_fetch)
            
            if data is None or data.empty:
                return {'keyword': keyword, 'regions': []}
            
            # Sort by interest and convert to list
            data = data.sort_values(by=keyword, ascending=False)
            regions = [
                {
                    'region': region,
                    'interest': int(score)
                }
                for region, score in zip(data.index, data[keyword])
                if score > 0
            ]
            
            return {
                'keyword': keyword,
                'resolution': resolution,
                'regions': regions,
                'top_region': regions[0] if regions else None
            }
        
        except Exception as e:
            print(f"❌ Trends API error: {e}")
            return {}
    
    def get_related_queries(self, keyword: str) -> Dict[str, Any]:
        """
        Get related and rising queries for a keyword.
        
        Returns top and rising related searches.
        """
        if not self.pytrends:
            return {}
        
        def _fetch():
            self.pytrends.build_payload([keyword])
            return self.pytrends.related_queries()
        
        try:
            related = self._retry_with_backoff(_fetch)
            
            if related is None or keyword not in related:
                return {'keyword': keyword, 'top': [], 'rising': []}
            
            keyword_data = related[keyword]
            
            # Extract top queries
            top_queries = []
            if keyword_data.get('top') is not None and not keyword_data['top'].empty:
                top_df = keyword_data['top']
                top_queries = [
                    {'query': row['query'], 'value': int(row['value'])}
                    for _, row in top_df.iterrows()
                ]
            
            # Extract rising queries
            rising_queries = []
            if keyword_data.get('rising') is not None and not keyword_data['rising'].empty:
                rising_df = keyword_data['rising']
                rising_queries = [
                    {'query': row['query'], 'value': row['value']}
                    for _, row in rising_df.iterrows()
                ]
            
            return {
                'keyword': keyword,
                'top': top_queries[:10],
                'rising': rising_queries[:10]
            }
        
        except Exception as e:
            print(f"❌ Trends API error: {e}")
            return {}
    
    def compare_keywords(
        self,
        keywords: List[str],
        timeframe: str = 'today 3-m',
        geo: str = ''
    ) -> Dict[str, Any]:
        """Compare multiple keywords to find the strongest."""
        data = self.get_interest_over_time(keywords, timeframe, geo)
        
        if not data.get('summary'):
            return {}
        
        summary = data['summary']
        
        # Rank by average interest
        ranked = sorted(
            summary.items(),
            key=lambda x: x[1]['avg'],
            reverse=True
        )
        
        return {
            'keywords': keywords,
            'timeframe': timeframe,
            'geo': geo or 'Worldwide',
            'ranking': [
                {
                    'keyword': kw,
                    'avg_interest': stats['avg'],
                    'max_interest': stats['max'],
                    'latest': stats['latest']
                }
                for kw, stats in ranked
            ],
            'winner': ranked[0][0] if ranked else None
        }
    
    def analyze_movie_interest(
        self,
        movie_title: str,
        cast_names: Optional[List[str]] = None,
        regions: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Comprehensive interest analysis for a movie.
        
        Args:
            movie_title: Movie name
            cast_names: Optional list of lead actors for comparison
            regions: Optional list of country codes to analyze
        """
        if not self.pytrends:
            return {}
        
        analysis = {
            'movie_title': movie_title,
            'global_trend': {},
            'regional_interest': {},
            'cast_comparison': {},
            'related_queries': {}
        }
        
        # Global trend over time
        analysis['global_trend'] = self.get_interest_over_time([movie_title])
        
        # Regional breakdown
        analysis['regional_interest'] = self.get_interest_by_region(movie_title)
        
        # Compare with cast if provided (skip to reduce API calls)
        if cast_names and False:  # Disabled to reduce rate limiting
            keywords = [movie_title] + cast_names[:2]  # Max 3 total to reduce load
            analysis['cast_comparison'] = self.compare_keywords(keywords)
        
        # Related queries (skip to reduce API calls)
        if False:  # Disabled to reduce rate limiting
            analysis['related_queries'] = self.get_related_queries(movie_title)
        
        # Multi-region analysis if specified (limit to 3 regions max)
        if regions:
            regional_details = {}
            # Only analyze top 3 regions to avoid rate limits
            for region in regions[:3]:
                trend = self.get_interest_over_time([movie_title], geo=region)
                if trend.get('summary'):
                    regional_details[region] = trend['summary'][movie_title]
                # Add delay between regional queries
                time.sleep(1.5)
            analysis['region_details'] = regional_details
        
        return analysis


# Example usage
if __name__ == "__main__":
    client = TrendsClient()
    
    if client.pytrends:
        # Analyze movie interest
        movie = "Dune Part Two"
        
        print(f"📈 Google Trends Analysis: {movie}")
        
        # Regional interest
        regional = client.get_interest_by_region(movie)
        print(f"\n🌍 Top Regions:")
        for region in regional['regions'][:5]:
            print(f"  {region['region']}: {region['interest']}/100")
        
        # Related queries
        related = client.get_related_queries(movie)
        print(f"\n🔍 Rising Queries:")
        for query in related['rising'][:5]:
            print(f"  - {query['query']}")
