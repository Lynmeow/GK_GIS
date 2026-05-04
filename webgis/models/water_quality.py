from django.db import models
from .monitoring_station import MonitoringStation

class WaterQualityData(models.Model):
    SOURCE_CHOICES = [
        ('sentinel2', 'Sentinel-2'),
        ('station', 'Trạm quan trắc'),
        ('api', 'API'),
    ]

    station = models.ForeignKey(
        MonitoringStation, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='water_data'
    )
    source = models.CharField(max_length=20, choices=SOURCE_CHOICES, default='sentinel2')
    timestamp = models.DateTimeField()

    # Chỉ số chất lượng nước
    ndwi = models.FloatField(null=True, blank=True, verbose_name='NDWI')
    mndwi = models.FloatField(null=True, blank=True, verbose_name='MNDWI')
    turbidity = models.FloatField(null=True, blank=True, verbose_name='Độ đục (NTU)')
    ph = models.FloatField(null=True, blank=True, verbose_name='pH')
    do = models.FloatField(null=True, blank=True, verbose_name='DO (mg/L)')
    bod = models.FloatField(null=True, blank=True, verbose_name='BOD (mg/L)')

    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    water_body = models.CharField(max_length=200, blank=True, verbose_name='Tên sông/kênh')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'water_quality_data'
        verbose_name = 'Dữ liệu chất lượng nước'
        ordering = ['-timestamp']