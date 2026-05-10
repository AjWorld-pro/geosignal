from rest_framework import serializers
from .models import BTSLocation, CoverageArea, SignalMeasurement, SimulatedBTS


class BTSLocationSerializer(serializers.ModelSerializer):
    provider_name = serializers.CharField(source='provider.name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = BTSLocation
        fields = [
            'id', 'name', 'bts_id', 'provider', 'provider_name', 'latitude', 'longitude',
            'height', 'status', 'status_display', 'address', 'city', 'state', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']


class CoverageAreaSerializer(serializers.ModelSerializer):
    bts_name = serializers.CharField(source='bts.name', read_only=True)
    network_type_display = serializers.CharField(source='network_type.get_type_display', read_only=True)

    class Meta:
        model = CoverageArea
        fields = [
            'id', 'bts', 'bts_name', 'network_type', 'network_type_display',
            'coverage_radius', 'signal_strength_center', 'signal_strength_edge',
            'population_covered', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']


class SignalMeasurementSerializer(serializers.ModelSerializer):
    provider_name = serializers.CharField(source='provider.name', read_only=True)
    network_type_display = serializers.CharField(source='network_type.get_type_display', read_only=True)
    nearest_bts_name = serializers.CharField(source='nearest_bts.name', read_only=True)

    class Meta:
        model = SignalMeasurement
        fields = [
            'id', 'latitude', 'longitude', 'network_type', 'network_type_display',
            'provider', 'provider_name', 'signal_strength', 'rsrp', 'rsrq', 'sinr',
            'signal_variance', 'jitter',
            'measured_at', 'nearest_bts', 'nearest_bts_name', 'distance_to_bts'
        ]
        read_only_fields = ['measured_at']


class SimulatedBTSSerializer(serializers.ModelSerializer):
    network_type_display = serializers.CharField(source='network_type.get_type_display', read_only=True)
    provider_name = serializers.CharField(source='provider.name', read_only=True, allow_null=True)

    class Meta:
        model = SimulatedBTS
        fields = [
            'id', 'name', 'latitude', 'longitude', 'height',
            'network_type', 'network_type_display', 'provider', 'provider_name',
            'coverage_radius', 'created_at'
        ]
        read_only_fields = ['created_at']
