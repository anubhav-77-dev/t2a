"""Command-line interface for Trailer-to-Campaign Autopilot."""

import click
import json
from pathlib import Path
from datetime import datetime

from src.autopilot import CampaignAutopilot
from src.utils.config import Config


@click.group()
@click.version_option(version='1.0.0')
def cli():
    """
    🎬 Trailer-to-Campaign Autopilot
    
    Transform movie trailers into data-driven marketing campaigns.
    """
    pass


@cli.command()
@click.option('--trailer-url', required=True, help='YouTube trailer URL')
@click.option('--movie-title', help='Movie title (for TMDb search)')
@click.option('--tmdb-id', type=int, help='TMDb movie ID')
@click.option('--regions', default='US,GB,CA,AU,IN', help='Comma-separated region codes')
@click.option('--output', '-o', help='Output JSON file path')
@click.option('--verbose', '-v', is_flag=True, help='Verbose output')
def generate(trailer_url, movie_title, tmdb_id, regions, output, verbose):
    """Generate a complete marketing campaign from a trailer."""
    
    # Validate config
    if not Config.validate():
        click.echo("❌ Configuration error. Please check your .env file.", err=True)
        return
    
    # Parse regions
    region_list = [r.strip() for r in regions.split(',')]
    
    # Initialize autopilot
    autopilot = CampaignAutopilot()
    
    try:
        # Run campaign generation
        campaign = autopilot.run_full_campaign(
            trailer_url=trailer_url,
            movie_title=movie_title,
            tmdb_id=tmdb_id,
            target_regions=region_list
        )
        
        # Check for errors
        if 'error' in campaign:
            click.echo(f"❌ Error: {campaign['error']}", err=True)
            return
        
        # Determine output path
        if not output:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            movie_name = campaign.get('movie_data', {}).get('title', 'campaign')
            safe_name = ''.join(c for c in movie_name if c.isalnum() or c in (' ', '-', '_')).strip()
            output = f"outputs/{safe_name}_{timestamp}.json"
        
        # Ensure output directory exists
        Path(output).parent.mkdir(parents=True, exist_ok=True)
        
        # Save campaign
        autopilot.save_campaign(campaign, output)
        
        # Print summary
        click.echo("\n" + "=" * 60)
        click.echo("📊 CAMPAIGN SUMMARY")
        click.echo("=" * 60)
        
        movie_data = campaign.get('movie_data', {})
        click.echo(f"\n🎬 Movie: {movie_data.get('title', 'Unknown')}")
        click.echo(f"   Genres: {', '.join(movie_data.get('genres', []))}")
        click.echo(f"   Cast: {', '.join(movie_data.get('cast', [])[:3])}")
        
        sentiment = campaign.get('sentiment_analysis', {})
        click.echo(f"\n💭 Sentiment: {sentiment.get('overall_sentiment', 'unknown').upper()}")
        
        regional = campaign.get('regional_analysis', {})
        top_regions = regional.get('ranked_regions', [])[:3]
        if top_regions:
            click.echo(f"\n🌍 Top Markets:")
            for i, region in enumerate(top_regions, 1):
                click.echo(f"   {i}. {region['region']} (Score: {region['total_score']}/100)")
        
        ad_variants = campaign.get('ad_copy', {}).get('variants', [])
        click.echo(f"\n📝 Generated Assets:")
        click.echo(f"   • {len(ad_variants)} ad copy variants")
        
        social = campaign.get('social_posts', {})
        social_platforms = [k for k in social.keys() if k != 'generated_at']
        click.echo(f"   • {len(social_platforms)} social media posts")
        
        rollout = campaign.get('rollout_plan', {})
        if rollout.get('phases'):
            click.echo(f"   • {len(rollout['phases'])}-phase rollout plan")
        
        click.echo(f"\n✅ Full campaign saved to: {output}")
        click.echo("=" * 60)
        
    except Exception as e:
        click.echo(f"❌ Error: {str(e)}", err=True)
        if verbose:
            import traceback
            traceback.print_exc()


@cli.command()
@click.argument('campaign_file', type=click.Path(exists=True))
@click.option('--format', type=click.Choice(['summary', 'ad-copy', 'social', 'rollout']), 
              default='summary', help='Output format')
