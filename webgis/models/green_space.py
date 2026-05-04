from django.db import models

class GreenSpaceData(models.Model):
    SOURCE_CHOICES = [
        ('sentinel2', 'Sentinel-2'),
        ('landsat8', 'Landsat 8'),
        ('landsat9', 'Landsat 9'),
    ]

    source = models.CharField(max_length=20, choices=SOURCE_CHOICES, default='sentinel2')
    timestamp = models.DateTimeField()
    district = models.CharField(max_length=100, blank=True)

    # Chỉ số thực vật
    ndvi = models.FloatField(null=True, blank=True, verbose_name='NDVI')
    evi = models.FloatField(null=True, blank=True, verbose_name='EVI')
    green_coverage_pct = models.FloatField(null=True, blank=True, verbose_name='Tỷ lệ phủ xanh (%)')
    green_area_km2 = models.FloatField(null=True, blank=True, verbose_name='Diện tích cây xanh (km²)')
    tree_canopy_pct = models.FloatField(null=True, blank=True, verbose_name='Tán cây che phủ (%)')

    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'green_space_data'
        verbose_name = 'Dữ liệu mảng xanh đô thị'
        ordering = ['-timestamp']

    def get_green_level(self):
        if self.green_coverage_pct is None:
            return 'unknown'
        if self.green_coverage_pct >= 30: return 'good'
        if self.green_coverage_pct >= 15: return 'moderate'
        return 'poor'