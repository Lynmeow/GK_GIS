from django.contrib.auth.models import User
import re

def validate_register_form(username, email, password, confirm_password):
    """Trả về error string nếu có lỗi, None nếu hợp lệ"""

    if not all([username, email, password, confirm_password]):
        return 'Vui lòng nhập đầy đủ thông tin.'

    if len(username) < 3:
        return 'Tên đăng nhập phải có ít nhất 3 ký tự.'

    if not re.match(r'^[\w.@+-]+$', username):
        return 'Tên đăng nhập chỉ được chứa chữ cái, số và @/./+/-/_'

    if not re.match(r'^[^@]+@[^@]+\.[^@]+$', email):
        return 'Email không hợp lệ.'

    if len(password) < 8:
        return 'Mật khẩu phải có ít nhất 8 ký tự.'

    if password != confirm_password:
        return 'Mật khẩu xác nhận không khớp.'

    if User.objects.filter(username=username).exists():
        return 'Tên đăng nhập đã được sử dụng.'

    if User.objects.filter(email=email).exists():
        return 'Email đã được đăng ký.'

    return None