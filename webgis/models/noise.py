from django.db import models
from .monitoring_station import MonitoringStation

class NoiseData(models.Model):
    SOURCE_CHOICES = [
        ('station', 'Trạm quan trắc'),
        ('model', 'Mô hình dự báo'),
        ('field', 'Khảo sát thực địa'),
    ]

    NOISE_SOURCE_CHOICES = [
        ('traffic', 'Giao thông'),
        ('construction', 'Xây dựng'),
        ('industrial', 'Công nghiệp'),
        ('community', 'Sinh hoạt'),
    ]

    station = models.ForeignKey(
        MonitoringStation, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='noise_data'
    )
    source = models.CharField(max_length=20, choices=SOURCE_CHOICES, default='station')
    noise_source = models.CharField(max_length=20, choices=NOISE_SOURCE_CHOICES, blank=True)
    timestamp = models.DateTimeField()
    district = models.CharField(max_length=100, blank=True)

    # Chỉ số tiếng ồn (dB)
    leq = models.FloatField(null=True, blank=True, verbose_name='Leq - Mức ồn tương đương (dB)')
    lmax = models.FloatField(null=True, blank=True, verbose_name='Lmax - Mức ồn cực đại (dB)')
    lmin = models.FloatField(null=True, blank=True, verbose_name='Lmin - Mức ồn cực tiểu (dB)')
    l90 = models.FloatField(null=True, blank=True, verbose_name='L90 - Tiếng ồn nền (dB)')

    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'noise_data'
        verbose_name = 'Dữ liệu tiếng ồn đô thị'
        ordering = ['-timestamp']

    def get_noise_level(self):
        """Theo QCVN 26:2010/BTNMT"""
        if self.leq is None:
            return 'unknown'
        if self.leq <= 55: return 'good'       # Khu dân cư ban ngày
        if self.leq <= 70: return 'moderate'    # Khu thương mại
        return 'exceeded'                        # Vượt chuẩn