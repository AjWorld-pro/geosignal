from rest_framework import serializers
from .models import CoverageAnalysis, NetworkComparison, DailyMetrics


class CoverageAnalysisSerializer(serializers.ModelSerializer):
    dominant_provider_name = serializers.CharField(source='dominant_provider.name', read_only=True)
    congestion_level_display = serializers.CharField(source='get_congestion_level_display', read_only=True)

    class Meta:
        model = CoverageAnalysis
        fields = [
            'id', 'region_name', 'latitude_min', 'latitude_max', 'longitude_min', 'longitude_max',
            'coverage_percentage_2g', 'coverage_percentage_3g', 'coverage_percentage_4g', 'coverage_percentage_5g',
            'avg_signal_strength_2g', 'avg_signal_strength_3g', 'avg_signal_strength_4g', 'avg_signal_strength_5g',
            'dominant_provider', 'dominant_provider_name', 'total_towers',
            'congestion_score', 'congestion_level', 'congestion_level_display',
            'analysis_date', 'updated_at'
        ]
        read_only_fields = ['analysis_date', 'updated_at']


class NetworkComparisonSerializer(serializers.ModelSerializer):
    provider1_name = serializers.CharField(source='provider1.name', read_only=True)
    provider2_name = serializers.CharField(source='provider2.name', read_only=True)

    class Meta:
        model = NetworkComparison
        fields = [
            'id', 'provider1', 'provider1_name', 'provider2', 'provider2_name',
            'region_name', 'avg_signal_provider1', 'avg_signal_provider2',
            'coverage_area_provider1', 'coverage_area_provider2',
            'reliability_score_provider1', 'reliability_score_provider2',
            'comparison_date'
        ]
        read_only_fields = ['comparison_date']


class DailyMetricsSerializer(serializers.ModelSerializer):
    provider_name = serializers.CharField(source='provider.name', read_only=True)
    network_type_display = serializers.CharField(source='network_type.get_type_display', read_only=True)

    class Meta:
        model = DailyMetrics
        fields = [
            'id', 'date', 'provider', 'provider_name', 'network_type', 'network_type_display',
            'measurements_count', 'avg_signal_strength', 'max_signal_strength',
            'min_signal_strength', 'signal_variance', 'uptime_percentage', 'user_satisfaction'
        ]
