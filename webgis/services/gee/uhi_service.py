import ee
from .gee_client import initialize_gee, get_hcmc_boundary
from datetime import datetime, timedelta


def get_lst_data(days_back=30):
    initialize_gee()
    end_date = datetime.now().strftime('%Y-%m-%d')
    start_date = (datetime.now() - timedelta(days=days_back)).strftime('%Y-%m-%d')
    hcmc = get_hcmc_boundary()
    try:
        landsat = (ee.ImageCollection('LANDSAT/LC08/C02/T1_L2')
            .filterDate(start_date, end_date)
            .filterBounds(hcmc)
            .filter(ee.Filter.lt('CLOUD_COVER', 20)))
        def compute_lst(image):
            lst = image.select('ST_B10').multiply(0.00341802).add(149.0).subtract(273.15)
            ndvi = image.normalizedDifference(['SR_B5', 'SR_B4'])
            ndbi = image.normalizedDifference(['SR_B6', 'SR_B5'])
            return image.addBands(lst.rename('LST')).addBands(ndvi.rename('NDVI')).addBands(ndbi.rename('NDBI'))
        result = (landsat.map(compute_lst).mean()
            .reduceRegion(reducer=ee.Reducer.mean(), geometry=hcmc, scale=100, maxPixels=1e13, bestEffort=True)
            .getInfo())

        data = {
            'lst':  round(result.get('LST', 0), 2),
            'ndvi': round(result.get('NDVI', 0), 4),
            'ndbi': round(result.get('NDBI', 0), 4),
            'start_date': start_date, 'end_date': end_date, 'source': 'Landsat 8'
        }

        # Ghi vào DB nếu có data hợp lệ
        if data['lst'] and data['lst'] != 0:
            try:
                from django.utils import timezone
                from webgis.models.uhi_data import UHIData
                six_hours_ago = timezone.now() - timedelta(hours=6)
                if not UHIData.objects.filter(timestamp__gte=six_hours_ago).exists():
                    UHIData.objects.create(
                        timestamp=timezone.now(),
                        lst=data['lst'],
                        ndvi=data['ndvi'],
                        ndbi=data['ndbi'],
                        source='landsat8',
                    )
            except Exception:
                pass

        return data
    except Exception as e:
        return {'error': str(e)}


def get_lst_tile_url(days_back=30):
    initialize_gee()
    end_date = datetime.now().strftime('%Y-%m-%d')
    start_date = (datetime.now() - timedelta(days=days_back)).strftime('%Y-%m-%d')
    hcmc = get_hcmc_boundary()
    landsat = (ee.ImageCollection('LANDSAT/LC08/C02/T1_L2')
        .filterDate(start_date, end_date)
        .filterBounds(hcmc)
        .filter(ee.Filter.lt('CLOUD_COVER', 20))
        .map(lambda img: img.addBands(
            img.select('ST_B10').multiply(0.00341802).add(149.0).subtract(273.15).rename('LST')))
        .select('LST').mean())
    vis_params = {'min': 25, 'max': 45, 'palette': ['blue', 'cyan', 'yellow', 'orange', 'red']}
    map_id = landsat.getMapId(vis_params)
    return map_id['tile_fetcher'].url_format


HCMC_COORDS = [
    [106.3539, 10.3467], [107.0312, 10.3467],
    [107.0312, 11.1600], [106.3539, 11.1600],
    [106.3539, 10.3467],
]


def get_satellite_image_info(band_type='rgb', month=None, year=None, days_back=60):
    initialize_gee()
    if month and year:
        import calendar
        year, month = int(year), int(month)
        start_date = f'{year}-{month:02d}-01'
        last_day   = calendar.monthrange(year, month)[1]
        end_date   = f'{year}-{month:02d}-{last_day}'
    else:
        end_date   = datetime.now().strftime('%Y-%m-%d')
        start_date = (datetime.now() - timedelta(days=days_back)).strftime('%Y-%m-%d')
    hcmc = get_hcmc_boundary()
    try:
        if band_type == 'tir':
            return _get_tir_image(hcmc, start_date, end_date)
        else:
            return _get_sentinel2_image(hcmc, start_date, end_date, band_type)
    except Exception as e:
        return {'error': str(e)}


