from django.shortcuts import render
from django.http import JsonResponse
from webgis.models.air_quality import AirQualityData
from webgis.models.uhi_data import UHIData
from webgis.models.water_quality import WaterQualityData
from django.utils import timezone
from datetime import timedelta

def analysis_view(request):
    return render(request, 'webgis/analysis.html')


def analysis_api(request):
    """Trả dữ liệu lịch sử từ DB cho biểu đồ"""
    days = int(request.GET.get('days', 7))
    since = timezone.now() - timedelta(days=days)

    air_qs = AirQualityData.objects.filter(
        timestamp__gte=since
    ).order_by('timestamp').values('timestamp', 'pm25', 'no2', 'co')

    uhi_qs = UHIData.objects.filter(
        timestamp__gte=since
    ).order_by('timestamp').values('timestamp', 'lst', 'ndvi')

    water_qs = WaterQualityData.objects.filter(
        timestamp__gte=since
    ).order_by('timestamp').values('timestamp', 'ndwi', 'mndwi')

    def fmt(qs):
        return [
            {
                'time': r['timestamp'].strftime('%d/%m %H:%M'),
                **{k: v for k, v in r.items() if k != 'timestamp'}
            }
            for r in qs
        ]

    return JsonResponse({
        'success': True,
        'air':   fmt(air_qs),
        'uhi':   fmt(uhi_qs),
        'water': fmt(water_qs),
    })


def analysis_monthly_api(request):
    """Lấy LST/NDVI theo từng tháng trong năm từ GEE — cho chart lịch sử"""
    import calendar
    from datetime import datetime
    from webgis.services.gee.uhi_service import get_lst_data

    year = int(request.GET.get('year', datetime.now().year))
    current_month = datetime.now().month if year == datetime.now().year else 12

    monthly = []
    for month in range(1, current_month + 1):
        # Lấy từ DB trước nếu có
        from django.db.models import Avg
        start = timezone.datetime(year, month, 1, tzinfo=timezone.utc)
        end_day = calendar.monthrange(year, month)[1]
        end = timezone.datetime(year, month, end_day, 23, 59, tzinfo=timezone.utc)

        uhi_avg = UHIData.objects.filter(
            timestamp__gte=start, timestamp__lte=end
        ).aggregate(lst=Avg('lst'), ndvi=Avg('ndvi'))

        if uhi_avg['lst']:
            monthly.append({
                'month': f'T{month}/{year}',
                'lst':   round(uhi_avg['lst'], 2),
                'ndvi':  round(uhi_avg['ndvi'] or 0, 4),
                'source': 'db'
            })
        else:
            # Fetch từ GEE nếu DB chưa có
            try:
                import ee
                from webgis.services.gee.gee_client import initialize_gee, get_hcmc_boundary
                initialize_gee()
                hcmc = get_hcmc_boundary()

                start_str = f'{year}-{month:02d}-01'
                end_str   = f'{year}-{month:02d}-{end_day}'

                landsat = (ee.ImageCollection('LANDSAT/LC08/C02/T1_L2')
                    .filterDate(start_str, end_str)
                    .filterBounds(hcmc)
                    .filter(ee.Filter.lt('CLOUD_COVER', 30)))

                def compute_lst(image):
                    lst  = image.select('ST_B10').multiply(0.00341802).add(149.0).subtract(273.15)
                    ndvi = image.normalizedDifference(['SR_B5', 'SR_B4'])
                    return image.addBands(lst.rename('LST')).addBands(ndvi.rename('NDVI'))

                result = (landsat.map(compute_lst).mean()
                    .reduceRegion(
                        reducer=ee.Reducer.mean(),
                        geometry=hcmc,
                        scale=100, maxPixels=1e13, bestEffort=True
                    ).getInfo())

                lst_val  = result.get('LST')
                ndvi_val = result.get('NDVI')

                if lst_val:
                    monthly.append({
                        'month': f'T{month}/{year}',
                        'lst':   round(lst_val, 2),
                        'ndvi':  round(ndvi_val or 0, 4),
                        'source': 'gee'
                    })
            except Exception:
                pass  # Bỏ qua tháng không có data

    return JsonResponse({'success': True, 'monthly': monthly, 'year': year})