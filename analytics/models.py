from django.db import models
from networks.models import NetworkProvider, NetworkType

COVERAGE_QUALITY_CHOICES = [
    ('excellent', 'Excellent (> -80 dBm)'),
    ('good', 'Good (-80 to -90 dBm)'),
    ('fair', 'Fair (-90 to -100 dBm)'),
    ('poor', 'Poor (-100 to -110 dBm)'),
    ('no_signal', 'No Signal (< -110 dBm)'),
]

CONGESTION_LEVEL_CHOICES = [
    ('low', 'Low'),
    ('moderate', 'Moderate'),
    ('high', 'High'),
    ('severe', 'Severe'),
]


class CoverageAnalysis(models.Model):
    region_name = models.CharField(max_length=100)
    latitude_min = models.FloatField()
    latitude_max = models.FloatField()
    longitude_min = models.FloatField()
    longitude_max = models.FloatField()

    coverage_percentage_2g = models.FloatField(default=0)
    coverage_percentage_3g = models.FloatField(default=0)
    coverage_percentage_4g = models.FloatField(default=0)
    coverage_percentage_5g = models.FloatField(default=0)

    avg_signal_strength_2g = models.FloatField(blank=True, null=True)
    avg_signal_strength_3g = models.FloatField(blank=True, null=True)
    avg_signal_strength_4g = models.FloatField(blank=True, null=True)
    avg_signal_strength_5g = models.FloatField(blank=True, null=True)

    dominant_provider = models.ForeignKey(NetworkProvider, on_delete=models.SET_NULL, null=True, blank=True)
    total_towers = models.IntegerField(default=0)
    congestion_score = models.FloatField(default=0, help_text="0-100 congestion score")
    congestion_level = models.CharField(max_length=20, choices=CONGESTION_LEVEL_CHOICES, default='low')
    analysis_date = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-analysis_date']
        verbose_name_plural = 'Coverage Analysis'

    def __str__(self):
        return f"Coverage Analysis - {self.region_name}"


class NetworkComparison(models.Model):
    provider1 = models.ForeignKey(NetworkProvider, on_delete=models.CASCADE, related_name='comparisons_as_provider1')
    provider2 = models.ForeignKey(NetworkProvider, on_delete=models.CASCADE, related_name='comparisons_as_provider2')
    region_name = models.CharField(max_length=100)

    avg_signal_provider1 = models.FloatField()
    avg_signal_provider2 = models.FloatField()

    coverage_area_provider1 = models.FloatField(help_text="Coverage area in sq km")
    coverage_area_provider2 = models.FloatField(help_text="Coverage area in sq km")

    reliability_score_provider1 = models.FloatField()
    reliability_score_provider2 = models.FloatField()

    comparison_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-comparison_date']
        unique_together = [['provider1', 'provider2', 'region_name']]

    def __str__(self):
        return f"{self.provider1} vs {self.provider2} - {self.region_name}"


class DailyMetrics(models.Model):
    date = models.DateField(auto_now_add=True)
    provider = models.ForeignKey(NetworkProvider, on_delete=models.CASCADE, related_name='daily_metrics')
    network_type = models.ForeignKey(NetworkType, on_delete=models.CASCADE)

    measurements_count = models.IntegerField(default=0)
    avg_signal_strength = models.FloatField()
    max_signal_strength = models.IntegerField()
    min_signal_strength = models.IntegerField()
    signal_variance = models.FloatField(default=0, help_text="Signal stability (lower = more stable)")

    uptime_percentage = models.FloatField(default=100)
    user_satisfaction = models.FloatField(help_text="0-100 scale", default=0)

    class Meta:
        ordering = ['-date']
        unique_together = [['date', 'provider', 'network_type']]
        verbose_name_plural = 'Daily Metrics'

    def __str__(self):
        return f"{self.provider} {self.network_type} - {self.date}"
