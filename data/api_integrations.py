"""
API Integration Module
MarineTraffic and OpenWeather API integrations
Data Engineer: API Integration Specialist
"""

import requests
from typing import List, Dict, Optional
from datetime import datetime
import logging
import time
from functools import lru_cache

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MarineTrafficAPI:
    """
    Integration with MarineTraffic API for vessel tracking
    """
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://services.marinetraffic.com/api"
        self.session = requests.Session()
    
    def get_vessel_positions(
        self,
        imo_list: List[str],
        timeout: int = 30
    ) -> List[Dict]:
        """
        Get real-time positions for list of vessels
        
        Args:
            imo_list: List of IMO numbers
            timeout: Request timeout in seconds
            
        Returns:
            List of vessel position data
        """
        try:
            endpoint = f"{self.base_url}/exportvessels"
            
            params = {
                'v': '8',
                'protocol': 'jsono',
                'msgtype': 'simple',
                'imo': ','.join(imo_list),
                'timespan': '20'  # Last 20 minutes
            }
            
            headers = {
                'Authorization': f'Bearer {self.api_key}'
            }
            
            logger.info(f"Fetching positions for {len(imo_list)} vessels")
            
            response = self.session.get(
                endpoint,
                params=params,
                headers=headers,
                timeout=timeout
            )
            response.raise_for_status()
            
            data = response.json()
            vessels = data.get('data', [])
            
            logger.info(f"Retrieved {len(vessels)} vessel positions")
            return vessels
            
        except requests.exceptions.RequestException as e:
            logger.error(f"MarineTraffic API error: {e}")
            return []
    
    def get_vessel_route(self, imo: str) -> Optional[Dict]:
        """
        Get planned route for a vessel
        
        Args:
            imo: IMO number
            
        Returns:
            Route information dictionary
        """
        try:
            endpoint = f"{self.base_url}/exportroute"
            
            params = {
                'v': '2',
                'imo': imo,
                'protocol': 'jsono'
            }
            
            headers = {
                'Authorization': f'Bearer {self.api_key}'
            }
            
            response = self.session.get(
                endpoint,
                params=params,
                headers=headers,
                timeout=30
            )
            response.raise_for_status()
            
            data = response.json()
            return data.get('data', {})
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching route for {imo}: {e}")
            return None
    
    def get_port_calls(
        self,
        port_id: str,
        days_ahead: int = 7
    ) -> List[Dict]:
        """
        Get expected port calls
        
        Args:
            port_id: Port identifier
            days_ahead: Number of days to look ahead
            
        Returns:
            List of expected port calls
        """
        try:
            endpoint = f"{self.base_url}/portcalls"
            
            params = {
                'v': '1',
                'portid': port_id,
                'days_ahead': days_ahead,
                'protocol': 'jsono'
            }
            
            headers = {
                'Authorization': f'Bearer {self.api_key}'
            }
            
            response = self.session.get(
                endpoint,
                params=params,
                headers=headers,
                timeout=30
            )
            response.raise_for_status()
            
            data = response.json()
            return data.get('data', [])
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching port calls: {e}")
            return []


