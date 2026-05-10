"""
Sample data initialization script for Geosginal
Run with: python manage.py shell < load_sample_data.py
"""

from networks.models import NetworkType, NetworkProvider, AvailableNetwork
from coverage.models import BTSLocation, CoverageArea, SignalMeasurement
from analytics.models import CoverageAnalysis, DailyMetrics, NetworkComparison
from django.utils import timezone
import random

print("Loading sample data...")

# Create Network Types
print("\nCreating network types...")
network_types = [
    {'type': '2G', 'description': '2G/EDGE network', 'frequency_band': '900-1800 MHz', 'max_speed': '384 Kbps'},
    {'type': '3G', 'description': '3G mobile network', 'frequency_band': '2100 MHz', 'max_speed': '21 Mbps'},
    {'type': '4G', 'description': '4G LTE network', 'frequency_band': '800-2600 MHz', 'max_speed': '300 Mbps'},
    {'type': '5G', 'description': '5G network', 'frequency_band': '600 MHz - 100 GHz', 'max_speed': '10 Gbps'},
]

type_map = {}
for t in network_types:
    obj, created = NetworkType.objects.get_or_create(**t)
    type_map[obj.type] = obj
    status = "Created" if created else "Already exists"
    print(f"  {status}: {obj.type} ({obj.max_speed})")

# Create Network Providers (Nigerian + European)
print("\nCreating network providers...")
providers_data = [
    # Nigerian providers
    {'name': 'MTN Nigeria', 'code': 'MTN', 'country': 'Nigeria'},
    {'name': 'Airtel Nigeria', 'code': 'AIRTEL', 'country': 'Nigeria'},
    {'name': 'Globacom (GLO)', 'code': 'GLO', 'country': 'Nigeria'},
    {'name': '9mobile', 'code': '9MOBILE', 'country': 'Nigeria'},
    # European providers
    {'name': 'Vodafone', 'code': 'VF', 'country': 'Germany'},
    {'name': 'Deutsche Telekom', 'code': 'DT', 'country': 'Germany'},
    {'name': 'O2', 'code': 'O2', 'country': 'Germany'},
]

providers = {}
for p in providers_data:
    obj, created = NetworkProvider.objects.get_or_create(**p)
    providers[p['code']] = obj
    status = "Created" if created else "Already exists"
    print(f"  {status}: {obj.name} ({obj.country})")

# Nigerian cities with coordinates
nigerian_cities = [
    {'name': 'Lagos', 'lat': 6.5244, 'lon': 3.3792, 'state': 'Lagos'},
    {'name': 'Abuja', 'lat': 9.0765, 'lon': 7.3986, 'state': 'FCT'},
    {'name': 'Port Harcourt', 'lat': 4.8156, 'lon': 7.0498, 'state': 'Rivers'},
    {'name': 'Ibadan', 'lat': 7.3775, 'lon': 3.9470, 'state': 'Oyo'},
    {'name': 'Kano', 'lat': 12.0022, 'lon': 8.5920, 'state': 'Kano'},
]

nigerian_providers = ['MTN', 'AIRTEL', 'GLO', '9MOBILE']

# Create BTS Locations
print("\nCreating BTS locations...")
bts_locations = {}
bts_index = 1

# Nigerian BTS
for city in nigerian_cities:
    for code in nigerian_providers:
        bts_id = f"BTS-NG-{city['name'][:3].upper()}-{code[:3]}-{bts_index:03d}"
        obj, created = BTSLocation.objects.get_or_create(
            bts_id=bts_id,
            defaults={
                'name': f"{city['name']} {providers[code].name} Tower",
                'provider': providers[code],
                'latitude': city['lat'] + random.uniform(-0.02, 0.02),
                'longitude': city['lon'] + random.uniform(-0.02, 0.02),
                'height': random.choice([45, 50, 60, 75]),
                'status': 'active',
                'city': city['name'],
                'state': city['state'],
            }
        )
        bts_locations[bts_id] = obj
        status = "Created" if created else "Already exists"
        if created:
            print(f"  {status}: {obj.name} ({city['name']})")
        bts_index += 1

# European BTS
european_cities = [
    {'name': 'Berlin', 'lat': 52.5200, 'lon': 13.4050, 'state': 'Berlin'},
    {'name': 'Munich', 'lat': 48.1351, 'lon': 11.5820, 'state': 'Bavaria'},
    {'name': 'Hamburg', 'lat': 53.5511, 'lon': 9.9937, 'state': 'Hamburg'},
]
euro_providers = ['VF', 'DT', 'O2']

