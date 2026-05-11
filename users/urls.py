from django.urls import path
from . import views

app_name = 'users'

urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    path('register/', views.RoleRegisterOptionsView.as_view(), name='register'),
    path('register/citizen/', views.CitizenRegistrationView.as_view(), name='register_citizen'),
    path('register/technician/', views.TechnicianRegistrationView.as_view(), name='register_technician'),
    path('register/operator/', views.OperatorRegistrationView.as_view(), name='register_operator'),
    path('register/admin/', views.AdminRegistrationView.as_view(), name='register_admin'),
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('logout/', views.CustomLogoutView.as_view(), name='logout'),
    path('dashboard/', views.DashboardRedirectView.as_view(), name='dashboard'),
    path('pending-approval/', views.PendingApprovalView.as_view(), name='pending_approval'),
    
    # Profile pages
    path('profile/citizen/', views.CitizenProfileView.as_view(), name='citizen_profile'),
    path('profile/operator/', views.OperatorProfileView.as_view(), name='operator_profile'),
    path('profile/technician/', views.TechnicianProfileView.as_view(), name='technician_profile'),
    path('profile/admin/', views.AdminProfileView.as_view(), name='admin_profile'),
    
    # Edit profile pages
    path('profile/citizen/edit/', views.CitizenEditProfileView.as_view(), name='citizen_edit_profile'),
    path('profile/operator/edit/', views.OperatorEditProfileView.as_view(), name='operator_edit_profile'),
    path('profile/technician/edit/', views.TechnicianEditProfileView.as_view(), name='technician_edit_profile'),
    path('profile/admin/edit/', views.AdminEditProfileView.as_view(), name='admin_edit_profile'),
    
    # Admin user management
    path('admin/citizens/', views.AdminCitizenListView.as_view(), name='admin_citizen_list'),
    path('admin/operators/', views.AdminOperatorListView.as_view(), name='admin_operator_list'),
    path('admin/technicians/', views.AdminTechnicianListView.as_view(), name='admin_technician_list'),
    path('admin/user/add/', views.AdminAddUserView.as_view(), name='admin_add_user'),
    path('admin/user/<int:pk>/delete/', views.AdminDeleteUserView.as_view(), name='admin_delete_user'),
    path('admin/user/<int:pk>/approve/', views.AdminApproveUserView.as_view(), name='admin_approve_user'),
]

