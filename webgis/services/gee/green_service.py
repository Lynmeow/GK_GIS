import ee
from .gee_client import initialize_gee, get_hcmc_boundary
from datetime import datetime, timedelta
from django.utils import timezone

def get_ndvi_data(days_back=30):
    initialize_gee()
    end_date = datetime.now().strftime('%Y-%m-%d')
    start_date = (datetime.now() - timedelta(days=days_back)).strftime('%Y-%m-%d')
    hcmc = get_hcmc_boundary()

    try:
        s2 = (ee.ImageCollection('COPERNICUS/S2_SR_HARMONIZED')
            .filterDate(start_date, end_date)
            .filterBounds(hcmc)
            .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', 20)))

        def compute_ndvi(image):
            ndvi = image.normalizedDifference(['B8', 'B4']).rename('NDVI')
            evi  = image.expression(
                '2.5 * ((NIR - RED) / (NIR + 6 * RED - 7.5 * BLUE + 1))',
                {'NIR': image.select('B8'), 'RED': image.select('B4'), 'BLUE': image.select('B2')}
            ).rename('EVI')
            return image.addBands(ndvi).addBands(evi)

        result = (s2.map(compute_ndvi).mean()
    .reduceRegion(
        reducer=ee.Reducer.mean(),
        geometry=hcmc,
        scale=100,
        maxPixels=1e13,
        bestEffort=True,
    ).getInfo())

        data = {
            'ndvi': round(result.get('NDVI', 0), 4),
            'evi':  round(result.get('EVI', 0), 4),
            'start_date': start_date,
            'end_date': end_date,
            'source': 'Sentinel-2'
        }

        from webgis.models.green_space import GreenSpaceData
        GreenSpaceData.objects.create(
            source='sentinel2',
            timestamp=timezone.now(),
            ndvi=data['ndvi'],
            evi=data['evi'],
        )

        return data

    except Exception as e:
        return {'error': str(e)}


def get_ndvi_tile_url(days_back=90):
    initialize_gee()
    end_date = datetime.now().strftime('%Y-%m-%d')
    start_date = (datetime.now() - timedelta(days=days_back)).strftime('%Y-%m-%d')
    hcmc = get_hcmc_boundary()

    s2 = (ee.ImageCollection('COPERNICUS/S2_SR_HARMONIZED')
        .filterDate(start_date, end_date)
        .filterBounds(hcmc)
        .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', 20))
        .map(lambda img: img.addBands(
            img.normalizedDifference(['B8', 'B4']).rename('NDVI')
        ))
        .select('NDVI')
        .mean())

    vis_params = {
        'min': -0.2, 'max': 0.8,
        'palette': ['#C1121F', '#FFD60A', '#AACC00', '#06D6A0', '#03045E']
    }

    map_id = s2.getMapId(vis_params)
    return map_id['tile_fetcher'].url_format