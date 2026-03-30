from django.contrib import admin
from django.urls import path, include
from .admin import VentasAdminSite
from django.views.generic import RedirectView

# Usar el AdminSite personalizado
admin.site.__class__ = VentasAdminSite

urlpatterns = [
    path('', RedirectView.as_view(url='/admin/', permanent=False)),  # ← AGREGAR ESTA LÍNEA
    path('admin/', admin.site.urls),
    path('dashboard/', include('dashboard.urls')),
    path('ventas/', include('ventas.urls')),
    path('stock/', include('stock.urls')),
    path('productos/', include('productos.urls')),  # 👈 ESTA LÍNEA
]

