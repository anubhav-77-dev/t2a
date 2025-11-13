#!/usr/bin/env python3
"""
Demo Mode - Run the autopilot with mock data (no API calls needed).

This is useful for:
- Testing the system without API dependencies
- Demonstrations when offline
- Understanding the output structure
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import datetime, timedelta
from src.analyzers.sentiment_analyzer import SentimentAnalyzer
from src.analyzers.trend_detector import TrendDetector
from src.analyzers.regional_scorer import RegionalScorer
from src.generators.ad_copy_generator import AdCopyGenerator
from src.generators.social_post_generator import SocialPostGenerator
from src.generators.gemini_enhancer import GeminiEnhancer
from src.planners.rollout_planner import RolloutPlanner
from src.utils.config import Config
from src.utils.source_tracker import SourceTracker


def create_mock_movie_data():
    """Create realistic mock movie data."""
    return {
        'id': 693134,
        'title': 'Dune: Part Two',
        'tagline': 'Long live the fighters.',
        'overview': 'Follow the mythic journey of Paul Atreides as he unites with Chani and the Fremen while on a path of revenge against the conspirators who destroyed his family.',
        'release_date': '2024-03-01',
        'genres': [
            {'id': 878, 'name': 'Science Fiction'},
            {'id': 12, 'name': 'Adventure'},
            {'id': 28, 'name': 'Action'}
        ],
        'runtime': 166,
        'budget': 190000000,
        'vote_average': 8.4,
        'vote_count': 5247,
        'cast': [
            {'name': 'Timothée Chalamet', 'character': 'Paul Atreides', 'order': 0},
            {'name': 'Zendaya', 'character': 'Chani', 'order': 1},
            {'name': 'Rebecca Ferguson', 'character': 'Lady Jessica', 'order': 2},
            {'name': 'Josh Brolin', 'character': 'Gurney Halleck', 'order': 3},
            {'name': 'Austin Butler', 'character': 'Feyd-Rautha', 'order': 4},
            {'name': 'Florence Pugh', 'character': 'Princess Irulan', 'order': 5}
        ],
        'director': {'name': 'Denis Villeneuve'},
        'keywords': ['desert', 'prophecy', 'spice', 'empire', 'revenge', 'sci-fi epic'],
        'poster_path': '/8b8R8l88Qje9dn9OE8PY05Nxl1X.jpg'
    }


def create_mock_youtube_data():
    """Create realistic mock YouTube comments."""
    return {
        'video_id': 'Way9Dexny3w',
        'title': 'DUNE: PART TWO - Official Trailer',
        'view_count': 28500000,
        'like_count': 520000,
        'comment_count': 15200,
        'comments': [
            {'text': 'This looks absolutely incredible! Denis Villeneuve is a master filmmaker.', 'likes': 8500, 'published': '2023-12-01'},
            {'text': 'The visuals are stunning. Can\'t wait to see this in IMAX!', 'likes': 6200, 'published': '2023-12-01'},
            {'text': 'Timothée and Zendaya together again! The chemistry is perfect.', 'likes': 5100, 'published': '2023-12-02'},
            {'text': 'Oscar worthy for sure. The cinematography alone deserves awards.', 'likes': 4800, 'published': '2023-12-02'},
            {'text': 'Austin Butler as Feyd-Rautha is going to be amazing!', 'likes': 4200, 'published': '2023-12-03'},
            {'text': 'March 1st can\'t come soon enough. Already bought tickets!', 'likes': 3900, 'published': '2023-12-03'},
            {'text': 'The soundtrack gives me chills every single time.', 'likes': 3500, 'published': '2023-12-04'},
            {'text': 'This is how you make a sci-fi epic. Hollywood take notes.', 'likes': 3200, 'published': '2023-12-04'},
            {'text': 'Finally a sequel that looks better than the first!', 'likes': 2900, 'published': '2023-12-05'},
            {'text': 'The desert scenes are breathtaking. Pure cinema.', 'likes': 2600, 'published': '2023-12-05'},
            # Add some varied sentiment
            {'text': 'Hope it\'s not too long though. Part one was a bit slow.', 'likes': 450, 'published': '2023-12-06'},
            {'text': 'Looks great but I\'m worried about the pacing', 'likes': 320, 'published': '2023-12-07'},
            {'text': 'Incredible! Best trailer I\'ve seen all year!', 'likes': 5600, 'published': '2023-12-08'},
            {'text': 'The scale of this movie is unmatched. Epic!', 'likes': 4100, 'published': '2023-12-09'},
            {'text': 'IMAX or nothing for this one!', 'likes': 3800, 'published': '2023-12-10'},
        ]
    }


def create_mock_wikipedia_data():
    """Create mock Wikipedia pageview data."""
    base_date = datetime.now() - timedelta(days=30)
    return {
        'title': 'Dune: Part Two',
        'views': [
            {'date': (base_date + timedelta(days=i)).strftime('%Y-%m-%d'), 
             'value': 15000 + (i * 500) + (2000 if i > 20 else 0)}  # Spike after day 20
            for i in range(30)
        ]
    }


def create_mock_trends_data():
    """Create mock Google Trends data."""
    return {
        'US': {'interest': 85, 'growth': 42},
        'UK': {'interest': 72, 'growth': 38},
        'IN': {'interest': 68, 'growth': 55},
        'CA': {'interest': 65, 'growth': 35},
        'AU': {'interest': 60, 'growth': 30}
    }


def run_demo():
    """Run the full autopilot pipeline with mock data."""
    print("🎬 Demo Mode - Trailer-to-Campaign Autopilot")
    print("=" * 60)
    print("📝 Note: Using mock data (no API calls)\n")
    
    # Initialize components
    source_tracker = SourceTracker()
    sentiment_analyzer = SentimentAnalyzer()
    trend_detector = TrendDetector()
    regional_scorer = RegionalScorer()
    ad_copy_gen = AdCopyGenerator()
    social_gen = SocialPostGenerator()
    rollout_planner = RolloutPlanner()
    
    # Initialize Gemini if available
    gemini_enhancer = None
    if Config.has_gemini():
        try:
            gemini_enhancer = GeminiEnhancer()
            print("✅ Gemini AI enabled for enhanced content\n")
        except:
            print("⚠️  Gemini not available, using template generation\n")
    
    # Create mock data
    print("📊 Step 1: Loading mock movie data...")
    movie_data = create_mock_movie_data()
    print(f"✓ Movie: {movie_data['title']}")
    print(f"  Tagline: {movie_data['tagline']}")
    print(f"  Release: {movie_data['release_date']}")
    print(f"  Cast: {', '.join([c['name'] for c in movie_data['cast'][:3]])}...\n")
    
    print("📊 Step 2: Loading YouTube engagement data...")
    youtube_data = create_mock_youtube_data()
    print(f"✓ Views: {youtube_data['view_count']:,}")
    print(f"  Likes: {youtube_data['like_count']:,}")
    print(f"  Comments: {len(youtube_data['comments'])}\n")
    
    print("📊 Step 3: Analyzing sentiment...")
    sentiment_data = sentiment_analyzer.analyze_comments(youtube_data['comments'])
    print(f"✓ Overall sentiment: {sentiment_data['overall_sentiment']}")
    sentiment_dist = sentiment_data['sentiment_distribution']
    print(f"  Positive: {sentiment_dist.get('positive', 0):.1f}%")
    print(f"  Negative: {sentiment_dist.get('negative', 0):.1f}%")
    print(f"  Top themes: {', '.join(list(sentiment_data['emotion_totals'].keys())[:3])}\n")
    
    print("📊 Step 4: Detecting trends...")
    wiki_data = create_mock_wikipedia_data()
    trend_data = trend_detector.detect_momentum(wiki_data['views'])
    print(f"✓ Momentum: {trend_data.get('momentum', 'unknown')}")
    print(f"  Trend: {trend_data.get('trend', 'unknown')}\n")
    
    print("📊 Step 5: Scoring regions...")
    trends_data = create_mock_trends_data()
    regions = ['US', 'UK', 'IN']
    regional_scores = regional_scorer.score_regions(
        regions, trends_data, sentiment_data, youtube_data
    )
    print("✓ Regional priorities:")
    for region in sorted(regional_scores, key=lambda r: regional_scores[r]['score'], reverse=True):
        score_data = regional_scores[region]
        print(f"  {region}: Tier {score_data['tier']} (Score: {score_data['score']:.1f})")
    print()
    
    print("📊 Step 6: Generating ad copy...")
    ad_variants = ad_copy_gen.generate_variants(
        movie_data, sentiment_data, regional_scores
    )
    print(f"✓ Generated {len(ad_variants)} template variants")
    print(f"  Example: {ad_variants[0]['text'][:80]}...\n")
    
    # Gemini enhancement
    if gemini_enhancer:
        print("🤖 Step 7: Enhancing with Gemini AI...")
        try:
            ai_variants = gemini_enhancer.enhance_ad_copy(
                movie_data, sentiment_data, trend_data
            )
            print(f"✓ Generated {len(ai_variants)} AI-enhanced variants")
            print(f"  Example: {ai_variants[0]['text'][:80]}...\n")
        except Exception as e:
            print(f"⚠️  Gemini enhancement skipped: {e}\n")
            ai_variants = []
    else:
        print("⏭️  Step 7: Skipping AI enhancement (Gemini not configured)\n")
        ai_variants = []
    
    print("📊 Step 8: Creating social posts...")
    social_posts = {}
    for platform in ['twitter', 'instagram', 'facebook', 'tiktok']:
        post = social_gen.generate_post(
            platform, movie_data, sentiment_data, ad_variants[0]
        )
        social_posts[platform] = post
    print(f"✓ Created posts for {len(social_posts)} platforms\n")
    
    print("📊 Step 9: Building rollout plan...")
    campaign = rollout_planner.create_rollout_plan(
        movie_data, regional_scores, sentiment_data, trend_data
    )
    print(f"✓ Campaign phases: {len(campaign['phases'])}")
    print(f"  Duration: {campaign['timeline']['total_weeks']} weeks")
    print(f"  Budget allocation: ${campaign['budget']['total_budget']:,}\n")
    
    # Display results
    print("\n" + "=" * 60)
    print("📊 CAMPAIGN SUMMARY")
    print("=" * 60)
    
    print(f"\n🎬 Movie: {movie_data['title']}")
    print(f"📅 Release: {movie_data['release_date']}")
    sentiment_dist = sentiment_data['sentiment_distribution']
    print(f"⭐ Sentiment: {sentiment_data['overall_sentiment']} ({sentiment_dist.get('positive', 0):.1f}% positive)")
    
    print(f"\n📈 Top 3 Ad Copy Variants:")
    for i, variant in enumerate(ad_variants[:3], 1):
        print(f"{i}. [{variant['length']}] {variant['text']}")
    
    if ai_variants:
        print(f"\n🤖 Top 3 AI-Enhanced Variants:")
        for i, variant in enumerate(ai_variants[:3], 1):
            print(f"{i}. [{variant['length']}] {variant['text']}")
    
    print(f"\n📱 Social Media Posts:")
    for platform, post in social_posts.items():
        print(f"\n{platform.upper()}:")
        print(f"  {post['text'][:120]}...")
    
    print(f"\n🌍 Regional Rollout:")
    for phase in campaign['phases']:
        print(f"\nPhase {phase['phase']}: {phase['name']}")
        print(f"  Regions: {', '.join(phase['regions'])}")
        print(f"  Duration: Week {phase['start_week']}-{phase['end_week']}")
        print(f"  Budget: ${phase['budget']:,}")
    
    print(f"\n💰 Total Budget: ${campaign['budget']['total_budget']:,}")
    print(f"🎯 Primary Markets: {', '.join([r for r, d in regional_scores.items() if d['tier'] == 'A'])}")
    
    # Gemini strategic insights
    if gemini_enhancer:
        print(f"\n🤖 Generating AI Strategic Insights...")
        try:
            insights = gemini_enhancer.generate_campaign_insights({
                'movie': movie_data,
                'sentiment': sentiment_data,
                'trends': trend_data,
                'regional_scores': regional_scores,
                'campaign': campaign
            })
            
            print(f"\n💡 AI Strategic Analysis:")
            print(f"\nOpportunities:")
            for opp in insights.get('opportunities', [])[:3]:
                print(f"  • {opp}")
            
            print(f"\nRisks:")
            for risk in insights.get('risks', [])[:3]:
                print(f"  • {risk}")
            
            print(f"\nRecommendations:")
            for rec in insights.get('recommendations', [])[:3]:
                print(f"  • {rec}")
        except Exception as e:
            print(f"⚠️  AI insights generation failed: {e}")
    
    print("\n" + "=" * 60)
    print("✅ Demo complete!")
    print("\n💡 To run with real data:")
    print("   1. Check your network connection")
    print("   2. Verify API keys in .env file")
    print("   3. Try: python main.py generate --trailer-url URL --movie-title TITLE")
    print("=" * 60)


if __name__ == '__main__':
    run_demo()
