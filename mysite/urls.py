from django.contrib import admin
from django.urls import path, include
from webgis.controllers.home_controller import custom_403, custom_404

handler403 = custom_403
handler404 = custom_404

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('webgis.urls')),
]