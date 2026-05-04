from django.db import models

class TrafficData(models.Model):
    SOURCE_CHOICES = [
        ('api', 'Traffic API'),
        ('model', 'Mô hình ước tính'),
        ('station', 'Trạm đếm xe'),
    ]

    ROAD_TYPE_CHOICES = [
        ('highway', 'Cao tốc'),
        ('main', 'Đường chính'),
        ('secondary', 'Đường phụ'),
        ('alley', 'Hẻm'),
    ]

    source = models.CharField(max_length=20, choices=SOURCE_CHOICES, default='api')
    road_type = models.CharField(max_length=20, choices=ROAD_TYPE_CHOICES, blank=True)
    timestamp = models.DateTimeField()
    district = models.CharField(max_length=100, blank=True)
    road_name = models.CharField(max_length=200, blank=True)

    vehicle_count = models.IntegerField(null=True, blank=True)
    congestion_index = models.FloatField(null=True, blank=True)
    avg_speed_kmh = models.FloatField(null=True, blank=True)
    co2_estimate = models.FloatField(null=True, blank=True)
    nox_estimate = models.FloatField(null=True, blank=True)

    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'traffic_data'
        verbose_name = 'Dữ liệu giao thông & khí thải'
        ordering = ['-timestamp']

    def get_congestion_level(self):
        if self.congestion_index is None:
            return 'unknown'
        if self.congestion_index <= 0.3: return 'free'
        if self.congestion_index <= 0.6: return 'moderate'
        if self.congestion_index <= 0.8: return 'heavy'
        return 'gridlock'