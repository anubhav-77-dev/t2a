"""Regional interest scoring and market prioritization."""

from typing import Dict, List, Any, Optional
from collections import defaultdict


class RegionalScorer:
    """Score and prioritize geographic regions for campaign rollout."""
    
    # Market size estimates (in millions)
    POPULATION_DATA = {
        'US': 331, 'CN': 1411, 'IN': 1380, 'ID': 273, 'PK': 220,
        'BR': 212, 'NG': 206, 'BD': 164, 'RU': 146, 'MX': 128,
        'JP': 126, 'ET': 115, 'PH': 109, 'EG': 102, 'VN': 97,
        'CD': 89, 'TR': 84, 'IR': 83, 'DE': 83, 'TH': 70,
        'GB': 68, 'FR': 65, 'IT': 60, 'ZA': 59, 'TZ': 59,
        'MM': 54, 'KR': 52, 'CO': 51, 'ES': 47, 'KE': 53,
        'AR': 45, 'UA': 44, 'DZ': 43, 'SD': 43, 'UG': 46,
        'CA': 38, 'PL': 38, 'MA': 37, 'SA': 35, 'AU': 26,
        'NL': 17, 'BE': 12, 'SE': 10, 'CH': 9, 'AT': 9
    }
    
    # Box office market tiers (approximate % of global box office)
    BOX_OFFICE_TIERS = {
        'Tier 1': ['US', 'CN'],  # ~60% combined
        'Tier 2': ['GB', 'JP', 'KR', 'FR', 'DE', 'AU'],  # ~20%
        'Tier 3': ['IN', 'BR', 'MX', 'IT', 'ES', 'RU', 'CA'],  # ~10%
        'Emerging': ['ID', 'TR', 'SA', 'TH', 'PH', 'VN']
    }
    
    # Language markets
    LANGUAGE_REGIONS = {
        'English': ['US', 'GB', 'CA', 'AU', 'NZ', 'IE'],
        'Spanish': ['ES', 'MX', 'AR', 'CO', 'CL', 'PE'],
        'French': ['FR', 'CA', 'BE', 'CH', 'MA', 'DZ'],
        'German': ['DE', 'AT', 'CH'],
        'Portuguese': ['BR', 'PT'],
        'Mandarin': ['CN', 'TW', 'SG'],
        'Hindi': ['IN'],
        'Japanese': ['JP'],
        'Korean': ['KR'],
        'Arabic': ['SA', 'EG', 'AE', 'MA', 'DZ']
    }
    
    def __init__(self):
        pass
    
    def score_region(
        self,
        region_code: str,
        interest_score: float = 50,
        engagement_rate: float = 0.0,
        growth_rate: float = 0.0,
        sentiment_score: float = 0.5,
        custom_factors: Optional[Dict[str, float]] = None
    ) -> Dict[str, Any]:
        """
        Calculate comprehensive score for a region.
        
        Args:
            region_code: ISO country code (e.g., 'US', 'GB')
            interest_score: Google Trends/Wikipedia interest (0-100)
            engagement_rate: Social engagement rate (0-1)
            growth_rate: Interest growth rate (-1 to 1+)
            sentiment_score: Sentiment score (0-1)
            custom_factors: Additional scoring factors
        """
        score = 0
        breakdown = {}
        
        # Interest level (0-30 points)
        interest_points = (interest_score / 100) * 30
        score += interest_points
        breakdown['interest'] = round(interest_points, 2)
        
        # Market size (0-20 points)
        population = self.POPULATION_DATA.get(region_code, 10)
        if population > 200:
            size_points = 20
        elif population > 100:
            size_points = 18
        elif population > 50:
            size_points = 15
        elif population > 20:
            size_points = 12
        else:
            size_points = 8
        
        # Boost for tier 1/2 markets
        tier = self._get_market_tier(region_code)
        if tier == 'Tier 1':
            size_points *= 1.2
        elif tier == 'Tier 2':
            size_points *= 1.1
        
        score += size_points
        breakdown['market_size'] = round(size_points, 2)
        
        # Engagement quality (0-15 points)
        engagement_points = engagement_rate * 15
        score += engagement_points
        breakdown['engagement'] = round(engagement_points, 2)
        
        # Growth momentum (0-20 points)
        if growth_rate > 0.3:
            growth_points = 20
        elif growth_rate > 0.15:
            growth_points = 15
        elif growth_rate > 0.05:
            growth_points = 10
        elif growth_rate > 0:
            growth_points = 5
        else:
            growth_points = 0
        score += growth_points
        breakdown['growth'] = growth_points
        
        # Sentiment (0-15 points)
        sentiment_points = sentiment_score * 15
        score += sentiment_points
        breakdown['sentiment'] = round(sentiment_points, 2)
        
        # Custom factors
        if custom_factors:
            custom_total = sum(custom_factors.values())
            score += custom_total
            breakdown['custom'] = round(custom_total, 2)
        
        # Normalize to 0-100
        max_possible = 100 + (sum(custom_factors.values()) if custom_factors else 0)
        normalized_score = (score / max_possible) * 100
        
        return {
            'region': region_code,
            'total_score': round(normalized_score, 2),
            'raw_score': round(score, 2),
            'breakdown': breakdown,
            'tier': self._get_tier_from_score(normalized_score),
            'market_tier': tier,
            'population_millions': population,
            'recommendation': self._generate_region_recommendation(
                normalized_score, tier, growth_rate
            )
        }
    
    def _get_market_tier(self, region_code: str) -> str:
        """Get box office market tier for region."""
        for tier, regions in self.BOX_OFFICE_TIERS.items():
            if region_code in regions:
                return tier
        return 'Other'
    
    def _get_tier_from_score(self, score: float) -> str:
        """Convert score to priority tier."""
        if score >= 80:
            return 'A'
        elif score >= 65:
            return 'B'
        elif score >= 50:
            return 'C'
        else:
            return 'D'
    
    def _generate_region_recommendation(
        self,
        score: float,
        market_tier: str,
        growth_rate: float
    ) -> str:
        """Generate campaign recommendation for region."""
        if score >= 80:
            return f"🎯 Primary target - allocate 25-35% of budget"
        elif score >= 65 and market_tier in ['Tier 1', 'Tier 2']:
            return f"✅ Secondary target - allocate 10-20% of budget"
        elif growth_rate > 0.2:
            return f"📈 Emerging opportunity - test with 5-10% budget"
        elif score >= 50:
            return f"🔄 Standard rollout - organic + targeted ads"
        else:
            return f"⏳ Lower priority - consider later phase"
    
    def compare_regions(
        self,
        regional_data: Dict[str, Dict[str, float]]
    ) -> Dict[str, Any]:
        """
        Compare and rank multiple regions.
        
        Args:
            regional_data: Dict of {region_code: {metrics}}
        """
        scored_regions = []
        
        for region_code, metrics in regional_data.items():
            score_result = self.score_region(
                region_code,
                interest_score=metrics.get('interest_score', 50),
                engagement_rate=metrics.get('engagement_rate', 0),
                growth_rate=metrics.get('growth_rate', 0),
                sentiment_score=metrics.get('sentiment_score', 0.5)
            )
            scored_regions.append(score_result)
        
        # Sort by score
        scored_regions.sort(key=lambda x: x['total_score'], reverse=True)
        
        # Group by tier
        by_tier = defaultdict(list)
        for region in scored_regions:
            by_tier[region['tier']].append(region)
        
        # Calculate budget allocation suggestions
        total_score = sum(r['total_score'] for r in scored_regions)
        for region in scored_regions:
            region['suggested_budget_pct'] = round(
                (region['total_score'] / total_score * 100) if total_score > 0 else 0,
                1
            )
        
        return {
            'ranked_regions': scored_regions,
            'by_tier': dict(by_tier),
            'top_5': scored_regions[:5],
            'total_regions': len(scored_regions),
            'recommendations': self._generate_rollout_strategy(scored_regions)
        }
    
    def _generate_rollout_strategy(
        self,
        scored_regions: List[Dict[str, Any]]
    ) -> List[str]:
        """Generate strategic rollout recommendations."""
        recs = []
        
        if not scored_regions:
            return recs
        
        # Identify clear leaders
        tier_a = [r for r in scored_regions if r['tier'] == 'A']
        if tier_a:
            regions_str = ', '.join(r['region'] for r in tier_a[:3])
            recs.append(f"Phase 1 (Week 1-2): Focus on {regions_str}")
        
        # Secondary markets
        tier_b = [r for r in scored_regions if r['tier'] == 'B']
        if tier_b:
            recs.append(f"Phase 2 (Week 3-4): Expand to {len(tier_b)} secondary markets")
        
        # Growth markets
        growth_markets = [r for r in scored_regions if r['breakdown'].get('growth', 0) > 15]
        if growth_markets:
            recs.append(f"Monitor high-growth markets: {', '.join(r['region'] for r in growth_markets[:3])}")
        
        # Language grouping
        recs.append(self._language_grouping_recommendation(scored_regions))
        
        return recs
    
    def _language_grouping_recommendation(
        self,
        scored_regions: List[Dict[str, Any]]
    ) -> str:
        """Suggest language-based grouping strategy."""
        region_codes = [r['region'] for r in scored_regions]
        
        language_coverage = {}
        for language, regions in self.LANGUAGE_REGIONS.items():
            coverage = [r for r in regions if r in region_codes]
            if coverage:
                language_coverage[language] = len(coverage)
        
        if language_coverage:
            top_lang = max(language_coverage, key=language_coverage.get)
            return f"🌍 Localization priority: {top_lang} ({language_coverage[top_lang]} markets)"
        return "Consider multi-language approach"
    
    def suggest_test_markets(
        self,
        all_regions: List[str],
        budget_constraint: str = 'medium'
    ) -> List[Dict[str, Any]]:
        """
        Suggest optimal test markets before full rollout.
        
        Args:
            all_regions: List of region codes to consider
            budget_constraint: 'low', 'medium', or 'high'
        """
        test_count = {
            'low': 2,
            'medium': 3,
            'high': 5
        }.get(budget_constraint, 3)
        
        # Prioritize diverse, representative markets
        test_markets = []
        
        # Always include US if available (largest market)
        if 'US' in all_regions:
            test_markets.append({
                'region': 'US',
                'rationale': 'Largest English-speaking market, bellwether'
            })
        
        # Add one major international market
        tier_1_2 = [r for r in all_regions if r in 
                    self.BOX_OFFICE_TIERS['Tier 1'] + self.BOX_OFFICE_TIERS['Tier 2']]
        if tier_1_2 and len(test_markets) < test_count:
            test_markets.append({
                'region': tier_1_2[0],
                'rationale': 'Major international market for comparison'
            })
        
        # Add emerging market if budget allows
        emerging = [r for r in all_regions if r in self.BOX_OFFICE_TIERS['Emerging']]
        if emerging and len(test_markets) < test_count:
            test_markets.append({
                'region': emerging[0],
                'rationale': 'Test emerging market potential'
            })
        
        return test_markets[:test_count]


