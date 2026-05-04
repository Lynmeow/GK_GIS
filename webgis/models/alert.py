from django.db import models
from django.contrib.auth.models import User

class Alert(models.Model):
    LEVEL_CHOICES = [
        ('info',    'Thông tin'),
        ('warning', 'Cảnh báo'),
        ('danger',  'Nguy hiểm'),
    ]

    TYPE_CHOICES = [
        ('air',   'Chất lượng không khí'),
        ('uhi',   'Nhiệt đô thị'),
        ('water', 'Chất lượng nước'),
        ('flood', 'Ngập úng'),
        ('ndvi',  'Thảm thực vật'),
        ('other', 'Khác'),
    ]

    title       = models.CharField(max_length=200)
    description = models.TextField()
    level       = models.CharField(max_length=10, choices=LEVEL_CHOICES, default='warning')
    alert_type  = models.CharField(max_length=10, choices=TYPE_CHOICES, default='air')
    district    = models.CharField(max_length=100, blank=True)
    value       = models.FloatField(null=True, blank=True)
    threshold   = models.FloatField(null=True, blank=True)
    is_active   = models.BooleanField(default=True)
    created_by  = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)
    created_at  = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'[{self.level}] {self.title}'