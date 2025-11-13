# Trailer-to-Campaign Autopilot 🎬

**Turn film/series trailer signals into grounded marketing campaigns—automatically.**

## Overview

This system analyzes public signals from movie/OTT trailers and generates:
- **Ad Copy** with source citations
- **Email & Social Posts** tailored to platforms
- **Thumbnail/Storyboard Concepts** with visual descriptions
- **Regional Rollout Plans** prioritized by engagement data

All outputs are **trace-linked to sources** (comments, trends, pageviews, metadata).

## Data Sources

| Source | Purpose | API/Library |
|--------|---------|-------------|
| **TMDb** | Movie metadata, cast, images | `requests` |
| **YouTube Data API** | Trailer comments, engagement | `google-api-python-client` |
| **Wikipedia Pageviews** | Daily attention spikes by region | `requests` |
| **Google Trends** | Topic/region interest over time | `pytrends` |
| **Open-Meteo** | Weather timing for outdoor promos | `requests` |

## Features

### 🔍 Signal Analysis
- Sentiment analysis of YouTube comments
- Wikipedia pageview trend detection
- Google Trends regional interest scoring
- Engagement metrics correlation

### 📝 Content Generation
- **Ad Copy**: Multiple variants (short, long, CTA-focused)
- **Social Posts**: Platform-optimized (Twitter, Instagram, Facebook)
- **Email Campaigns**: Subject lines + body templates
- **Thumbnail Concepts**: Visual descriptions with mood boards

### 🌍 Regional Intelligence
- Geographic prioritization based on interest scores
- Language/cultural considerations
- Release timing optimization
- Market-specific messaging suggestions

### 🔗 Source Tracing
Every generated asset includes:
- Source citations (comment IDs, trend data, metadata)
- Confidence scores
- Supporting evidence snippets

## Installation

```bash
# Clone or navigate to the project
cd t2a

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## Configuration

Create a `.env` file in the project root:

```env
# Required
TMDB_API_KEY=your_tmdb_key_here
YOUTUBE_API_KEY=your_youtube_key_here

# Optional (for advanced features)
OPENAI_API_KEY=your_openai_key_here  # For enhanced copy generation
```

### Getting API Keys

1. **TMDb**: Register at https://www.themoviedb.org/settings/api
2. **YouTube**: Create project at https://console.developers.google.com/
   - Enable YouTube Data API v3
   - Create credentials (API key)

## Quick Start

```bash
# Basic usage - analyze a trailer
python main.py --trailer-url "https://www.youtube.com/watch?v=TRAILER_ID" --movie-title "Dune Part Two"

# With TMDb ID
python main.py --tmdb-id 693134 --trailer-url "https://www.youtube.com/watch?v=Way9Dexny3w"

# Generate specific content types
python main.py --trailer-url "URL" --generate ad-copy,social-posts,rollout-plan

# Regional focus
python main.py --trailer-url "URL" --regions US,UK,IN,BR
```

## Project Structure

```
t2a/
├── src/
│   ├── collectors/          # Data collection modules
│   │   ├── tmdb_client.py
│   │   ├── youtube_client.py
│   │   ├── wikipedia_client.py
│   │   ├── trends_client.py
│   │   └── weather_client.py
│   ├── analyzers/           # Signal analysis
│   │   ├── sentiment_analyzer.py
│   │   ├── trend_detector.py
│   │   └── regional_scorer.py
│   ├── generators/          # Content generation
│   │   ├── ad_copy_generator.py
│   │   ├── social_post_generator.py
│   │   ├── email_generator.py
│   │   └── thumbnail_generator.py
│   ├── planners/            # Campaign planning
│   │   └── rollout_planner.py
│   └── utils/               # Helpers
│       ├── source_tracker.py
│       └── config.py
├── examples/                # Example outputs
├── tests/                   # Unit tests
├── main.py                  # CLI entry point
├── requirements.txt
└── README.md
```

## Example Output

```json
{
  "campaign_id": "dune-part-two-2024",
  "generated_at": "2024-03-15T10:30:00Z",
  "ad_copy": [
    {
      "variant": "short",
      "text": "The desert calls. #DunePartTwo - In theaters March 15",
      "sources": ["youtube_comment:xyz", "tmdb:tagline"],
      "confidence": 0.92
    }
  ],
  "rollout_plan": {
    "priority_regions": [
      {"region": "US", "score": 0.95, "reasoning": "High Google Trends + pageviews"},
      {"region": "UK", "score": 0.87, "reasoning": "Strong comment engagement"}
    ]
  }
}
```

## Use Cases

- **Marketing Teams**: Auto-generate campaign materials from trailer drops
- **Distribution**: Prioritize markets based on real-time interest
- **Social Media Managers**: Platform-optimized content with trending hooks
- **Agencies**: Rapid campaign prototyping with data backing

## Roadmap

- [ ] Multi-language support for international campaigns
- [ ] A/B testing variant generator
- [ ] TikTok/Shorts optimization
- [ ] Competitive analysis (compare similar films)
- [ ] Budget allocation suggestions
- [ ] Real-time dashboard

## License

MIT License - see LICENSE file

## Contributing

Contributions welcome! Please open an issue first to discuss major changes.

---

Built with publicly available APIs and transparent data sourcing. 🎥✨