def _get_sentinel2_image(hcmc, start_date, end_date, band_type='rgb'):
    collection = (ee.ImageCollection('COPERNICUS/S2_SR_HARMONIZED')
        .filterDate(start_date, end_date)
        .filterBounds(hcmc)
        .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', 50))
        .sort('system:time_start', False)
        .limit(10))
    try:
        first_props = collection.first().get('system:time_start').getInfo()
        date_str    = datetime.fromtimestamp(first_props / 1000).strftime('%d/%m/%Y')
        cloud_info  = collection.first().get('CLOUDY_PIXEL_PERCENTAGE').getInfo()
        cloud_pct   = round(cloud_info, 1) if cloud_info else 0
    except Exception:
        date_str  = start_date
        cloud_pct = 0
    image = collection.mosaic()
    if band_type == 'ndvi':
        vis_image  = image.normalizedDifference(['B8', 'B4']).rename('NDVI')
        vis_params = {'min': -0.2, 'max': 0.8, 'palette': ['#d73027','#f46d43','#fdae61','#fee08b','#d9ef8b','#a6d96a','#66bd63','#1a9850']}
    else:
        vis_image  = image.select(['B4', 'B3', 'B2'])
        vis_params = {'min': 0, 'max': 3000, 'gamma': 1.4}
    map_id   = vis_image.getMapId(vis_params)
    tile_url = map_id['tile_fetcher'].url_format
    hcmc_geom   = ee.Geometry.Polygon([HCMC_COORDS])
    vis_clipped = vis_image.clip(hcmc_geom)
    thumb_params = {'region': HCMC_COORDS, 'dimensions': 200, 'format': 'png'}
    thumb_params.update(vis_params)
    thumb_url = vis_clipped.getThumbURL(thumb_params)
    dl_image = image.select(['B4', 'B3', 'B2']) if band_type == 'rgb' else vis_image
    download_url = dl_image.clip(hcmc_geom).getDownloadURL({'region': HCMC_COORDS, 'scale': 100, 'format': 'GEO_TIFF'})
    return {'success': True, 'band_type': band_type, 'tile_url': tile_url, 'thumb_url': thumb_url, 'download_url': download_url, 'date': date_str, 'cloud_pct': cloud_pct, 'source': 'Sentinel-2 SR', 'resolution': '10m/px'}


def _get_tir_image(hcmc, start_date, end_date):
    landsat = (ee.ImageCollection('LANDSAT/LC08/C02/T1_L2')
        .filterDate(start_date, end_date)
        .filterBounds(hcmc)
        .filter(ee.Filter.lt('CLOUD_COVER', 20))
        .map(lambda img: img.addBands(img.select('ST_B10').multiply(0.00341802).add(149.0).subtract(273.15).rename('LST')))
        .sort('CLOUD_COVER'))
    image    = landsat.first()
    lst_band = image.select('LST')
    props      = image.getInfo()['properties']
    image_date = props.get('system:time_start', 0)
    cloud_pct  = round(props.get('CLOUD_COVER', 0), 1)
    date_str   = datetime.fromtimestamp(image_date / 1000).strftime('%d/%m/%Y')
    vis_params = {'min': 25, 'max': 45, 'palette': ['#313695','#4575b4','#74add1','#abd9e9','#e0f3f8','#fee090','#fdae61','#f46d43','#d73027','#a50026']}
    map_id    = lst_band.getMapId(vis_params)
    tile_url  = map_id['tile_fetcher'].url_format
    hcmc_geom    = ee.Geometry.Polygon([HCMC_COORDS])
    lst_clipped  = lst_band.clip(hcmc_geom)
    thumb_params = {'region': HCMC_COORDS, 'dimensions': 200, 'format': 'png'}
    thumb_params.update(vis_params)
    thumb_url    = lst_clipped.getThumbURL(thumb_params)
    download_url = lst_clipped.getDownloadURL({'region': HCMC_COORDS, 'scale': 100, 'format': 'GEO_TIFF'})
    return {'success': True, 'band_type': 'tir', 'tile_url': tile_url, 'thumb_url': thumb_url, 'download_url': download_url, 'date': date_str, 'cloud_pct': cloud_pct, 'source': 'Landsat 8 TIR', 'resolution': '30m/px'}