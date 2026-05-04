from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from webgis.models.alert import Alert
from webgis.services.weather.openweather_service import get_air_pollution


def alert_view(request):
    return render(request, 'webgis/alert.html')


def alert_api(request):
    auto_alerts = []
    try:
        air = get_air_pollution()
        if not air.get('error'):
            if air['aqi'] > 100:
                auto_alerts.append({
                    'title':       f'AQI vượt ngưỡng: {air["aqi"]}',
                    'description': f'Chỉ số AQI tại TPHCM đang ở mức {air["aqi"]} — Không tốt cho sức khỏe',
                    'level':       'danger' if air['aqi'] > 150 else 'warning',
                    'type':        'air',
                    'value':       air['aqi'],
                    'threshold':   100,
                })
            if air['pm25'] > 25:
                auto_alerts.append({
                    'title':       f'PM2.5 vượt ngưỡng WHO: {air["pm25"]} µg/m³',
                    'description': f'PM2.5 = {air["pm25"]} µg/m³ vượt ngưỡng WHO (25 µg/m³)',
                    'level':       'danger' if air['pm25'] > 50 else 'warning',
                    'type':        'air',
                    'value':       air['pm25'],
                    'threshold':   25,
                })
    except Exception:
        pass

    db_alerts = list(Alert.objects.filter(is_active=True).values(
        'id', 'title', 'description', 'level', 'alert_type',
        'district', 'value', 'threshold', 'created_at'
    ))
    for a in db_alerts:
        a['created_at'] = a['created_at'].strftime('%d/%m/%Y %H:%M')

    return JsonResponse({
        'success':     True,
        'auto_alerts': auto_alerts,
        'db_alerts':   db_alerts,
        'total':       len(auto_alerts) + len(db_alerts),
    })


@login_required
def create_alert(request):
    if request.method == 'POST':
        Alert.objects.create(
            title=request.POST.get('title'),
            description=request.POST.get('description'),
            level=request.POST.get('level', 'warning'),
            alert_type=request.POST.get('alert_type', 'other'),
            district=request.POST.get('district', ''),
            created_by=request.user,
        )
    return redirect('alert')


@login_required
def submit_proposal(request):
    if request.method == 'POST':
        try:
            from webgis.models.proposal import Proposal
            Proposal.objects.create(
                author        = request.user,
                district_name = request.POST.get('district_name', '').strip(),
                alert_type    = request.POST.get('alert_type', ''),
                problem_type  = request.POST.get('problem_type', 'combined'),
                solution      = request.POST.get('solution', '').strip(),
                evidence      = request.POST.get('evidence', '').strip(),
            )
            messages.success(request, '✅ Đề xuất đã được gửi thành công! Admin sẽ xem xét sớm.')
        except Exception as e:
            messages.error(request, f'❌ Lỗi khi gửi đề xuất: {str(e)}')
    return redirect('alert')