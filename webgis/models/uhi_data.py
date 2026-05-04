from django.db import models

class UHIData(models.Model):
    SOURCE_CHOICES = [
        ('landsat8', 'Landsat 8'),
        ('landsat9', 'Landsat 9'),
        ('modis', 'MODIS'),
    ]

    source = models.CharField(max_length=20, choices=SOURCE_CHOICES, default='landsat8')
    timestamp = models.DateTimeField()
    district = models.CharField(max_length=100, blank=True)

    # Chỉ số nhiệt
    lst = models.FloatField(null=True, blank=True, verbose_name='Nhiệt độ bề mặt LST (°C)')
    ndvi = models.FloatField(null=True, blank=True, verbose_name='NDVI')
    ndbi = models.FloatField(null=True, blank=True, verbose_name='NDBI')
    uhi_intensity = models.FloatField(null=True, blank=True, verbose_name='Cường độ UHI (°C)')

    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'uhi_data'
        verbose_name = 'Dữ liệu Urban Heat Island'
        ordering = ['-timestamp']

    def __str__(self):
        return f"UHI {self.district} - {self.timestamp.strftime('%Y-%m-%d')}"