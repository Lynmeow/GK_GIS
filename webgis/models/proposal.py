from django.db import models
from django.contrib.auth.models import User

class Proposal(models.Model):
    STATUS_CHOICES = [
        ('pending',  'Chờ xét duyệt'),
        ('approved', 'Đã duyệt'),
        ('rejected', 'Từ chối'),
    ]
    PROBLEM_CHOICES = [
        ('aqi',      'Ô nhiễm không khí'),
        ('uhi',      'Đảo nhiệt đô thị'),
        ('ndvi',     'Thiếu cây xanh'),
        ('combined', 'Kết hợp nhiều yếu tố'),
    ]

    author        = models.ForeignKey(User, on_delete=models.CASCADE, related_name='proposals')
    district_name = models.CharField(max_length=200, verbose_name='Khu vực')
    alert_type    = models.CharField(max_length=50, blank=True)
    problem_type  = models.CharField(max_length=20, choices=PROBLEM_CHOICES, default='combined')
    solution      = models.TextField(verbose_name='Giải pháp đề xuất')
    evidence      = models.TextField(blank=True, verbose_name='Cơ sở khoa học')
    status        = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    admin_note    = models.TextField(blank=True, verbose_name='Phản hồi admin')
    created_at    = models.DateTimeField(auto_now_add=True)
    reviewed_at   = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'proposals'
        verbose_name = 'Đề xuất giải pháp'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.author.username} — {self.district_name} ({self.get_status_display()})"