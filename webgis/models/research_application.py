from django.db import models

class ResearchApplication(models.Model):
    STATUS_CHOICES = [
        ('pending',  'Chờ xét duyệt'),
        ('approved', 'Đã duyệt'),
        ('rejected', 'Từ chối'),
    ]

    full_name    = models.CharField(max_length=200, verbose_name='Họ và tên')
    email        = models.EmailField(verbose_name='Email')
    institution  = models.CharField(max_length=300, verbose_name='Trường/Cơ quan')
    purpose      = models.TextField(verbose_name='Mục đích nghiên cứu')
    status       = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at   = models.DateTimeField(auto_now_add=True)
    reviewed_at  = models.DateTimeField(null=True, blank=True)
    admin_note   = models.TextField(blank=True, verbose_name='Ghi chú admin')

    class Meta:
        db_table = 'research_applications'
        verbose_name = 'Đơn nghiên cứu sinh'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.full_name} — {self.get_status_display()}"