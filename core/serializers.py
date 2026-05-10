from rest_framework import serializers
from django.contrib.auth.models import User
from .models import SavedScan, Notification, NotificationPreference, ActivityLog
from .models import UsageStat, ScanLocationStat, ExportedReport, DatabaseBackup, SystemHealthCheck, UserSettings


class UserSerializer(serializers.ModelSerializer):
    role = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'is_active', 'is_staff', 'last_login', 'date_joined', 'role']

    def get_role(self, obj):
        if obj.is_superuser:
            return 'Administrator'
        if obj.is_staff:
            return 'Analyst'
        return 'Viewer'


class SavedScanSerializer(serializers.ModelSerializer):
    class Meta:
        model = SavedScan
        fields = '__all__'
        read_only_fields = ['user', 'created_at']


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = '__all__'
        read_only_fields = ['user', 'created_at']


class NotificationPreferenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = NotificationPreference
        fields = '__all__'
        read_only_fields = ['user']


class ActivityLogSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True, default='')

    class Meta:
        model = ActivityLog
        fields = '__all__'


class UsageStatSerializer(serializers.ModelSerializer):
    class Meta:
        model = UsageStat
        fields = '__all__'


class ScanLocationStatSerializer(serializers.ModelSerializer):
    class Meta:
        model = ScanLocationStat
        fields = '__all__'


class ExportedReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExportedReport
        fields = '__all__'
        read_only_fields = ['user', 'created_at']


class DatabaseBackupSerializer(serializers.ModelSerializer):
    class Meta:
        model = DatabaseBackup
        fields = '__all__'


class SystemHealthCheckSerializer(serializers.ModelSerializer):
    class Meta:
        model = SystemHealthCheck
        fields = '__all__'


class UserSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserSettings
        fields = '__all__'
        read_only_fields = ['user']
