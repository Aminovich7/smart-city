from django.urls import path
from . import views

app_name = 'incidents'

urlpatterns = [
    path('', views.CitizenIncidentListView.as_view(), name='citizen_incident_list'),
    path('create/', views.CitizenIncidentCreateView.as_view(), name='citizen_incident_create'),
    path('<int:pk>/', views.IncidentDetailView.as_view(), name='incident_detail'),
    path('<int:pk>/feedback/', views.CitizenFeedbackView.as_view(), name='citizen_feedback'),
    path('operator/', views.OperatorIncidentListView.as_view(), name='operator_incident_list'),
    path('operator/<int:pk>/assign/', views.OperatorAssignTechnicianView.as_view(), name='assign_technician'),
    path('operator/<int:pk>/add-photos/', views.OperatorAddCompletionPhotosView.as_view(), name='operator_add_photos'),
    path('operator/<int:pk>/close/', views.OperatorCloseIncidentView.as_view(), name='operator_close_incident'),
    path('operator/<int:pk>/priority/', views.OperatorUpdatePriorityView.as_view(), name='update_priority'),
    path('operator/technicians/', views.OperatorTechnicianListView.as_view(), name='operator_technician_list'),
    path('operator/incidents/', views.OperatorIncidentListView.as_view(), name='operator_incident_list'),
    path('technician/', views.TechnicianAssignedIncidentListView.as_view(), name='technician_incident_list'),
    path('technician/<int:pk>/resolve/', views.TechnicianResolveIncidentView.as_view(), name='resolve_incident'),


]