for city in european_cities:
    for code in euro_providers:
        bts_id = f"BTS-EU-{city['name'][:3].upper()}-{code}-{bts_index:03d}"
        obj, created = BTSLocation.objects.get_or_create(
            bts_id=bts_id,
            defaults={
                'name': f"{city['name']} {providers[code].name} Tower",
                'provider': providers[code],
                'latitude': city['lat'] + random.uniform(-0.02, 0.02),
                'longitude': city['lon'] + random.uniform(-0.02, 0.02),
                'height': random.choice([50, 60, 75]),
                'status': 'active',
                'city': city['name'],
                'state': city['state'],
            }
        )
        bts_locations[bts_id] = obj
        status = "Created" if created else "Already exists"
        if created:
            print(f"  {status}: {obj.name} ({city['name']})")
        bts_index += 1

# Create Coverage Areas
print("\nCreating coverage areas...")
for bts_id, bts in list(bts_locations.items()):
    for nt in NetworkType.objects.all():
        is_ng = bts.city in [c['name'] for c in nigerian_cities]
        if nt.type == '5G':
            radius = 3.0 if is_ng else 5.0
            center_signal = -80 if is_ng else -75
        elif nt.type == '4G':
            radius = 8.0 if is_ng else 10.0
            center_signal = -85 if is_ng else -80
        elif nt.type == '3G':
            radius = 10.0 if is_ng else 12.0
            center_signal = -90 if is_ng else -85
        else:  # 2G
            radius = 15.0
            center_signal = -95

        obj, created = CoverageArea.objects.get_or_create(
            bts=bts,
            network_type=nt,
            defaults={
                'coverage_radius': radius,
                'signal_strength_center': center_signal,
                'signal_strength_edge': center_signal - 20,
            }
        )
        if created:
            print(f"  Created coverage: {bts.name} - {nt.type}")

# Create Available Networks
print("\nCreating available networks...")
for provider in providers.values():
    for nt in NetworkType.objects.all():
        # Use different base coordinates per country
        if provider.country == 'Nigeria':
            base_lat, base_lon = 8.0, 6.0
        else:
            base_lat, base_lon = 51.0, 10.0

        # Vary signal strength by provider and type
        if nt.type == '5G':
            strength = random.randint(-80, -65)
        elif nt.type == '4G':
            strength = random.randint(-90, -75)
        elif nt.type == '3G':
            strength = random.randint(-100, -85)
        else:
            strength = random.randint(-110, -95)

        quality = 'excellent' if strength >= -75 else 'good' if strength >= -90 else 'fair' if strength >= -105 else 'poor'

        obj, created = AvailableNetwork.objects.get_or_create(
            provider=provider,
            network_type=nt,
            latitude=base_lat + random.uniform(-5, 5),
            longitude=base_lon + random.uniform(-5, 5),
            defaults={
                'signal_strength': strength,
                'signal_quality': quality,
            }
        )
        if created:
            print(f"  Created: {provider.name} {nt.type}")

# Create Signal Measurements
print("\nCreating signal measurements...")
for bts_id, bts in list(bts_locations.items()):
    for nt in NetworkType.objects.all():
        for i in range(random.randint(2, 4)):
            strength = -75 - (i * 8) - random.randint(0, 10)
            SignalMeasurement.objects.create(
                latitude=bts.latitude + random.uniform(-0.01, 0.01),
                longitude=bts.longitude + random.uniform(-0.01, 0.01),
                network_type=nt,
                provider=bts.provider,
                signal_strength=strength,
                rsrp=strength - random.randint(0, 5),
                rsrq=-10 - random.randint(0, 5),
                sinr=random.randint(5, 20),
                signal_variance=random.uniform(1, 20),
                jitter=random.uniform(1, 30),
                nearest_bts=bts,
                distance_to_bts=float(random.randint(50, 500)),
            )
    print(f"  Created measurements for: {bts.name}")

# Create Coverage Analysis
print("\nCreating coverage analysis...")
regions = [
    {'name': 'Lagos Metro', 'provider': providers['MTN'], 'lat_min': 6.3, 'lat_max': 6.7, 'lon_min': 3.1, 'lon_max': 3.6},
    {'name': 'Abuja Region', 'provider': providers['AIRTEL'], 'lat_min': 8.8, 'lat_max': 9.3, 'lon_min': 7.1, 'lon_max': 7.7},
    {'name': 'Port Harcourt Area', 'provider': providers['GLO'], 'lat_min': 4.6, 'lat_max': 5.0, 'lon_min': 6.8, 'lon_max': 7.3},
    {'name': 'Northern Nigeria', 'provider': providers['9MOBILE'], 'lat_min': 10.0, 'lat_max': 13.0, 'lon_min': 7.0, 'lon_max': 10.0},
    {'name': 'Berlin Metro', 'provider': providers['VF'], 'lat_min': 52.3, 'lat_max': 52.7, 'lon_min': 13.2, 'lon_max': 13.6},
    {'name': 'Bavaria Region', 'provider': providers['DT'], 'lat_min': 47.8, 'lat_max': 48.5, 'lon_min': 11.0, 'lon_max': 12.5},
]

