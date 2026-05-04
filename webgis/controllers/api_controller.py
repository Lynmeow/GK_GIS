from django.http import JsonResponse
from webgis.services.gee.air_service import get_air_tile_url, get_air_quality_data
from webgis.services.gee.uhi_service import get_lst_tile_url, get_lst_data
from webgis.services.gee.water_service import get_water_tile_url, get_water_quality_data
from webgis.services.gee.green_service import get_ndvi_tile_url, get_ndvi_data
from webgis.services.gee.flood_service import get_flood_tile_url, get_flood_data
from ..services.gee.uhi_service import get_satellite_image_info
from webgis.services.weather.district_service import get_risk_classification, get_districts_air_quality
from webgis.services.weather.openweather_service import get_current_weather, get_air_pollution
from ..services.gee.flood_service import get_flood_by_district


def public_stations_api(request):
    from webgis.models.monitoring_station import MonitoringStation
    qs = MonitoringStation.objects.filter(status='active').values(
        'id', 'name', 'station_code', 'station_type',
        'district', 'address', 'latitude', 'longitude', 'status',
    )
    return JsonResponse({'success': True, 'stations': list(qs)})


def flood_district_api(request):
    days_back = int(request.GET.get('days', 30))
    data = get_flood_by_district(days_back)
    return JsonResponse({'success': True, 'districts': data})


def districts_api(request):
    try:
        data = get_districts_air_quality()
        return JsonResponse({'success': True, 'districts': data})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


def weather_api(request):
    try:
        weather = get_current_weather()
        air     = get_air_pollution()
        return JsonResponse({'success': True, 'weather': weather, 'air': air})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


def gee_tile_api(request):
    layer     = request.GET.get('layer', 'air')
    days_back = int(request.GET.get('days', 7))
    try:
        if layer == 'air':
            tile_url = get_air_tile_url(days_back)
            data     = get_air_quality_data(days_back)
        elif layer == 'lst':
            tile_url = get_lst_tile_url(90)
            data     = get_lst_data(90)
        elif layer == 'water':
            tile_url = get_water_tile_url(days_back)
            data     = get_water_quality_data(days_back)
        elif layer == 'ndvi':
            tile_url = get_ndvi_tile_url(90)
            data     = get_ndvi_data(90)
        elif layer == 'flood':
            tile_url = get_flood_tile_url(days_back)
            data     = get_flood_data(days_back)
        else:
            return JsonResponse({'error': 'Layer không hợp lệ'}, status=400)
        return JsonResponse({'success': True, 'tile_url': tile_url, 'data': data, 'layer': layer})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


def air_quality_api(request):
    days_back = int(request.GET.get('days', 7))
    try:
        data = get_air_quality_data(days_back)
        return JsonResponse({'success': True, 'data': data})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


def uhi_api(request):
    days_back = int(request.GET.get('days', 30))
    try:
        data = get_lst_data(days_back)
        return JsonResponse({'success': True, 'data': data})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


def water_api(request):
    days_back = int(request.GET.get('days', 30))
    try:
        data = get_water_quality_data(days_back)
        return JsonResponse({'success': True, 'data': data})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


def satellite_image_api(request):
    band_type = request.GET.get('type', 'rgb')
    month     = request.GET.get('month')
    year      = request.GET.get('year')
    data = get_satellite_image_info(band_type=band_type, month=month, year=year)
    return JsonResponse({'success': True, 'data': data})


def risk_api(request):
    try:
        data = get_risk_classification()
        return JsonResponse({'success': True, 'districts': data})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


def _user_is_admin(user):
    if not user.is_authenticated:
        return False
    profile = getattr(user, 'profile', None)
    return profile is not None and profile.is_admin()


def proposals_api(request):
    """Admin xem danh sách đề xuất giải pháp"""
    if not _user_is_admin(request.user):
        return JsonResponse({'success': False, 'error': 'Unauthorized'}, status=403)
    try:
        from webgis.models.proposal import Proposal
        qs   = Proposal.objects.select_related('author').order_by('-created_at')
        data = [{
            'id':                   p.id,
            'author':               p.author.username,
            'district_name':        p.district_name,
            'problem_type':         p.problem_type,
            'problem_type_display': p.get_problem_type_display(),
            'solution':             p.solution,
            'evidence':             p.evidence,
            'status':               p.status,
            'admin_note':           p.admin_note,
            'created_at':           p.created_at.strftime('%d/%m/%Y %H:%M'),
        } for p in qs]
        return JsonResponse({'success': True, 'proposals': data})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


def review_proposal_api(request):
    """Admin duyệt hoặc từ chối đề xuất"""
    if not _user_is_admin(request.user):
        return JsonResponse({'success': False, 'error': 'Unauthorized'}, status=403)
    if request.method != 'POST':
        return JsonResponse({'success': False}, status=405)
    try:
        import json as json_lib
        from django.utils import timezone
        from webgis.models.proposal import Proposal
        body = json_lib.loads(request.body)
        p = Proposal.objects.get(id=body.get('id'))
        p.status      = body.get('action')  # 'approved' or 'rejected'
        p.admin_note  = body.get('note', '')
        p.reviewed_at = timezone.now()
        p.save()
        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})