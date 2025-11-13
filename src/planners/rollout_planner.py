"""Regional rollout campaign planner."""

from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from collections import defaultdict

from ..analyzers.regional_scorer import RegionalScorer


class RolloutPlanner:
    """Plan geographic and temporal campaign rollout strategy."""
    
    def __init__(self):
        self.scorer = RegionalScorer()
    
    def create_rollout_plan(
        self,
        regional_data: Dict[str, Dict[str, Any]],
        release_date: str,
        budget_total: float = 1000000,
        campaign_weeks: int = 6
    ) -> Dict[str, Any]:
        """
        Create comprehensive regional rollout plan.
        
        Args:
            regional_data: Dict of {region_code: {metrics}}
            release_date: Movie release date (YYYY-MM-DD)
            budget_total: Total campaign budget
            campaign_weeks: Weeks before release to start campaign
        """
        # Score and rank regions
        comparison = self.scorer.compare_regions(regional_data)
        ranked_regions = comparison['ranked_regions']
        
        # Parse release date
        try:
            release_dt = datetime.strptime(release_date, '%Y-%m-%d')
        except:
            release_dt = datetime.now() + timedelta(days=60)
        
        campaign_start = release_dt - timedelta(weeks=campaign_weeks)
        
        # Create phased rollout
        phases = self._create_phases(ranked_regions, campaign_start, release_dt)
        
        # Allocate budget
        budget_allocation = self._allocate_budget(ranked_regions, budget_total)
        
        # Create timeline
        timeline = self._create_timeline(phases, campaign_start, release_dt)
        
        # Channel recommendations
        channels = self._recommend_channels(ranked_regions)
        
        return {
            'campaign_overview': {
                'release_date': release_date,
                'campaign_start': campaign_start.strftime('%Y-%m-%d'),
                'duration_weeks': campaign_weeks,
                'total_budget': budget_total,
                'target_regions': len(ranked_regions)
            },
            'phases': phases,
            'budget_allocation': budget_allocation,
            'timeline': timeline,
            'channel_strategy': channels,
            'key_milestones': self._generate_milestones(campaign_start, release_dt),
            'recommendations': comparison['recommendations']
        }
    
    def _create_phases(
        self,
        ranked_regions: List[Dict[str, Any]],
        start_date: datetime,
        release_date: datetime
    ) -> List[Dict[str, Any]]:
        """Create phased rollout schedule."""
        # Group regions by tier
        tier_a = [r for r in ranked_regions if r['tier'] == 'A']
        tier_b = [r for r in ranked_regions if r['tier'] == 'B']
        tier_c = [r for r in ranked_regions if r['tier'] == 'C']
        
        phases = []
        
        # Phase 1: Tier A (Primary markets) - Start immediately
        if tier_a:
            phases.append({
                'phase': 1,
                'name': 'Primary Markets Launch',
                'start_date': start_date.strftime('%Y-%m-%d'),
                'duration_weeks': (release_date - start_date).days // 7,
                'regions': [r['region'] for r in tier_a],
                'intensity': 'High',
                'focus': 'Brand awareness, trailer push, early ticket sales',
                'budget_percentage': 50
            })
        
        # Phase 2: Tier B - Week 2-3
        if tier_b:
            phase2_start = start_date + timedelta(weeks=2)
            phases.append({
                'phase': 2,
                'name': 'Secondary Markets Expansion',
                'start_date': phase2_start.strftime('%Y-%m-%d'),
                'duration_weeks': max(1, (release_date - phase2_start).days // 7),
                'regions': [r['region'] for r in tier_b],
                'intensity': 'Medium',
                'focus': 'Leverage primary market success, localized content',
                'budget_percentage': 30
            })
        
        # Phase 3: Tier C - Week 4
        if tier_c:
            phase3_start = start_date + timedelta(weeks=4)
            if phase3_start < release_date:
                phases.append({
                    'phase': 3,
                    'name': 'Tertiary Markets & Long-tail',
                    'start_date': phase3_start.strftime('%Y-%m-%d'),
                    'duration_weeks': max(1, (release_date - phase3_start).days // 7),
                    'regions': [r['region'] for r in tier_c],
                    'intensity': 'Low',
                    'focus': 'Cost-effective digital campaigns, organic growth',
                    'budget_percentage': 20
                })
        
        return phases
    
    def _allocate_budget(
        self,
        ranked_regions: List[Dict[str, Any]],
        total_budget: float
    ) -> List[Dict[str, Any]]:
        """Allocate budget across regions."""
        allocations = []
        
        # Use suggested percentages from scoring
        total_pct = sum(r['suggested_budget_pct'] for r in ranked_regions)
        
        for region_data in ranked_regions:
            # Normalize percentage
            pct = (region_data['suggested_budget_pct'] / total_pct * 100) if total_pct > 0 else 0
            amount = (pct / 100) * total_budget
            
            allocations.append({
                'region': region_data['region'],
                'budget_amount': round(amount, 2),
                'percentage': round(pct, 2),
                'tier': region_data['tier'],
                'justification': region_data['recommendation']
            })
        
        return sorted(allocations, key=lambda x: x['budget_amount'], reverse=True)
    
    def _create_timeline(
        self,
        phases: List[Dict[str, Any]],
        start_date: datetime,
        release_date: datetime
    ) -> List[Dict[str, Any]]:
        """Create week-by-week timeline."""
        timeline = []
        current = start_date
        week = 1
        
        while current < release_date:
            week_end = min(current + timedelta(days=7), release_date)
            
            # Determine active phase
            active_phase = None
            for phase in phases:
                phase_start = datetime.strptime(phase['start_date'], '%Y-%m-%d')
                if phase_start <= current:
                    active_phase = phase
            
            # Determine activities based on weeks to release
            weeks_to_release = (release_date - current).days // 7
            activities = self._get_weekly_activities(weeks_to_release)
            
            timeline.append({
                'week': week,
                'start_date': current.strftime('%Y-%m-%d'),
                'end_date': week_end.strftime('%Y-%m-%d'),
                'phase': active_phase['name'] if active_phase else 'Pre-campaign',
                'active_regions': active_phase['regions'] if active_phase else [],
                'key_activities': activities,
                'intensity': active_phase['intensity'] if active_phase else 'Low'
            })
            
            current = week_end
            week += 1
        
        return timeline
    
    def _get_weekly_activities(self, weeks_to_release: int) -> List[str]:
        """Get recommended activities based on weeks until release."""
        if weeks_to_release >= 6:
            return [
                "Launch teaser campaign",
                "Build social media presence",
                "Secure media partnerships"
            ]
        elif weeks_to_release >= 4:
            return [
                "Release official trailer",
                "Start paid social campaigns",
                "Begin PR tour"
            ]
        elif weeks_to_release >= 2:
            return [
                "Intensify digital ads",
                "Launch ticket pre-sales",
                "Host premiere events"
            ]
        else:
            return [
                "Final push - all channels",
                "Leverage reviews & testimonials",
                "Drive ticket sales"
            ]
    
    def _recommend_channels(
        self,
        ranked_regions: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Recommend marketing channels by region tier."""
        return {
            'tier_a_regions': {
                'regions': [r['region'] for r in ranked_regions if r['tier'] == 'A'],
                'channels': [
                    'TV spots (prime time)',
                    'YouTube pre-roll',
                    'Instagram/Facebook ads',
                    'Outdoor billboards (major cities)',
                    'Influencer partnerships',
                    'Podcast sponsorships'
                ],
                'investment_level': 'High'
            },
            'tier_b_regions': {
                'regions': [r['region'] for r in ranked_regions if r['tier'] == 'B'],
                'channels': [
                    'Digital video ads',
                    'Social media ads',
                    'Streaming platform ads',
                    'Local radio spots'
                ],
                'investment_level': 'Medium'
            },
            'tier_c_regions': {
                'regions': [r['region'] for r in ranked_regions if r['tier'] == 'C'],
                'channels': [
                    'Social media organic',
                    'Display ads',
                    'Email campaigns',
                    'Search engine marketing'
                ],
                'investment_level': 'Low-Medium'
            }
        }
    
    def _generate_milestones(
        self,
        start_date: datetime,
        release_date: datetime
    ) -> List[Dict[str, Any]]:
        """Generate key campaign milestones."""
        milestones = []
        
        # Campaign launch
        milestones.append({
            'date': start_date.strftime('%Y-%m-%d'),
            'milestone': 'Campaign Launch',
            'description': 'Teaser release, social media kickoff'
        })
        
        # Trailer release (4 weeks before)
        trailer_date = release_date - timedelta(weeks=4)
        if trailer_date > start_date:
            milestones.append({
                'date': trailer_date.strftime('%Y-%m-%d'),
                'milestone': 'Official Trailer Release',
                'description': 'Major media push, paid amplification'
            })
        
        # Ticket pre-sales (2 weeks before)
        presale_date = release_date - timedelta(weeks=2)
        if presale_date > start_date:
            milestones.append({
                'date': presale_date.strftime('%Y-%m-%d'),
                'milestone': 'Ticket Pre-Sales Open',
                'description': 'Drive early bookings, create urgency'
            })
        
        # Premiere (1 week before)
        premiere_date = release_date - timedelta(weeks=1)
        if premiere_date > start_date:
            milestones.append({
                'date': premiere_date.strftime('%Y-%m-%d'),
                'milestone': 'World Premiere',
                'description': 'Red carpet event, press coverage, reviews'
            })
        
        # Release day
        milestones.append({
            'date': release_date.strftime('%Y-%m-%d'),
            'milestone': '🎬 RELEASE DAY',
            'description': 'Full availability, maximize opening weekend'
        })
        
        return sorted(milestones, key=lambda x: x['date'])


# Example usage
if __name__ == "__main__":
    planner = RolloutPlanner()
    
    regional_data = {
        'US': {'interest_score': 95, 'engagement_rate': 0.08, 'growth_rate': 0.12, 'sentiment_score': 0.85},
        'GB': {'interest_score': 87, 'engagement_rate': 0.09, 'growth_rate': 0.15, 'sentiment_score': 0.82},
        'IN': {'interest_score': 72, 'engagement_rate': 0.12, 'growth_rate': 0.35, 'sentiment_score': 0.78},
        'BR': {'interest_score': 65, 'engagement_rate': 0.07, 'growth_rate': 0.08, 'sentiment_score': 0.75},
    }
    
    plan = planner.create_rollout_plan(
        regional_data,
        release_date='2024-06-15',
        budget_total=2000000,
        campaign_weeks=6
    )
    
    print("🎬 Campaign Rollout Plan\n")
    print(f"Release: {plan['campaign_overview']['release_date']}")
    print(f"Budget: ${plan['campaign_overview']['total_budget']:,.0f}\n")
    
    print("📅 Phases:")
    for phase in plan['phases']:
        print(f"  Phase {phase['phase']}: {phase['name']}")
        print(f"  Regions: {', '.join(phase['regions'])}")
        print(f"  Budget: {phase['budget_percentage']}%\n")
