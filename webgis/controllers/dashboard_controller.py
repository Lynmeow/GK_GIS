from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from webgis.services.gee.uhi_service import get_lst_data, get_lst_tile_url
from webgis.services.gee.air_service import get_air_quality_data, get_air_tile_url
from webgis.services.gee.water_service import get_water_quality_data, get_water_tile_url
from webgis.services.weather.openweather_service import get_current_weather, get_air_pollution

@login_required(login_url='login')
def dashboard_view(request):
    # Lấy dữ liệu từ GEE và OpenWeather
    weather = get_current_weather()
    air_pollution = get_air_pollution()
    lst_data = get_lst_data()
    water_data = get_water_quality_data()

    context = {
        'user': request.user,
        'weather': weather,
        'air_pollution': air_pollution,
        'lst_data': lst_data,
        'water_data': water_data,
    }
    return render(request, 'webgis/dashboard.html', context)


@login_required(login_url='login')
def map_view(request):
    map_type = request.GET.get('type', 'uhi')

    tile_url = ''
    if map_type == 'uhi':
        tile_url = get_lst_tile_url()
    elif map_type == 'air':
        tile_url = get_air_tile_url()
    elif map_type == 'water':
        tile_url = get_water_tile_url()

    context = {
        'tile_url': tile_url,
        'map_type': map_type,
    }
    return render(request, 'webgis/map/map.html', context)