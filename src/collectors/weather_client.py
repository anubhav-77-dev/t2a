"""Weather data client using Open-Meteo API (no key required)."""

import requests
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta


class WeatherClient:
    """Client for Open-Meteo weather API (free, no key required)."""
    
    def __init__(self):
        self.base_url = "https://api.open-meteo.com/v1"
    
    def get_forecast(
        self,
        latitude: float,
        longitude: float,
        days: int = 7
    ) -> Dict[str, Any]:
        """
        Get weather forecast for a location.
        
        Args:
            latitude: Location latitude
            longitude: Location longitude
            days: Number of forecast days (1-16)
        """
        url = f"{self.base_url}/forecast"
        
        params = {
            'latitude': latitude,
            'longitude': longitude,
            'daily': 'temperature_2m_max,temperature_2m_min,precipitation_sum,weathercode',
            'forecast_days': min(days, 16),
            'timezone': 'auto'
        }
        
        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            daily = data.get('daily', {})
            dates = daily.get('time', [])
            temp_max = daily.get('temperature_2m_max', [])
            temp_min = daily.get('temperature_2m_min', [])
            precipitation = daily.get('precipitation_sum', [])
            weather_codes = daily.get('weathercode', [])
            
            forecast = []
            for i in range(len(dates)):
                forecast.append({
                    'date': dates[i],
                    'temp_max': temp_max[i],
                    'temp_min': temp_min[i],
                    'precipitation': precipitation[i],
                    'weather_code': weather_codes[i],
                    'condition': self._interpret_weather_code(weather_codes[i])
                })
            
            return {
                'location': {
                    'latitude': latitude,
                    'longitude': longitude
                },
                'forecast': forecast
            }
        
        except requests.exceptions.RequestException as e:
            print(f"❌ Weather API error: {e}")
            return {}
    
    @staticmethod
    def _interpret_weather_code(code: int) -> str:
        """Interpret WMO weather code into readable condition."""
        codes = {
            0: 'Clear sky',
            1: 'Mainly clear',
            2: 'Partly cloudy',
            3: 'Overcast',
            45: 'Foggy',
            48: 'Depositing rime fog',
            51: 'Light drizzle',
            53: 'Moderate drizzle',
            55: 'Dense drizzle',
            61: 'Slight rain',
            63: 'Moderate rain',
            65: 'Heavy rain',
            71: 'Slight snow',
            73: 'Moderate snow',
            75: 'Heavy snow',
            77: 'Snow grains',
            80: 'Slight rain showers',
            81: 'Moderate rain showers',
            82: 'Violent rain showers',
            85: 'Slight snow showers',
            86: 'Heavy snow showers',
            95: 'Thunderstorm',
            96: 'Thunderstorm with slight hail',
            99: 'Thunderstorm with heavy hail'
        }
        return codes.get(code, 'Unknown')
    
    def get_best_outdoor_promo_days(
        self,
        latitude: float,
        longitude: float,
        days: int = 14
    ) -> List[Dict[str, Any]]:
        """
        Identify best days for outdoor promotional events.
        
        Returns days sorted by weather suitability (clear, warm, no rain).
        """
        forecast = self.get_forecast(latitude, longitude, days)
        
        if not forecast.get('forecast'):
            return []
        
        # Score each day
        scored_days = []
        for day in forecast['forecast']:
            score = 0
            
            # Temperature (prefer 15-25°C / 59-77°F)
            temp_avg = (day['temp_max'] + day['temp_min']) / 2
            if 15 <= temp_avg <= 25:
                score += 30
            elif 10 <= temp_avg <= 30:
                score += 20
            elif 5 <= temp_avg <= 35:
                score += 10
            
            # No precipitation is best
            if day['precipitation'] == 0:
                score += 40
            elif day['precipitation'] < 1:
                score += 20
            elif day['precipitation'] < 5:
                score += 10
            
            # Clear weather
            weather_code = day['weather_code']
            if weather_code == 0:  # Clear sky
                score += 30
            elif weather_code in [1, 2]:  # Mainly clear / partly cloudy
                score += 20
            elif weather_code == 3:  # Overcast
                score += 10
            
            scored_days.append({
                **day,
                'promo_score': score,
                'suitable': score >= 60
            })
        
        # Sort by score
        scored_days.sort(key=lambda x: x['promo_score'], reverse=True)
        
        return scored_days
    
    def get_multi_city_forecast(
        self,
        cities: Dict[str, Dict[str, float]],
        days: int = 7
    ) -> Dict[str, Any]:
        """
        Get forecasts for multiple cities.
        
        Args:
            cities: Dict of {city_name: {'lat': float, 'lon': float}}
        """
        results = {}
        
        for city, coords in cities.items():
            forecast = self.get_forecast(
                coords['lat'],
                coords['lon'],
                days
            )
            
            if forecast:
                # Find best promo days
                promo_days = self.get_best_outdoor_promo_days(
                    coords['lat'],
                    coords['lon'],
                    days
                )
                
                suitable_days = [d for d in promo_days if d['suitable']]
                
                results[city] = {
                    'coordinates': coords,
                    'forecast': forecast['forecast'],
                    'best_promo_days': suitable_days[:3],
                    'suitable_days_count': len(suitable_days)
                }
        
        return results


# Major cities coordinates for easy reference
MAJOR_CITIES = {
    'Los Angeles': {'lat': 34.0522, 'lon': -118.2437},
    'New York': {'lat': 40.7128, 'lon': -74.0060},
    'London': {'lat': 51.5074, 'lon': -0.1278},
    'Paris': {'lat': 48.8566, 'lon': 2.3522},
    'Tokyo': {'lat': 35.6762, 'lon': 139.6503},
    'Mumbai': {'lat': 19.0760, 'lon': 72.8777},
    'Sydney': {'lat': -33.8688, 'lon': 151.2093},
    'Toronto': {'lat': 43.6532, 'lon': -79.3832},
    'Berlin': {'lat': 52.5200, 'lon': 13.4050},
    'São Paulo': {'lat': -23.5505, 'lon': -46.6333}
}


# Example usage
if __name__ == "__main__":
    client = WeatherClient()
    
    # Get forecast for Los Angeles
    la_coords = MAJOR_CITIES['Los Angeles']
    forecast = client.get_forecast(la_coords['lat'], la_coords['lon'], days=7)
    
    print("🌤️  7-Day Weather Forecast - Los Angeles")
    for day in forecast['forecast']:
        print(f"{day['date']}: {day['condition']} | {day['temp_min']}°C - {day['temp_max']}°C")
    
    # Find best promo days
    print("\n🎬 Best Days for Outdoor Promo Events:")
    promo_days = client.get_best_outdoor_promo_days(
        la_coords['lat'],
        la_coords['lon'],
        days=14
    )
    
    for day in promo_days[:3]:
        if day['suitable']:
            print(f"  {day['date']}: {day['condition']} (Score: {day['promo_score']}/100)")
