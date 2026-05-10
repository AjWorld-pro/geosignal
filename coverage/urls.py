from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import BTSLocationViewSet, CoverageAreaViewSet, SignalMeasurementViewSet, SimulatedBTSViewSet

router = DefaultRouter()
router.register(r'bts', BTSLocationViewSet)
router.register(r'coverage-areas', CoverageAreaViewSet)
router.register(r'measurements', SignalMeasurementViewSet)
router.register(r'sim-bts', SimulatedBTSViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