for region in regions:
    is_ng = region['provider'].country == 'Nigeria'
    obj, created = CoverageAnalysis.objects.get_or_create(
        region_name=region['name'],
        latitude_min=region['lat_min'],
        latitude_max=region['lat_max'],
        longitude_min=region['lon_min'],
        longitude_max=region['lon_max'],
        defaults={
            'coverage_percentage_2g': random.randint(90, 98),
            'coverage_percentage_3g': random.randint(80, 95),
            'coverage_percentage_4g': random.randint(60, 90) if is_ng else random.randint(85, 98),
            'coverage_percentage_5g': random.randint(10, 30) if is_ng else random.randint(35, 60),
            'avg_signal_strength_2g': random.uniform(-105, -90),
            'avg_signal_strength_3g': random.uniform(-95, -80),
            'avg_signal_strength_4g': random.uniform(-90, -75),
            'avg_signal_strength_5g': random.uniform(-80, -65),
            'congestion_score': random.uniform(20, 80),
            'congestion_level': random.choice(['low', 'moderate', 'high']),
            'dominant_provider': region['provider'],
            'total_towers': BTSLocation.objects.filter(
                city=region['name'].split(' ')[0]
            ).count() or random.randint(20, 50),
        }
    )
    if created:
        print(f"  Created analysis: {region['name']}")

# Create Daily Metrics
print("\nCreating daily metrics...")
today = timezone.now().date()
for provider in providers.values():
    for nt in NetworkType.objects.all():
        for day_offset in range(7):
            date = today - timezone.timedelta(days=day_offset)
            obj, created = DailyMetrics.objects.get_or_create(
                date=date,
                provider=provider,
                network_type=nt,
                defaults={
                    'measurements_count': random.randint(500, 2000),
                    'avg_signal_strength': random.uniform(-95, -70),
                    'max_signal_strength': random.uniform(-60, -45),
                    'min_signal_strength': random.uniform(-115, -100),
                    'uptime_percentage': random.uniform(95.0, 99.9),
                    'user_satisfaction': random.uniform(3.0, 4.8),
                    'signal_variance': random.uniform(2, 18),
                }
            )
            if created:
                print(f"  Created metrics: {provider.name} {nt.type} ({date})")

# Create Network Comparisons (Nigeria focus)
print("\nCreating network comparisons...")
ng_codes = ['MTN', 'AIRTEL', 'GLO', '9MOBILE']
for i in range(len(ng_codes)):
    for j in range(i+1, len(ng_codes)):
        p1 = providers[ng_codes[i]]
        p2 = providers[ng_codes[j]]
        obj, created = NetworkComparison.objects.get_or_create(
            provider1=p1,
            provider2=p2,
            region_name='Nigeria National',
            defaults={
                'avg_signal_provider1': random.uniform(-90, -75),
                'avg_signal_provider2': random.uniform(-90, -75),
                'coverage_area_provider1': random.uniform(100, 500),
                'coverage_area_provider2': random.uniform(100, 500),
                'reliability_score_provider1': random.uniform(3.0, 4.8),
                'reliability_score_provider2': random.uniform(3.0, 4.8),
            }
        )
        if created:
            print(f"  Created comparison: {p1.name} vs {p2.name}")

print("\nSample data loaded successfully!")
print(f"  Providers: {NetworkProvider.objects.count()}")
print(f"  Network Types: {NetworkType.objects.count()}")
print(f"  BTS Locations: {BTSLocation.objects.count()}")
print(f"  Coverage Areas: {CoverageArea.objects.count()}")
print(f"  Available Networks: {AvailableNetwork.objects.count()}")
print(f"  Signal Measurements: {SignalMeasurement.objects.count()}")
print(f"  Coverage Analyses: {CoverageAnalysis.objects.count()}")
print(f"  Daily Metrics: {DailyMetrics.objects.count()}")
print(f"  Network Comparisons: {NetworkComparison.objects.count()}")
