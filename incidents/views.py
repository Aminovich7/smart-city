from django.contrib import messages
from notifications.utils import notify, notify_many
from users.models import CustomUser
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ValidationError
from django.core.paginator import Paginator
from django.db import transaction
from django.http import Http404, HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views.generic import CreateView, DetailView, ListView, View
from .forms import (
    AdditionalCompletionPhotosForm,
    AssignTechnicianForm,
    FeedbackForm,
    IncidentCreationForm,
    ResolutionForm, PriorityUpdateForm,
)
from .models import Incident, IncidentPhoto
from users.mixins import CitizenRequiredMixin, OperatorRequiredMixin, TechnicianRequiredMixin
from users.models import CustomUser


class IncidentAccessMixin(LoginRequiredMixin):
    def get_queryset(self):
        user = self.request.user
        queryset = Incident.objects.select_related('citizen', 'operator', 'technician').prefetch_related('photos', 'updates', 'resolution_reports')
        if user.role == CustomUser.Role.CITIZEN:
            return queryset.filter(citizen=user)
        if user.role in {CustomUser.Role.OPERATOR, CustomUser.Role.ADMIN}:
            return queryset
        if user.role == CustomUser.Role.TECHNICIAN:
            return queryset.filter(technician=user)
        return queryset.none()


class CitizenIncidentListView(CitizenRequiredMixin, ListView):
    template_name = 'incidents/citizen_incident_list.html'
    context_object_name = 'incidents'
    paginate_by = 10

    def get_queryset(self):
        return Incident.objects.filter(citizen=self.request.user).select_related('technician').order_by('-created_at')


class CitizenIncidentCreateView(CitizenRequiredMixin, CreateView):
    model = Incident
    form_class = IncidentCreationForm
    template_name = 'incidents/create_incident_form.html'
    success_url = reverse_lazy('incidents:citizen_incident_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category_cards'] = [
            {'key': Incident.Category.SANITATION, 'title': 'Tozalik', 'tech': 'Tozalovchi', 'desc': 'Chiqindi, noqonuniy tashlangan axlat, konteyner muammolari.'},
            {'key': Incident.Category.ELECTRICITY, 'title': 'Elektr', 'tech': 'Elektrik', 'desc': 'Kabellar, elektr uzilishi, ustun yoki quti nosozliklari.'},
            {'key': Incident.Category.WATER, 'title': 'Suv', 'tech': 'Santexnik', 'desc': 'Quvur yorilishi, sizib chiqish, suv bosimi bilan bog`liq muammolar.'},
            {'key': Incident.Category.LIGHTING, 'title': 'Yoritish', 'tech': 'Yoritish texnigi', 'desc': 'Ko`cha chiroqlari, lampalar va ustunlardagi nosozliklar.'},
            {'key': Incident.Category.ROAD, 'title': 'Yo`l', 'tech': 'Yo`l ustasi', 'desc': 'Chuqur, asfalt buzilishi, trotuar sinishi.'},
            {'key': Incident.Category.DRAINAGE, 'title': 'Drenaj', 'tech': 'Kanalizatsiya ustasi', 'desc': 'Tiqilib qolgan drenaj, quduq, kanalizatsiya oqimi.'},
            {'key': Incident.Category.LANDSCAPING, 'title': 'Ko`kalamzor', 'tech': 'Ko`kalamzorlashtirish ustasi', 'desc': 'Daraxt kesish, buta tozalash, yashil hudud muammolari.'},
            {'key': Incident.Category.SIGNAL, 'title': 'Svetofor', 'tech': 'Belgi ustasi', 'desc': 'Svetofor, yo`l belgilari va xavfsizlik infratuzilmasi.'},
            {'key': Incident.Category.OTHER, 'title': 'Boshqa', 'tech': 'Universal texnik', 'desc': 'Ro`yxatda bo`lmagan holatlar uchun qo`shimcha izoh yoziladi.'},
        ]
        return context

    def form_valid(self, form):
        photos = form.cleaned_data.get('photos', [])
        if not isinstance(photos, list):
            photos = [photos]
        if len(photos) != 3:
            form.add_error('photos', "Aynan 3 ta foto yuklash majburiy.")
            return self.form_invalid(form)
        form.instance.citizen = self.request.user
        form.instance.status = Incident.Status.NEW
        with transaction.atomic():
            self.object = form.save()
            for photo in photos:
                IncidentPhoto.objects.create(
                    incident=self.object,
                    uploaded_by=self.request.user,
                    kind=IncidentPhoto.Kind.INITIAL,
                    round_number=0,
                    image=photo,
                )
            self.object.add_update(
                actor=self.request.user,
                from_status=Incident.Status.NEW,
                to_status=Incident.Status.NEW,
                note="Incident yaratildi.",
            )
        # --- NOTIFICATION ADDED: notify all approved operators about new incident
        operators = CustomUser.objects.filter(role=CustomUser.Role.OPERATOR, is_approved=True)
        notify_many(
            users=operators,
            incident=self.object,
            message=f"Yangi incident yaratildi: #{self.object.pk} — {self.object.title}",
            notification_type='status_change',
        )
        messages.success(self.request, "Incident yuborildi.")
        return HttpResponseRedirect(self.success_url)


