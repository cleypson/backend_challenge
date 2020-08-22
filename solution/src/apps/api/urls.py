from django.urls import path
from django.conf.urls import include
from rest_framework import routers
from .views import CarViewSet, TyreViewSet, TripViewSet, OrderViewSet

router = routers.DefaultRouter()
router.register(r'cars', CarViewSet)
router.register(r'tyres', TyreViewSet)
router.register(r'trips', TripViewSet)
router.register(r'orders', OrderViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('auth/', include('rest_framework.urls', namespace='rest_framework')),
]
