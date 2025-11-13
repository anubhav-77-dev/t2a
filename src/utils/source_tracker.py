"""Source tracking utilities for transparent citation of data sources."""

from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import List, Dict, Any, Optional
from enum import Enum
import json


class SourceType(Enum):
    """Types of data sources."""
    YOUTUBE_COMMENT = "youtube_comment"
    YOUTUBE_STATS = "youtube_stats"
    TMDB_METADATA = "tmdb_metadata"
    WIKIPEDIA_PAGEVIEWS = "wikipedia_pageviews"
    GOOGLE_TRENDS = "google_trends"
    WEATHER_DATA = "weather_data"


@dataclass
class Source:
    """A single data source citation."""
    source_type: SourceType
    source_id: str
    content: str
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)
    confidence: float = 1.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        data = asdict(self)
        data['source_type'] = self.source_type.value
        data['timestamp'] = self.timestamp.isoformat()
        return data


class SourceTracker:
    """Track and manage data sources for generated content."""
    
    def __init__(self):
        self.sources: List[Source] = []
    
    def add_source(
        self,
        source_type: SourceType,
        source_id: str,
        content: str,
        metadata: Optional[Dict[str, Any]] = None,
        confidence: float = 1.0
    ) -> Source:
        """Add a new source citation."""
        source = Source(
            source_type=source_type,
            source_id=source_id,
            content=content,
            metadata=metadata or {},
            confidence=confidence
        )
        self.sources.append(source)
        return source
    
    def add_youtube_comment(
        self,
        comment_id: str,
        text: str,
        likes: int = 0,
        author: str = "",
        confidence: float = 1.0
    ) -> Source:
        """Add a YouTube comment source."""
        return self.add_source(
            SourceType.YOUTUBE_COMMENT,
            f"yt_comment:{comment_id}",
            text,
            metadata={"likes": likes, "author": author},
            confidence=confidence
        )
    
    def add_tmdb_metadata(
        self,
        field: str,
        value: Any,
        movie_id: int
    ) -> Source:
        """Add TMDb metadata source."""
        return self.add_source(
            SourceType.TMDB_METADATA,
            f"tmdb:{movie_id}:{field}",
            str(value),
            metadata={"field": field, "movie_id": movie_id}
        )
    
    def add_trend_data(
        self,
        keyword: str,
        region: str,
        interest_score: float,
        timeframe: str
    ) -> Source:
        """Add Google Trends source."""
        return self.add_source(
            SourceType.GOOGLE_TRENDS,
            f"trends:{region}:{keyword}",
            f"Interest score: {interest_score}",
            metadata={
                "keyword": keyword,
                "region": region,
                "interest_score": interest_score,
                "timeframe": timeframe
            },
            confidence=min(interest_score / 100, 1.0)
        )
    
    def add_pageview_data(
        self,
        title: str,
        views: int,
        date: str,
        region: str = "all"
    ) -> Source:
        """Add Wikipedia pageviews source."""
        return self.add_source(
            SourceType.WIKIPEDIA_PAGEVIEWS,
            f"wiki:{region}:{title}:{date}",
            f"{views:,} views on {date}",
            metadata={
                "title": title,
                "views": views,
                "date": date,
                "region": region
            }
        )
    
    def get_sources_by_type(self, source_type: SourceType) -> List[Source]:
        """Get all sources of a specific type."""
        return [s for s in self.sources if s.source_type == source_type]
    
    def get_high_confidence_sources(self, threshold: float = 0.7) -> List[Source]:
        """Get sources above a confidence threshold."""
        return [s for s in self.sources if s.confidence >= threshold]
    
    def to_citation_list(self) -> List[str]:
        """Generate a list of human-readable citations."""
        citations = []
        for source in self.sources:
            if source.source_type == SourceType.YOUTUBE_COMMENT:
                author = source.metadata.get('author', 'User')
                likes = source.metadata.get('likes', 0)
                citations.append(f"YouTube comment by {author} ({likes} likes): \"{source.content[:100]}...\"")
            elif source.source_type == SourceType.TMDB_METADATA:
                field = source.metadata.get('field', 'field')
                citations.append(f"TMDb {field}: {source.content}")
            elif source.source_type == SourceType.GOOGLE_TRENDS:
                region = source.metadata.get('region', '')
                score = source.metadata.get('interest_score', 0)
                citations.append(f"Google Trends ({region}): {score}/100 interest")
            elif source.source_type == SourceType.WIKIPEDIA_PAGEVIEWS:
                citations.append(f"Wikipedia: {source.content}")
            else:
                citations.append(f"{source.source_type.value}: {source.content}")
        return citations
    
    def to_json(self, indent: int = 2) -> str:
        """Export sources as JSON."""
        data = {
            "total_sources": len(self.sources),
            "by_type": {
                source_type.value: len(self.get_sources_by_type(source_type))
                for source_type in SourceType
            },
            "sources": [s.to_dict() for s in self.sources]
        }
        return json.dumps(data, indent=indent)
    
    def clear(self):
        """Clear all tracked sources."""
        self.sources.clear()
