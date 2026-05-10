from django.db import models
from networks.models import NetworkProvider, NetworkType

TOWER_STATUS_CHOICES = [
    ('active', 'Active'),
    ('inactive', 'Inactive'),
    ('maintenance', 'Maintenance'),
    ('planned', 'Planned'),
]


class BTSLocation(models.Model):
    name = models.CharField(max_length=100)
    bts_id = models.CharField(max_length=50, unique=True)
    provider = models.ForeignKey(NetworkProvider, on_delete=models.CASCADE, related_name='bts_locations')
    latitude = models.FloatField()
    longitude = models.FloatField()
    height = models.IntegerField(help_text="Tower height in meters")
    status = models.CharField(max_length=20, choices=TOWER_STATUS_CHOICES, default='active')
    address = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']
        indexes = [
            models.Index(fields=['latitude', 'longitude']),
            models.Index(fields=['provider']),
        ]
        verbose_name = 'BTS Location'
        verbose_name_plural = 'BTS Locations'

    def __str__(self):
        return f"{self.name} ({self.bts_id})"


class CoverageArea(models.Model):
    bts = models.ForeignKey(BTSLocation, on_delete=models.CASCADE, related_name='coverage_areas')
    network_type = models.ForeignKey(NetworkType, on_delete=models.CASCADE, related_name='coverage_areas')
    coverage_radius = models.FloatField(help_text="Coverage radius in kilometers")
    signal_strength_center = models.IntegerField(help_text="Signal strength at center in dBm")
    signal_strength_edge = models.IntegerField(help_text="Signal strength at edge in dBm")
    population_covered = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        unique_together = ['bts', 'network_type']

    def __str__(self):
        return f"{self.bts} - {self.network_type}"


class SignalMeasurement(models.Model):
    latitude = models.FloatField()
    longitude = models.FloatField()
    network_type = models.ForeignKey(NetworkType, on_delete=models.CASCADE)
    provider = models.ForeignKey(NetworkProvider, on_delete=models.CASCADE)
    signal_strength = models.IntegerField(help_text="Signal strength in dBm")
    rsrp = models.IntegerField(blank=True, null=True, help_text="Reference Signal Received Power")
    rsrq = models.IntegerField(blank=True, null=True, help_text="Reference Signal Received Quality")
    sinr = models.FloatField(blank=True, null=True, help_text="Signal to Interference plus Noise Ratio")
    signal_variance = models.FloatField(blank=True, null=True, help_text="Signal variance over time (stability)")
    jitter = models.FloatField(blank=True, null=True, help_text="Signal jitter in ms")
    measured_at = models.DateTimeField(auto_now_add=True)
    nearest_bts = models.ForeignKey(BTSLocation, on_delete=models.SET_NULL, null=True, blank=True, related_name='measurements')
    distance_to_bts = models.FloatField(blank=True, null=True, help_text="Distance to nearest BTS in meters")

    class Meta:
        ordering = ['-measured_at']
        indexes = [
            models.Index(fields=['latitude', 'longitude', '-measured_at']),
        ]

    def __str__(self):
        return f"{self.provider} {self.network_type} @ ({self.latitude}, {self.longitude})"


class SimulatedBTS(models.Model):
    name = models.CharField(max_length=100)
    latitude = models.FloatField()
    longitude = models.FloatField()
    height = models.IntegerField(help_text="Tower height in meters", default=30)
    network_type = models.ForeignKey(NetworkType, on_delete=models.CASCADE)
    provider = models.ForeignKey(NetworkProvider, on_delete=models.CASCADE, null=True, blank=True)
    coverage_radius = models.FloatField(help_text="Predicted coverage radius in km", default=5)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} (Simulated)"
