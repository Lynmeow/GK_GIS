import ee
from .gee_client import initialize_gee, get_hcmc_boundary
from datetime import datetime, timedelta
from django.utils import timezone

def get_flood_data(days_back=30):
    initialize_gee()
    end_date = datetime.now().strftime('%Y-%m-%d')
    start_date = (datetime.now() - timedelta(days=days_back)).strftime('%Y-%m-%d')
    hcmc = get_hcmc_boundary()

    try:
        s1 = (ee.ImageCollection('COPERNICUS/S1_GRD')
            .filterDate(start_date, end_date)
            .filterBounds(hcmc)
            .filter(ee.Filter.eq('instrumentMode', 'IW'))
            .filter(ee.Filter.listContains('transmitterReceiverPolarisation', 'VV'))
            .select('VV'))

        result = (s1.mean()
            .reduceRegion(
                reducer=ee.Reducer.mean(),
                geometry=hcmc,
                scale=10,
                maxPixels=1e9
            ).getInfo())

        data = {
            'vv_backscatter': round(result.get('VV', 0), 4),
            'start_date': start_date,
            'end_date': end_date,
            'source': 'Sentinel-1 SAR'
        }

        from webgis.models.flood import FloodData
        FloodData.objects.create(
            source='sentinel1',
            timestamp=timezone.now(),
            vv_backscatter=data['vv_backscatter'],
        )

        return data

    except Exception as e:
        return {'error': str(e)}


def get_flood_tile_url(days_back=30):
    initialize_gee()
    end_date = datetime.now().strftime('%Y-%m-%d')
    start_date = (datetime.now() - timedelta(days=days_back)).strftime('%Y-%m-%d')
    hcmc = get_hcmc_boundary()

    s1 = (ee.ImageCollection('COPERNICUS/S1_GRD')
        .filterDate(start_date, end_date)
        .filterBounds(hcmc)
        .filter(ee.Filter.eq('instrumentMode', 'IW'))
        .filter(ee.Filter.listContains('transmitterReceiverPolarisation', 'VV'))
        .select('VV')
        .mean())

    vis_params = {
        'min': -25, 'max': 0,
        'palette': ['#03045E', '#0077B6', '#00B4D8', '#90E0EF', '#CAF0F8']
    }

    map_id = s1.getMapId(vis_params)
    return map_id['tile_fetcher'].url_format


# ── VV Backscatter theo từng quận ──
DISTRICTS_COORDS = {
    'Quận 1':     (10.7769, 106.7009),
    'Quận 3':     (10.7838, 106.6861),
    'Quận 7':     (10.7340, 106.7218),
    'Quận 12':    (10.8627, 106.6564),
    'Bình Chánh': (10.6746, 106.5956),
    'Hóc Môn':    (10.8914, 106.5929),
    'Thủ Đức':    (10.8600, 106.7515),
    'Bình Thạnh': (10.8119, 106.7106),
    'Gò Vấp':     (10.8383, 106.6658),
    'Nhà Bè':     (10.6910, 106.7381),
    'Cần Giờ':    (10.4110, 106.9529),
    'Củ Chi':     (11.0019, 106.4942),
}

def get_flood_by_district(days_back=30):
    """Lấy VV backscatter trung bình theo từng quận"""
    initialize_gee()
    end_date   = datetime.now().strftime('%Y-%m-%d')
    start_date = (datetime.now() - timedelta(days=days_back)).strftime('%Y-%m-%d')

    try:
        s1_mean = (ee.ImageCollection('COPERNICUS/S1_GRD')
            .filterDate(start_date, end_date)
            .filter(ee.Filter.eq('instrumentMode', 'IW'))
            .filter(ee.Filter.listContains('transmitterReceiverPolarisation', 'VV'))
            .select('VV')
            .mean())

        results = []
        for name, (lat, lng) in DISTRICTS_COORDS.items():
            # Tạo vùng buffer 3km quanh tâm quận
            point  = ee.Geometry.Point([lng, lat])
            buffer = point.buffer(3000)

            val = s1_mean.reduceRegion(
                reducer=ee.Reducer.mean(),
                geometry=buffer,
                scale=100,
                maxPixels=1e8,
                bestEffort=True,
            ).get('VV').getInfo()

            vv = round(val, 2) if val else -15.0

            # Tính flood risk: VV càng thấp (âm nhiều) → nguy cơ ngập càng cao
            # Thang: < -18 dB = nguy hiểm, -18 to -12 = trung bình, > -12 = an toàn
            if vv < -18:
                risk = 'high'
                risk_label = 'Nguy cơ cao'
            elif vv < -12:
                risk = 'medium'
                risk_label = 'Trung bình'
            else:
                risk = 'low'
                risk_label = 'Thấp'

            results.append({
                'name': name,
                'lat': lat,
                'lng': lng,
                'vv': vv,
                'risk': risk,
                'risk_label': risk_label,
            })

        return results

    except Exception as e:
        return {'error': str(e)}