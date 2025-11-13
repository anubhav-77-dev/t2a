# Quick Start Guide

## Installation

```bash
# 1. Navigate to project
cd t2a

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set up API keys
cp .env.example .env
# Edit .env with your API keys
```

## Get API Keys

### TMDb (Required)
1. Go to https://www.themoviedb.org/settings/api
2. Register for an account
3. Request an API key (free)
4. Copy key to `.env` file

### YouTube Data API (Required)
1. Go to https://console.developers.google.com/
2. Create a new project
3. Enable "YouTube Data API v3"
4. Create credentials (API key)
5. Copy key to `.env` file

## Basic Usage

### Using CLI

```bash
# Generate campaign from trailer URL
python main.py generate \
  --trailer-url "https://www.youtube.com/watch?v=VIDEO_ID" \
  --movie-title "Movie Name" \
  --regions US,GB,CA,AU,IN

# With TMDb ID (recommended)
python main.py generate \
  --trailer-url "https://www.youtube.com/watch?v=VIDEO_ID" \
  --tmdb-id 12345 \
  --regions US,GB,FR,DE

# Check configuration
python main.py config-check

# View saved campaign
python main.py show outputs/campaign_file.json
```

### Using Python

```python
from src.autopilot import CampaignAutopilot

autopilot = CampaignAutopilot()

campaign = autopilot.run_full_campaign(
    trailer_url="https://www.youtube.com/watch?v=VIDEO_ID",
    movie_title="Your Movie Title",
    target_regions=['US', 'GB', 'IN']
)

# Save results
autopilot.save_campaign(campaign, "my_campaign.json")
```

## Running Examples

```bash
# Basic example
python examples/basic_usage.py

# Advanced component examples
python examples/advanced_usage.py
```

## Output Structure

Generated campaigns include:

- **Movie Data**: Metadata from TMDb
- **Trailer Analysis**: Views, engagement, comments
- **Sentiment Analysis**: Overall sentiment + distribution
- **Trend Analysis**: Google Trends + Wikipedia pageviews
- **Regional Analysis**: Scored and ranked markets
- **Ad Copy**: 5+ variants with source citations
- **Social Posts**: Twitter, Instagram, Facebook, TikTok
- **Rollout Plan**: Phased strategy with budget allocation

## Tips

1. **Use TMDb ID when possible** - More accurate than title search
2. **Limit regions initially** - Start with 5-10 to avoid API throttling
3. **Check API quotas** - YouTube API has daily limits
4. **Review generated content** - Always review before using in production

## Common Issues

**"Missing API keys"**
- Make sure `.env` file exists with correct keys
- Check key format (no quotes, no spaces)

**"Could not find movie"**
- Try using TMDb ID instead of title
- Check movie exists on TMDb

**"Rate limit exceeded"**
- YouTube API has daily quota (default 10,000 units)
- Reduce regions or wait 24 hours

**"Trends data unavailable"**
- Install pytrends: `pip install pytrends`
- Some movies may have low search volume

## Next Steps

- Customize templates in `src/generators/`
- Add new data sources in `src/collectors/`
- Modify scoring weights in `src/analyzers/`
- Integrate with your existing tools

## Support

For issues or questions:
1. Check the main README.md
2. Review example scripts
3. Check API documentation for each service
