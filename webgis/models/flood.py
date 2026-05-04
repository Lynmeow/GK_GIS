from django.db import models

class FloodData(models.Model):
    SOURCE_CHOICES = [
        ('sentinel1', 'Sentinel-1 SAR'),
        ('sentinel2', 'Sentinel-2'),
        ('station', 'Trạm thủy văn'),
        ('report', 'Báo cáo thực địa'),
    ]

    SEVERITY_CHOICES = [
        ('low', 'Nhẹ (< 0.3m)'),
        ('medium', 'Trung bình (0.3 - 0.5m)'),
        ('high', 'Nặng (0.5 - 1m)'),
        ('severe', 'Rất nặng (> 1m)'),
    ]

    source = models.CharField(max_length=20, choices=SOURCE_CHOICES, default='sentinel1')
    severity = models.CharField(max_length=10, choices=SEVERITY_CHOICES, blank=True)
    timestamp = models.DateTimeField()
    district = models.CharField(max_length=100, blank=True)
    street = models.CharField(max_length=200, blank=True)

    flood_extent_km2 = models.FloatField(null=True, blank=True)
    water_depth_m = models.FloatField(null=True, blank=True)
    duration_hours = models.FloatField(null=True, blank=True)
    vv_backscatter = models.FloatField(null=True, blank=True)
    vh_backscatter = models.FloatField(null=True, blank=True)

    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'flood_data'
        verbose_name = 'Dữ liệu ngập lụt'
        ordering = ['-timestamp']