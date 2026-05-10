from django.db import models
from django.contrib.auth.models import User
from django.conf import settings


class SavedScan(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='saved_scans')
    location_name = models.CharField(max_length=255)
    latitude = models.FloatField()
    longitude = models.FloatField()
    networks_found = models.IntegerField(default=0)
    top_provider = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.location_name} - {self.user.username}"


class Notification(models.Model):
    TYPE_CHOICES = [('info', 'Info'), ('success', 'Success'), ('warning', 'Warning'), ('error', 'Error')]
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notifications')
    title = models.CharField(max_length=200, blank=True)
    message = models.TextField()
    notification_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='info')
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"[{self.get_notification_type_display()}] {self.message[:50]}"


class NotificationPreference(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notification_prefs')
    coverage_alerts = models.BooleanField(default=True)
    network_updates = models.BooleanField(default=True)
    system_announcements = models.BooleanField(default=True)
    report_ready = models.BooleanField(default=False)

    def __str__(self):
        return f"Preferences - {self.user.username}"


class ActivityLog(models.Model):
    EVENT_CHOICES = [
        ('login', 'Login'), ('logout', 'Logout'), ('failed_login', 'Failed Login'),
        ('permission_change', 'Permission Change'), ('data_export', 'Data Export'),
        ('settings_change', 'Settings Change'), ('scan', 'Location Scan'),
    ]
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='activity_logs')
    event_type = models.CharField(max_length=30, choices=EVENT_CHOICES)
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    details = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = 'Activity Logs'

    def __str__(self):
        return f"{self.get_event_type_display()} - {self.user or 'anonymous'}"


class UsageStat(models.Model):
    date = models.DateField(unique=True)
    active_users = models.IntegerField(default=0)
    total_scans = models.IntegerField(default=0)
    api_calls = models.IntegerField(default=0)
    locations_scanned = models.IntegerField(default=0)

    class Meta:
        ordering = ['-date']

    def __str__(self):
        return f"Usage - {self.date}"


class ScanLocationStat(models.Model):
    location_name = models.CharField(max_length=255)
    latitude = models.FloatField()
    longitude = models.FloatField()
    scan_count = models.IntegerField(default=0)
    last_scanned = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-scan_count']
        verbose_name_plural = 'Scan Location Stats'

    def __str__(self):
        return f"{self.location_name} ({self.scan_count} scans)"


class ExportedReport(models.Model):
    REPORT_CHOICES = [('user_report', 'User Report'), ('coverage_data', 'Coverage Data'), ('admin_summary', 'Admin Summary')]
    FORMAT_CHOICES = [('csv', 'CSV'), ('pdf', 'PDF')]
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='exported_reports')
    report_type = models.CharField(max_length=30, choices=REPORT_CHOICES)
    format = models.CharField(max_length=10, choices=FORMAT_CHOICES)
    file = models.FileField(upload_to='reports/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.get_report_type_display()} ({self.get_format_display()})"


class DatabaseBackup(models.Model):
    filename = models.CharField(max_length=255)
    file_size = models.CharField(max_length=20, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.filename


class SystemHealthCheck(models.Model):
    STATUS_CHOICES = [('passed', 'Passed'), ('warning', 'Warning'), ('failed', 'Failed')]
    check_type = models.CharField(max_length=100)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    detail = models.TextField(blank=True)
    checked_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-checked_at']

    def __str__(self):
        return f"{self.check_type}: {self.status}"


class UserSettings(models.Model):
    THEME_CHOICES = [('light', 'Light'), ('dark', 'Dark'), ('auto', 'Auto')]
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='settings')
    default_map_center_lat = models.FloatField(default=52.52)
    default_map_center_lon = models.FloatField(default=13.405)
    default_zoom = models.IntegerField(default=10)
    theme = models.CharField(max_length=10, choices=THEME_CHOICES, default='light')

    def __str__(self):
        return f"Settings - {self.user.username}"
