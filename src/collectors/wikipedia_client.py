"""Wikipedia Pageviews API client."""

import requests
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta

from ..utils.config import Config


class WikipediaClient:
    """Client for Wikipedia Pageviews API."""
    
    def __init__(self):
        self.base_url = Config.WIKIPEDIA_PAGEVIEWS_URL
    
    def _make_request(self, endpoint: str) -> Dict[str, Any]:
        """Make a request to Wikipedia API."""
        url = f"{self.base_url}/{endpoint}"
        headers = {'User-Agent': 'TrailerCampaignAutopilot/1.0'}
        
        try:
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"❌ Wikipedia API error: {e}")
            return {}
    
    @staticmethod
    def _format_date(date: datetime) -> str:
        """Format date for Wikipedia API (YYYYMMDD00)."""
        return date.strftime('%Y%m%d00')
    
    def get_pageviews(
        self,
        article: str,
        start_date: datetime,
        end_date: datetime,
        project: str = 'en.wikipedia',
        access: str = 'all-access',
        agent: str = 'user'
    ) -> Dict[str, Any]:
        """
        Get pageview data for a specific article.
        
        Args:
            article: Article title (use underscores for spaces)
            start_date: Start date for data
            end_date: End date for data
            project: Wikipedia project (e.g., 'en.wikipedia', 'fr.wikipedia')
            access: Access method ('all-access', 'desktop', 'mobile-app', 'mobile-web')
            agent: User agent type ('user', 'spider', 'automated')
        """
        start = self._format_date(start_date)
        end = self._format_date(end_date)
        
        endpoint = f"per-article/{project}/{access}/{agent}/{article}/daily/{start}/{end}"
        
        data = self._make_request(endpoint)
        
        if not data or 'items' not in data:
            return {'article': article, 'views': []}
        
        views = [
            {
                'date': item['timestamp'][:8],  # YYYYMMDD
                'views': item['views']
            }
            for item in data.get('items', [])
        ]
        
        return {
            'article': article,
            'project': project,
            'total_views': sum(v['views'] for v in views),
            'daily_views': views
        }
    
    def get_recent_pageviews(
        self,
        article: str,
        days: int = 30,
        project: str = 'en.wikipedia'
    ) -> Dict[str, Any]:
        """Get pageviews for the last N days."""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        return self.get_pageviews(article, start_date, end_date, project)
    
    def detect_attention_spikes(
        self,
        article: str,
        days: int = 30,
        spike_threshold: float = 2.0
    ) -> Dict[str, Any]:
        """
        Detect days with unusual attention spikes.
        
        Args:
            article: Article title
            days: Number of days to analyze
            spike_threshold: Multiple of average views to consider a spike
        """
        data = self.get_recent_pageviews(article, days)
        
        if not data.get('daily_views'):
            return {'article': article, 'spikes': [], 'average_views': 0}
        
        views = [v['views'] for v in data['daily_views']]
        avg_views = sum(views) / len(views) if views else 0
        
        spikes = [
            {
                'date': v['date'],
                'views': v['views'],
                'multiple': round(v['views'] / avg_views, 2) if avg_views > 0 else 0
            }
            for v in data['daily_views']
            if v['views'] >= avg_views * spike_threshold
        ]
        
        spikes.sort(key=lambda x: x['views'], reverse=True)
        
        return {
            'article': article,
            'average_views': int(avg_views),
            'max_views': max(views) if views else 0,
            'spikes': spikes,
            'spike_count': len(spikes)
        }
    
    def compare_articles(
        self,
        articles: List[str],
        days: int = 30,
        project: str = 'en.wikipedia'
    ) -> Dict[str, Any]:
        """Compare pageviews across multiple articles."""
        results = {}
        
        for article in articles:
            data = self.get_recent_pageviews(article, days, project)
            results[article] = {
                'total_views': data.get('total_views', 0),
                'avg_daily_views': data.get('total_views', 0) / days if days > 0 else 0
            }
        
        # Sort by total views
        sorted_articles = sorted(
            results.items(),
            key=lambda x: x[1]['total_views'],
            reverse=True
        )
        
        return {
            'comparison_period_days': days,
            'articles': dict(sorted_articles),
            'top_article': sorted_articles[0][0] if sorted_articles else None
        }
    
    def get_multi_language_views(
        self,
        article_translations: Dict[str, str],
        days: int = 30
    ) -> Dict[str, Any]:
        """
        Get pageviews across multiple language editions.
        
        Args:
            article_translations: Dict of {language_code: article_title}
                                 e.g., {'en': 'Dune_(2021_film)', 'fr': 'Dune_(film,_2021)'}
        """
        results = {}
        total_views = 0
        
        for lang_code, article in article_translations.items():
            project = f"{lang_code}.wikipedia"
            data = self.get_recent_pageviews(article, days, project)
            views = data.get('total_views', 0)
            
            results[lang_code] = {
                'article': article,
                'views': views,
                'avg_daily': views / days if days > 0 else 0
            }
            total_views += views
        
        # Sort by views
        sorted_langs = sorted(
            results.items(),
            key=lambda x: x[1]['views'],
            reverse=True
        )
        
        return {
            'period_days': days,
            'total_views_all_languages': total_views,
            'by_language': dict(sorted_langs),
            'top_language': sorted_langs[0][0] if sorted_langs else None
        }


# Example usage
if __name__ == "__main__":
    client = WikipediaClient()
    
    # Analyze pageviews for a movie
    article = "Dune:_Part_Two"
    
    print(f"📊 Wikipedia Pageviews for '{article}'")
    
    # Get recent views
    recent = client.get_recent_pageviews(article, days=30)
    print(f"\nTotal views (30 days): {recent['total_views']:,}")
    print(f"Average per day: {recent['total_views'] / 30:,.0f}")
    
    # Detect spikes
    spikes = client.detect_attention_spikes(article, days=30)
    print(f"\n🔥 Attention Spikes: {spikes['spike_count']}")
    for spike in spikes['spikes'][:3]:
        print(f"  {spike['date']}: {spike['views']:,} views ({spike['multiple']}x average)")
    
    # Multi-language comparison
    translations = {
        'en': 'Dune:_Part_Two',
        'fr': 'Dune_(film,_2024)',
        'de': 'Dune:_Part_Two',
        'es': 'Dune:_Part_Two'
    }
    multi = client.get_multi_language_views(translations, days=30)
    print(f"\n🌍 Global Interest:")
    print(f"Total across languages: {multi['total_views_all_languages']:,}")
    print(f"Top language: {multi['top_language']}")
