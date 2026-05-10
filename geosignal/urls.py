from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from .views import map_view, login_view, logout_view, user_settings, user_management, system_monitoring, data_management, security_logs, api_status

urlpatterns = [
    path('', map_view, name='map'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('settings/', user_settings, name='settings'),
    path('admin/users/', user_management, name='user_management'),
    path('admin/monitoring/', system_monitoring, name='system_monitoring'),
    path('admin/data/', data_management, name='data_management'),
    path('admin/security-logs/', security_logs, name='security_logs'),
    path('api/status/', api_status, name='api_status'),
    path('admin/', admin.site.urls),
    path('api/networks/', include('networks.urls')),
    path('api/coverage/', include('coverage.urls')),
    path('api/analytics/', include('analytics.urls')),
    path('api/core/', include('core.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
