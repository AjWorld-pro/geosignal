from django.contrib import admin
from .models import NetworkProvider, NetworkType, AvailableNetwork


@admin.register(NetworkProvider)
class NetworkProviderAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'country', 'website')
    search_fields = ('name', 'code', 'country')
    list_filter = ('country', 'created_at')


@admin.register(NetworkType)
class NetworkTypeAdmin(admin.ModelAdmin):
    list_display = ('type', 'frequency_band', 'max_speed')
    search_fields = ('type', 'description')


@admin.register(AvailableNetwork)
class AvailableNetworkAdmin(admin.ModelAdmin):
    list_display = ('provider', 'network_type', 'signal_quality', 'signal_strength', 'detected_at')
    list_filter = ('provider', 'network_type', 'signal_quality', 'is_active', 'detected_at')
    search_fields = ('provider__name', 'network_type__type')
    readonly_fields = ('detected_at', 'updated_at')
