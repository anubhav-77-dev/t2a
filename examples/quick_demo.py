#!/usr/bin/env python3
"""
Quick Demo - See the Trailer-to-Campaign Autopilot in action (offline mode).
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

print("🎬 Trailer-to-Campaign Autopilot - Quick Demo")
print("=" * 70)
print("📝 Using mock data (no API calls required)\n")

# Mock movie data
movie = {
    'title': 'Dune: Part Two',
    'tagline': 'Long live the fighters.',
    'release_date': '2024-03-01',
    'genres': ['Science Fiction', 'Adventure', 'Action'],
    'cast': ['Timothée Chalamet', 'Zendaya', 'Rebecca Ferguson', 'Josh Brolin'],
    'director': 'Denis Villeneuve',
    'runtime': 166
}

# Mock engagement data
engagement = {
    'views': 28500000,
    'likes': 520000,
    'comments': 15200,
    'sentiment': 'positive',
    'positive_pct': 82.5,
    'negative_pct': 4.7
}

# Mock regional data
regions = {
    'US': {'tier': 'A', 'score': 92, 'interest': 85},
    'UK': {'tier': 'A', 'score': 85, 'interest': 72},
    'IN': {'tier': 'B', 'score': 78, 'interest': 68}
}

print(f"🎬 MOVIE: {movie['title']}")
print(f"   Tagline: {movie['tagline']}")
print(f"   Release: {movie['release_date']}")
print(f"   Director: {movie['director']}")
print(f"   Cast: {', '.join(movie['cast'][:3])}...")
print()

print(f"📊 ENGAGEMENT METRICS:")
print(f"   YouTube Views: {engagement['views']:,}")
print(f"   Likes: {engagement['likes']:,}")
print(f"   Comments: {engagement['comments']:,}")
print()

print(f"💭 SENTIMENT ANALYSIS:")
print(f"   Overall: {engagement['sentiment'].upper()}")
print(f"   Positive: {engagement['positive_pct']}%")
print(f"   Negative: {engagement['negative_pct']}%")
print()

print(f"🌍 REGIONAL PRIORITIES:")
for region, data in sorted(regions.items(), key=lambda x: x[1]['score'], reverse=True):
    print(f"   {region}: Tier {data['tier']} (Score: {data['score']}, Interest: {data['interest']})")
print()

# Generate sample ad copy
print("=" * 70)
print("📝 GENERATED AD COPY")
print("=" * 70)

ad_variants = [
    {
        'type': 'Short (Social)',
        'text': f"{movie['tagline']} 🎬 {movie['title']} - {movie['release_date'].split('-')[1]}/{movie['release_date'].split('-')[-1]}"
    },
    {
        'type': 'Medium (Display)',
        'text': f"The sands of Arrakis await. Experience the epic continuation of Paul Atreides' journey. {movie['title']} - Only in theaters {movie['release_date']}."
    },
    {
        'type': 'Long (Video Pre-roll)',
        'text': f"From visionary director {movie['director']}, witness the next chapter in the greatest sci-fi saga of our time. {', '.join(movie['cast'][:2])} return in {movie['title']}, an epic adventure of prophecy, revenge, and destiny. Experience it in IMAX - {movie['release_date']}."
    }
]

for variant in ad_variants:
    print(f"\n{variant['type']}:")
    print(f"  {variant['text']}")

# Social posts
print(f"\n{'=' * 70}")
print("📱 SOCIAL MEDIA POSTS")
print("=" * 70)

social_posts = {
    'Twitter/X': f"{movie['tagline']} 🏜️\n\n{movie['title']} arrives {movie['release_date']}\n\n#DunePartTwo #Dune",
    'Instagram': f"The journey continues. {movie['title']} 🎬\n\nStarring {', '.join(movie['cast'][:2])}\nDirected by {movie['director']}\n\nIn theaters {movie['release_date']} 🏜️\n\n#DunePartTwo #SciFi #Cinema",
    'Facebook': f"🎬 {movie['title']}\n\n{movie['tagline']}\n\nThe epic conclusion to Paul Atreides' journey arrives in theaters {movie['release_date']}. Get your tickets now!\n\n⭐ {engagement['positive_pct']}% positive audience reception\n🎥 Directed by {movie['director']}\n⏱️ {movie['runtime']} minutes of pure cinema",
    'TikTok': f"POV: You're about to experience the movie event of the year 🏜️✨\n\n{movie['title']} • {movie['release_date']} • In theaters\n\n#DunePartTwo #Movies #MustWatch"
}

for platform, post in social_posts.items():
    print(f"\n{platform}:")
    for line in post.split('\n'):
        print(f"  {line}")

# Campaign rollout
print(f"\n{'=' * 70}")
print("📅 CAMPAIGN ROLLOUT PLAN")
print("=" * 70)

phases = [
    {
        'name': 'Teaser Phase',
        'weeks': 'Week 1-2',
        'regions': ['US', 'UK'],
        'budget': '$500,000',
        'activities': ['Social media teasers', 'Influencer partnerships', 'First look reveals']
    },
    {
        'name': 'Awareness Phase',
        'weeks': 'Week 3-5',
        'regions': ['US', 'UK', 'IN'],
        'budget': '$1,200,000',
        'activities': ['TV spots', 'YouTube ads', 'Billboard campaigns', 'Press junket']
    },
    {
        'name': 'Conversion Phase',
        'weeks': 'Week 6-8',
        'regions': ['US', 'UK', 'IN', 'CA', 'AU'],
        'budget': '$800,000',
        'activities': ['Ticket pre-sales', 'Fan events', 'IMAX promotion', 'Countdown campaign']
    }
]

for phase in phases:
    print(f"\n{phase['name']} ({phase['weeks']}):")
    print(f"  Regions: {', '.join(phase['regions'])}")
    print(f"  Budget: {phase['budget']}")
    print(f"  Activities:")
    for activity in phase['activities']:
        print(f"    • {activity}")

total_budget = sum([int(p['budget'].replace('$', '').replace(',', '')) for p in phases])
print(f"\n💰 Total Campaign Budget: ${total_budget:,}")

# AI insights (if Gemini available)
print(f"\n{'=' * 70}")
print("🤖 AI STRATEGIC INSIGHTS")
print("=" * 70)

try:
    from src.utils.config import Config
    if Config.has_gemini():
        print("\n✅ Gemini AI Available - Generating insights...")
        from src.generators.gemini_enhancer import GeminiEnhancer
        
        enhancer = GeminiEnhancer()
        
        # Generate AI-enhanced ad copy
        print("\n📝 AI-Enhanced Ad Variants:")
        ai_ads = enhancer.enhance_ad_copy(
            {
                'title': movie['title'],
                'tagline': movie['tagline'],
                'overview': f"The epic continuation of Paul Atreides' journey on Arrakis",
                'release_date': movie['release_date'],
                'genres': [{'name': g} for g in movie['genres']],
                'cast': [{'name': c} for c in movie['cast'][:4]]
            },
            {'overall_sentiment': engagement['sentiment']},
            {'momentum': 'accelerating', 'trend': 'upward'}
        )
        
        for i, ad in enumerate(ai_ads[:3], 1):
            print(f"\n{i}. [{ad.get('length', 'medium')}] {ad['text']}")
        
        # Generate strategic insights
        print("\n💡 Campaign Strategy Analysis:")
        insights = enhancer.generate_campaign_insights({
            'movie': {
                'title': movie['title'],
                'release_date': movie['release_date'],
                'genres': [{'name': g} for g in movie['genres']]
            },
            'sentiment': {'overall_sentiment': engagement['sentiment']},
            'trends': {'momentum': 'accelerating'},
            'regional_scores': regions
        })
        
        print("\nOpportunities:")
        for opp in insights.get('opportunities', [])[:3]:
            print(f"  ✓ {opp}")
        
        print("\nRisks:")
        for risk in insights.get('risks', [])[:3]:
            print(f"  ⚠ {risk}")
        
        print("\nRecommendations:")
        for rec in insights.get('recommendations', [])[:3]:
            print(f"  → {rec}")
        
    else:
        print("\n⚪ Gemini AI not configured")
        print("   Add GEMINI_API_KEY to .env for AI-enhanced insights")
        print("   Get your free key at: https://aistudio.google.com/app/apikey")

except Exception as e:
    print(f"\n⚠️  AI insights unavailable: {str(e)[:100]}")

print(f"\n{'=' * 70}")
print("✅ Demo Complete!")
print(f"{'=' * 70}")

print("\n💡 Next Steps:")
print("   1. Fix network connectivity for TMDb/YouTube APIs")
print("   2. Or use this offline demo to understand the system")
print("   3. Check QUICKSTART.md for full setup instructions")
print()
