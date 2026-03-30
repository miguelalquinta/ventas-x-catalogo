from django.urls import path
from .views import producto_api

urlpatterns = [
    path('api/producto/<int:pk>/', producto_api),
]