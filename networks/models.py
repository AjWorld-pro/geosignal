from django.db import models

NETWORK_TYPE_CHOICES = [
    ('2G', '2G GSM'),
    ('EDGE', 'EDGE'),
    ('3G', '3G'),
    ('4G', '4G LTE'),
    ('5G', '5G'),
]

SIGNAL_QUALITY_CHOICES = [
    ('excellent', 'Excellent'),
    ('good', 'Good'),
    ('fair', 'Fair'),
    ('poor', 'Poor'),
    ('no_signal', 'No Signal'),
]


class NetworkProvider(models.Model):
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=10, unique=True)
    country = models.CharField(max_length=100)
    website = models.URLField(blank=True, null=True)
    logo = models.ImageField(upload_to='provider_logos/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']
        verbose_name_plural = 'Network Providers'

    def __str__(self):
        return f"{self.name} ({self.code})"


class NetworkType(models.Model):
    type = models.CharField(max_length=10, choices=NETWORK_TYPE_CHOICES, unique=True)
    description = models.TextField()
    frequency_band = models.CharField(max_length=100)
    max_speed = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['type']

    def __str__(self):
        return self.get_type_display()


class AvailableNetwork(models.Model):
    provider = models.ForeignKey(NetworkProvider, on_delete=models.CASCADE, related_name='available_networks')
    network_type = models.ForeignKey(NetworkType, on_delete=models.CASCADE, related_name='available_networks')
    signal_strength = models.IntegerField(help_text="Signal strength in dBm")
    signal_quality = models.CharField(max_length=20, choices=SIGNAL_QUALITY_CHOICES)
    latitude = models.FloatField()
    longitude = models.FloatField()
    detected_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['-detected_at']
        indexes = [
            models.Index(fields=['latitude', 'longitude']),
            models.Index(fields=['provider', 'network_type']),
        ]

    def __str__(self):
        return f"{self.provider} {self.network_type} @ ({self.latitude}, {self.longitude})"
