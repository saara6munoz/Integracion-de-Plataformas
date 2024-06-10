from django.urls import path
from . import views

urlpatterns = [
    path('delivery/', views.DeliveryViewSet.as_view({
        'get': 'list',
        'post': 'create'
    })),
    path('delivery/<int:pk>/', views.DeliveryViewSet.as_view({
        'get': 'retrieve',
        'put': 'update',
        'delete': 'destroy'
    })),
]