class IncidentDetailView(IncidentAccessMixin, DetailView):
    model = Incident
    template_name = 'incidents/incident_detail.html'
    context_object_name = 'incident'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        incident = self.object
        context['feedback'] = getattr(incident, 'feedback_entry', None)
        context['resolution_report'] = incident.resolution_reports.order_by('-round_number', '-created_at').first()
        return context

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        if obj.close_if_overdue():
            # Notify citizen
            notify(
                user=obj.citizen,
                incident=obj,
                message=f"#{obj.pk} — {obj.title}: 7 kun ichida fikr bildirilmagani uchun avtomatik yopildi.",
                notification_type='closed',
            )
            # Notify all approved operators
            operators = CustomUser.objects.filter(role=CustomUser.Role.OPERATOR, is_approved=True)
            notify_many(
                users=operators,
                incident=obj,
                message=f"#{obj.pk} — {obj.title}: avtomatik yopildi.",
                notification_type='closed',
            )
            obj.refresh_from_db()  # optional but safe
        return obj


class OperatorIncidentListView(OperatorRequiredMixin, ListView):
    template_name = 'incidents/operator_incident_list.html'
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
        context['available_technicians'] = CustomUser.objects.filter(
            role=CustomUser.Role.TECHNICIAN, is_approved=True, current_workload=0
        ).order_by('specialization', 'first_name')
        context['specialization_labels'] = CustomUser.specialization_choices_map()
        context['current_filters'] = {
            'priority': self.request.GET.get('priority', ''),
            'assigned': self.request.GET.get('assigned', ''),
            'status': self.request.GET.get('status', ''),
        }
        context['priority_choices'] = Incident.Priority.choices
        context['status_choices'] = Incident.Status.choices
        return context


class OperatorAssignTechnicianView(OperatorRequiredMixin, View):
    template_name = 'incidents/operator/assign_technician.html'

    def get_incident(self, pk):
        return get_object_or_404(Incident.objects.select_related('technician'), pk=pk)

    def technician_queryset(self, incident):
        return CustomUser.objects.filter(
            role=CustomUser.Role.TECHNICIAN,
            is_approved=True,
            specialization__in=incident.matching_specializations,
        ).order_by('current_workload', 'first_name')

    def get(self, request, pk):
        incident = self.get_incident(pk)
        form = AssignTechnicianForm(instance=incident)
        form.fields['technician'].queryset = self.technician_queryset(incident)
        return render(
            request,
            self.template_name,
            {
                'form': form,
                'incident': incident,
                'matching_specializations': [CustomUser.specialization_choices_map()[item] for item in incident.matching_specializations],
            },
        )

    def post(self, request, pk):
        incident = self.get_incident(pk)
        form = AssignTechnicianForm(request.POST, instance=incident)
        form.fields['technician'].queryset = self.technician_queryset(incident)
        if not form.is_valid():
            return render(
                request,
                self.template_name,
                {
                    'form': form,
                    'incident': incident,
                    'matching_specializations': [CustomUser.specialization_choices_map()[item] for item in incident.matching_specializations],
                },
            )
        try:
            incident.assign_technician(
                operator=request.user,
                technician=form.cleaned_data['technician'],
                note="Operator texnik biriktirdi." if incident.status == Incident.Status.NEW else "Operator incidentni qayta biriktirdi.",
            )
        except ValidationError as exc:
            form.add_error(None, exc.message)
            return render(
                request,
                self.template_name,
                {
                    'form': form,
                    'incident': incident,
                    'matching_specializations': [CustomUser.specialization_choices_map()[item] for item in incident.matching_specializations],
                },
            )
        # --- NOTIFICATION ADDED: notify technician and citizen about assignment
        notify(
            user=incident.technician,
            incident=incident,
            message=f"Sizga yangi incident biriktirildi: #{incident.pk} — {incident.title}",
            notification_type='assignment',
        )
        notify(
            user=incident.citizen,
            incident=incident,
            message=f"#{incident.pk} — {incident.title} incidentingizga texnik biriktirildi.",
            notification_type='status_change',
        )
        messages.success(request, "Texnik muvaffaqiyatli biriktirildi.")
        return redirect('incidents:operator_incident_list')


