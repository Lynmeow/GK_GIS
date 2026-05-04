from django.db import models
from .monitoring_station import MonitoringStation

class AirQualityData(models.Model):
    SOURCE_CHOICES = [
        ('station', 'Trạm quan trắc'),
        ('gee', 'Google Earth Engine'),
        ('api', 'OpenWeather API'),
    ]

    station = models.ForeignKey(
        MonitoringStation, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='air_data'
    )
    source = models.CharField(max_length=20, choices=SOURCE_CHOICES, default='api')
    timestamp = models.DateTimeField()

    # Chỉ số chất lượng không khí
    aqi = models.FloatField(null=True, blank=True, verbose_name='AQI')
    pm25 = models.FloatField(null=True, blank=True, verbose_name='PM2.5 (µg/m³)')
    pm10 = models.FloatField(null=True, blank=True, verbose_name='PM10 (µg/m³)')
    no2 = models.FloatField(null=True, blank=True, verbose_name='NO₂ (µg/m³)')
    co = models.FloatField(null=True, blank=True, verbose_name='CO (mg/m³)')
    o3 = models.FloatField(null=True, blank=True, verbose_name='O₃ (µg/m³)')

    # Vị trí nếu không có trạm
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'air_quality_data'
        verbose_name = 'Dữ liệu chất lượng không khí'
        ordering = ['-timestamp']

    def get_aqi_level(self):
        if self.aqi is None:
            return 'unknown'
        if self.aqi <= 50: return 'good'
        if self.aqi <= 100: return 'moderate'
        if self.aqi <= 150: return 'unhealthy_sensitive'
        if self.aqi <= 200: return 'unhealthy'
        if self.aqi <= 300: return 'very_unhealthy'
        return 'hazardous'