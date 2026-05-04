from django.db import models

class MonitoringStation(models.Model):
    STATION_TYPE_CHOICES = [
        ('air', 'Trạm quan trắc không khí'),
        ('water', 'Trạm quan trắc nước'),
        ('weather', 'Trạm khí tượng'),
    ]

    STATUS_CHOICES = [
        ('active', 'Hoạt động'),
        ('inactive', 'Ngừng hoạt động'),
        ('maintenance', 'Bảo trì'),
    ]

    name = models.CharField(max_length=200)
    station_code = models.CharField(max_length=50, unique=True)
    station_type = models.CharField(max_length=20, choices=STATION_TYPE_CHOICES)
    district = models.CharField(max_length=100)
    address = models.TextField(blank=True)
    latitude = models.FloatField()
    longitude = models.FloatField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'monitoring_stations'
        verbose_name = 'Trạm quan trắc'

    def __str__(self):
        return f"{self.station_code} - {self.name}"