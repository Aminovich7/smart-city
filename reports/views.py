from django.views.generic import ListView, TemplateView
from incidents.models import Incident
from users.mixins import AdminRequiredMixin, CitizenRequiredMixin, TechnicianRequiredMixin


class CitizenDashboardView(CitizenRequiredMixin, TemplateView):
    template_name = 'reports/citizen_dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        incidents = Incident.objects.filter(citizen=self.request.user)
        context['total_incidents'] = incidents.count()
        context['new_incidents'] = incidents.filter(status=Incident.Status.NEW).count()
        context['in_progress_incidents'] = incidents.filter(status=Incident.Status.IN_PROGRESS).count()
        context['resolved_incidents'] = incidents.filter(status=Incident.Status.RESOLVED).count()
        context['closed_incidents'] = incidents.filter(status=Incident.Status.CLOSED).count()
        return context


class TechnicianDashboardView(TechnicianRequiredMixin, TemplateView):
    template_name = 'reports/technician_dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        incidents = Incident.objects.filter(technician=self.request.user)
        context['active_count'] = incidents.filter(status=Incident.Status.IN_PROGRESS).count()
        context['resolved_count'] = incidents.filter(status=Incident.Status.RESOLVED).count()
        context['closed_count'] = incidents.filter(status=Incident.Status.CLOSED).count()
        return context


class SystemReportsView(AdminRequiredMixin, ListView):
    template_name = 'reports/admin_system_reports.html'
    context_object_name = 'incidents'
    paginate_by = 10

    def get_queryset(self):
        qs = Incident.objects.select_related('citizen', 'technician', 'operator').order_by('-created_at')

        priority = self.request.GET.get('priority')
        if priority in [p.value for p in Incident.Priority]:
            qs = qs.filter(priority=priority)

        assigned = self.request.GET.get('assigned')
        if assigned == 'yes':
            qs = qs.filter(technician__isnull=False)
        elif assigned == 'no':
            qs = qs.filter(technician__isnull=True)

        status = self.request.GET.get('status')
        if status in [s.value for s in Incident.Status]:
            qs = qs.filter(status=status)

        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['current_filters'] = {
            'priority': self.request.GET.get('priority', ''),
            'assigned': self.request.GET.get('assigned', ''),
            'status': self.request.GET.get('status', ''),
        }
        context['priority_choices'] = Incident.Priority.choices
        context['status_choices'] = Incident.Status.choices
        return context
