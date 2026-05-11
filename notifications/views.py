from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View
from django.views.generic import ListView
from django.shortcuts import get_object_or_404, redirect
from .models import Notification

class NotificationListView(LoginRequiredMixin, ListView):
    template_name = 'notifications/notification_list.html'
    context_object_name = 'notifications'
    paginate_by = 10

    def get_queryset(self):
        qs = Notification.objects.filter(user=self.request.user)
        # Mark all as read when the list is viewed
        qs.filter(is_read=False).update(is_read=True)
        return qs

class MarkNotificationReadView(LoginRequiredMixin, View):
    def post(self, request, pk):
        notification = get_object_or_404(Notification, pk=pk, user=request.user)
        notification.is_read = True
        notification.save(update_fields=['is_read'])
        if notification.incident:
            return redirect('incidents:incident_detail', pk=notification.incident.pk)
        return redirect('notifications:notification_list')

class MarkAllReadView(LoginRequiredMixin, View):
    def post(self, request):
        Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
        return redirect('notifications:notification_list')
