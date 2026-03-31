from django.urls import path
from . import views
app_name = 'informes'
urlpatterns = [
    path('', views.home, name='home'),
    path('clientes/', views.clientes_list, name='clientes_list'),
    path('productos/', views.productos_list, name='productos_list'),
    path('ventas/', views.ventas_list, name='ventas_list'),
    path('pagos/', views.pagos_list, name='pagos_list'),
    path('campanas/', views.campanas_list, name='campanas_list'),
    path('deudas/', views.deudas_list, name='deudas_list'),
]
