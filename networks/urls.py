from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import NetworkProviderViewSet, NetworkTypeViewSet, AvailableNetworkViewSet

router = DefaultRouter()
router.register(r'providers', NetworkProviderViewSet)
router.register(r'types', NetworkTypeViewSet)
router.register(r'available', AvailableNetworkViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
