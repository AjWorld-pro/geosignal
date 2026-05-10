from rest_framework import serializers
from .models import NetworkProvider, NetworkType, AvailableNetwork


class NetworkProviderSerializer(serializers.ModelSerializer):
    class Meta:
        model = NetworkProvider
        fields = ['id', 'name', 'code', 'country', 'website', 'logo', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']


class NetworkTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = NetworkType
        fields = ['id', 'type', 'description', 'frequency_band', 'max_speed', 'created_at']
        read_only_fields = ['created_at']


class AvailableNetworkSerializer(serializers.ModelSerializer):
    provider_name = serializers.CharField(source='provider.name', read_only=True)
    network_type_display = serializers.CharField(source='network_type.get_type_display', read_only=True)
    signal_quality_display = serializers.CharField(source='get_signal_quality_display', read_only=True)
    max_speed = serializers.CharField(source='network_type.max_speed', read_only=True)
    frequency_band = serializers.CharField(source='network_type.frequency_band', read_only=True)

    class Meta:
        model = AvailableNetwork
        fields = [
            'id', 'provider', 'provider_name', 'network_type', 'network_type_display',
            'signal_strength', 'signal_quality', 'signal_quality_display',
            'max_speed', 'frequency_band',
            'latitude', 'longitude', 'detected_at', 'updated_at', 'is_active'
        ]
        read_only_fields = ['detected_at', 'updated_at']
