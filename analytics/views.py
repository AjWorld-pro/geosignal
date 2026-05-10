from datetime import timedelta
from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Avg, Sum, Max, Count
from django.utils import timezone
from networks.models import AvailableNetwork
from coverage.models import BTSLocation
from .models import CoverageAnalysis, NetworkComparison, DailyMetrics
from .serializers import CoverageAnalysisSerializer, NetworkComparisonSerializer, DailyMetricsSerializer


class CoverageAnalysisViewSet(viewsets.ModelViewSet):
    queryset = CoverageAnalysis.objects.all()
    serializer_class = CoverageAnalysisSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['dominant_provider']
    search_fields = ['region_name']
    ordering_fields = ['analysis_date', 'coverage_percentage_3g', 'coverage_percentage_4g', 'coverage_percentage_5g']
    ordering = ['-analysis_date']

    @action(detail=False, methods=['get'])
    def regional_summary(self, request):
        try:
            analyses = CoverageAnalysis.objects.values('region_name').annotate(
                avg_2g=Avg('coverage_percentage_2g'),
                avg_3g=Avg('coverage_percentage_3g'),
                avg_4g=Avg('coverage_percentage_4g'),
                avg_5g=Avg('coverage_percentage_5g'),
                avg_congestion=Avg('congestion_score'),
                latest_date=Max('analysis_date')
            )
            return Response(list(analyses))
        except Exception as e:
            return Response(
                {'error': 'Failed to compute regional summary', 'detail': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=['get'])
    def congestion_map(self, request):
        try:
            regions = CoverageAnalysis.objects.filter(congestion_score__gt=0).values(
                'region_name', 'congestion_score', 'congestion_level', 'total_towers'
            ).order_by('-congestion_score')
            return Response(list(regions))
        except Exception as e:
            return Response(
                {'error': 'Failed to load congestion data', 'detail': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=['get'])
    def detect_congestion(self, request):
        try:
            region = request.query_params.get('region')
            lat = request.query_params.get('latitude')
            lon = request.query_params.get('longitude')
            radius = float(request.query_params.get('radius', 5))

            from django.db.models.functions import ACos, Cos, Radians, Sin

            networks_nearby = AvailableNetwork.objects.all()
            bts_nearby = BTSLocation.objects.all()

            if lat and lon:
                try:
                    lat_f = float(lat)
                    lon_f = float(lon)
                    networks_nearby = networks_nearby.annotate(
                        distance=6371 * ACos(
                            Cos(Radians(lat_f)) * Cos(Radians('latitude'))
                            * Cos(Radians('longitude') - Radians(lon_f))
                            + Sin(Radians(lat_f)) * Sin(Radians('latitude'))
                        )
                    ).filter(distance__lte=radius)
                    bts_nearby = bts_nearby.annotate(
                        distance=6371 * ACos(
                            Cos(Radians(lat_f)) * Cos(Radians('latitude'))
                            * Cos(Radians('longitude') - Radians(lon_f))
                            + Sin(Radians(lat_f)) * Sin(Radians('latitude'))
                        )
                    ).filter(distance__lte=radius)
                except (TypeError, ValueError):
                    pass

            total_bts = bts_nearby.count()
            total_networks = networks_nearby.count()

            if total_bts == 0:
                return Response({
                    'congestion_score': 0,
                    'congestion_level': 'low',
                    'total_bts': 0,
                    'total_networks': total_networks,
                    'networks_per_bts': 0,
                    'assessment': 'No base stations in this area.'
                })

            ratio = total_networks / total_bts
            congestion_score = min(100, ratio * 20)
            if congestion_score < 25:
                level = 'low'
            elif congestion_score < 50:
                level = 'moderate'
            elif congestion_score < 75:
                level = 'high'
            else:
                level = 'severe'

            return Response({
                'congestion_score': round(congestion_score, 1),
                'congestion_level': level,
                'total_bts': total_bts,
                'total_networks': total_networks,
                'networks_per_bts': round(ratio, 2),
                'assessment': f"{level.capitalize()} congestion detected. {ratio:.1f} networks per tower."
            })

        except Exception as e:
            return Response(
                {'error': 'Failed to detect congestion', 'detail': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class NetworkComparisonViewSet(viewsets.ModelViewSet):
    queryset = NetworkComparison.objects.all()
    serializer_class = NetworkComparisonSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['provider1', 'provider2', 'region_name']
    ordering_fields = ['comparison_date']
    ordering = ['-comparison_date']

    @action(detail=False, methods=['get'])
    def comparison_summary(self, request):
        provider1 = request.query_params.get('provider1')
        provider2 = request.query_params.get('provider2')

        if not provider1 or not provider2:
            return Response(
                {'error': 'provider1 and provider2 parameters required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            comparisons = NetworkComparison.objects.filter(
                provider1_id=provider1, provider2_id=provider2
            ).order_by('-comparison_date')

            serializer = self.get_serializer(comparisons, many=True)
            return Response(serializer.data)
        except Exception as e:
            return Response(
                {'error': 'Failed to retrieve comparison summary', 'detail': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class DailyMetricsViewSet(viewsets.ModelViewSet):
    queryset = DailyMetrics.objects.all()
    serializer_class = DailyMetricsSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['date', 'provider', 'network_type']
    ordering_fields = ['date', 'avg_signal_strength', 'uptime_percentage']
    ordering = ['-date']

    @action(detail=False, methods=['get'])
    def trend(self, request):
        provider_id = request.query_params.get('provider')
        network_type_id = request.query_params.get('network_type')
        days = request.query_params.get('days', 30)

        if not provider_id or not network_type_id:
            return Response(
                {'error': 'provider and network_type parameters required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            days = int(days)
            start_date = timezone.now() - timedelta(days=days)

            metrics = DailyMetrics.objects.filter(
                provider_id=provider_id,
                network_type_id=network_type_id,
                date__gte=start_date
            ).order_by('date')

            serializer = self.get_serializer(metrics, many=True)
            return Response(serializer.data)
        except ValueError:
            return Response(
                {'error': 'days must be a valid integer'},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {'error': 'Failed to retrieve trend data', 'detail': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=['get'])
    def performance_report(self, request):
        try:
            report = DailyMetrics.objects.values('provider__name', 'network_type__type').annotate(
                latest_date=Max('date'),
                avg_uptime=Avg('uptime_percentage'),
                avg_satisfaction=Avg('user_satisfaction'),
                avg_stability=Avg('signal_variance'),
                latest_signal=Avg('avg_signal_strength')
            ).order_by('-avg_uptime')

            return Response(list(report))
        except Exception as e:
            return Response(
                {'error': 'Failed to generate performance report', 'detail': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
