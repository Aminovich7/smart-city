from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView, LogoutView
from django.urls import reverse_lazy
from django.shortcuts import get_object_or_404, redirect
from django.views.generic import CreateView, RedirectView, TemplateView, DetailView, UpdateView, ListView, DeleteView, View
from django.contrib import messages
from django import forms
from .forms import (
    AdminRegistrationForm,
    CitizenRegistrationForm,
    OperatorRegistrationForm,
    StyledFormMixin,
    TechnicianRegistrationForm,
)
from .models import CustomUser
from users.mixins import CitizenRequiredMixin, OperatorRequiredMixin, TechnicianRequiredMixin


class HomeView(TemplateView):
    template_name = 'home.html'


class RoleRegisterOptionsView(TemplateView):
    template_name = 'users/register_options.html'


class BaseRoleRegistrationView(CreateView):
    model = CustomUser
    template_name = 'users/role_register.html'
    success_url = reverse_lazy('users:login')
    role_label = ''

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['role_label'] = self.role_label
        return context


class CitizenRegistrationView(BaseRoleRegistrationView):
    form_class = CitizenRegistrationForm
    role_label = 'Fuqaro'


class TechnicianRegistrationView(BaseRoleRegistrationView):
    form_class = TechnicianRegistrationForm
    role_label = 'Texnik'


class OperatorRegistrationView(BaseRoleRegistrationView):
    form_class = OperatorRegistrationForm
    role_label = 'Operator'


class AdminRegistrationView(BaseRoleRegistrationView):
    form_class = AdminRegistrationForm
    role_label = 'Admin'


class CustomLoginView(LoginView):
    template_name = 'users/login.html'
    redirect_authenticated_user = True

    def get_success_url(self):
        user = self.request.user
        if user.role == CustomUser.Role.CITIZEN:
            return reverse_lazy('incidents:citizen_incident_list')
        if user.role == CustomUser.Role.OPERATOR:
            return reverse_lazy('incidents:operator_incident_list')
        if user.role == CustomUser.Role.TECHNICIAN:
            return reverse_lazy('incidents:technician_incident_list')
        if user.role == CustomUser.Role.ADMIN:
            return reverse_lazy('reports:admin_system_reports')
        return reverse_lazy('users:home')


class CustomLogoutView(LogoutView):
    next_page = reverse_lazy('users:home')


class DashboardRedirectView(RedirectView):
    permanent = False

    def get_redirect_url(self, *args, **kwargs):
        if not self.request.user.is_authenticated:
            return reverse_lazy('users:login')
        user = self.request.user
        if user.role == CustomUser.Role.CITIZEN:
            return reverse_lazy('incidents:citizen_incident_list')
        if user.role == CustomUser.Role.OPERATOR:
            return reverse_lazy('incidents:operator_incident_list')
        if user.role == CustomUser.Role.TECHNICIAN:
            return reverse_lazy('incidents:technician_incident_list')
        if user.role == CustomUser.Role.ADMIN:
            return reverse_lazy('reports:admin_system_reports')
        return reverse_lazy('users:home')




class PendingApprovalView(LoginRequiredMixin, TemplateView):
    template_name = 'users/pending_approval.html'


# Profile Views
from django.views.generic import DetailView, UpdateView, ListView
from django.contrib.auth.forms import PasswordChangeForm
from django.core.paginator import Paginator
from django.db.models import Avg
from users.mixins import AdminRequiredMixin as AdminMixin

class CitizenProfileView(CitizenRequiredMixin, DetailView):
    model = CustomUser
    template_name = 'users/citizen_profile.html'
    context_object_name = 'user'

    def get_object(self):
        return self.request.user

    def get_context_data(self, **kwargs):
        from incidents.models import Incident
        context = super().get_context_data(**kwargs)
        incidents = Incident.objects.filter(citizen=self.request.user)
        context['total_incidents'] = incidents.count()
        context['resolved_count'] = incidents.filter(status=Incident.Status.RESOLVED).count()
        context['closed_count'] = incidents.filter(status=Incident.Status.CLOSED).count()
        return context


class OperatorProfileView(OperatorRequiredMixin, DetailView):
    model = CustomUser
    template_name = 'users/operator_profile.html'
    context_object_name = 'user'

    def get_object(self):
        return self.request.user

    def get_context_data(self, **kwargs):
        from incidents.models import Incident
        context = super().get_context_data(**kwargs)
        incidents = Incident.objects.filter(operator=self.request.user)
        context['total_incidents_handled'] = incidents.count()
        context['closed_count'] = incidents.filter(status=Incident.Status.CLOSED).count()
        context['pending_count'] = incidents.filter(status__in=[Incident.Status.NEW, Incident.Status.IN_PROGRESS]).count()
        return context


class TechnicianProfileView(TechnicianRequiredMixin, DetailView):
    model = CustomUser
    template_name = 'users/technician_profile.html'
    context_object_name = 'user'

    def get_object(self):
        return self.request.user

    def get_context_data(self, **kwargs):
        from incidents.models import CitizenFeedback, Incident
        context = super().get_context_data(**kwargs)
        incidents = Incident.objects.filter(technician=self.request.user)
        context['active_count'] = incidents.filter(status=Incident.Status.IN_PROGRESS).count()
        context['completed_count'] = incidents.filter(status=Incident.Status.RESOLVED).count()
        # Calculate average rating from feedback
        feedbacks = CitizenFeedback.objects.filter(incident__technician=self.request.user).exclude(rating__isnull=True)
        if feedbacks.exists():
            avg_rating = feedbacks.aggregate(avg=Avg('rating'))['avg']
            context['average_rating'] = round(avg_rating, 2) if avg_rating else None
        return context


