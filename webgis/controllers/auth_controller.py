from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from webgis.models.user_profile import UserProfile


def _is_admin(user):
    profile = getattr(user, 'profile', None)
    return profile is not None and profile.is_admin()


def login_view(request):
    if request.user.is_authenticated:
        if _is_admin(request.user):
            return redirect('dashboard')
        return redirect('home')

    context = {'error': None, 'app_error': None, 'app_success': False}

    # ── Xử lý form nộp đơn nghiên cứu sinh ──
    if request.method == 'POST' and request.POST.get('apply'):
        full_name   = request.POST.get('full_name', '').strip()
        email       = request.POST.get('email', '').strip()
        institution = request.POST.get('institution', '').strip()
        purpose     = request.POST.get('purpose', '').strip()

        if not all([full_name, email, institution, purpose]):
            context['app_error'] = 'Vui lòng điền đầy đủ tất cả các trường.'
        else:
            try:
                from webgis.models.research_application import ResearchApplication
                # Kiểm tra email đã nộp đơn chưa
                if ResearchApplication.objects.filter(email=email, status='pending').exists():
                    context['app_error'] = 'Email này đã có đơn đang chờ xét duyệt.'
                else:
                    ResearchApplication.objects.create(
                        full_name=full_name,
                        email=email,
                        institution=institution,
                        purpose=purpose,
                    )
                    context['app_success'] = True
            except Exception as e:
                context['app_error'] = f'Lỗi hệ thống: {str(e)}'

        return render(request, 'webgis/login.html', context)

    # ── Xử lý đăng nhập ──
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '').strip()

        if not username or not password:
            context['error'] = 'Vui lòng nhập đầy đủ thông tin.'
        else:
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                if _is_admin(user):
                    return redirect('dashboard')
                else:
                    return redirect('home')
            else:
                context['error'] = 'Sai tên đăng nhập hoặc mật khẩu.'

    return render(request, 'webgis/login.html', context)


@login_required(login_url='login')
def dashboard_view(request):
    if not _is_admin(request.user):
        return redirect('home')
    context = {
        'user':    request.user,
        'profile': getattr(request.user, 'profile', None),
    }
    return render(request, 'webgis/dashboard.html', context)


def logout_view(request):
    if request.method == 'POST':
        logout(request)
        return redirect('home')
    return redirect('home')