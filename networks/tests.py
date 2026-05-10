from django.test import TestCase
from rest_framework.test import APIClient
from django.urls import reverse
from .models import NetworkProvider, NetworkType, AvailableNetwork


class NetworkProviderModelTests(TestCase):
    def setUp(self):
        self.provider = NetworkProvider.objects.create(
            name='Test Provider',
            code='TP',
            country='Testland'
        )

    def test_provider_creation(self):
        self.assertEqual(self.provider.name, 'Test Provider')
        self.assertEqual(self.provider.code, 'TP')
        self.assertEqual(self.provider.country, 'Testland')
        self.assertIsNotNone(self.provider.created_at)

    def test_provider_str(self):
        self.assertEqual(str(self.provider), 'Test Provider (TP)')


class NetworkTypeModelTests(TestCase):
    def setUp(self):
        self.network_type = NetworkType.objects.create(
            type='5G',
            description='Fifth Generation',
            frequency_band='mmWave',
            max_speed='10 Gbps'
        )

    def test_network_type_creation(self):
        self.assertEqual(self.network_type.type, '5G')
        self.assertEqual(self.network_type.description, 'Fifth Generation')

    def test_network_type_str(self):
        self.assertEqual(str(self.network_type), '5G')


class AvailableNetworkModelTests(TestCase):
    def setUp(self):
        self.provider = NetworkProvider.objects.create(name='P1', code='P1', country='C')
        self.network_type = NetworkType.objects.create(type='4G', description='4G', frequency_band='Band', max_speed='100 Mbps')
        self.network = AvailableNetwork.objects.create(
            provider=self.provider,
            network_type=self.network_type,
            signal_strength=-70,
            signal_quality='good',
            latitude=52.52,
            longitude=13.405,
            is_active=True
        )

    def test_network_creation(self):
        self.assertEqual(self.network.signal_strength, -70)
        self.assertEqual(self.network.signal_quality, 'good')
        self.assertTrue(self.network.is_active)

    def test_active_filter(self):
        active = AvailableNetwork.objects.filter(is_active=True).count()
        self.assertEqual(active, 1)


class NetworkAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.provider = NetworkProvider.objects.create(name='API Provider', code='API', country='Test')
        self.network_type = NetworkType.objects.create(type='5G', description='5G', frequency_band='mmWave', max_speed='10 Gbps')

    def test_list_providers(self):
        response = self.client.get(reverse('networkprovider-list'))
        self.assertEqual(response.status_code, 200)
        self.assertIn('results', response.data)

    def test_list_network_types(self):
        response = self.client.get(reverse('networktype-list'))
        self.assertEqual(response.status_code, 200)

    def test_available_types_action(self):
        response = self.client.get(reverse('networktype-available-types'))
        self.assertEqual(response.status_code, 200)

    def test_network_stats(self):
        response = self.client.get(reverse('availablenetwork-stats'))
        self.assertEqual(response.status_code, 200)
        self.assertIn('total_networks', response.data)

    def test_by_location_missing_params(self):
        response = self.client.get(reverse('availablenetwork-by-location'))
        self.assertEqual(response.status_code, 400)
        self.assertIn('error', response.data)

    def test_by_location_invalid_params(self):
        response = self.client.get(reverse('availablenetwork-by-location'), {'latitude': 'abc', 'longitude': '12'})
        self.assertEqual(response.status_code, 400)

    def test_filter_by_country(self):
        response = self.client.get(reverse('networkprovider-list'), {'country': 'Test'})
        self.assertEqual(response.status_code, 200)

    def test_search_providers(self):
        response = self.client.get(reverse('networkprovider-list'), {'search': 'API'})
        self.assertEqual(response.status_code, 200)
