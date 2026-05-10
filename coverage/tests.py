from django.test import TestCase
from rest_framework.test import APIClient
from django.urls import reverse
from networks.models import NetworkProvider, NetworkType
from .models import BTSLocation, CoverageArea, SignalMeasurement


class BTSLocationModelTests(TestCase):
    def setUp(self):
        self.provider = NetworkProvider.objects.create(name='BTS Prov', code='BTS', country='C')
        self.bts = BTSLocation.objects.create(
            name='Test Tower',
            bts_id='TWR-001',
            provider=self.provider,
            latitude=52.52,
            longitude=13.405,
            height=50,
            status='active',
            city='Berlin'
        )

    def test_bts_creation(self):
        self.assertEqual(self.bts.name, 'Test Tower')
        self.assertEqual(self.bts.bts_id, 'TWR-001')
        self.assertEqual(self.bts.status, 'active')

    def test_bts_str(self):
        self.assertEqual(str(self.bts), 'Test Tower (TWR-001)')


class CoverageAreaModelTests(TestCase):
    def setUp(self):
        provider = NetworkProvider.objects.create(name='CA Prov', code='CA', country='C')
        net_type = NetworkType.objects.create(type='4G', description='4G', frequency_band='B3', max_speed='150 Mbps')
        bts = BTSLocation.objects.create(name='CA Tower', bts_id='CA-001', provider=provider, latitude=0, longitude=0, height=30)
        self.ca = CoverageArea.objects.create(
            bts=bts,
            network_type=net_type,
            coverage_radius=5.0,
            signal_strength_center=-60,
            signal_strength_edge=-95,
            population_covered=10000
        )

    def test_coverage_area_creation(self):
        self.assertEqual(self.ca.coverage_radius, 5.0)
        self.assertEqual(self.ca.population_covered, 10000)


class SignalMeasurementModelTests(TestCase):
    def setUp(self):
        provider = NetworkProvider.objects.create(name='Meas Prov', code='MP', country='C')
        net_type = NetworkType.objects.create(type='5G', description='5G', frequency_band='mmWave', max_speed='10 Gbps')
        self.meas = SignalMeasurement.objects.create(
            latitude=52.52,
            longitude=13.405,
            network_type=net_type,
            provider=provider,
            signal_strength=-75,
            rsrp=-85,
            rsrq=-12,
            sinr=15.5
        )

    def test_measurement_creation(self):
        self.assertEqual(self.meas.signal_strength, -75)
        self.assertEqual(self.meas.sinr, 15.5)


class CoverageAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.provider = NetworkProvider.objects.create(name='Cov Prov', code='CP', country='Test')
        self.net_type = NetworkType.objects.create(type='4G', description='4G LTE', frequency_band='B3', max_speed='150 Mbps')
        self.bts = BTSLocation.objects.create(
            name='API Tower', bts_id='API-001', provider=self.provider,
            latitude=52.52, longitude=13.405, height=40, status='active', city='Berlin'
        )

    def test_list_bts(self):
        response = self.client.get(reverse('btslocation-list'))
        self.assertEqual(response.status_code, 200)

    def test_list_coverage_areas(self):
        response = self.client.get(reverse('coveragearea-list'))
        self.assertEqual(response.status_code, 200)

    def test_list_measurements(self):
        response = self.client.get(reverse('signalmeasurement-list'))
        self.assertEqual(response.status_code, 200)

    def test_nearby_missing_params(self):
        response = self.client.get(reverse('btslocation-nearby'))
        self.assertEqual(response.status_code, 400)

    def test_nearby_invalid_params(self):
        response = self.client.get(reverse('btslocation-nearby'), {'latitude': 'abc', 'longitude': '12'})
        self.assertEqual(response.status_code, 400)

    def test_signal_stats_missing_params(self):
        response = self.client.get(reverse('signalmeasurement-signal-stats'))
        self.assertEqual(response.status_code, 400)

    def test_filter_by_provider(self):
        response = self.client.get(reverse('btslocation-list'), {'provider': self.provider.id})
        self.assertEqual(response.status_code, 200)

    def test_search_bts(self):
        response = self.client.get(reverse('btslocation-list'), {'search': 'API'})
        self.assertEqual(response.status_code, 200)
