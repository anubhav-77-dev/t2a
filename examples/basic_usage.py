"""Example: Basic campaign generation for a movie trailer."""

from src.autopilot import CampaignAutopilot
from datetime import datetime
import json

def main():
    """Run a basic campaign generation example."""
    
    print("=" * 70)
    print(" EXAMPLE: Generating Campaign for a Movie Trailer")
    print("=" * 70)
    
    # Initialize the autopilot
    autopilot = CampaignAutopilot()
    
    # Example 1: Using TMDb ID (most accurate)
    print("\n📍 Example 1: Using TMDb ID")
    print("-" * 70)
    
    campaign = autopilot.run_full_campaign(
        trailer_url="https://www.youtube.com/watch?v=U2Qp5pL3ovA",  # Example trailer
        tmdb_id=693134,  # Dune: Part Two
        target_regions=['US', 'GB', 'FR', 'DE', 'AU', 'BR', 'IN']
    )
    
    # Display some results
    if 'error' not in campaign:
        print("\n✅ Campaign Generated Successfully!")
        
        # Movie info
        movie = campaign.get('movie_data', {})
        print(f"\n🎬 Movie: {movie.get('title')}")
        print(f"   Tagline: {movie.get('tagline')}")
        print(f"   Genres: {', '.join(movie.get('genres', []))}")
        
        # Sentiment
        sentiment = campaign.get('sentiment_analysis', {})
        print(f"\n💭 Sentiment Analysis:")
        print(f"   Overall: {sentiment.get('overall_sentiment', 'unknown').upper()}")
        dist = sentiment.get('sentiment_distribution', {})
        for sent, pct in dist.items():
            print(f"   {sent.capitalize()}: {pct:.1f}%")
        
        # Top ad copy
        ad_copy = campaign.get('ad_copy', {}).get('variants', [])
        if ad_copy:
            print(f"\n📝 Sample Ad Copy (1 of {len(ad_copy)}):")
            print(f"   {ad_copy[0]['text']}")
        
        # Top markets
        regional = campaign.get('regional_analysis', {})
        top_markets = regional.get('ranked_regions', [])[:5]
        print(f"\n🌍 Top 5 Target Markets:")
        for i, market in enumerate(top_markets, 1):
            print(f"   {i}. {market['region']} - Score: {market['total_score']}/100 (Tier {market['tier']})")
        
        # Save to file
        output_file = f"examples/output/example_campaign_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        autopilot.save_campaign(campaign, output_file)
    
    # Example 2: Using movie title (search-based)
    print("\n\n📍 Example 2: Using Movie Title Search")
    print("-" * 70)
    
    campaign2 = autopilot.run_full_campaign(
        trailer_url="https://www.youtube.com/watch?v=qEVUtrk8_B4",  # Example trailer
        movie_title="Oppenheimer",
        target_regions=['US', 'GB', 'JP', 'IN']
    )
    
    if 'error' not in campaign2:
        print("\n✅ Second Campaign Generated!")
        movie2 = campaign2.get('movie_data', {})
        print(f"   Movie: {movie2.get('title')}")
        
        # Save
        output_file2 = f"examples/output/example_campaign_2_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        autopilot.save_campaign(campaign2, output_file2)
    
    print("\n" + "=" * 70)
    print("✅ Examples Complete! Check the outputs/ folder for full JSON files.")
    print("=" * 70)


if __name__ == "__main__":
    main()
