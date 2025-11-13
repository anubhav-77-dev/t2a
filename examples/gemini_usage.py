"""Example: Using Gemini AI for enhanced content generation."""

from src.autopilot import CampaignAutopilot
from src.generators.gemini_enhancer import GeminiEnhancer
from src.utils.config import Config
from datetime import datetime

def example_gemini_enhanced_campaign():
    """Generate a campaign with Gemini AI enhancement."""
    
    print("=" * 70)
    print(" EXAMPLE: Gemini AI-Enhanced Campaign Generation")
    print("=" * 70)
    
    # Check if Gemini is configured
    if not Config.has_gemini():
        print("\n⚠️  Gemini API key not configured!")
        print("Add your Gemini API key to .env file:")
        print("GEMINI_API_KEY=your_key_here")
        print("\nGet your key at: https://aistudio.google.com/app/apikey")
        return
    
    # Initialize autopilot (will auto-detect Gemini)
    autopilot = CampaignAutopilot()
    
    print("\n✅ Gemini AI detected and initialized!")
    print("   AI-enhanced content will be generated automatically\n")
    
    # Generate campaign (Gemini will be used automatically)
    campaign = autopilot.run_full_campaign(
        trailer_url="https://www.youtube.com/watch?v=U2Qp5pL3ovA",
        tmdb_id=693134,  # Dune: Part Two
        target_regions=['US', 'GB', 'FR', 'DE', 'IN']
    )
    
    if 'error' not in campaign:
        print("\n" + "=" * 70)
        print(" AI-ENHANCED RESULTS")
        print("=" * 70)
        
        # Show AI-enhanced ad copy
        ad_copy = campaign.get('ad_copy', {})
        ai_variants = ad_copy.get('ai_enhanced_variants', [])
        
        if ai_variants:
            print(f"\n🤖 AI-Generated Ad Copy ({len(ai_variants)} variants):\n")
            for i, variant in enumerate(ai_variants[:3], 1):
                print(f"{i}. [{variant.get('variant', 'unknown').upper()}]")
                print(f"   {variant.get('text', '')}")
                print(f"   Platform: {variant.get('platform', 'Unknown')}")
                print()
        
        # Show AI strategic insights
        insights = campaign.get('insights', {})
        ai_analysis = insights.get('ai_strategic_analysis', {})
        
        if ai_analysis:
            print("\n🎯 AI Strategic Analysis:\n")
            
            if 'opportunities' in ai_analysis:
                print("💡 Key Opportunities:")
                for opp in ai_analysis['opportunities']:
                    print(f"   • {opp}")
            
            if 'risks' in ai_analysis:
                print("\n⚠️  Risk Factors:")
                for risk in ai_analysis['risks']:
                    print(f"   • {risk}")
            
            if 'recommendations' in ai_analysis:
                print("\n✅ Strategic Recommendations:")
                for rec in ai_analysis['recommendations']:
                    print(f"   • {rec}")
            
            if 'budget_advice' in ai_analysis:
                print(f"\n💰 Budget Allocation Advice:")
                print(f"   {ai_analysis['budget_advice']}")
        
        # Save
        output_file = f"outputs/gemini_enhanced_campaign_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        autopilot.save_campaign(campaign, output_file)
        
        print("\n" + "=" * 70)
        print("✅ AI-Enhanced Campaign Complete!")
        print("=" * 70)


