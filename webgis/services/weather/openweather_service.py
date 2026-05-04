import requests
import os
from django.utils import timezone
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv('OPENWEATHER_API_KEY')
LAT, LON = 10.8231, 106.6297  # TPHCM

def get_current_weather():
    try:
        url = f'https://api.openweathermap.org/data/2.5/weather?lat={LAT}&lon={LON}&appid={API_KEY}&units=metric&lang=vi'
        res = requests.get(url, timeout=10)
        data = res.json()

        return {
            'temp':        round(data['main']['temp'], 1),
            'feels_like':  round(data['main']['feels_like'], 1),
            'humidity':    data['main']['humidity'],
            'wind_speed':  data['wind']['speed'],
            'description': data['weather'][0]['description'],
            'icon':        data['weather'][0]['icon'],
        }
    except Exception as e:
        return {'error': str(e)}


def get_air_pollution():
    try:
        url = f'https://api.openweathermap.org/data/2.5/air_pollution?lat={LAT}&lon={LON}&appid={API_KEY}'
        res = requests.get(url, timeout=10)
        data = res.json()

        comp = data['list'][0]['components']
        aqi  = data['list'][0]['main']['aqi']

        # Chuyển AQI 1-5 sang thang 0-500
        aqi_map = {1: 25, 2: 75, 3: 125, 4: 200, 5: 300}

        result = {
            'aqi':   aqi_map.get(aqi, 0),
            'aqi_level': aqi,
            'pm25':  round(comp.get('pm2_5', 0), 1),
            'pm10':  round(comp.get('pm10', 0), 1),
            'no2':   round(comp.get('no2', 0), 1),
            'co':    round(comp.get('co', 0), 1),
            'o3':    round(comp.get('o3', 0), 1),
        }

        # Lưu DB
        from webgis.models.air_quality import AirQualityData
        AirQualityData.objects.create(
            source='openweather',
            timestamp=timezone.now(),
            no2=result['no2'],
            co=result['co'],
            pm25=result['pm25'],
            pm10=result['pm10'],
            o3=result['o3'],
        )

        return result

    except Exception as e:
        return {'error': str(e)}