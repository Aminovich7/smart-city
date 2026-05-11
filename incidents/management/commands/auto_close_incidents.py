from django.core.management.base import BaseCommand
from django.utils import timezone
from incidents.models import Incident
from notifications.utils import notify, notify_many
from users.models import CustomUser


class Command(BaseCommand):
    help = "7 kundan keyin feedback kelmagan RESOLVED incidentlarni yopadi."

    def handle(self, *args, **options):
        count = 0
        now = timezone.now()
        for incident in Incident.objects.filter(status=Incident.Status.RESOLVED).select_related('citizen'):
            if incident.close_if_overdue(now=now):
                self.stdout.write(f'Yopildi: #{incident.id}')
                # --- NOTIFY CITIZEN ---
                notify(
                    user=incident.citizen,
                    incident=incident,
                    message=f"#{incident.pk} — {incident.title}: 7 kun ichida fikr bildirilmagani uchun avtomatik yopildi.",
                    notification_type='closed',
                )
                # --- NOTIFY ALL APPROVED OPERATORS ---
                operators = CustomUser.objects.filter(role=CustomUser.Role.OPERATOR, is_approved=True)
                notify_many(
                    users=operators,
                    incident=incident,
                    message=f"#{incident.pk} — {incident.title}: avtomatik yopildi.",
                    notification_type='closed',
                )
                count += 1
        self.stdout.write(f'Jami yopilgan incidentlar: {count}')