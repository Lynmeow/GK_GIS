from django.db import models
from .monitoring_station import MonitoringStation

class SoilQualityData(models.Model):
    SOURCE_CHOICES = [
        ('sentinel2', 'Sentinel-2'),
        ('landsat8', 'Landsat 8'),
        ('station', 'Trạm quan trắc'),
        ('field', 'Khảo sát thực địa'),
    ]

    LAND_USE_CHOICES = [
        ('residential', 'Khu dân cư'),
        ('industrial', 'Khu công nghiệp'),
        ('agricultural', 'Nông nghiệp'),
        ('commercial', 'Thương mại'),
        ('green', 'Cây xanh/Công viên'),
    ]

    station = models.ForeignKey(
        MonitoringStation, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='soil_data'
    )
    source = models.CharField(max_length=20, choices=SOURCE_CHOICES, default='sentinel2')
    land_use = models.CharField(max_length=20, choices=LAND_USE_CHOICES, blank=True)
    timestamp = models.DateTimeField()
    district = models.CharField(max_length=100, blank=True)

    # Chỉ số từ viễn thám
    ndsi = models.FloatField(null=True, blank=True, verbose_name='NDSI (Soil Index)')
    bsi = models.FloatField(null=True, blank=True, verbose_name='BSI (Bare Soil Index)')
    impervious_pct = models.FloatField(null=True, blank=True, verbose_name='Tỷ lệ bê tông hóa (%)')

    # Chỉ số hóa học (từ trạm/thực địa)
    heavy_metal_index = models.FloatField(null=True, blank=True, verbose_name='Chỉ số kim loại nặng')
    ph = models.FloatField(null=True, blank=True, verbose_name='pH đất')
    organic_matter = models.FloatField(null=True, blank=True, verbose_name='Chất hữu cơ (%)')

    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'soil_quality_data'
        verbose_name = 'Dữ liệu chất lượng đất'
        ordering = ['-timestamp']