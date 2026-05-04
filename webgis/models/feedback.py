from django.db import models
from django.contrib.auth.models import User

class Feedback(models.Model):
    CATEGORY_CHOICES = [
        ('air',   'Chất lượng không khí'),
        ('water', 'Chất lượng nước'),
        ('noise', 'Tiếng ồn'),
        ('waste', 'Rác thải'),
        ('green', 'Cây xanh'),
        ('other', 'Khác'),
    ]

    STATUS_CHOICES = [
        ('pending',  'Chờ xử lý'),
        ('reviewing','Đang xem xét'),
        ('resolved', 'Đã xử lý'),
    ]

    user        = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)
    category    = models.CharField(max_length=10, choices=CATEGORY_CHOICES, default='other')
    title       = models.CharField(max_length=200)
    description = models.TextField()
    district    = models.CharField(max_length=100, blank=True)
    image_url   = models.URLField(blank=True)
    status      = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    created_at  = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.title} ({self.status})'