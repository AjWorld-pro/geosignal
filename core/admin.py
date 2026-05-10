from django.contrib import admin
from .models import SavedScan, Notification, NotificationPreference, ActivityLog
from .models import UsageStat, ScanLocationStat, ExportedReport, DatabaseBackup, SystemHealthCheck, UserSettings

@admin.register(SavedScan)
class SavedScanAdmin(admin.ModelAdmin): list_display = ['location_name', 'user', 'networks_found', 'created_at']

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin): list_display = ['title', 'user', 'notification_type', 'is_read', 'created_at']

@admin.register(NotificationPreference)
class NotificationPreferenceAdmin(admin.ModelAdmin): list_display = ['user', 'coverage_alerts', 'network_updates']

@admin.register(ActivityLog)
class ActivityLogAdmin(admin.ModelAdmin): list_display = ['event_type', 'user', 'ip_address', 'created_at']

@admin.register(UsageStat)
class UsageStatAdmin(admin.ModelAdmin): list_display = ['date', 'active_users', 'total_scans', 'api_calls']

@admin.register(ScanLocationStat)
class ScanLocationStatAdmin(admin.ModelAdmin): list_display = ['location_name', 'scan_count', 'last_scanned']

@admin.register(ExportedReport)
class ExportedReportAdmin(admin.ModelAdmin): list_display = ['user', 'report_type', 'format', 'created_at']

@admin.register(DatabaseBackup)
class DatabaseBackupAdmin(admin.ModelAdmin): list_display = ['filename', 'file_size', 'created_at']

@admin.register(SystemHealthCheck)
class SystemHealthCheckAdmin(admin.ModelAdmin): list_display = ['check_type', 'status', 'checked_at']

@admin.register(UserSettings)
class UserSettingsAdmin(admin.ModelAdmin): list_display = ['user', 'theme', 'default_zoom']
