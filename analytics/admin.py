from django.contrib import admin
from .models import CoverageAnalysis, NetworkComparison, DailyMetrics


@admin.register(CoverageAnalysis)
class CoverageAnalysisAdmin(admin.ModelAdmin):
    list_display = ('region_name', 'coverage_percentage_5g', 'dominant_provider', 'total_towers', 'analysis_date')
    list_filter = ('dominant_provider', 'analysis_date')
    search_fields = ('region_name',)
    readonly_fields = ('analysis_date', 'updated_at')


@admin.register(NetworkComparison)
class NetworkComparisonAdmin(admin.ModelAdmin):
    list_display = ('provider1', 'provider2', 'region_name', 'reliability_score_provider1', 'reliability_score_provider2')
    list_filter = ('region_name', 'comparison_date')
    search_fields = ('provider1__name', 'provider2__name', 'region_name')
    readonly_fields = ('comparison_date',)


@admin.register(DailyMetrics)
class DailyMetricsAdmin(admin.ModelAdmin):
    list_display = ('date', 'provider', 'network_type', 'avg_signal_strength', 'uptime_percentage')
    list_filter = ('date', 'provider', 'network_type')
    search_fields = ('provider__name', 'network_type__type')
