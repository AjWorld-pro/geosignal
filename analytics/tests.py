from django.test import TestCase
from rest_framework.test import APIClient
from django.urls import reverse
from networks.models import NetworkProvider, NetworkType
from .models import CoverageAnalysis, NetworkComparison, DailyMetrics


class CoverageAnalysisModelTests(TestCase):
    def setUp(self):
        provider = NetworkProvider.objects.create(name='Analysis Prov', code='AP', country='C')
        self.analysis = CoverageAnalysis.objects.create(
            region_name='Test Region',
            latitude_min=52.0,
            latitude_max=53.0,
            longitude_min=13.0,
            longitude_max=14.0,
            coverage_percentage_3g=80.0,
            coverage_percentage_4g=90.0,
            coverage_percentage_5g=60.0,
            dominant_provider=provider,
            total_towers=50
        )

    def test_analysis_creation(self):
        self.assertEqual(self.analysis.region_name, 'Test Region')
        self.assertEqual(self.analysis.coverage_percentage_5g, 60.0)
        self.assertEqual(self.analysis.total_towers, 50)

    def test_analysis_str(self):
        self.assertEqual(str(self.analysis), 'Coverage Analysis - Test Region')


class NetworkComparisonModelTests(TestCase):
    def setUp(self):
        p1 = NetworkProvider.objects.create(name='Comp A', code='CA', country='C')
        p2 = NetworkProvider.objects.create(name='Comp B', code='CB', country='C')
        self.comp = NetworkComparison.objects.create(
            provider1=p1,
            provider2=p2,
            region_name='Region X',
            avg_signal_provider1=-70.0,
            avg_signal_provider2=-75.0,
            coverage_area_provider1=100.0,
            coverage_area_provider2=90.0,
            reliability_score_provider1=95.0,
            reliability_score_provider2=88.0
        )

    def test_comparison_creation(self):
        self.assertEqual(self.comp.avg_signal_provider1, -70.0)
        self.assertEqual(self.comp.reliability_score_provider2, 88.0)


class DailyMetricsModelTests(TestCase):
    def setUp(self):
        provider = NetworkProvider.objects.create(name='Metrics Prov', code='MP', country='C')
        net_type = NetworkType.objects.create(type='5G', description='5G', frequency_band='mmWave', max_speed='10 Gbps')
        self.metric = DailyMetrics.objects.create(
            provider=provider,
            network_type=net_type,
            measurements_count=100,
            avg_signal_strength=-72.5,
            max_signal_strength=-50,
            min_signal_strength=-95,
            uptime_percentage=99.5,
            user_satisfaction=85.0
        )

    def test_metrics_creation(self):
        self.assertEqual(self.metric.avg_signal_strength, -72.5)
        self.assertEqual(self.metric.uptime_percentage, 99.5)


class AnalyticsAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.provider = NetworkProvider.objects.create(name='Analytics API', code='AA', country='Test')
        self.net_type = NetworkType.objects.create(type='4G', description='4G LTE', frequency_band='B3', max_speed='150 Mbps')
        self.analysis = CoverageAnalysis.objects.create(
            region_name='Test Region',
            latitude_min=52.0, latitude_max=53.0,
            longitude_min=13.0, longitude_max=14.0,
            coverage_percentage_3g=80, coverage_percentage_4g=90, coverage_percentage_5g=60,
            dominant_provider=self.provider, total_towers=50
        )
        self.comp = NetworkComparison.objects.create(
            provider1=self.provider, provider2=self.provider,
            region_name='Test Region',
            avg_signal_provider1=-70, avg_signal_provider2=-75,
            coverage_area_provider1=100, coverage_area_provider2=90,
            reliability_score_provider1=95, reliability_score_provider2=88
        )

    def test_list_coverage_analysis(self):
        response = self.client.get(reverse('coverageanalysis-list'))
        self.assertEqual(response.status_code, 200)

    def test_list_comparisons(self):
        response = self.client.get(reverse('networkcomparison-list'))
        self.assertEqual(response.status_code, 200)

    def test_list_daily_metrics(self):
        response = self.client.get(reverse('dailymetrics-list'))
        self.assertEqual(response.status_code, 200)

    def test_regional_summary(self):
        response = self.client.get(reverse('coverageanalysis-regional-summary'))
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.data, list)

    def test_comparison_summary_missing_params(self):
        response = self.client.get(reverse('networkcomparison-comparison-summary'))
        self.assertEqual(response.status_code, 400)

    def test_trend_missing_params(self):
        response = self.client.get(reverse('dailymetrics-trend'))
        self.assertEqual(response.status_code, 400)

    def test_performance_report(self):
        response = self.client.get(reverse('dailymetrics-performance-report'))
        self.assertEqual(response.status_code, 200)

    def test_filter_by_region(self):
        response = self.client.get(reverse('networkcomparison-list'), {'region_name': 'Test Region'})
        self.assertEqual(response.status_code, 200)

    def test_search_analysis(self):
        response = self.client.get(reverse('coverageanalysis-list'), {'search': 'Test'})
        self.assertEqual(response.status_code, 200)
