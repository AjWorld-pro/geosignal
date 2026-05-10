from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    UserViewSet, SavedScanViewSet, NotificationViewSet, NotificationPreferenceView,
    ActivityLogViewSet, UsageStatViewSet, ScanLocationStatViewSet, ExportedReportViewSet,
    DatabaseBackupViewSet, SystemHealthCheckViewSet, UserSettingsView,
    monitoring_summary, run_health_check, log_activity
)

router = DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'saved-scans', SavedScanViewSet, basename='saved-scan')
router.register(r'notifications', NotificationViewSet, basename='notification')
router.register(r'activity-logs', ActivityLogViewSet, basename='activity-log')
router.register(r'usage-stats', UsageStatViewSet, basename='usage-stat')
router.register(r'scan-locations', ScanLocationStatViewSet, basename='scan-location')
router.register(r'exported-reports', ExportedReportViewSet, basename='exported-report')
router.register(r'database-backups', DatabaseBackupViewSet, basename='database-backup')
router.register(r'health-checks', SystemHealthCheckViewSet, basename='health-check')

urlpatterns = [
    path('', include(router.urls)),
    path('notification-preferences/', NotificationPreferenceView.as_view(), name='notification-preferences'),
    path('user-settings/', UserSettingsView.as_view(), name='user-settings'),
    path('monitoring-summary/', monitoring_summary, name='monitoring-summary'),
    path('run-health-check/', run_health_check, name='run-health-check'),
    path('log-activity/', log_activity, name='log-activity'),
]