class OperatorAddCompletionPhotosView(OperatorRequiredMixin, View):
    template_name = 'incidents/operator/add_additional_completion_photos.html'

    def get(self, request, pk):
        incident = get_object_or_404(Incident, pk=pk)
        form = AdditionalCompletionPhotosForm()
        return render(request, self.template_name, {'incident': incident, 'form': form})

    def post(self, request, pk):
        incident = get_object_or_404(Incident, pk=pk)
        form = AdditionalCompletionPhotosForm(request.POST, request.FILES)
        if not form.is_valid():
            return render(request, self.template_name, {'incident': incident, 'form': form})

        photos = form.cleaned_data.get('photos', [])
        if not isinstance(photos, list):
            photos = [photos]
        if len(photos) > 2:
            form.add_error('photos', "Operator ko`pi bilan 2 ta foto yuklay oladi.")
            return render(request, self.template_name, {'incident': incident, 'form': form})

        try:
            for photo in photos:
                IncidentPhoto.objects.create(
                    incident=incident,
                    uploaded_by=request.user,
                    kind=IncidentPhoto.Kind.OPERATOR_COMPLETION,
                    round_number=incident.workflow_round,
                    image=photo,
                )
        except ValidationError as exc:
            form.add_error(None, exc.message)
            return render(request, self.template_name, {'incident': incident, 'form': form})
        messages.success(request, "Qo`shimcha fotolar saqlandi.")
        return redirect('incidents:incident_detail', pk=incident.pk)


class OperatorCloseIncidentView(OperatorRequiredMixin, View):
    def post(self, request, pk):
        incident = get_object_or_404(Incident, pk=pk)
        feedback = getattr(incident, 'feedback_entry', None)
        can_close = incident.workflow_round > 1 or (feedback is not None and feedback.is_resolved)
        if not can_close:
            messages.error(request, "Bu incidentni hozir operator yopishi mumkin emas.")
            return redirect('incidents:incident_detail', pk=incident.pk)
        try:
            incident.mark_closed(actor=request.user, note="Operator incidentni yakuniy yopdi.")
        except ValidationError as exc:
            messages.error(request, exc.message)
            return redirect('incidents:incident_detail', pk=incident.pk)
        # --- NOTIFICATION ADDED: inform citizen that incident is closed
        notify(
            user=incident.citizen,
            incident=incident,
            message=f"#{incident.pk} — {incident.title} incidenti yopildi.",
            notification_type='closed',
        )
        messages.success(request, "Incident yopildi.")
        return redirect('incidents:operator_incident_list')


class TechnicianAssignedIncidentListView(TechnicianRequiredMixin, ListView):
    template_name = 'incidents/technician/technician_assigned_list.html'
    context_object_name = 'active_incidents'
    paginate_by = 10

    def get_queryset(self):
        return Incident.objects.filter(technician=self.request.user, status=Incident.Status.IN_PROGRESS).order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        resolved_qs = Incident.objects.filter(
            technician=self.request.user, status=Incident.Status.RESOLVED
        ).order_by('-created_at')
        closed_qs = Incident.objects.filter(
            technician=self.request.user, status=Incident.Status.CLOSED
        ).order_by('-created_at')

        resolved_paginator = Paginator(resolved_qs, self.paginate_by)
        resolved_page_number = self.request.GET.get('resolved_page')
        resolved_page_obj = resolved_paginator.get_page(resolved_page_number)

        closed_paginator = Paginator(closed_qs, self.paginate_by)
        closed_page_number = self.request.GET.get('closed_page')
        closed_page_obj = closed_paginator.get_page(closed_page_number)

        context['resolved_page_obj'] = resolved_page_obj
        context['closed_page_obj'] = closed_page_obj
        context['resolved_incidents'] = resolved_page_obj.object_list
        context['closed_incidents'] = closed_page_obj.object_list
        return context


