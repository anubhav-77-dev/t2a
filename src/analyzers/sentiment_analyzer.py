"""Sentiment analysis for YouTube comments and text content."""

from typing import Dict, List, Any, Tuple
from collections import Counter
import re

try:
    from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
    VADER_AVAILABLE = True
except ImportError:
    print("⚠️  vaderSentiment not installed. Using basic sentiment analysis.")
    VADER_AVAILABLE = False

try:
    from textblob import TextBlob
    TEXTBLOB_AVAILABLE = True
except ImportError:
    print("⚠️  textblob not installed. Sentiment analysis will be limited.")
    TEXTBLOB_AVAILABLE = False


class SentimentAnalyzer:
    """Analyze sentiment from comments and text content."""
    
    def __init__(self):
        self.vader = SentimentIntensityAnalyzer() if VADER_AVAILABLE else None
        
        # Marketing-relevant emotion keywords
        self.positive_keywords = {
            'excited', 'amazing', 'love', 'awesome', 'incredible', 'perfect',
            'masterpiece', 'brilliant', 'fantastic', 'stunning', 'beautiful',
            'epic', 'cant wait', "can't wait", 'hyped', 'hype', 'goat',
            'legendary', 'insane', 'phenomenal', 'outstanding', 'breathtaking'
        }
        
        self.negative_keywords = {
            'disappointed', 'boring', 'bad', 'terrible', 'awful', 'hate',
            'worst', 'poor', 'weak', 'underwhelming', 'overrated', 'trash',
            'disaster', 'mess', 'flop', 'waste', 'skip', 'avoid'
        }
        
        self.anticipation_keywords = {
            'cant wait', "can't wait", 'excited', 'hype', 'hyped', 'anticipate',
            'looking forward', 'finally', 'soon', 'release', 'premiere',
            'countdown', 'ready', 'prepared'
        }
        
        self.concern_keywords = {
            'worried', 'concerned', 'hope', 'please', 'nervous', 'scared',
            'afraid', 'doubt', 'skeptical', 'unsure'
        }
    
    def analyze_text(self, text: str) -> Dict[str, Any]:
        """
        Analyze sentiment of a single text.
        
        Returns compound score, polarity, and emotion signals.
        """
        text_lower = text.lower()
        
        # VADER sentiment (if available)
        vader_scores = None
        if self.vader:
            vader_scores = self.vader.polarity_scores(text)
        
        # TextBlob sentiment (if available)
        textblob_scores = None
        if TEXTBLOB_AVAILABLE:
            blob = TextBlob(text)
            textblob_scores = {
                'polarity': blob.sentiment.polarity,
                'subjectivity': blob.sentiment.subjectivity
            }
        
        # Keyword-based emotion detection
        positive_count = sum(1 for kw in self.positive_keywords if kw in text_lower)
        negative_count = sum(1 for kw in self.negative_keywords if kw in text_lower)
        anticipation_count = sum(1 for kw in self.anticipation_keywords if kw in text_lower)
        concern_count = sum(1 for kw in self.concern_keywords if kw in text_lower)
        
        # Determine primary sentiment
        if vader_scores:
            compound = vader_scores['compound']
        elif textblob_scores:
            compound = textblob_scores['polarity']
        else:
            # Fallback: keyword ratio
            total_keywords = positive_count + negative_count
            compound = ((positive_count - negative_count) / total_keywords) if total_keywords > 0 else 0
        
        # Classify sentiment
        if compound >= 0.05:
            sentiment_label = 'positive'
        elif compound <= -0.05:
            sentiment_label = 'negative'
        else:
            sentiment_label = 'neutral'
        
        return {
            'text': text[:200],  # Store snippet
            'compound_score': round(compound, 3),
            'sentiment': sentiment_label,
            'vader_scores': vader_scores,
            'textblob_scores': textblob_scores,
            'emotions': {
                'positive_signals': positive_count,
                'negative_signals': negative_count,
                'anticipation': anticipation_count,
                'concern': concern_count
            }
        }
    
    def analyze_comments(
        self,
        comments: List[Dict[str, Any]],
        weight_by_likes: bool = True
    ) -> Dict[str, Any]:
        """
        Analyze sentiment across multiple comments.
        
        Args:
            comments: List of comment dicts with 'text' and 'like_count'
            weight_by_likes: Whether to weight by like count
        """
        if not comments:
            return {
                'total_comments': 0,
                'overall_sentiment': 'neutral',
                'sentiment_distribution': {},
                'top_emotions': {}
            }
        
        analyzed = []
        total_weight = 0
        weighted_compound = 0
        sentiment_counts = Counter()
        emotion_totals = Counter()
        
        for comment in comments:
            text = comment.get('text', '')
            likes = comment.get('like_count', 0)
            
            if not text:
                continue
            
            analysis = self.analyze_text(text)
            
            # Weight calculation
            weight = (likes + 1) if weight_by_likes else 1
            total_weight += weight
            
            # Weighted compound score
            weighted_compound += analysis['compound_score'] * weight
            
            # Count sentiments
            sentiment_counts[analysis['sentiment']] += weight
            
            # Sum emotions
            for emotion, count in analysis['emotions'].items():
                emotion_totals[emotion] += count
            
            analyzed.append({
                **analysis,
                'likes': likes,
                'weight': weight
            })
        
        # Calculate averages
        avg_compound = weighted_compound / total_weight if total_weight > 0 else 0
        
        # Determine overall sentiment
        if avg_compound >= 0.05:
            overall = 'positive'
        elif avg_compound <= -0.05:
            overall = 'negative'
        else:
            overall = 'neutral'
        
        # Sentiment distribution percentages
        sentiment_dist = {
            sentiment: (count / total_weight * 100) if total_weight > 0 else 0
            for sentiment, count in sentiment_counts.items()
        }
        
        # Get top positive and negative comments
        top_positive = sorted(
            [c for c in analyzed if c['sentiment'] == 'positive'],
            key=lambda x: (x['compound_score'], x['likes']),
            reverse=True
        )[:5]
        
        top_negative = sorted(
            [c for c in analyzed if c['sentiment'] == 'negative'],
            key=lambda x: (x['compound_score'], x['likes'])
        )[:5]
        
        return {
            'total_comments': len(comments),
            'analyzed_comments': len(analyzed),
            'overall_sentiment': overall,
            'average_compound_score': round(avg_compound, 3),
            'sentiment_distribution': {
                k: round(v, 2) for k, v in sentiment_dist.items()
            },
            'emotion_totals': dict(emotion_totals),
            'top_positive_comments': [
                {
                    'text': c['text'],
                    'score': c['compound_score'],
                    'likes': c['likes']
                }
                for c in top_positive
            ],
            'top_negative_comments': [
                {
                    'text': c['text'],
                    'score': c['compound_score'],
                    'likes': c['likes']
                }
                for c in top_negative
            ],
            'marketing_insights': self._generate_insights(
                overall,
                sentiment_dist,
                emotion_totals
            )
        }
    
    def _generate_insights(
        self,
        overall: str,
        sentiment_dist: Dict[str, float],
        emotions: Dict[str, int]
    ) -> List[str]:
        """Generate marketing insights from sentiment data."""
        insights = []
        
        # Overall sentiment insight
        positive_pct = sentiment_dist.get('positive', 0)
        negative_pct = sentiment_dist.get('negative', 0)
        
        if positive_pct > 70:
            insights.append("Strong positive reception - ideal for testimonial-based marketing")
        elif positive_pct > 50:
            insights.append("Generally positive sentiment - safe for broad campaigns")
        elif negative_pct > 30:
            insights.append("Mixed reception - consider addressing concerns in messaging")
        
        # Anticipation insight
        anticipation = emotions.get('anticipation', 0)
        positive_signals = emotions.get('positive_signals', 0)
        if anticipation > positive_signals * 0.3 and positive_signals > 0:
            insights.append("High anticipation detected - leverage countdown/FOMO tactics")
        
        # Concern insight
        concern = emotions.get('concern', 0)
        if concern > 5:
            insights.append("Some audience concerns present - consider FAQ/reassurance content")
        
        return insights
    
    def extract_trending_phrases(
        self,
        comments: List[Dict[str, Any]],
        min_frequency: int = 3
    ) -> List[Dict[str, Any]]:
        """Extract commonly mentioned phrases for ad copy inspiration."""
        # Combine all comment text
        all_text = ' '.join(comment.get('text', '') for comment in comments)
        
        # Simple n-gram extraction (2-4 words)
        words = re.findall(r'\b\w+\b', all_text.lower())
        
        # Bigrams and trigrams
        phrases = Counter()
        for i in range(len(words) - 1):
            bigram = ' '.join(words[i:i+2])
            phrases[bigram] += 1
        
        for i in range(len(words) - 2):
            trigram = ' '.join(words[i:i+3])
            phrases[trigram] += 1
        
        # Filter by frequency and remove common stopwords
        stopwords = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for'}
        trending = [
            {'phrase': phrase, 'count': count}
            for phrase, count in phrases.most_common(20)
            if count >= min_frequency and not any(sw in phrase.split() for sw in stopwords)
        ]
        
        return trending[:10]


# Example usage
if __name__ == "__main__":
    analyzer = SentimentAnalyzer()
    
    # Sample comments
    sample_comments = [
        {'text': "This looks absolutely incredible! Can't wait to see it!", 'like_count': 150},
        {'text': "The visuals are stunning. This is going to be epic!", 'like_count': 89},
        {'text': "I'm worried about the pacing, but hoping for the best", 'like_count': 23},
        {'text': "Disappointed with the trailer, seems underwhelming", 'like_count': 12},
        {'text': "Masterpiece incoming. The hype is real!", 'like_count': 200},
    ]
    
    results = analyzer.analyze_comments(sample_comments)
    
    print("📊 Sentiment Analysis Results:")
    print(f"Overall: {results['overall_sentiment'].upper()}")
    print(f"Average Score: {results['average_compound_score']}")
    print(f"\nDistribution:")
    for sentiment, pct in results['sentiment_distribution'].items():
        print(f"  {sentiment}: {pct:.1f}%")
    print(f"\n💡 Insights:")
    for insight in results['marketing_insights']:
        print(f"  - {insight}")
