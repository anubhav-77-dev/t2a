"""YouTube Data API client for analyzing trailer engagement."""

import re
from typing import Dict, List, Optional, Any
from datetime import datetime

try:
    from googleapiclient.discovery import build
    from googleapiclient.errors import HttpError
except ImportError:
    print("⚠️  google-api-python-client not installed. YouTube features will be limited.")
    build = None
    HttpError = Exception

from ..utils.config import Config


class YouTubeClient:
    """Client for interacting with YouTube Data API v3."""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or Config.YOUTUBE_API_KEY
        
        if not self.api_key:
            raise ValueError("YouTube API key is required. Set YOUTUBE_API_KEY in .env file.")
        
        if build:
            self.youtube = build('youtube', 'v3', developerKey=self.api_key)
        else:
            self.youtube = None
            print("⚠️  YouTube client not initialized. Install google-api-python-client.")
    
    @staticmethod
    def extract_video_id(url: str) -> Optional[str]:
        """Extract video ID from various YouTube URL formats."""
        patterns = [
            r'(?:youtube\.com\/watch\?v=|youtu\.be\/)([^&\n?#]+)',
            r'youtube\.com\/embed\/([^&\n?#]+)',
            r'youtube\.com\/v\/([^&\n?#]+)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        return None
    
    def get_video_stats(self, video_id: str) -> Dict[str, Any]:
        """Get video statistics (views, likes, comments count)."""
        if not self.youtube:
            return {}
        
        try:
            request = self.youtube.videos().list(
                part='statistics,snippet,contentDetails',
                id=video_id
            )
            response = request.execute()
            
            if not response.get('items'):
                return {}
            
            item = response['items'][0]
            stats = item.get('statistics', {})
            snippet = item.get('snippet', {})
            content = item.get('contentDetails', {})
            
            return {
                'video_id': video_id,
                'title': snippet.get('title', ''),
                'description': snippet.get('description', ''),
                'published_at': snippet.get('publishedAt', ''),
                'channel_title': snippet.get('channelTitle', ''),
                'view_count': int(stats.get('viewCount', 0)),
                'like_count': int(stats.get('likeCount', 0)),
                'comment_count': int(stats.get('commentCount', 0)),
                'duration': content.get('duration', ''),
                'tags': snippet.get('tags', [])
            }
        except HttpError as e:
            print(f"❌ YouTube API error: {e}")
            return {}
    
    def get_comments(
        self,
        video_id: str,
        max_results: int = 100,
        order: str = 'relevance'
    ) -> List[Dict[str, Any]]:
        """
        Get comments from a video.
        
        Args:
            video_id: YouTube video ID
            max_results: Maximum number of comments to fetch
            order: 'relevance' or 'time'
        """
        if not self.youtube:
            return []
        
        comments = []
        next_page_token = None
        
        try:
            while len(comments) < max_results:
                request = self.youtube.commentThreads().list(
                    part='snippet',
                    videoId=video_id,
                    maxResults=min(100, max_results - len(comments)),
                    order=order,
                    pageToken=next_page_token,
                    textFormat='plainText'
                )
                response = request.execute()
                
                for item in response.get('items', []):
                    snippet = item['snippet']['topLevelComment']['snippet']
                    comments.append({
                        'comment_id': item['id'],
                        'author': snippet.get('authorDisplayName', 'Unknown'),
                        'text': snippet.get('textDisplay', ''),
                        'like_count': snippet.get('likeCount', 0),
                        'published_at': snippet.get('publishedAt', ''),
                        'reply_count': item['snippet'].get('totalReplyCount', 0)
                    })
                
                next_page_token = response.get('nextPageToken')
                if not next_page_token:
                    break
            
            return comments[:max_results]
        
        except HttpError as e:
            print(f"❌ Error fetching comments: {e}")
            return comments
    
    def get_top_comments(
        self,
        video_id: str,
        limit: int = 50,
        min_likes: int = 5
    ) -> List[Dict[str, Any]]:
        """Get top comments by relevance and likes."""
        comments = self.get_comments(video_id, max_results=limit * 2, order='relevance')
        
        # Filter by minimum likes and sort
        top_comments = [c for c in comments if c['like_count'] >= min_likes]
        top_comments.sort(key=lambda x: x['like_count'], reverse=True)
        
        return top_comments[:limit]
    
    def analyze_trailer(self, video_url: str) -> Dict[str, Any]:
        """
        Comprehensive analysis of a trailer video.
        
        Returns engagement metrics, top comments, and key insights.
        """
        video_id = self.extract_video_id(video_url)
        
        if not video_id:
            return {'error': 'Invalid YouTube URL'}
        
        # Get video statistics
        stats = self.get_video_stats(video_id)
        
        if not stats:
            return {'error': 'Could not fetch video data'}
        
        # Get top comments for sentiment analysis
        top_comments = self.get_top_comments(
            video_id,
            limit=Config.MAX_COMMENTS_ANALYZE
        )
        
        # Calculate engagement rate
        views = stats.get('view_count', 1)
        likes = stats.get('like_count', 0)
        comments_count = stats.get('comment_count', 0)
        
        engagement_rate = ((likes + comments_count) / views * 100) if views > 0 else 0
        
        # Calculate days since published
        published = stats.get('published_at', '')
        if published:
            pub_date = datetime.fromisoformat(published.replace('Z', '+00:00'))
            days_since = (datetime.now(pub_date.tzinfo) - pub_date).days
        else:
            days_since = 0
        
        return {
            'video_id': video_id,
            'video_url': f"https://www.youtube.com/watch?v={video_id}",
            'stats': stats,
            'engagement_rate': round(engagement_rate, 4),
            'days_since_published': days_since,
            'views_per_day': round(views / max(days_since, 1)),
            'top_comments': top_comments,
            'comment_sample_size': len(top_comments)
        }


# Example usage
if __name__ == "__main__":
    client = YouTubeClient()
    
    # Example: Analyze a trailer
    trailer_url = "https://www.youtube.com/watch?v=Way9Dexny3w"  # Dune Part Two
    
    analysis = client.analyze_trailer(trailer_url)
    
    if 'error' not in analysis:
        print(f"📊 Trailer Analysis:")
        print(f"Views: {analysis['stats']['view_count']:,}")
        print(f"Likes: {analysis['stats']['like_count']:,}")
        print(f"Comments: {analysis['stats']['comment_count']:,}")
        print(f"Engagement Rate: {analysis['engagement_rate']:.2f}%")
        print(f"\n💬 Top Comments Sample ({len(analysis['top_comments'])}):")
        for comment in analysis['top_comments'][:3]:
            print(f"  - [{comment['like_count']} likes] {comment['text'][:80]}...")
