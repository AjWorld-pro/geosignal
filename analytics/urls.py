from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CoverageAnalysisViewSet, NetworkComparisonViewSet, DailyMetricsViewSet

router = DefaultRouter()
router.register(r'coverage', CoverageAnalysisViewSet)
router.register(r'comparisons', NetworkComparisonViewSet)
router.register(r'daily-metrics', DailyMetricsViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
