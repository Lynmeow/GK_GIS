from django.db import models
from django.contrib.auth.models import User


class UserProfile(models.Model):
    role_choices = [
        ('admin',      'Quản Trị Viên'),
        ('researcher', 'Nhà Nghiên Cứu'),
        ('viewer',     'Người Xem'),       # ← fix typo 'Viwer'
    ]

    user         = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role         = models.CharField(max_length=20, choices=role_choices, default='viewer')
    is_owner     = models.BooleanField(default=False)  # ← thêm dòng này
    organization = models.CharField(max_length=200, blank=True)
    phone        = models.CharField(max_length=15, blank=True)
    avatar       = models.ImageField(upload_to='avatars/', blank=True, null=True)
    created_at   = models.DateTimeField(auto_now_add=True)
    update_at    = models.DateTimeField(auto_now=True)

    class Meta:
        db_table     = 'user_profiles'
        verbose_name = 'Hồ sơ người dùng'

    def __str__(self):
        return f"{self.user.username} ({self.get_role_display()})"

    def is_admin(self):
        return self.role == 'admin'