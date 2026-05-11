from django.urls import path
from . import views

app_name = 'reports'

urlpatterns = [
    path('citizen/', views.CitizenDashboardView.as_view(), name='citizen_dashboard'),
    path('technician/', views.TechnicianDashboardView.as_view(), name='technician_dashboard'),
    path('admin/', views.SystemReportsView.as_view(), name='admin_system_reports'),
]
