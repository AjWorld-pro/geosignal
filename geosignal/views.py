from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib.auth import login as auth_login, logout as auth_logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required, user_passes_test


def staff_required(view_func):
    decorated_view = login_required(login_url='/login/')(view_func)
    return user_passes_test(lambda u: u.is_staff, login_url='/login/')(decorated_view)


@login_required(login_url='/login/')
def map_view(request):
    return render(request, 'map.html')


@login_required(login_url='/login/')
def user_settings(request):
    return render(request, 'settings.html')


@staff_required
def user_management(request):
    return render(request, 'user_management.html')


@staff_required
def system_monitoring(request):
    return render(request, 'system_monitoring.html')


@staff_required
def data_management(request):
    return render(request, 'data_management.html')


@staff_required
def security_logs(request):
    return render(request, 'security_logs.html')


def login_view(request):
    if request.user.is_authenticated:
        return redirect('map')
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            auth_login(request, form.get_user())
            return redirect(request.GET.get('next', 'map'))
    else:
        form = AuthenticationForm(request)
    return render(request, 'login.html', {'form': form})


def logout_view(request):
    auth_logout(request)
    return redirect('login')


def api_status(request):
    try:
        from django.db import connection
        connection.ensure_connection()
        db_status = 'connected'
    except Exception:
        db_status = 'disconnected'
    return JsonResponse({'status': 'online', 'database': db_status, 'version': '1.0.0'})
