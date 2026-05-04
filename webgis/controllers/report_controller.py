from django.shortcuts import render
from django.http import JsonResponse
from webgis.models.air_quality import AirQualityData
from webgis.models.uhi_data import UHIData
from webgis.models.water_quality import WaterQualityData
from webgis.models.feedback import Feedback
from webgis.models.alert import Alert
from webgis.services.weather.openweather_service import get_current_weather, get_air_pollution
from django.utils import timezone
from datetime import timedelta

def report_view(request):
    return render(request, 'webgis/report.html')

def report_api(request):
    now   = timezone.now()
    month = now - timedelta(days=30)
    week  = now - timedelta(days=7)

    # Thống kê
    air_count   = AirQualityData.objects.filter(timestamp__gte=month).count()
    uhi_count   = UHIData.objects.filter(timestamp__gte=month).count()
    water_count = WaterQualityData.objects.filter(timestamp__gte=month).count()
    alert_count = Alert.objects.filter(created_at__gte=month).count()
    fb_count    = Feedback.objects.filter(created_at__gte=month).count()
    fb_resolved = Feedback.objects.filter(created_at__gte=month, status='resolved').count()

    # Số liệu trung bình tháng
    from django.db.models import Avg
    air_avg = AirQualityData.objects.filter(timestamp__gte=month).aggregate(
        pm25=Avg('pm25'), no2=Avg('no2'), co=Avg('co')
    )
    uhi_avg = UHIData.objects.filter(timestamp__gte=month).aggregate(
        lst=Avg('lst'), ndvi=Avg('ndvi')
    )
    water_avg = WaterQualityData.objects.filter(timestamp__gte=month).aggregate(
        ndwi=Avg('ndwi')
    )

    # Thời tiết hiện tại
    try:
        weather = get_current_weather()
        air_now = get_air_pollution()
    except:
        weather = {}
        air_now = {}

    return JsonResponse({
        'success': True,
        'period': f"{month.strftime('%d/%m/%Y')} – {now.strftime('%d/%m/%Y')}",
        'stats': {
            'air_records':   air_count,
            'uhi_records':   uhi_count,
            'water_records': water_count,
            'alerts':        alert_count,
            'feedbacks':     fb_count,
            'fb_resolved':   fb_resolved,
        },
        'averages': {
            'pm25': round(air_avg['pm25'] or 0, 2),
            'no2':  round(air_avg['no2']  or 0, 2),
            'co':   round(air_avg['co']   or 0, 2),
            'lst':  round(uhi_avg['lst']  or 0, 2),
            'ndvi': round(uhi_avg['ndvi'] or 0, 4),
            'ndwi': round(water_avg['ndwi'] or 0, 4),
        },
        'current': {
            'temp':     weather.get('temp', '--'),
            'humidity': weather.get('humidity', '--'),
            'aqi':      air_now.get('aqi', '--'),
            'pm25':     air_now.get('pm25', '--'),
        }
    })