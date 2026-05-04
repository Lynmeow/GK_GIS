from django.shortcuts import redirect
from functools import wraps

def role_required(*roles):
    """Decorator kiểm tra role người dùng"""
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('login')
            profile = getattr(request.user, 'profile', None)
            if profile and profile.role in roles:
                return view_func(request, *args, **kwargs)
            return redirect('dashboard')  # Không đủ quyền
        return wrapper
    return decorator