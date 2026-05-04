import ee
from .gee_client import initialize_gee, get_hcmc_boundary
from datetime import datetime, timedelta

HCMC_COORDS = [
    [106.3539, 10.3467], [107.0312, 10.3467],
    [107.0312, 11.1600], [106.3539, 11.1600],
    [106.3539, 10.3467],
]

def get_water_quality_data(days_back=30):
    initialize_gee()
    end_date   = datetime.now().strftime('%Y-%m-%d')
    start_date = (datetime.now() - timedelta(days=days_back)).strftime('%Y-%m-%d')
    hcmc = get_hcmc_boundary()
    try:
        s2 = (ee.ImageCollection('COPERNICUS/S2_SR_HARMONIZED')
            .filterDate(start_date, end_date)
            .filterBounds(hcmc)
            .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', 20)))

        def compute_indices(image):
            ndwi  = image.normalizedDifference(['B3', 'B8']).rename('NDWI')
            mndwi = image.normalizedDifference(['B3', 'B11']).rename('MNDWI')
            return image.addBands(ndwi).addBands(mndwi)

        result = (s2.map(compute_indices).mean()
            .reduceRegion(
                reducer=ee.Reducer.mean(),
                geometry=hcmc,
                scale=100,
                maxPixels=1e9,
                bestEffort=True,
            ).getInfo())

        data = {
            'ndwi':       round(result.get('NDWI', 0), 4),
            'mndwi':      round(result.get('MNDWI', 0), 4),
            'start_date': start_date,
            'end_date':   end_date,
            'source':     'Sentinel-2'
        }

        if data['ndwi'] and data['ndwi'] != 0:
            try:
                from django.utils import timezone
                from webgis.models.water_quality import WaterQualityData
                six_hours_ago = timezone.now() - timedelta(hours=6)
                if not WaterQualityData.objects.filter(timestamp__gte=six_hours_ago).exists():
                    WaterQualityData.objects.create(
                        timestamp=timezone.now(),
                        ndwi=data['ndwi'],
                        mndwi=data['mndwi'],
                        source='sentinel2',
                    )
            except Exception:
                pass

        return data
    except Exception as e:
        return {'error': str(e)}


def get_water_tile_url(days_back=30):
    initialize_gee()
    end_date   = datetime.now().strftime('%Y-%m-%d')
    start_date = (datetime.now() - timedelta(days=days_back)).strftime('%Y-%m-%d')
    hcmc       = get_hcmc_boundary()
    hcmc_geom  = ee.Geometry.Polygon([HCMC_COORDS])

    s2 = (ee.ImageCollection('COPERNICUS/S2_SR_HARMONIZED')
        .filterDate(start_date, end_date)
        .filterBounds(hcmc)
        .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', 20))
        .map(lambda img: img.addBands(
            img.normalizedDifference(['B3', 'B8']).rename('NDWI')
        ))
        .select('NDWI')
        .mean()
        .clip(hcmc_geom))

    vis_params = {
        'min': -0.3, 'max': 0.6,
        'palette': ['#8B4513', '#F5DEB3', '#87CEEB', '#0077B6', '#03045E']
    }

    map_id = s2.getMapId(vis_params)
    return map_id['tile_fetcher'].url_format