class AdminProfileView(AdminMixin, DetailView):
    model = CustomUser
    template_name = 'users/admin_profile.html'
    context_object_name = 'user'

    def get_object(self):
        return self.request.user

    def get_context_data(self, **kwargs):
        from incidents.models import Incident
        context = super().get_context_data(**kwargs)
        context['total_citizens'] = CustomUser.objects.filter(role=CustomUser.Role.CITIZEN).count()
        context['total_operators'] = CustomUser.objects.filter(role=CustomUser.Role.OPERATOR).count()
        context['total_technicians'] = CustomUser.objects.filter(role=CustomUser.Role.TECHNICIAN).count()
        context['total_incidents'] = Incident.objects.count()
        context['pending_approvals'] = CustomUser.objects.filter(
            role__in=[CustomUser.Role.OPERATOR, CustomUser.Role.TECHNICIAN],
            is_approved=False
        ).count()
        return context


# Edit Profile Forms and Views
from django import forms

class EditProfileForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'email', 'phone']


class CitizenEditProfileForm(EditProfileForm):
    class Meta(EditProfileForm.Meta):
        fields = ['first_name', 'last_name', 'email', 'phone', 'address']


class OperatorEditProfileForm(EditProfileForm):
    class Meta(EditProfileForm.Meta):
        fields = ['first_name', 'last_name', 'email', 'phone', 'department']


class TechnicianEditProfileForm(EditProfileForm):
    class Meta(EditProfileForm.Meta):
        fields = ['first_name', 'last_name', 'email', 'phone', 'specialization']


class AdminEditProfileForm(EditProfileForm):
    class Meta(EditProfileForm.Meta):
        fields = ['first_name', 'last_name', 'email']


class CitizenEditProfileView(CitizenRequiredMixin, UpdateView):
    model = CustomUser
    form_class = CitizenEditProfileForm
    template_name = 'users/citizen_edit_profile.html'
    success_url = reverse_lazy('users:citizen_profile')

    def get_object(self):
        return self.request.user


class OperatorEditProfileView(OperatorRequiredMixin, UpdateView):
    model = CustomUser
    form_class = OperatorEditProfileForm
    template_name = 'users/operator_edit_profile.html'
    success_url = reverse_lazy('users:operator_profile')

    def get_object(self):
        return self.request.user


class TechnicianEditProfileView(TechnicianRequiredMixin, UpdateView):
    model = CustomUser
    form_class = TechnicianEditProfileForm
    template_name = 'users/technician_edit_profile.html'
    success_url = reverse_lazy('users:technician_profile')

    def get_object(self):
        return self.request.user


class AdminEditProfileView(AdminMixin, UpdateView):
    model = CustomUser
    form_class = AdminEditProfileForm
    template_name = 'users/admin_edit_profile.html'
    success_url = reverse_lazy('users:admin_profile')

    def get_object(self):
        return self.request.user


# Admin User Management Views
class AdminCitizenListView(AdminMixin, ListView):
    model = CustomUser
    template_name = 'users/admin_citizen_list.html'
    context_object_name = 'users'
    paginate_by = 20

    def get_queryset(self):
        return CustomUser.objects.filter(role=CustomUser.Role.CITIZEN).order_by('-date_joined')


class AdminOperatorListView(AdminMixin, ListView):
    model = CustomUser
    template_name = 'users/admin_operator_list.html'
    context_object_name = 'users'
    paginate_by = 20

    def get_queryset(self):
        return CustomUser.objects.filter(role=CustomUser.Role.OPERATOR).order_by('-date_joined')


class AdminTechnicianListView(AdminMixin, ListView):
    model = CustomUser
    template_name = 'users/admin_technician_list.html'
    context_object_name = 'users'
    paginate_by = 20

    def get_queryset(self):
        return CustomUser.objects.filter(role=CustomUser.Role.TECHNICIAN).order_by('-date_joined')


class AdminAddUserView(AdminMixin, CreateView):
    model = CustomUser
    form_class = None  # Will use role-specific form
    template_name = 'users/admin_add_user.html'
    success_url = reverse_lazy('users:admin_profile')

    def get_form_class(self):
        role = self.request.GET.get('role', 'citizen')
        if role == 'citizen':
            return CitizenRegistrationForm
        elif role == 'operator':
            return OperatorRegistrationForm
        elif role == 'technician':
            return TechnicianRegistrationForm
        elif role == 'admin':
            return AdminRegistrationForm
        return CitizenRegistrationForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['role'] = self.request.GET.get('role', 'citizen')
        return context


class AdminDeleteUserView(AdminMixin, DeleteView):
    model = CustomUser
    template_name = 'users/admin_user_confirm_delete.html'
    success_url = reverse_lazy('users:admin_profile')


class AdminApproveUserView(AdminMixin, View):
    def post(self, request, *args, **kwargs):
        target_user = get_object_or_404(CustomUser, pk=kwargs['pk'])
        if target_user.role not in [CustomUser.Role.OPERATOR, CustomUser.Role.TECHNICIAN]:
            messages.error(request, "Faqat operator yoki texnik tasdiqlanishi mumkin.")
            return redirect('users:admin_profile')
        target_user.is_approved = not target_user.is_approved
        target_user.save(update_fields=['is_approved'])
        return redirect(request.META.get('HTTP_REFERER', reverse_lazy('users:admin_profile')))
