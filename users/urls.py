from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.operator_dashboard, name='operator_dashboard'),
    path('task/assign/', views.assign_task_to_me, name='assign_task_to_me'),
    path('task/complete/', views.complete_task, name='complete_task'),
    path('colleagues/', views.department_colleagues, name='department_colleagues'),
]