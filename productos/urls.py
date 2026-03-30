from django.urls import path
from .views import producto_campana_api

urlpatterns = [
    path('api/producto-campana/<int:pk>/', producto_campana_api),
]