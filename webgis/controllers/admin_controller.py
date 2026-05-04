from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone
from functools import wraps
from webgis.models import UserProfile, MonitoringStation, Proposal
from auditlog.models import LogEntry


def admin_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        try:
            if not request.user.profile.is_admin():
                return render(request, 'webgis/403.html', status=403)
        except UserProfile.DoesNotExist:
            return render(request, 'webgis/403.html', status=403)
        return view_func(request, *args, **kwargs)
    return wrapper


@admin_required
def admin_dashboard(request):
    context = {
        'total_users':       User.objects.count(),
        'total_stations':    MonitoringStation.objects.count(),
        'active_stations':   MonitoringStation.objects.filter(status='active').count(),
        'total_admins':      UserProfile.objects.filter(role='admin').count(),
        'total_researchers': UserProfile.objects.filter(role='researcher').count(),
        'total_viewers':     UserProfile.objects.filter(role='viewer').count(),
        'recent_users':      User.objects.select_related('profile').order_by('-date_joined')[:5],
    }
    return render(request, 'webgis/admin/dashboard.html', context)


@admin_required
def admin_users(request):
    users = User.objects.select_related('profile').order_by('-date_joined')
    return render(request, 'webgis/admin/users.html', {'users': users})


@admin_required
def admin_user_create(request):
    if request.method == 'POST':
        username     = request.POST.get('username', '').strip()
        email        = request.POST.get('email', '').strip()
        password     = request.POST.get('password', '')
        role         = request.POST.get('role', 'viewer')
        organization = request.POST.get('organization', '').strip()
        phone        = request.POST.get('phone', '').strip()

        if len(password) < 8:
            messages.error(request, 'Mật khẩu phải có ít nhất 8 ký tự.')
            return redirect('admin_users')
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Tên đăng nhập đã tồn tại.')
            return redirect('admin_users')
        if role == 'admin' and not request.user.profile.is_owner:
            messages.error(request, 'Chỉ owner mới có thể tạo tài khoản admin.')
            return redirect('admin_users')

        user = User.objects.create_user(username=username, email=email, password=password)
        UserProfile.objects.create(user=user, role=role, organization=organization, phone=phone)
        messages.success(request, f'Tạo tài khoản {username} thành công.')
    return redirect('admin_users')


@admin_required
def admin_user_edit(request, user_id):
    user    = get_object_or_404(User, id=user_id)
    profile = get_object_or_404(UserProfile, user=user)

    if request.method == 'POST':
        user.email     = request.POST.get('email', '').strip()
        user.is_active = request.POST.get('is_active') == 'on'
        new_password   = request.POST.get('password', '').strip()

        if new_password:
            if len(new_password) < 8:
                messages.error(request, 'Mật khẩu mới phải có ít nhất 8 ký tự.')
                return redirect('admin_users')
            user.set_password(new_password)

        user.save()

        new_role = request.POST.get('role', 'viewer')
        if new_role == 'admin' and not request.user.profile.is_owner:
            messages.error(request, 'Chỉ owner mới có thể nâng quyền admin.')
            return redirect('admin_users')

        profile.role         = new_role
        profile.organization = request.POST.get('organization', '').strip()
        profile.phone        = request.POST.get('phone', '').strip()
        profile.save()

        messages.success(request, f'Cập nhật tài khoản {user.username} thành công.')
        return redirect('admin_users')

    return render(request, 'webgis/admin/user_edit.html', {'edit_user': user, 'profile': profile})


@admin_required
def admin_user_delete(request, user_id):
    user = get_object_or_404(User, id=user_id)
    if user == request.user:
        messages.error(request, 'Không thể xóa tài khoản đang đăng nhập.')
        return redirect('admin_users')
    if user.profile.role == 'admin' and not request.user.profile.is_owner:
        messages.error(request, 'Chỉ owner mới có thể xóa tài khoản admin.')
        return redirect('admin_users')
    username = user.username
    user.delete()
    messages.success(request, f'Đã xóa tài khoản {username}.')
    return redirect('admin_users')


@admin_required
def admin_stations(request):
    stations = MonitoringStation.objects.all().order_by('station_code')
    return render(request, 'webgis/admin/stations.html', {'stations': stations})


@admin_required
def admin_station_create(request):
    if request.method == 'POST':
        try:
            MonitoringStation.objects.create(
                name         = request.POST.get('name'),
                station_code = request.POST.get('station_code'),
                station_type = request.POST.get('station_type'),
                district     = request.POST.get('district'),
                address      = request.POST.get('address', ''),
                latitude     = float(request.POST.get('latitude')),
                longitude    = float(request.POST.get('longitude')),
                status       = request.POST.get('status', 'active'),
            )
            messages.success(request, 'Thêm trạm quan trắc thành công.')
        except Exception as e:
            messages.error(request, f'Lỗi: {str(e)}')
    return redirect('admin_stations')


