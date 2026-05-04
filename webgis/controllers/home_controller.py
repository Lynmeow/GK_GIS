from django.shortcuts import render

def home(request):
    return render(request, 'webgis/home.html')

def stations_route_view(request):
    return render(request, 'webgis/stations_route.html')

def custom_403(request, exception=None):
    return render(request, 'webgis/403.html', status=403)

def custom_404(request, exception=None):
    return render(request, 'webgis/404.html', status=404)