def example_gemini_standalone():
    """Use Gemini enhancer standalone."""
    
    print("\n" + "=" * 70)
    print(" EXAMPLE: Standalone Gemini Usage")
    print("=" * 70)
    
    enhancer = GeminiEnhancer()
    
    if not enhancer.is_available():
        print("\n⚠️  Gemini not available. Check API key in .env file.")
        return
    
    # Sample movie data
    movie_data = {
        'title': 'Dune: Part Two',
        'tagline': 'Long live the fighters',
        'overview': 'Follow the mythic journey of Paul Atreides as he unites with Chani and the Fremen.',
        'genres': ['Science Fiction', 'Adventure'],
        'cast': ['Timothée Chalamet', 'Zendaya', 'Rebecca Ferguson'],
        'directors': ['Denis Villeneuve']
    }
    
    sentiment_data = {
        'overall_sentiment': 'positive',
        'sentiment_distribution': {'positive': 82.5, 'neutral': 12.8, 'negative': 4.7}
    }
    
    print("\n🤖 Generating AI ad copy...")
    variants = enhancer.enhance_ad_copy(movie_data, sentiment_data)
    
    if variants:
        print(f"\n✅ Generated {len(variants)} AI variants:\n")
        for variant in variants:
            print(f"[{variant.get('variant', 'unknown').upper()}] ({variant.get('character_count')} chars)")
            print(f"{variant.get('text', '')}")
            print(f"Platform: {variant.get('platform', 'Unknown')}\n")
    
    print("\n🤖 Generating Instagram post...")
    instagram_post = enhancer.enhance_social_post(movie_data, 'instagram', sentiment_data)
    
    if instagram_post:
        print(f"\n📸 AI-Generated Instagram Post:\n")
        print(instagram_post)
    
    print("\n" + "=" * 70)


def compare_ai_vs_template():
    """Compare AI-generated vs template-based content."""
    
    print("\n" + "=" * 70)
    print(" COMPARISON: AI vs Template-Based Content")
    print("=" * 70)
    
    from src.generators.ad_copy_generator import AdCopyGenerator
    
    movie_data = {
        'movie_id': 693134,
        'title': 'Dune: Part Two',
        'tagline': 'Long live the fighters',
        'overview': 'Follow the mythic journey of Paul Atreides.',
        'genres': ['Science Fiction', 'Adventure'],
        'cast': ['Timothée Chalamet', 'Zendaya'],
        'directors': ['Denis Villeneuve'],
        'release_date': '2024-03-01'
    }
    
    sentiment_data = {
        'overall_sentiment': 'positive',
        'sentiment_distribution': {'positive': 85}
    }
    
    # Template-based
    print("\n📋 Template-Based Ad Copy:")
    template_gen = AdCopyGenerator()
    template_result = template_gen.generate_with_sources(movie_data, sentiment_data, count=2)
    for v in template_result['variants'][:2]:
        print(f"   • {v['text']}")
    
    # AI-based
    print("\n🤖 AI-Enhanced Ad Copy:")
    enhancer = GeminiEnhancer()
    if enhancer.is_available():
        ai_variants = enhancer.enhance_ad_copy(movie_data, sentiment_data)
        for v in ai_variants[:2]:
            print(f"   • {v.get('text', '')}")
    else:
        print("   ⚠️  Gemini not available")
    
    print("\n💡 AI Advantages:")
    print("   • More creative and varied phrasing")
    print("   • Better understanding of context")
    print("   • Adapts to sentiment dynamically")
    print("   • Can follow complex instructions")
    
    print("\n" + "=" * 70)


if __name__ == "__main__":
    # Check configuration
    if Config.has_gemini():
        print("\n✅ Gemini API configured!")
        print("Running AI-enhanced examples...\n")
        
        # Run examples
        example_gemini_standalone()
        example_gemini_enhanced_campaign()
        compare_ai_vs_template()
    else:
        print("\n⚠️  Gemini API not configured")
        print("\nTo use Gemini AI features:")
        print("1. Get your API key: https://aistudio.google.com/app/apikey")
        print("2. Add to .env file: GEMINI_API_KEY=your_key_here")
        print("3. Install: pip install google-generativeai")
        print("\nRunning without AI enhancement for now...\n")
        
        # Show what would work with Gemini
        print("=" * 70)
        print(" What Gemini AI Would Enable:")
        print("=" * 70)
        print("\n✨ AI-Enhanced Features:")
        print("   • Creative, varied ad copy generation")
        print("   • Platform-optimized social posts")
        print("   • Strategic campaign insights")
        print("   • Sentiment-aware messaging")
        print("   • Competitive positioning advice")
        print("   • Budget allocation reasoning")
        print("\n" + "=" * 70)