def show(campaign_file, format):
    """Display campaign details from a saved JSON file."""
    
    with open(campaign_file, 'r') as f:
        campaign = json.load(f)
    
    if format == 'summary':
        _show_summary(campaign)
    elif format == 'ad-copy':
        _show_ad_copy(campaign)
    elif format == 'social':
        _show_social(campaign)
    elif format == 'rollout':
        _show_rollout(campaign)


def _show_summary(campaign: dict):
    """Show campaign summary."""
    click.echo("\n🎬 Campaign Summary\n")
    
    movie = campaign.get('movie_data', {})
    click.echo(f"Movie: {movie.get('title', 'Unknown')}")
    click.echo(f"Release: {movie.get('release_date', 'Unknown')}")
    
    sentiment = campaign.get('sentiment_analysis', {})
    click.echo(f"\nSentiment: {sentiment.get('overall_sentiment', 'unknown').upper()}")
    
    dist = sentiment.get('sentiment_distribution', {})
    for sent, pct in dist.items():
        click.echo(f"  {sent}: {pct:.1f}%")


def _show_ad_copy(campaign: dict):
    """Show generated ad copy."""
    click.echo("\n📝 Ad Copy Variants\n")
    
    variants = campaign.get('ad_copy', {}).get('variants', [])
    for variant in variants:
        click.echo(f"[{variant['variant'].upper()}] ({variant['character_count']} chars)")
        click.echo(f"{variant['text']}")
        click.echo(f"Platform: {variant['platform']}\n")


def _show_social(campaign: dict):
    """Show social media posts."""
    click.echo("\n📱 Social Media Posts\n")
    
    social = campaign.get('social_posts', {})
    for platform, post in social.items():
        if platform != 'generated_at' and isinstance(post, dict):
            click.echo(f"=== {post.get('platform', platform).upper()} ===")
            click.echo(f"{post.get('text', '')}\n")


def _show_rollout(campaign: dict):
    """Show rollout plan."""
    click.echo("\n🗓️  Rollout Plan\n")
    
    rollout = campaign.get('rollout_plan', {})
    overview = rollout.get('campaign_overview', {})
    
    click.echo(f"Release: {overview.get('release_date')}")
    click.echo(f"Campaign Start: {overview.get('campaign_start')}")
    click.echo(f"Budget: ${overview.get('total_budget', 0):,.0f}\n")
    
    click.echo("Phases:")
    for phase in rollout.get('phases', []):
        click.echo(f"\nPhase {phase['phase']}: {phase['name']}")
        click.echo(f"  Start: {phase['start_date']}")
        click.echo(f"  Regions: {', '.join(phase['regions'])}")
        click.echo(f"  Budget: {phase['budget_percentage']}%")


@cli.command()
def config_check():
    """Check configuration and API keys."""
    click.echo("\n🔧 Configuration Check\n")
    
    click.echo(f"TMDb API Key: {'✓ Set' if Config.TMDB_API_KEY else '✗ Missing'}")
    click.echo(f"YouTube API Key: {'✓ Set' if Config.YOUTUBE_API_KEY else '✗ Missing'}")
    click.echo(f"Gemini API Key: {'✓ Set' if Config.GEMINI_API_KEY else '✗ Not set (optional)'}")
    click.echo(f"OpenAI API Key: {'✓ Set' if Config.OPENAI_API_KEY else '✗ Not set (optional)'}")
    
    if Config.has_gemini():
        click.echo("\n✨ AI Enhancement: Enabled (Gemini)")
    elif Config.has_openai():
        click.echo("\n✨ AI Enhancement: Enabled (OpenAI)")
    else:
        click.echo("\n⚪ AI Enhancement: Disabled (optional)")
    
    click.echo(f"\nDefault Regions: {', '.join(Config.DEFAULT_REGIONS)}")
    click.echo(f"Max Comments: {Config.MAX_COMMENTS_ANALYZE}")
    
    if Config.validate():
        click.echo("\n✅ Configuration is valid!")
    else:
        click.echo("\n⚠️  Some required API keys are missing.")
        click.echo("Please update your .env file. See .env.example for reference.")


if __name__ == '__main__':
    cli()
