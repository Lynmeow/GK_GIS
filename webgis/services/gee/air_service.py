import ee
from .gee_client import initialize_gee, get_hcmc_boundary
from datetime import datetime, timedelta

def get_air_quality_data(days_back=7):
    """Lấy dữ liệu NO₂, CO từ Sentinel-5P"""
    initialize_gee()
    
    end_date = datetime.now().strftime('%Y-%m-%d')
    start_date = (datetime.now() - timedelta(days=days_back)).strftime('%Y-%m-%d')
    hcmc = get_hcmc_boundary()

    try:
        # NO2 từ Sentinel-5P
        no2 = (ee.ImageCollection('COPERNICUS/S5P/NRTI/L3_NO2')
            .filterDate(start_date, end_date)
            .filterBounds(hcmc)
            .select('NO2_column_number_density')
            .mean()
            .reduceRegion(
                reducer=ee.Reducer.mean(),
                geometry=hcmc,
                scale=1000,
                maxPixels=1e9
            ).getInfo())

        # CO từ Sentinel-5P
        co = (ee.ImageCollection('COPERNICUS/S5P/NRTI/L3_CO')
            .filterDate(start_date, end_date)
            .filterBounds(hcmc)
            .select('CO_column_number_density')
            .mean()
            .reduceRegion(
                reducer=ee.Reducer.mean(),
                geometry=hcmc,
                scale=1000,
                maxPixels=1e9
            ).getInfo())

        return {
            'no2': round(no2.get('NO2_column_number_density', 0) * 1e6, 4),  # mol/m² → µmol/m²
            'co': round(co.get('CO_column_number_density', 0), 4),
            'start_date': start_date,
            'end_date': end_date,
            'source': 'Sentinel-5P'
        }
    except Exception as e:
        return {'error': str(e)}


def get_air_tile_url(days_back=7):
    """Lấy tile URL để hiển thị trên Leaflet"""
    initialize_gee()

    end_date = datetime.now().strftime('%Y-%m-%d')
    start_date = (datetime.now() - timedelta(days=days_back)).strftime('%Y-%m-%d')
    hcmc = get_hcmc_boundary()

    no2_image = (ee.ImageCollection('COPERNICUS/S5P/NRTI/L3_NO2')
        .filterDate(start_date, end_date)
        .filterBounds(hcmc)
        .select('NO2_column_number_density')
        .mean())

    vis_params = {
        'min': 0,
        'max': 0.0002,
        'palette': ['green', 'yellow', 'orange', 'red', 'purple']
    }

    map_id = no2_image.getMapId(vis_params)
    return map_id['tile_fetcher'].url_format