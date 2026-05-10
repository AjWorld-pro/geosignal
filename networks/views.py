from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.db import models
from django.db.models.functions import ACos, Cos, Radians, Sin
from .models import NetworkProvider, NetworkType, AvailableNetwork
from .serializers import NetworkProviderSerializer, NetworkTypeSerializer, AvailableNetworkSerializer


class NetworkProviderViewSet(viewsets.ModelViewSet):
    queryset = NetworkProvider.objects.all()
    serializer_class = NetworkProviderSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ['name', 'code', 'country']
    filterset_fields = ['country']


class NetworkTypeViewSet(viewsets.ModelViewSet):
    queryset = NetworkType.objects.all()
    serializer_class = NetworkTypeSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['type', 'description']

    @action(detail=False, methods=['get'])
    def available_types(self, request):
        types = NetworkType.objects.all()
        serializer = self.get_serializer(types, many=True)
        return Response(serializer.data)


class AvailableNetworkViewSet(viewsets.ModelViewSet):
    queryset = AvailableNetwork.objects.all()
    serializer_class = AvailableNetworkSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['provider', 'network_type', 'is_active', 'signal_quality']
    search_fields = ['provider__name', 'network_type__type']
    ordering_fields = ['signal_strength', 'detected_at', 'updated_at']
    ordering = ['-detected_at']

    @action(detail=False, methods=['get'])
    def by_location(self, request):
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
            networks = AvailableNetwork.objects.annotate(
                distance=6371 * ACos(
                    Cos(Radians(latitude)) * Cos(Radians('latitude'))
                    * Cos(Radians('longitude') - Radians(longitude))
                    + Sin(Radians(latitude)) * Sin(Radians('latitude'))
                )
            ).filter(distance__lte=radius_km).order_by('distance')

            serializer = self.get_serializer(networks, many=True)
            return Response(serializer.data)
        except Exception as e:
            return Response(
                {'error': 'Failed to query networks by location', 'detail': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=['get'])
    def best_network(self, request):
        latitude = request.query_params.get('latitude')
        longitude = request.query_params.get('longitude')

        if not latitude or not longitude:
            return Response(
                {'error': 'latitude and longitude parameters required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            latitude = float(latitude)
            longitude = float(longitude)
        except (TypeError, ValueError):
            return Response(
                {'error': 'latitude and longitude must be valid numbers'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            from coverage.models import BTSLocation
            from django.db.models import Min, F, FloatField
            from django.db.models.functions import ACos, Cos, Radians, Sin

            networks = AvailableNetwork.objects.filter(is_active=True).annotate(
                distance=6371 * ACos(
                    Cos(Radians(latitude)) * Cos(Radians('latitude'))
                    * Cos(Radians('longitude') - Radians(longitude))
                    + Sin(Radians(latitude)) * Sin(Radians('latitude'))
                )
            ).order_by('-signal_strength', 'distance')

            best = networks.first()
            if not best:
                return Response({'error': 'No networks found in range'}, status=status.HTTP_404_NOT_FOUND)

            nearby_bts = BTSLocation.objects.annotate(
                distance=6371 * ACos(
                    Cos(Radians(latitude)) * Cos(Radians('latitude'))
                    * Cos(Radians('longitude') - Radians(longitude))
                    + Sin(Radians(latitude)) * Sin(Radians('latitude'))
                )
            ).filter(status='active').order_by('distance').first()

            serializer = self.get_serializer(networks[:5], many=True)

            result = {
                'best_network': serializer.data[0] if serializer.data else None,
                'top_networks': serializer.data,
                'nearest_bts': {
                    'name': nearby_bts.name,
                    'bts_id': nearby_bts.bts_id,
                    'distance_km': round(nearby_bts.distance, 2),
                    'provider': nearby_bts.provider.name,
                    'latitude': nearby_bts.latitude,
                    'longitude': nearby_bts.longitude,
                } if nearby_bts else None,
                'recommendation': 'The strongest network at your location.'
            }

            return Response(result)

        except Exception as e:
            return Response(
                {'error': 'Failed to find best network', 'detail': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=['get'])
    def stats(self, request):
        try:
            stats = {
                'total_networks': AvailableNetwork.objects.count(),
                'active_networks': AvailableNetwork.objects.filter(is_active=True).count(),
                'by_quality': dict(
                    AvailableNetwork.objects.values('signal_quality').annotate(
                        count=models.Count('id')
                    ).values_list('signal_quality', 'count')
                ),
                'by_provider': dict(
                    AvailableNetwork.objects.values('provider__name').annotate(
                        count=models.Count('id')
                    ).values_list('provider__name', 'count')
                ),
            }
            return Response(stats)
        except Exception as e:
            return Response(
                {'error': 'Failed to compute network statistics', 'detail': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
