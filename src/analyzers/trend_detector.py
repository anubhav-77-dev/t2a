"""Trend detection and pattern recognition for campaign timing."""

from typing import Dict, List, Any, Tuple
from datetime import datetime, timedelta
from collections import defaultdict
import statistics


class TrendDetector:
    """Detect trends and patterns in engagement data."""
    
    def __init__(self):
        pass
    
    def detect_momentum(
        self,
        time_series: List[Dict[str, Any]],
        value_key: str = 'value',
        date_key: str = 'date'
    ) -> Dict[str, Any]:
        """
        Detect if a trend is accelerating, stable, or declining.
        
        Args:
            time_series: List of data points with dates and values
            value_key: Key for the numeric value
            date_key: Key for the date
        """
        if len(time_series) < 3:
            return {'momentum': 'insufficient_data', 'trend': 'unknown'}
        
        # Sort by date
        sorted_data = sorted(time_series, key=lambda x: x[date_key])
        values = [item[value_key] for item in sorted_data]
        
        # Calculate rolling averages
        if len(values) >= 7:
            recent_avg = statistics.mean(values[-7:])
            older_avg = statistics.mean(values[-14:-7] if len(values) >= 14 else values[:7])
        else:
            recent_avg = statistics.mean(values[len(values)//2:])
            older_avg = statistics.mean(values[:len(values)//2])
        
        # Calculate rate of change
        change_pct = ((recent_avg - older_avg) / older_avg * 100) if older_avg > 0 else 0
        
        # Determine momentum
        if change_pct > 15:
            momentum = 'accelerating'
        elif change_pct < -15:
            momentum = 'declining'
        elif abs(change_pct) < 5:
            momentum = 'stable'
        else:
            momentum = 'gradual_change'
        
        # Determine overall trend
        first_half_avg = statistics.mean(values[:len(values)//2])
        second_half_avg = statistics.mean(values[len(values)//2:])
        
        if second_half_avg > first_half_avg * 1.1:
            trend = 'upward'
        elif second_half_avg < first_half_avg * 0.9:
            trend = 'downward'
        else:
            trend = 'flat'
        
        return {
            'momentum': momentum,
            'trend': trend,
            'change_percentage': round(change_pct, 2),
            'recent_average': round(recent_avg, 2),
            'older_average': round(older_avg, 2),
            'peak_value': max(values),
            'current_value': values[-1],
            'recommendation': self._momentum_recommendation(momentum, trend)
        }
    
    def _momentum_recommendation(self, momentum: str, trend: str) -> str:
        """Generate campaign timing recommendation."""
        if momentum == 'accelerating' and trend == 'upward':
            return "🚀 Strike now! Momentum is building - ideal for major push"
        elif momentum == 'declining':
            return "⚠️  Interest declining - consider refreshing creative or targeting"
        elif momentum == 'stable' and trend == 'upward':
            return "✅ Steady growth - maintain current strategy"
        else:
            return "📊 Monitor closely - consider A/B testing new approaches"
    
    def detect_spikes(
        self,
        time_series: List[Dict[str, Any]],
        value_key: str = 'value',
        date_key: str = 'date',
        threshold: float = 2.0
    ) -> List[Dict[str, Any]]:
        """
        Detect anomalous spikes in data.
        
        Args:
            threshold: Multiple of standard deviation to consider a spike
        """
        if len(time_series) < 5:
            return []
        
        values = [item[value_key] for item in time_series]
        mean = statistics.mean(values)
        
        try:
            stdev = statistics.stdev(values)
        except statistics.StatisticsError:
            stdev = 0
        
        if stdev == 0:
            return []
        
        spike_threshold = mean + (threshold * stdev)
        
        spikes = []
        for item in time_series:
            if item[value_key] >= spike_threshold:
                spikes.append({
                    'date': item[date_key],
                    'value': item[value_key],
                    'deviation': round((item[value_key] - mean) / stdev, 2),
                    'percentage_above_mean': round((item[value_key] / mean - 1) * 100, 1)
                })
        
        return sorted(spikes, key=lambda x: x['value'], reverse=True)
    
    def identify_best_posting_times(
        self,
        engagement_by_hour: Dict[int, int]
    ) -> List[Dict[str, Any]]:
        """
        Identify peak engagement hours for social media posting.
        
        Args:
            engagement_by_hour: Dict of {hour: engagement_count}
        """
        if not engagement_by_hour:
            return []
        
        # Sort by engagement
        sorted_hours = sorted(
            engagement_by_hour.items(),
            key=lambda x: x[1],
            reverse=True
        )
        
        # Get top 5 hours
        top_hours = []
        for hour, engagement in sorted_hours[:5]:
            # Convert to readable time
            time_str = f"{hour:02d}:00"
            period = "AM" if hour < 12 else "PM"
            display_hour = hour if hour <= 12 else hour - 12
            if display_hour == 0:
                display_hour = 12
            
            top_hours.append({
                'hour': hour,
                'time_display': f"{display_hour}:00 {period}",
                'engagement': engagement,
                'recommendation': self._time_recommendation(hour)
            })
        
        return top_hours
    
    def _time_recommendation(self, hour: int) -> str:
        """Generate recommendation for posting time."""
        if 6 <= hour <= 9:
            return "Morning commute - mobile-optimized content"
        elif 12 <= hour <= 14:
            return "Lunch break - quick, engaging content"
        elif 17 <= hour <= 20:
            return "Evening wind-down - longer-form content works"
        elif 21 <= hour <= 23:
            return "Late night - entertainment focus"
        else:
            return "Off-peak - test experimental content"
    
    def analyze_geographic_trends(
        self,
        regional_data: Dict[str, Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Analyze and prioritize geographic regions.
        
        Args:
            regional_data: Dict of {region: {metrics}}
        """
        regions = []
        
        for region, data in regional_data.items():
            # Calculate composite score
            score = 0
            factors = {}
            
            # Interest/engagement (0-40 points)
            interest = data.get('interest_score', 0)
            interest_points = min(interest / 100 * 40, 40)
            score += interest_points
            factors['interest'] = interest_points
            
            # Growth trend (0-30 points)
            growth = data.get('growth_rate', 0)
            if growth > 20:
                growth_points = 30
            elif growth > 10:
                growth_points = 20
            elif growth > 0:
                growth_points = 10
            else:
                growth_points = 0
            score += growth_points
            factors['growth'] = growth_points
            
            # Market size (0-20 points)
            population = data.get('population', 0)
            if population > 100_000_000:
                size_points = 20
            elif population > 50_000_000:
                size_points = 15
            elif population > 10_000_000:
                size_points = 10
            else:
                size_points = 5
            score += size_points
            factors['market_size'] = size_points
            
            # Engagement quality (0-10 points)
            engagement_rate = data.get('engagement_rate', 0)
            engagement_points = min(engagement_rate * 10, 10)
            score += engagement_points
            factors['engagement'] = engagement_points
            
            regions.append({
                'region': region,
                'priority_score': round(score, 2),
                'score_factors': factors,
                'tier': self._determine_tier(score),
                'data': data
            })
        
        # Sort by score
        regions.sort(key=lambda x: x['priority_score'], reverse=True)
        
        return {
            'prioritized_regions': regions,
            'top_tier': [r for r in regions if r['tier'] == 'A'],
            'recommendations': self._geographic_recommendations(regions)
        }
    
    def _determine_tier(self, score: float) -> str:
        """Determine region tier based on score."""
        if score >= 75:
            return 'A'
        elif score >= 60:
            return 'B'
        elif score >= 40:
            return 'C'
        else:
            return 'D'
    
    def _geographic_recommendations(self, regions: List[Dict]) -> List[str]:
        """Generate geographic campaign recommendations."""
        recs = []
        
        if not regions:
            return recs
        
        # Identify clear leader
        if regions[0]['priority_score'] > regions[1]['priority_score'] * 1.5 if len(regions) > 1 else True:
            recs.append(f"Focus primary budget on {regions[0]['region']} - clear market leader")
        
        # Identify growth opportunities
        growth_regions = [r for r in regions if r['score_factors'].get('growth', 0) >= 20]
        if growth_regions:
            recs.append(f"Emerging markets: {', '.join(r['region'] for r in growth_regions[:3])}")
        
        # Tier strategy
        a_tier = [r for r in regions if r['tier'] == 'A']
        if len(a_tier) > 1:
            recs.append(f"Multi-market approach: {len(a_tier)} tier-A regions detected")
        
        return recs
    
    def calculate_viral_coefficient(
        self,
        initial_views: int,
        current_views: int,
        days_elapsed: int
    ) -> Dict[str, Any]:
        """
        Estimate content's viral potential.
        
        Returns growth rate and virality score.
        """
        if days_elapsed == 0 or initial_views == 0:
            return {'viral_coefficient': 0, 'assessment': 'insufficient_data'}
        
        # Calculate daily growth rate
        growth_rate = (current_views / initial_views) ** (1 / days_elapsed) - 1
        
        # Estimate doubling time
        if growth_rate > 0:
            doubling_days = 70 / (growth_rate * 100)  # Rule of 70
        else:
            doubling_days = float('inf')
        
        # Assess virality
        if growth_rate > 0.15:  # >15% daily growth
            assessment = 'highly_viral'
            score = 90
        elif growth_rate > 0.08:  # >8% daily growth
            assessment = 'viral'
            score = 75
        elif growth_rate > 0.03:  # >3% daily growth
            assessment = 'growing'
            score = 60
        elif growth_rate > 0:
            assessment = 'slow_growth'
            score = 40
        else:
            assessment = 'declining'
            score = 20
        
        return {
            'viral_coefficient': round(growth_rate, 4),
            'daily_growth_rate': f"{growth_rate * 100:.2f}%",
            'doubling_time_days': round(doubling_days, 1) if doubling_days != float('inf') else 'N/A',
            'virality_score': score,
            'assessment': assessment,
            'recommendation': self._virality_recommendation(assessment)
        }
    
    def _virality_recommendation(self, assessment: str) -> str:
        """Generate recommendation based on virality."""
        recommendations = {
            'highly_viral': "🔥 Maximize spend NOW - ride the viral wave",
            'viral': "📈 Scale up campaigns - strong organic traction",
            'growing': "✅ Maintain momentum - consider boosting top content",
            'slow_growth': "🔄 Test new creative - current pace is moderate",
            'declining': "⚠️  Refresh strategy - interest is fading"
        }
        return recommendations.get(assessment, "Monitor and adjust")


# Example usage
if __name__ == "__main__":
    detector = TrendDetector()
    
    # Sample pageview data
    pageviews = [
        {'date': '2024-01-01', 'value': 1000},
        {'date': '2024-01-02', 'value': 1200},
        {'date': '2024-01-03', 'value': 1500},
        {'date': '2024-01-04', 'value': 2000},
        {'date': '2024-01-05', 'value': 2800},
        {'date': '2024-01-06', 'value': 3500},
        {'date': '2024-01-07', 'value': 4200},
    ]
    
    momentum = detector.detect_momentum(pageviews)
    print("📊 Trend Analysis:")
    print(f"Momentum: {momentum['momentum']}")
    print(f"Trend: {momentum['trend']}")
    print(f"Change: {momentum['change_percentage']}%")
    print(f"💡 {momentum['recommendation']}")
    
    # Detect spikes
    spikes = detector.detect_spikes(pageviews)
    if spikes:
        print(f"\n🔥 Detected {len(spikes)} spikes:")
        for spike in spikes:
            print(f"  {spike['date']}: {spike['percentage_above_mean']}% above average")