class OpenWeatherAPI:
    """
    Integration with OpenWeather API for weather data
    """
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.openweathermap.org/data/2.5"
        self.session = requests.Session()
    
    @lru_cache(maxsize=100)
    def get_port_weather(
        self,
        lat: float,
        lon: float,
        units: str = "metric"
    ) -> Optional[Dict]:
        """
        Get current weather for port location
        
        Args:
            lat: Latitude
            lon: Longitude
            units: Unit system (metric/imperial)
            
        Returns:
            Weather data dictionary
        """
        try:
            endpoint = f"{self.base_url}/weather"
            
            params = {
                'lat': lat,
                'lon': lon,
                'appid': self.api_key,
                'units': units
            }
            
            logger.info(f"Fetching weather for coordinates: {lat}, {lon}")
            
            response = self.session.get(endpoint, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            # Format response
            formatted = {
                'temperature': data['main']['temp'],
                'feels_like': data['main']['feels_like'],
                'humidity': data['main']['humidity'],
                'pressure': data['main']['pressure'],
                'wind_speed': data['wind']['speed'],
                'wind_direction': data['wind'].get('deg', 0),
                'weather': data['weather'][0]['description'],
                'visibility': data.get('visibility', 0) / 1000,  # Convert to km
                'timestamp': datetime.fromtimestamp(data['dt'])
            }
            
            logger.info(f"Weather retrieved: {formatted['weather']}, {formatted['temperature']}°C")
            return formatted
            
        except requests.exceptions.RequestException as e:
            logger.error(f"OpenWeather API error: {e}")
            return None
    
    def get_weather_forecast(
        self,
        lat: float,
        lon: float,
        units: str = "metric"
    ) -> List[Dict]:
        """
        Get 5-day weather forecast
        
        Args:
            lat: Latitude
            lon: Longitude
            units: Unit system
            
        Returns:
            List of forecast data
        """
        try:
            endpoint = f"{self.base_url}/forecast"
            
            params = {
                'lat': lat,
                'lon': lon,
                'appid': self.api_key,
                'units': units
            }
            
            logger.info(f"Fetching forecast for coordinates: {lat}, {lon}")
            
            response = self.session.get(endpoint, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            # Format forecast list
            forecasts = []
            for item in data['list']:
                forecasts.append({
                    'timestamp': datetime.fromtimestamp(item['dt']),
                    'temperature': item['main']['temp'],
                    'feels_like': item['main']['feels_like'],
                    'humidity': item['main']['humidity'],
                    'wind_speed': item['wind']['speed'],
                    'wind_direction': item['wind'].get('deg', 0),
                    'weather': item['weather'][0]['description'],
                    'precipitation_probability': item.get('pop', 0) * 100
                })
            
            logger.info(f"Retrieved {len(forecasts)} forecast intervals")
            return forecasts
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Forecast API error: {e}")
            return []
    
    def get_marine_forecast(
        self,
        lat: float,
        lon: float
    ) -> Optional[Dict]:
        """
        Get marine-specific weather (wave height, sea conditions)
        Note: Requires OpenWeather Marine subscription
        
        Args:
            lat: Latitude
            lon: Longitude
            
        Returns:
            Marine weather data
        """
        try:
            # This would use the Marine API endpoint if subscribed
            # Fallback to standard weather for now
            weather = self.get_port_weather(lat, lon)
            
            if weather:
                # Estimate wave conditions based on wind speed
                wind_speed = weather['wind_speed']
                wave_height = self._estimate_wave_height(wind_speed)
                
                weather['wave_height'] = wave_height
                weather['sea_condition'] = self._get_sea_condition(wind_speed)
            
            return weather
            
        except Exception as e:
            logger.error(f"Marine forecast error: {e}")
            return None
    
    def _estimate_wave_height(self, wind_speed: float) -> float:
        """
        Estimate wave height from wind speed (simplified Beaufort scale)
        
        Args:
            wind_speed: Wind speed in m/s
            
        Returns:
            Estimated wave height in meters
        """
        # Simplified estimation
        if wind_speed < 1:
            return 0.0
        elif wind_speed < 3:
            return 0.1
        elif wind_speed < 6:
            return 0.5
        elif wind_speed < 10:
            return 1.0
        elif wind_speed < 15:
            return 2.5
        elif wind_speed < 20:
            return 4.0
        else:
            return 6.0
    
    def _get_sea_condition(self, wind_speed: float) -> str:
        """
        Determine sea condition from wind speed
        
        Args:
            wind_speed: Wind speed in m/s
            
        Returns:
            Sea condition description
        """
        if wind_speed < 1:
            return "Calm"
        elif wind_speed < 3:
            return "Light Air"
        elif wind_speed < 6:
            return "Light Breeze"
        elif wind_speed < 10:
            return "Moderate"
        elif wind_speed < 15:
            return "Fresh"
        elif wind_speed < 20:
            return "Strong"
        else:
            return "Gale"


class ETLPipeline:
    """
    ETL Pipeline for ingesting data from APIs to database
    """
    
    def __init__(
        self,
        marine_api: MarineTrafficAPI,
        weather_api: OpenWeatherAPI,
        db_manager
    ):
        self.marine_api = marine_api
        self.weather_api = weather_api
        self.db = db_manager
        
        # Port coordinates for weather tracking
        self.ports = {
            'Singapore': {'lat': 1.3521, 'lon': 103.8198, 'id': 'SGSIN'},
            'Rotterdam': {'lat': 51.9225, 'lon': 4.47917, 'id': 'NLRTM'},
            'Shanghai': {'lat': 31.2304, 'lon': 121.4737, 'id': 'CNSHA'},
            'Los Angeles': {'lat': 33.7701, 'lon': -118.1937, 'id': 'USLAX'},
            'Antwerp': {'lat': 51.2194, 'lon': 4.4025, 'id': 'BEANR'}
        }
    
    def sync_vessel_positions(self, imo_list: List[str]) -> int:
        """
        Sync vessel positions from MarineTraffic to database
        
        Args:
            imo_list: List of IMO numbers to track
            
        Returns:
            Number of vessels updated
        """
        logger.info(f"Syncing positions for {len(imo_list)} vessels")
        
        # Fetch positions from API
        positions = self.marine_api.get_vessel_positions(imo_list)
        
        updated_count = 0
        for position in positions:
            vessel_data = {
                'vessel_name': position.get('SHIPNAME'),
                'imo_number': position.get('IMO'),
                'operator': position.get('SHIPTYPE'),
                'service': position.get('TYPE_NAME'),
                'lat': position.get('LAT'),
                'lon': position.get('LON')
            }
            
            if self.db.insert_vessel(vessel_data):
                updated_count += 1
        
        logger.info(f"Updated {updated_count} vessel positions")
        return updated_count
    
    def sync_weather_data(self) -> int:
        """
        Sync weather data for all tracked ports
        
        Returns:
            Number of weather records inserted
        """
        logger.info(f"Syncing weather for {len(self.ports)} ports")
        
        updated_count = 0
        for port_name, coords in self.ports.items():
            # Get current weather
            weather = self.weather_api.get_port_weather(
                coords['lat'],
                coords['lon']
            )
            
            if weather:
                # Get marine forecast
                marine = self.weather_api.get_marine_forecast(
                    coords['lat'],
                    coords['lon']
                )
                
                weather_data = {
                    'port': port_name,
                    'timestamp': weather['timestamp'],
                    'temperature': weather['temperature'],
                    'wind_speed': weather['wind_speed'],
                    'wind_direction': weather['wind_direction'],
                    'wave_height': marine.get('wave_height', 0) if marine else 0,
                    'visibility': weather['visibility'],
                    'precipitation': 0  # Would come from forecast
                }
                
                if self.db.insert_weather_data(weather_data):
                    updated_count += 1
        
        logger.info(f"Inserted {updated_count} weather records")
        return updated_count
    
    def sync_weather_forecast(self) -> int:
        """
        Sync 5-day weather forecast for all ports
        
        Returns:
            Number of forecast records inserted
        """
        logger.info("Syncing weather forecasts")
        
        updated_count = 0
        for port_name, coords in self.ports.items():
            forecasts = self.weather_api.get_weather_forecast(
                coords['lat'],
                coords['lon']
            )
            
            for forecast in forecasts:
                weather_data = {
                    'port': port_name,
                    'timestamp': forecast['timestamp'],
                    'temperature': forecast['temperature'],
                    'wind_speed': forecast['wind_speed'],
                    'wind_direction': forecast['wind_direction'],
                    'wave_height': self.weather_api._estimate_wave_height(
                        forecast['wind_speed']
                    ),
                    'visibility': 10,  # Default visibility
                    'precipitation': forecast.get('precipitation_probability', 0)
                }
                
                if self.db.insert_weather_data(weather_data):
                    updated_count += 1
        
        logger.info(f"Inserted {updated_count} forecast records")
        return updated_count
    
    def run_scheduled_sync(self):
        """
        Run complete scheduled data synchronization
        Should be called every 15 minutes via cron/scheduler
        """
        logger.info("Starting scheduled data sync")
        
        try:
            # Get list of tracked vessels from database
            recent_vessels = self.db.get_recent_vessels(limit=100)
            imo_list = [v['imo_number'] for v in recent_vessels if v.get('imo_number')]
            
            # Sync vessel positions
            vessel_count = self.sync_vessel_positions(imo_list)
            
            # Sync weather data
            weather_count = self.sync_weather_data()
            
            # Sync forecasts (less frequently - once per hour)
            current_minute = datetime.now().minute
            if current_minute < 15:  # Only on first run of the hour
                forecast_count = self.sync_weather_forecast()
            else:
                forecast_count = 0
            
            logger.info(
                f"Sync complete: {vessel_count} vessels, "
                f"{weather_count} weather, {forecast_count} forecasts"
            )
            
            return {
                'vessels_updated': vessel_count,
                'weather_updated': weather_count,
                'forecasts_updated': forecast_count,
                'timestamp': datetime.now()
            }
            
        except Exception as e:
            logger.error(f"Scheduled sync error: {e}")
            return {'error': str(e)}


# Example usage in scheduler
if __name__ == "__main__":
    import os
    from data.database_manager import DatabaseManager, DatabaseConfig
    
    # Initialize APIs
    marine_api = MarineTrafficAPI(os.getenv('MARINETRAFFIC_API_KEY'))
    weather_api = OpenWeatherAPI(os.getenv('OPENWEATHER_API_KEY'))
    
    # Initialize database
    db_config = DatabaseConfig(
        host=os.getenv('MYSQL_HOST'),
        user=os.getenv('MYSQL_USER'),
        password=os.getenv('MYSQL_PASSWORD'),
        database=os.getenv('MYSQL_DATABASE')
    )
    db = DatabaseManager(db_config)
    
    # Create ETL pipeline
    etl = ETLPipeline(marine_api, weather_api, db)
    
    # Run sync
    result = etl.run_scheduled_sync()
    print(f"Sync result: {result}")