@admin_required
def admin_station_edit(request, station_id):
    station = get_object_or_404(MonitoringStation, id=station_id)
    if request.method == 'POST':
        try:
            station.name         = request.POST.get('name')
            station.station_code = request.POST.get('station_code')
            station.station_type = request.POST.get('station_type')
            station.district     = request.POST.get('district')
            station.address      = request.POST.get('address', '')
            station.latitude     = float(request.POST.get('latitude'))
            station.longitude    = float(request.POST.get('longitude'))
            station.status       = request.POST.get('status', 'active')
            station.save()
            messages.success(request, 'Cập nhật trạm thành công.')
        except Exception as e:
            messages.error(request, f'Lỗi: {str(e)}')
        return redirect('admin_stations')
    return render(request, 'webgis/admin/station_edit.html', {'station': station})


@admin_required
def admin_station_delete(request, station_id):
    station = get_object_or_404(MonitoringStation, id=station_id)
    name = station.name
    station.delete()
    messages.success(request, f'Đã xóa trạm {name}.')
    return redirect('admin_stations')


@admin_required
def admin_proposals(request):
    proposals = Proposal.objects.select_related('author').order_by('-created_at')
    return render(request, 'webgis/admin/proposals.html', {'proposals': proposals})


@admin_required
def admin_proposal_review(request, proposal_id):
    proposal = get_object_or_404(Proposal, id=proposal_id)
    if request.method == 'POST':
        action = request.POST.get('action')
        note   = request.POST.get('note', '')
        if action in ['approved', 'rejected']:
            proposal.status      = action
            proposal.admin_note  = note
            proposal.reviewed_at = timezone.now()
            proposal.save()
            messages.success(request, f'Đã {"duyệt" if action == "approved" else "từ chối"} đề xuất.')
    return redirect('admin_proposals')


@admin_required
def admin_audit_log(request):
    logs = LogEntry.objects.all().select_related('actor', 'content_type').order_by('-timestamp')

    action = request.GET.get('action', '')
    if action in ['0', '1', '2']:
        logs = logs.filter(action=action)

    obj_type = request.GET.get('type', '')
    if obj_type:
        logs = logs.filter(content_type__model=obj_type)

    search = request.GET.get('search', '')
    if search:
        logs = logs.filter(actor__username__icontains=search)

    object_types = LogEntry.objects.values_list(
        'content_type__model', flat=True
    ).distinct().order_by('content_type__model')

    return render(request, 'webgis/admin/audit_log.html', {
        'logs':           logs[:200],
        'object_types':   object_types,
        'current_action': action,
        'current_type':   obj_type,
        'current_search': search,
    })


@admin_required
def admin_stations_api(request):
    stations = MonitoringStation.objects.all()
    data = [{
        'id':           s.id,
        'name':         s.name,
        'station_code': s.station_code,
        'station_type': s.station_type,
        'district':     s.district,
        'latitude':     s.latitude,
        'longitude':    s.longitude,
        'status':       s.status,
    } for s in stations]
    return JsonResponse({'stations': data})

@admin_required
def admin_proposal_revert(request, pk):
    if request.method == 'POST':
        proposal = get_object_or_404(Proposal, pk=pk)
        proposal.status = 'pending'
        proposal.admin_note = ''
        proposal.save()
        messages.success(request, 'Đã hoàn tác đề xuất về Chờ duyệt')
    return redirect('admin_proposals')

@admin_required
def admin_about_edit(request):
    from webgis.models import SiteConfig
    c = SiteConfig.get_config()
    if request.method == 'POST':
        fields = [
            'hero_subtitle', 'about_desc',
            'mission1_title', 'mission1_desc', 'mission2_title', 'mission2_desc',
            'mission3_title', 'mission3_desc', 'mission4_title', 'mission4_desc',
            'module1_title', 'module1_desc', 'module2_title', 'module2_desc',
            'module3_title', 'module3_desc', 'module4_title', 'module4_desc',
            'module5_title', 'module5_desc', 'module6_title', 'module6_desc',
            'module7_title', 'module7_desc',
            'index1_name', 'index1_desc', 'index2_name', 'index2_desc',
            'index3_name', 'index3_desc', 'index4_name', 'index4_desc',
            'index5_name', 'index5_desc', 'index6_name', 'index6_desc',
            'contact_desc',
        ]
        for f in fields:
            setattr(c, f, request.POST.get(f, ''))
        c.save()
        messages.success(request, 'Đã lưu thay đổi trang Giới thiệu.')
        return redirect('admin_about_edit')
    return render(request, 'webgis/admin/about_edit.html', {'c': c})


def about(request):
    from webgis.models import SiteConfig
    c = SiteConfig.get_config()
    return render(request, 'webgis/about.html', {'c': c})
