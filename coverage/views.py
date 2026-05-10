from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Avg, Max, Min, Count
from django.utils import timezone
from django.db.models.functions import ACos, Cos, Radians, Sin
from .models import BTSLocation, CoverageArea, SignalMeasurement, SimulatedBTS
from .serializers import (BTSLocationSerializer, CoverageAreaSerializer,
                           SignalMeasurementSerializer, SimulatedBTSSerializer)


class BTSLocationViewSet(viewsets.ModelViewSet):
    queryset = BTSLocation.objects.all()
    serializer_class = BTSLocationSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['provider', 'status', 'city', 'state']
    search_fields = ['name', 'bts_id', 'address', 'city']
    ordering_fields = ['name', 'height', 'created_at']
    ordering = ['name']

    @action(detail=False, methods=['get'])
    def nearby(self, request):
        latitude = request.query_params.get('latitude')
        longitude = request.query_params.get('longitude')
        radius_km = request.query_params.get('radius', 10)

        if not latitude or not longitude:
            return Response(
                {'error': 'latitude and longitude parameters required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            latitude = float(latitude)
            longitude = float(longitude)
            radius_km = float(radius_km)
        except (TypeError, ValueError):
            return Response(
                {'error': 'latitude, longitude, and radius must be valid numbers'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            locations = BTSLocation.objects.annotate(
                distance=6371 * ACos(
                    Cos(Radians(latitude)) * Cos(Radians('latitude'))
                    * Cos(Radians('longitude') - Radians(longitude))
                    + Sin(Radians(latitude)) * Sin(Radians('latitude'))
                )
            ).filter(distance__lte=radius_km, status='active').order_by('distance')

            serializer = self.get_serializer(locations, many=True)
            return Response(serializer.data)
        except Exception as e:
            return Response(
                {'error': 'Failed to query nearby BTS locations', 'detail': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class CoverageAreaViewSet(viewsets.ModelViewSet):
    queryset = CoverageArea.objects.all()
    serializer_class = CoverageAreaSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['bts', 'network_type']
    ordering_fields = ['coverage_radius', 'signal_strength_center', 'created_at']
    ordering = ['-created_at']


class SignalMeasurementViewSet(viewsets.ModelViewSet):
    queryset = SignalMeasurement.objects.all()
    serializer_class = SignalMeasurementSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['provider', 'network_type']
    ordering_fields = ['signal_strength', 'measured_at', 'distance_to_bts']
    ordering = ['-measured_at']

    @action(detail=False, methods=['post'])
    def create_measurement(self, request):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'])
    def by_location(self, request):
        latitude = request.query_params.get('latitude')
        longitude = request.query_params.get('longitude')
        radius_km = request.query_params.get('radius', 1)
        limit = request.query_params.get('limit', 100)

        if not latitude or not longitude:
            return Response(
                {'error': 'latitude and longitude parameters required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            latitude = float(latitude)
            longitude = float(longitude)
            radius_km = float(radius_km)
            limit = int(limit)
        except (TypeError, ValueError):
            return Response(
                {'error': 'latitude, longitude, radius must be numbers and limit must be an integer'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            measurements = SignalMeasurement.objects.annotate(
                distance=6371 * ACos(
                    Cos(Radians(latitude)) * Cos(Radians('latitude'))
                    * Cos(Radians('longitude') - Radians(longitude))
                    + Sin(Radians(latitude)) * Sin(Radians('latitude'))
                )
            ).filter(distance__lte=radius_km).order_by('distance')[:limit]

            serializer = self.get_serializer(measurements, many=True)
            return Response(serializer.data)
        except Exception as e:
            return Response(
                {'error': 'Failed to query measurements by location', 'detail': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=['get'])
    def signal_stats(self, request):
        latitude = request.query_params.get('latitude')
        longitude = request.query_params.get('longitude')
        radius_km = request.query_params.get('radius', 5)

        if not latitude or not longitude:
            return Response(
                {'error': 'latitude and longitude parameters required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            latitude = float(latitude)
            longitude = float(longitude)
            radius_km = float(radius_km)
        except (TypeError, ValueError):
            return Response(
                {'error': 'latitude, longitude, and radius must be valid numbers'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            measurements = SignalMeasurement.objects.annotate(
                distance=6371 * ACos(
                    Cos(Radians(latitude)) * Cos(Radians('latitude'))
                    * Cos(Radians('longitude') - Radians(longitude))
                    + Sin(Radians(latitude)) * Sin(Radians('latitude'))
                )
            ).filter(distance__lte=radius_km)

            stats = measurements.aggregate(
                avg_signal=Avg('signal_strength'),
                max_signal=Max('signal_strength'),
                min_signal=Min('signal_strength'),
                avg_variance=Avg('signal_variance'),
                avg_jitter=Avg('jitter'),
                count=Count('id')
            )

            return Response(stats)
        except Exception as e:
            return Response(
                {'error': 'Failed to compute signal statistics', 'detail': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=['get'])
    def stability_report(self, request):
        try:
            report = SignalMeasurement.objects.values('provider__name', 'network_type__type').annotate(
                avg_signal=Avg('signal_strength'),
                avg_variance=Avg('signal_variance'),
                avg_jitter=Avg('jitter'),
                count=Count('id')
            ).order_by('avg_variance')

            return Response(list(report))
        except Exception as e:
            return Response(
                {'error': 'Failed to generate stability report', 'detail': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class SimulatedBTSViewSet(viewsets.ModelViewSet):
    queryset = SimulatedBTS.objects.all()
    serializer_class = SimulatedBTSSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['network_type', 'provider']
    ordering_fields = ['created_at']
    ordering = ['-created_at']

    @action(detail=False, methods=['post'])
    def simulate(self, request):
        data = request.data.copy()
        if not data.get('name'):
            data['name'] = f"Sim-BTS-{timezone.now().strftime('%Y%m%d%H%M%S')}"
        serializer = self.get_serializer(data=data)
        if serializer.is_valid():
            sim = serializer.save()
            from math import cos, radians
            radius_km = sim.coverage_radius
            center_lat = sim.latitude
            center_lon = sim.longitude
            lat_delta = radius_km / 111.0
            lon_delta = radius_km / (111.0 * abs(cos(radians(center_lat))) or 1)

            coverage_preview = {
                'center': {'lat': center_lat, 'lon': center_lon},
                'radius_km': radius_km,
                'bounds': {
                    'north': center_lat + lat_delta,
                    'south': center_lat - lat_delta,
                    'east': center_lon + lon_delta,
                    'west': center_lon - lon_delta,
                },
                'estimated_signal_at_center': -50,
                'estimated_signal_at_edge': -95,
                'network_type': sim.network_type.type,
            }
            result = serializer.data
            result['coverage_preview'] = coverage_preview
            return Response(result, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'])
    def clear_simulated(self, request):
        count, _ = SimulatedBTS.objects.all().delete()
        return Response({'deleted': count})
