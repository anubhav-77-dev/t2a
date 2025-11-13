"""Main orchestrator for Trailer-to-Campaign Autopilot."""

import json
from typing import Dict, List, Any, Optional
from datetime import datetime

from .collectors import TMDbClient, YouTubeClient, WikipediaClient, TrendsClient
from .analyzers import SentimentAnalyzer, TrendDetector, RegionalScorer
from .generators.ad_copy_generator import AdCopyGenerator
from .generators.social_post_generator import SocialPostGenerator
from .generators.gemini_enhancer import GeminiEnhancer
from .planners.rollout_planner import RolloutPlanner
from .utils.source_tracker import SourceTracker
from .utils.config import Config


class CampaignAutopilot:
    """Main orchestrator for generating trailer-based campaigns."""
    
    def __init__(self):
        # Initialize clients
        self.tmdb = TMDbClient()
        self.youtube = YouTubeClient()
        self.wikipedia = WikipediaClient()
        self.trends = TrendsClient()
        
        # Initialize analyzers
        self.sentiment_analyzer = SentimentAnalyzer()
        self.trend_detector = TrendDetector()
        self.regional_scorer = RegionalScorer()
        
        # Initialize generators
        self.source_tracker = SourceTracker()
        self.ad_copy_gen = AdCopyGenerator(self.source_tracker)
        self.social_gen = SocialPostGenerator(self.source_tracker)
        
        # Initialize AI enhancer (optional)
        self.gemini_enhancer = GeminiEnhancer() if Config.has_gemini() else None
        
        # Initialize planner
        self.rollout_planner = RolloutPlanner()
    
    def run_full_campaign(
        self,
        trailer_url: str,
        movie_title: Optional[str] = None,
        tmdb_id: Optional[int] = None,
        target_regions: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Run complete campaign generation pipeline.
        
        Args:
            trailer_url: YouTube trailer URL
            movie_title: Movie title (for TMDb search if no ID)
            tmdb_id: TMDb movie ID (if known)
            target_regions: List of region codes to analyze
        
        Returns:
            Complete campaign package with all generated assets
        """
        print("🎬 Trailer-to-Campaign Autopilot Starting...")
        print("=" * 60)
        
        campaign = {
            'generated_at': datetime.now().isoformat(),
            'input': {
                'trailer_url': trailer_url,
                'movie_title': movie_title,
                'tmdb_id': tmdb_id,
                'target_regions': target_regions or Config.DEFAULT_REGIONS
            }
        }
        
        # Step 1: Collect movie metadata
        print("\n📊 Step 1: Collecting Movie Metadata...")
        movie_data = self._collect_movie_data(tmdb_id, movie_title)
        campaign['movie_data'] = movie_data
        
        if not movie_data:
            return {'error': 'Could not find movie data'}
        
        print(f"   ✓ Found: {movie_data.get('title', 'Unknown')}")
        
        # Step 2: Analyze trailer engagement
        print("\n💬 Step 2: Analyzing Trailer Engagement...")
        trailer_analysis = self.youtube.analyze_trailer(trailer_url)
        campaign['trailer_analysis'] = trailer_analysis
        
        if 'error' not in trailer_analysis:
            stats = trailer_analysis['stats']
            print(f"   ✓ Views: {stats.get('view_count', 0):,}")
            print(f"   ✓ Engagement Rate: {trailer_analysis.get('engagement_rate', 0):.2f}%")
            print(f"   ✓ Comments Analyzed: {trailer_analysis.get('comment_sample_size', 0)}")
        
        # Step 3: Sentiment analysis
        print("\n🎭 Step 3: Analyzing Sentiment...")
        sentiment_results = self._analyze_sentiment(trailer_analysis)
        campaign['sentiment_analysis'] = sentiment_results
        
        print(f"   ✓ Overall Sentiment: {sentiment_results.get('overall_sentiment', 'unknown').upper()}")
        print(f"   ✓ Confidence: {sentiment_results.get('average_compound_score', 0):.2f}")
        
        # Step 4: Trend analysis (with graceful fallback)
        print("\n📈 Step 4: Detecting Trends...")
        try:
            trend_results = self._analyze_trends(movie_data, target_regions or Config.DEFAULT_REGIONS)
            campaign['trend_analysis'] = trend_results
            if trend_results.get('note') == 'Trend analysis unavailable':
                print("   ⚠️  Google Trends unavailable (rate limited or disabled)")
        except Exception as e:
            print(f"   ⚠️  Skipping trends: {str(e)[:50]}")
            trend_results = {'note': 'Trend analysis skipped due to rate limits'}
            campaign['trend_analysis'] = trend_results
        
        # Step 5: Regional scoring
        print("\n🌍 Step 5: Scoring Regional Markets...")
        regional_results = self._score_regions(movie_data, trend_results, target_regions or Config.DEFAULT_REGIONS)
        campaign['regional_analysis'] = regional_results
        
        if regional_results.get('ranked_regions'):
            top_3 = regional_results['ranked_regions'][:3]
            print(f"   ✓ Top Markets: {', '.join(r['region'] for r in top_3)}")
        
        # Step 6: Generate ad copy
        print("\n📝 Step 6: Generating Ad Copy...")
        ad_copy = self.ad_copy_gen.generate_with_sources(
            movie_data,
            sentiment_results,
            count=5
        )
        
        # Step 6b: AI-enhance with Gemini (if available)
        print(f"   🔍 DEBUG: self.gemini_enhancer = {self.gemini_enhancer}")
        if self.gemini_enhancer:
            print(f"   🔍 DEBUG: gemini_enhancer.is_available() = {self.gemini_enhancer.is_available()}")
            print(f"   🔍 DEBUG: gemini_enhancer.model = {self.gemini_enhancer.model}")
            print(f"   🔍 DEBUG: gemini_enhancer.api_key = {'YES' if self.gemini_enhancer.api_key else 'NO'}")
        else:
            print(f"   🔍 DEBUG: Gemini enhancer is None!")
            print(f"   🔍 DEBUG: Config.has_gemini() = {Config.has_gemini()}")
            print(f"   🔍 DEBUG: Config.GEMINI_API_KEY = {'YES' if Config.GEMINI_API_KEY else 'NO'}")
        
        if self.gemini_enhancer and self.gemini_enhancer.is_available():
            print("   🤖 Enhancing with Gemini AI...")
            try:
                ai_variants = self.gemini_enhancer.enhance_ad_copy(
                    movie_data,
                    sentiment_results
                )
                if ai_variants:
                    ad_copy['ai_enhanced_variants'] = ai_variants
                    print(f"   ✓ Generated {len(ai_variants)} AI-enhanced variants")
                else:
                    print(f"   ⚠️  AI enhancement returned no variants")
            except Exception as e:
                print(f"   ⚠️  AI enhancement failed: {e}")
                import traceback
                traceback.print_exc()
        else:
            print("   ⚠️  Skipping AI enhancement (not available)")
        
        campaign['ad_copy'] = ad_copy
        print(f"   ✓ Generated {len(ad_copy.get('variants', []))} base variants")
        
        # Step 7: Generate social posts
        print("\n📱 Step 7: Generating Social Media Posts...")
        social_posts = self.social_gen.generate_all_platforms(
            movie_data,
            sentiment_results
        )
        campaign['social_posts'] = social_posts
        print(f"   ✓ Created posts for {len([k for k in social_posts if k != 'generated_at'])} platforms")
        
        # Step 8: Create rollout plan
        print("\n🗓️  Step 8: Creating Rollout Plan...")
        rollout_plan = self._create_rollout_plan(
            regional_results,
            movie_data
        )
        campaign['rollout_plan'] = rollout_plan
        
        if rollout_plan.get('phases'):
            print(f"   ✓ {len(rollout_plan['phases'])} phases planned")
        
        # Step 9: Generate insights & recommendations
        print("\n💡 Step 9: Generating Insights...")
        insights = self._generate_insights(campaign)
        
        # Step 9b: AI-enhanced insights (if available)
        if self.gemini_enhancer and self.gemini_enhancer.is_available():
            print("   🤖 Generating AI strategic insights...")
            try:
                ai_insights = self.gemini_enhancer.generate_campaign_insights(campaign)
                if ai_insights:
                    insights['ai_strategic_analysis'] = ai_insights
                    print(f"   ✓ AI insights generated")
            except Exception as e:
                print(f"   ⚠️  AI insights failed: {e}")
        
        campaign['insights'] = insights
        
        print("\n" + "=" * 60)
        print("✅ Campaign Generation Complete!")
        
        return campaign
    
    def _collect_movie_data(
        self,
        tmdb_id: Optional[int],
        movie_title: Optional[str]
    ) -> Dict[str, Any]:
        """Collect movie metadata from TMDb."""
        if tmdb_id:
            return self.tmdb.extract_marketing_metadata(tmdb_id)
        elif movie_title:
            results = self.tmdb.search_movie(movie_title)
            if results:
                return self.tmdb.extract_marketing_metadata(results[0]['id'])
        return {}
    
    def _analyze_sentiment(
        self,
        trailer_analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Analyze sentiment from trailer comments."""
        comments = trailer_analysis.get('top_comments', [])
        
        if not comments:
            return {
                'overall_sentiment': 'neutral',
                'note': 'No comments available for analysis'
            }
        
        # Add comment sources to tracker
        for comment in comments[:50]:
            self.source_tracker.add_youtube_comment(
                comment.get('comment_id', ''),
                comment.get('text', ''),
                comment.get('like_count', 0),
                comment.get('author', '')
            )
        
        return self.sentiment_analyzer.analyze_comments(comments)
    
    def _analyze_trends(
        self,
        movie_data: Dict[str, Any],
        regions: List[str]
    ) -> Dict[str, Any]:
        """Analyze interest trends across regions."""
        movie_title = movie_data.get('title', '')
        
        if not movie_title or not self.trends.pytrends:
            return {'note': 'Trend analysis unavailable'}
        
        try:
            # Limit to 3 regions max to avoid rate limiting
            limited_regions = regions[:3]
            
            # Use shorter timeout for trends to fail fast if rate limited
            import signal
            
            def timeout_handler(signum, frame):
                raise TimeoutError("Trends request timed out")
            
            # Set 10 second timeout for entire trends analysis
            signal.signal(signal.SIGALRM, timeout_handler)
            signal.alarm(15)
            
            try:
                analysis = self.trends.analyze_movie_interest(
                    movie_title,
                    cast_names=movie_data.get('cast', [])[:2],
                    regions=limited_regions
                )
            finally:
                signal.alarm(0)  # Cancel alarm
            
            # Add trend sources to tracker
            if analysis.get('regional_interest', {}).get('regions'):
                for region_data in analysis['regional_interest']['regions'][:10]:
                    self.source_tracker.add_trend_data(
                        movie_title,
                        region_data['region'],
                        region_data['interest'],
                        'recent'
                    )
            
            return analysis
        except TimeoutError:
            print(f"   ⏭️  Trends timed out (rate limited), continuing without trends")
            return {'note': 'Trend analysis skipped - rate limited'}
        except Exception as e:
            # Silently skip trends on any error
            return {'note': f'Trend analysis unavailable'}
    
    def _score_regions(
        self,
        movie_data: Dict[str, Any],
        trend_results: Dict[str, Any],
        regions: List[str]
    ) -> Dict[str, Any]:
        """Score and rank target regions."""
        regional_data = {}
        
        # Extract data for each region
        for region in regions:
            region_info = {
                'interest_score': 50,  # Default
                'engagement_rate': 0.05,
                'growth_rate': 0.0,
                'sentiment_score': 0.7
            }
            
            # Get trend data if available
            region_details = trend_results.get('region_details', {}).get(region, {})
            if region_details:
                region_info['interest_score'] = region_details.get('avg', 50)
            
            regional_data[region] = region_info
        
        return self.regional_scorer.compare_regions(regional_data)
    
    def _create_rollout_plan(
        self,
        regional_results: Dict[str, Any],
        movie_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Create phased rollout plan."""
        # Prepare regional data for planner
        regional_data = {}
        for region in regional_results.get('ranked_regions', []):
            regional_data[region['region']] = {
                'interest_score': region.get('breakdown', {}).get('interest', 50),
                'engagement_rate': 0.05,
                'growth_rate': 0.1,
                'sentiment_score': 0.7
            }
        
        return self.rollout_planner.create_rollout_plan(
            regional_data,
            movie_data.get('release_date', '2024-12-31'),
            budget_total=1000000,
            campaign_weeks=6
        )
    
    def _generate_insights(self, campaign: Dict[str, Any]) -> Dict[str, Any]:
        """Generate high-level insights and recommendations."""
        insights = {
            'key_findings': [],
            'recommendations': [],
            'warnings': []
        }
        
        # Sentiment insights
        sentiment = campaign.get('sentiment_analysis', {})
        if sentiment.get('overall_sentiment') == 'positive':
            insights['key_findings'].append(
                f"Strong positive sentiment ({sentiment.get('sentiment_distribution', {}).get('positive', 0):.0f}%) - ideal for testimonial marketing"
            )
        elif sentiment.get('overall_sentiment') == 'negative':
            insights['warnings'].append("Mixed reception detected - consider addressing concerns")
        
        # Engagement insights
        trailer = campaign.get('trailer_analysis', {})
        engagement = trailer.get('engagement_rate', 0)
        if engagement > 5:
            insights['key_findings'].append(f"High engagement rate ({engagement:.1f}%) - strong organic interest")
        
        # Regional insights
        regional = campaign.get('regional_analysis', {})
        top_region = regional.get('ranked_regions', [{}])[0]
        if top_region:
            insights['recommendations'].append(
                f"Prioritize {top_region.get('region')} market - highest potential ROI"
            )
        
        return insights
    
    def save_campaign(self, campaign: Dict[str, Any], output_path: str):
        """Save campaign to JSON file."""
        with open(output_path, 'w') as f:
            json.dump(campaign, f, indent=2)
        print(f"\n💾 Campaign saved to: {output_path}")


# Example usage
if __name__ == "__main__":
    autopilot = CampaignAutopilot()
    
    # Example: Dune Part Two
    campaign = autopilot.run_full_campaign(
        trailer_url="https://www.youtube.com/watch?v=Way9Dexny3w",
        movie_title="Dune Part Two",
        target_regions=['US', 'GB', 'FR', 'DE', 'AU']
    )
    
    # Save results
    output_file = f"outputs/campaign_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    autopilot.save_campaign(campaign, output_file)
