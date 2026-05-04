from django.db import models

class WasteData(models.Model):
    WASTE_TYPE_CHOICES = [
        ('municipal', 'Rác sinh hoạt'),
        ('industrial', 'Rác công nghiệp'),
        ('medical', 'Rác y tế'),
        ('construction', 'Rác xây dựng'),
        ('hazardous', 'Chất thải nguy hại'),
    ]

    STATUS_CHOICES = [
        ('collected', 'Đã thu gom'),
        ('pending', 'Chờ thu gom'),
        ('illegal_dump', 'Đổ trái phép'),
        ('processed', 'Đã xử lý'),
    ]

    district = models.CharField(max_length=100)
    waste_type = models.CharField(max_length=20, choices=WASTE_TYPE_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    timestamp = models.DateTimeField()

    # Số liệu
    volume_tons = models.FloatField(null=True, blank=True, verbose_name='Khối lượng (tấn/ngày)')
    collection_rate_pct = models.FloatField(null=True, blank=True, verbose_name='Tỷ lệ thu gom (%)')
    illegal_dump_count = models.IntegerField(default=0, verbose_name='Số điểm đổ trái phép')

    # Vị trí (nếu là điểm đổ trái phép)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'waste_data'
        verbose_name = 'Dữ liệu rác thải'
        ordering = ['-timestamp']