class TechnicianResolveIncidentView(TechnicianRequiredMixin, View):
    template_name = 'incidents/technician/resolve_incident.html'

    def get_incident(self, request, pk):
        return get_object_or_404(Incident, pk=pk, technician=request.user)

    def get(self, request, pk):
        incident = self.get_incident(request, pk)
        if incident.status != Incident.Status.IN_PROGRESS:
            raise Http404
        return render(request, self.template_name, {'incident': incident, 'form': ResolutionForm()})

    def post(self, request, pk):
        incident = self.get_incident(request, pk)
        form = ResolutionForm(request.POST, request.FILES)

        if incident.status != Incident.Status.IN_PROGRESS:
            form.add_error(None, "Bu incidentni hozir yakunlab bo'lmaydi.")
            return render(request, self.template_name, {'incident': incident, 'form': form})

        if not form.is_valid():
            return render(request, self.template_name, {'incident': incident, 'form': form})

        # Now safely use cleaned data
        photos = form.cleaned_data.get('photos', [])
        if not isinstance(photos, list):
            photos = [photos]
        if len(photos) != 3:
            form.add_error('photos', "Texnik aynan 3 ta yakuniy foto yuklashi kerak.")
            return render(request, self.template_name, {'incident': incident, 'form': form})

        try:
            with transaction.atomic():
                report = form.save(commit=False)
                report.incident = incident
                report.technician = request.user
                report.round_number = incident.workflow_round
                report.full_clean()
                report.save()
                for photo in photos:
                    IncidentPhoto.objects.create(
                        incident=incident,
                        uploaded_by=request.user,
                        kind=IncidentPhoto.Kind.TECHNICIAN_COMPLETION,
                        round_number=incident.workflow_round,
                        image=photo,
                    )
                incident.mark_resolved(
                    technician=request.user,
                    note="Texnik 3 ta yakuniy foto va hisobot bilan incidentni hal qildi.",
                )
        except ValidationError as exc:
            form.add_error(None, exc.message)
            return render(request, self.template_name, {'incident': incident, 'form': form})

        # Notifications (unchanged)
        notify(
            user=incident.citizen,
            incident=incident,
            message=f"#{incident.pk} — {incident.title} incidentingiz hal qilindi.",
            notification_type='resolution',
        )
        operators = CustomUser.objects.filter(role=CustomUser.Role.OPERATOR, is_approved=True)
        notify_many(
            users=operators,
            incident=incident,
            message=f"#{incident.pk} — {incident.title} texnik tomonidan yakunlandi.",
            notification_type='resolution',
        )
        messages.success(request, "Incident RESOLVED holatiga o`tkazildi.")
        return redirect('incidents:technician_incident_list')

class CitizenFeedbackView(CitizenRequiredMixin, View):
    template_name = 'incidents/citizen_feedback_form.html'

    def get_incident(self, request, pk):
        return get_object_or_404(Incident, pk=pk, citizen=request.user)

    def get(self, request, pk):
        incident = self.get_incident(request, pk)
        if incident.status != Incident.Status.RESOLVED or hasattr(incident, 'feedback_entry'):
            messages.error(request, "Bu incident uchun fikr yuborish imkoni mavjud emas.")
            return redirect('incidents:incident_detail', pk=incident.pk)
        return render(request, self.template_name, {'incident': incident, 'form': FeedbackForm()})

    def post(self, request, pk):
        incident = self.get_incident(request, pk)
        if incident.status != Incident.Status.RESOLVED or hasattr(incident, 'feedback_entry'):
            messages.error(request, "Fikr faqat bir marta yuboriladi.")
            return redirect('incidents:incident_detail', pk=incident.pk)
        form = FeedbackForm(request.POST)
        if not form.is_valid():
            return render(request, self.template_name, {'incident': incident, 'form': form})
        feedback = form.save(commit=False)
        feedback.incident = incident
        feedback.citizen = request.user
        try:
            feedback.full_clean()
            feedback.save()
        except ValidationError as exc:
            form.add_error(None, exc.message)
            return render(request, self.template_name, {'incident': incident, 'form': form})
        # --- NOTIFICATION ADDED: if citizen says problem not resolved, alert all approved operators
        if not feedback.is_resolved:
            operators = CustomUser.objects.filter(role=CustomUser.Role.OPERATOR, is_approved=True)
            notify_many(
                users=operators,
                incident=incident,
                message=f"#{incident.pk} — {incident.title}: fuqaro muammo hal bo'lmaganligini bildirdi.",
                notification_type='feedback',
            )
        messages.success(request, "Fikringiz saqlandi.")
        return redirect('incidents:incident_detail', pk=incident.pk)





class OperatorUpdatePriorityView(OperatorRequiredMixin, View):
    def post(self, request, pk):
        incident = get_object_or_404(Incident, pk=pk)
        form = PriorityUpdateForm(request.POST, instance=incident)
        if form.is_valid():
            form.save()
            messages.success(request, "Muhimlik darajasi yangilandi.")
        else:
            messages.error(request, "Noto'g'ri qiymat.")
        return redirect('incidents:incident_detail', pk=incident.pk)




class OperatorTechnicianListView(OperatorRequiredMixin, ListView):
    template_name = 'incidents/operator/technician_list.html'
    context_object_name = 'technicians'
    paginate_by = 20

    def get_queryset(self):
        return CustomUser.objects.filter(
            role=CustomUser.Role.TECHNICIAN,
            is_approved=True,
        ).order_by('specialization', 'first_name')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['specialization_labels'] = CustomUser.specialization_choices_map()
        return context
