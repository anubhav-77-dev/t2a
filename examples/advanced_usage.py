"""Example: Analyzing specific campaign components."""

from src.collectors import TMDbClient, YouTubeClient, WikipediaClient, TrendsClient
from src.analyzers import SentimentAnalyzer, RegionalScorer
from src.generators.ad_copy_generator import AdCopyGenerator
from src.generators.social_post_generator import SocialPostGenerator

def example_sentiment_analysis():
    """Example: Analyze trailer comments for sentiment."""
    print("\n" + "=" * 60)
    print("Example: Sentiment Analysis")
    print("=" * 60)
    
    youtube = YouTubeClient()
    analyzer = SentimentAnalyzer()
    
    # Get trailer comments
    trailer_url = "https://www.youtube.com/watch?v=Way9Dexny3w"
    analysis = youtube.analyze_trailer(trailer_url)
    
    if 'error' not in analysis:
        comments = analysis['top_comments']
        
        # Analyze sentiment
        results = analyzer.analyze_comments(comments[:100])
        
        print(f"\n📊 Analyzed {results['analyzed_comments']} comments")
        print(f"Overall Sentiment: {results['overall_sentiment'].upper()}")
        print(f"\nDistribution:")
        for sentiment, pct in results['sentiment_distribution'].items():
            print(f"  {sentiment}: {pct:.1f}%")
        
        print(f"\n💡 Marketing Insights:")
        for insight in results['marketing_insights']:
            print(f"  • {insight}")


def example_regional_comparison():
    """Example: Compare regional interest."""
    print("\n" + "=" * 60)
    print("Example: Regional Market Comparison")
    print("=" * 60)
    
    scorer = RegionalScorer()
    
    # Sample data (in real use, this comes from APIs)
    regional_data = {
        'US': {
            'interest_score': 95,
            'engagement_rate': 0.08,
            'growth_rate': 0.12,
            'sentiment_score': 0.85
        },
        'GB': {
            'interest_score': 87,
            'engagement_rate': 0.09,
            'growth_rate': 0.15,
            'sentiment_score': 0.82
        },
        'IN': {
            'interest_score': 72,
            'engagement_rate': 0.12,
            'growth_rate': 0.35,
            'sentiment_score': 0.78
        },
        'BR': {
            'interest_score': 65,
            'engagement_rate': 0.07,
            'growth_rate': 0.08,
            'sentiment_score': 0.75
        },
        'AU': {
            'interest_score': 80,
            'engagement_rate': 0.06,
            'growth_rate': 0.10,
            'sentiment_score': 0.80
        }
    }
    
    comparison = scorer.compare_regions(regional_data)
    
    print("\n🌍 Regional Priority Ranking:")
    for i, region in enumerate(comparison['top_5'], 1):
        print(f"\n{i}. {region['region']} (Tier {region['tier']})")
        print(f"   Score: {region['total_score']}/100")
        print(f"   Budget Allocation: {region['suggested_budget_pct']}%")
        print(f"   {region['recommendation']}")


def example_content_generation():
    """Example: Generate marketing content."""
    print("\n" + "=" * 60)
    print("Example: Content Generation")
    print("=" * 60)
    
    # Sample movie data
    movie_data = {
        'movie_id': 693134,
        'title': 'Dune: Part Two',
        'tagline': 'Long live the fighters',
        'overview': 'Follow the mythic journey of Paul Atreides as he unites with Chani and the Fremen while seeking revenge against those who destroyed his family.',
        'cast': ['Timothée Chalamet', 'Zendaya', 'Rebecca Ferguson'],
        'directors': ['Denis Villeneuve'],
        'genres': ['Science Fiction', 'Adventure', 'Drama'],
        'release_date': '2024-03-01'
    }
    
    sentiment_data = {
        'overall_sentiment': 'positive',
        'sentiment_distribution': {'positive': 82, 'neutral': 13, 'negative': 5},
        'emotion_totals': {'anticipation': 45}
    }
    
    # Generate ad copy
    print("\n📝 Generating Ad Copy...")
    ad_gen = AdCopyGenerator()
    ad_result = ad_gen.generate_with_sources(movie_data, sentiment_data, count=3)
    
    for variant in ad_result['variants']:
        print(f"\n[{variant['variant'].upper()}] ({variant['length']})")
        print(f"{variant['text']}")
        print(f"Platform: {variant['platform']}")
    
    # Generate social posts
    print("\n\n📱 Generating Social Media Posts...")
    social_gen = SocialPostGenerator()
    social_posts = social_gen.generate_all_platforms(movie_data, sentiment_data)
    
    # Show Twitter post
    twitter = social_posts.get('twitter', {})
    print(f"\n🐦 Twitter/X Post:")
    print(f"{twitter.get('text', '')}")
    
    # Show Instagram post
    instagram = social_posts.get('instagram', {})
    print(f"\n📸 Instagram Post:")
    print(f"{instagram.get('text', '')[:200]}...")


def example_data_collection():
    """Example: Collect data from various sources."""
    print("\n" + "=" * 60)
    print("Example: Multi-Source Data Collection")
    print("=" * 60)
    
    # TMDb data
    print("\n🎬 Collecting from TMDb...")
    tmdb = TMDbClient()
    movie_data = tmdb.extract_marketing_metadata(693134)  # Dune: Part Two
    print(f"   Title: {movie_data.get('title')}")
    print(f"   Cast: {', '.join(movie_data.get('cast', [])[:3])}")
    print(f"   Keywords: {', '.join(movie_data.get('keywords', [])[:5])}")
    
    # Wikipedia pageviews
    print("\n📚 Collecting from Wikipedia...")
    wiki = WikipediaClient()
    pageviews = wiki.get_recent_pageviews("Dune:_Part_Two", days=30)
    print(f"   Total pageviews (30 days): {pageviews.get('total_views', 0):,}")
    
    spikes = wiki.detect_attention_spikes("Dune:_Part_Two", days=30)
    print(f"   Attention spikes detected: {spikes.get('spike_count', 0)}")
    
    # Google Trends
    print("\n📈 Collecting from Google Trends...")
    trends = TrendsClient()
    if trends.pytrends:
        regional = trends.get_interest_by_region("Dune Part Two")
        top_regions = regional.get('regions', [])[:5]
        print(f"   Top 5 interested regions:")
        for region in top_regions:
            print(f"     • {region['region']}: {region['interest']}/100")
    else:
        print("   ⚠️  Trends client not available")


if __name__ == "__main__":
    # Run all examples
    example_data_collection()
    example_sentiment_analysis()
    example_regional_comparison()
    example_content_generation()
    
    print("\n" + "=" * 60)
    print("✅ All Examples Complete!")
    print("=" * 60)
