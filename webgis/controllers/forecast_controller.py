from django.shortcuts import render
from django.http import JsonResponse
from webgis.services.weather.openweather_service import get_current_weather, get_air_pollution
from datetime import datetime, timedelta
import random

def forecast_view(request):
    return render(request, 'webgis/forecast.html')

def forecast_api(request):
    """Dự báo 7 ngày dựa trên data hiện tại + trend giả lập"""
    try:
        weather = get_current_weather()
        air     = get_air_pollution()

        base_temp  = weather.get('temp', 30)
        base_aqi   = air.get('aqi', 80)
        base_pm25  = air.get('pm25', 15)

        # Python weekday(): 0=T2, 1=T3, 2=T4, 3=T5, 4=T6, 5=T7, 6=CN
        labels = ['T2', 'T3', 'T4', 'T5', 'T6', 'T7', 'CN']
        today  = datetime.now()

        days = []
        for i in range(7):
            d     = today + timedelta(days=i)
            label = 'Hôm nay' if i == 0 else labels[d.weekday()]
            noise = random.uniform(-0.05, 0.05)
            days.append({
                'day':      label,
                'date':     d.strftime('%d/%m'),
                'temp_max': round(base_temp + random.uniform(0, 3) + i * 0.2, 1),
                'temp_min': round(base_temp - random.uniform(2, 5), 1),
                'aqi':      max(0, round(base_aqi  * (1 + noise + i * 0.02))),
                'pm25':     round(base_pm25 * (1 + noise), 1),
                'humidity': random.randint(60, 85),
                'rain':     random.choice([0, 0, 0, 10, 20, 40, 60]),
                'icon':     '🌤' if random.random() > 0.4 else '🌧',
            })

        return JsonResponse({'success': True, 'forecast': days})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})