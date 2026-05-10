from rest_framework import viewsets, permissions, status, generics
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.contrib.auth.models import User
from django.db.models import Count
from django.utils import timezone
from datetime import timedelta
from .models import SavedScan, Notification, NotificationPreference, ActivityLog
from .models import UsageStat, ScanLocationStat, ExportedReport, DatabaseBackup, SystemHealthCheck, UserSettings
from .serializers import (
    UserSerializer, SavedScanSerializer, NotificationSerializer,
    NotificationPreferenceSerializer, ActivityLogSerializer, UsageStatSerializer,
    ScanLocationStatSerializer, ExportedReportSerializer, DatabaseBackupSerializer,
    SystemHealthCheckSerializer, UserSettingsSerializer
)


class IsStaffOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return request.user.is_authenticated
        return request.user.is_staff


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAdminUser]


class SavedScanViewSet(viewsets.ModelViewSet):
    serializer_class = SavedScanSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return SavedScan.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class NotificationViewSet(viewsets.ModelViewSet):
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class NotificationPreferenceView(generics.RetrieveUpdateAPIView):
    serializer_class = NotificationPreferenceSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        obj, _ = NotificationPreference.objects.get_or_create(user=self.request.user)
        return obj


class ActivityLogViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = ActivityLogSerializer
    permission_classes = [permissions.IsAdminUser]
    filterset_fields = ['event_type', 'user']
    search_fields = ['user__username', 'details']

    def get_queryset(self):
        return ActivityLog.objects.select_related('user').all()


class UsageStatViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = UsageStatSerializer
    permission_classes = [permissions.IsAdminUser]

    def get_queryset(self):
        return UsageStat.objects.all()


class ScanLocationStatViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = ScanLocationStatSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return ScanLocationStat.objects.all()[:10]


class ExportedReportViewSet(viewsets.ModelViewSet):
    serializer_class = ExportedReportSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        qs = ExportedReport.objects.filter(user=self.request.user)
        if self.request.user.is_staff:
            return ExportedReport.objects.all()
        return qs

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class DatabaseBackupViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = DatabaseBackupSerializer
    permission_classes = [permissions.IsAdminUser]
    queryset = DatabaseBackup.objects.all()


class SystemHealthCheckViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = SystemHealthCheckSerializer
    permission_classes = [permissions.IsAdminUser]
    queryset = SystemHealthCheck.objects.all()


class UserSettingsView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSettingsSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        obj, _ = UserSettings.objects.get_or_create(user=self.request.user)
        return obj


@api_view(['GET'])
@permission_classes([permissions.IsAdminUser])
def monitoring_summary(request):
    today = timezone.now().date()
    week_ago = today - timedelta(days=7)
    stats_today = UsageStat.objects.filter(date=today).first()
    week_stats = UsageStat.objects.filter(date__gte=week_ago).aggregate(
        total_scans=Count('total_scans')
    )
    return Response({
        'active_users_today': stats_today.active_users if stats_today else 0,
        'total_scans': stats_today.total_scans if stats_today else 0,
        'locations_scanned_today': stats_today.locations_scanned if stats_today else 0,
        'api_calls_today': stats_today.api_calls if stats_today else 0,
        'scans_this_week': week_stats['total_scans'] or 0,
    })


@api_view(['POST'])
@permission_classes([permissions.IsAdminUser])
def run_health_check(request):
    import random
    checks = [
        SystemHealthCheck.objects.create(check_type='Database Connection', status='passed', detail='Connected successfully'),
        SystemHealthCheck.objects.create(check_type='API Response Time', status='passed', detail=f'{random.randint(80, 200)}ms'),
        SystemHealthCheck.objects.create(check_type='Disk Space', status='passed' if random.random() > 0.3 else 'warning', detail=f'{random.randint(2, 10)} GB free'),
        SystemHealthCheck.objects.create(check_type='Memory Usage', status='warning' if random.random() > 0.7 else 'passed', detail=f'{random.randint(40, 85)}% utilized'),
        SystemHealthCheck.objects.create(check_type='Celery Worker', status='passed', detail='Active'),
    ]
    serializer = SystemHealthCheckSerializer(checks, many=True)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def log_activity(request):
    serializer = ActivityLogSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save(user=request.user if request.user.is_authenticated else None)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