# Example usage
if __name__ == "__main__":
    scorer = RegionalScorer()
    
    # Example: Score multiple regions
    regional_data = {
        'US': {'interest_score': 95, 'engagement_rate': 0.08, 'growth_rate': 0.12, 'sentiment_score': 0.85},
        'GB': {'interest_score': 87, 'engagement_rate': 0.09, 'growth_rate': 0.15, 'sentiment_score': 0.82},
        'IN': {'interest_score': 72, 'engagement_rate': 0.12, 'growth_rate': 0.35, 'sentiment_score': 0.78},
        'BR': {'interest_score': 65, 'engagement_rate': 0.07, 'growth_rate': 0.08, 'sentiment_score': 0.75},
        'AU': {'interest_score': 80, 'engagement_rate': 0.06, 'growth_rate': 0.10, 'sentiment_score': 0.80},
    }
    
    comparison = scorer.compare_regions(regional_data)
    
    print("🌍 Regional Priority Ranking:")
    for i, region in enumerate(comparison['top_5'], 1):
        print(f"{i}. {region['region']} - Score: {region['total_score']}/100 (Tier {region['tier']})")
        print(f"   Budget: {region['suggested_budget_pct']}% | {region['recommendation']}")
    
    print(f"\n📋 Rollout Strategy:")
    for rec in comparison['recommendations']:
        print(f"  - {rec}")
