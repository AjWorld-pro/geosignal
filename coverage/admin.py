from django.contrib import admin
from .models import BTSLocation, CoverageArea, SignalMeasurement


@admin.register(BTSLocation)
class BTSLocationAdmin(admin.ModelAdmin):
    list_display = ('name', 'bts_id', 'provider', 'height', 'status', 'city')
    list_filter = ('provider', 'status', 'city', 'state')
    search_fields = ('name', 'bts_id', 'address', 'city')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(CoverageArea)
class CoverageAreaAdmin(admin.ModelAdmin):
    list_display = ('bts', 'network_type', 'coverage_radius', 'signal_strength_center')
    list_filter = ('network_type', 'bts__provider', 'created_at')
    search_fields = ('bts__name', 'network_type__type')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(SignalMeasurement)
class SignalMeasurementAdmin(admin.ModelAdmin):
    list_display = ('provider', 'network_type', 'signal_strength', 'nearest_bts', 'measured_at')
    list_filter = ('provider', 'network_type', 'measured_at')
    search_fields = ('nearest_bts__name', 'provider__name')
    readonly_fields = ('measured_at',)
