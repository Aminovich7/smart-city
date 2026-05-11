from datetime import timedelta
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.management import call_command
from django.test import Client, TestCase
from django.urls import reverse
from django.utils import timezone
from users.models import CustomUser
from .models import CitizenFeedback, Incident, IncidentPhoto, ResolutionReport


def uploaded(name):
    return SimpleUploadedFile(name, b'filecontent', content_type='image/jpeg')


class IncidentWorkflowTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.citizen = CustomUser.objects.create_user(
            username='citizen1',
            password='StrongPass123',
            first_name='Ali',
            last_name='Valiyev',
            phone='+998901111111',
            role=CustomUser.Role.CITIZEN,
            address='Toshkent',
        )
        self.operator = CustomUser.objects.create_user(
            username='operator1',
            password='StrongPass123',
            first_name='Olim',
            last_name='Karimov',
            phone='+998902222222',
            role=CustomUser.Role.OPERATOR,
            department='Dispetcherlik',
        )
        self.technician = CustomUser.objects.create_user(
            username='technician1',
            password='StrongPass123',
            first_name='Temur',
            last_name='Sodiqov',
            phone='+998903333333',
            role=CustomUser.Role.TECHNICIAN,
            specialization=CustomUser.Specialization.LIGHTING_TECH,
        )

    def create_incident(self):
        return Incident.objects.create(
            citizen=self.citizen,
            title='Chiroq ishlamayapti',
            description='Ko`chadagi chiroq o`chib qolgan.',
            category=Incident.Category.LIGHTING,
            priority=Incident.Priority.MEDIUM,
            region=Incident.Region.TOSHKENT,
            address='Yunusobod, 12-uy',
        )

    def test_citizen_initial_photos_are_stored_as_exactly_three(self):
        incident = self.create_incident()
        for index in range(3):
            IncidentPhoto.objects.create(
                incident=incident,
                uploaded_by=self.citizen,
                kind=IncidentPhoto.Kind.INITIAL,
                round_number=0,
                image=uploaded(f'init{index}.jpg'),
            )
        self.assertEqual(incident.photos.count(), 3)
        with self.assertRaises(Exception):
            IncidentPhoto.objects.create(
                incident=incident,
                uploaded_by=self.citizen,
                kind=IncidentPhoto.Kind.INITIAL,
                round_number=0,
                image=uploaded('extra.jpg'),
            )

    def test_operator_assigns_technician_and_workload_increments(self):
        incident = self.create_incident()
        incident.assign_technician(operator=self.operator, technician=self.technician)
        incident.refresh_from_db()
        self.technician.refresh_from_db()
        self.assertEqual(incident.status, Incident.Status.IN_PROGRESS)
        self.assertEqual(incident.technician, self.technician)
        self.assertEqual(incident.workflow_round, 1)
        self.assertEqual(self.technician.current_workload, 1)

    def test_other_category_requires_note(self):
        incident = Incident(
            citizen=self.citizen,
            title='Lift ishlamayapti',
            description='Ko`p qavatli uy lifti to`xtagan.',
            category=Incident.Category.OTHER,
            priority=Incident.Priority.MEDIUM,
            region=Incident.Region.TOSHKENT,
            address='Mirzo Ulug`bek tumani',
        )
        with self.assertRaises(Exception):
            incident.full_clean()

    def test_technician_resolves_incident_with_three_completion_photos(self):
        incident = self.create_incident()
        incident.assign_technician(operator=self.operator, technician=self.technician)
        report = ResolutionReport.objects.create(
            incident=incident,
            technician=self.technician,
            round_number=incident.workflow_round,
            description='Elektr tarmog`i tiklandi.',
            materials_used='Lampochka',
        )
        self.assertEqual(report.round_number, 1)
        for index in range(3):
            IncidentPhoto.objects.create(
                incident=incident,
                uploaded_by=self.technician,
                kind=IncidentPhoto.Kind.TECHNICIAN_COMPLETION,
                round_number=incident.workflow_round,
                image=uploaded(f'r{index}.jpg'),
            )
        incident.mark_resolved(technician=self.technician)
        incident.refresh_from_db()
        self.technician.refresh_from_db()
        self.assertEqual(incident.status, Incident.Status.RESOLVED)
        self.assertEqual(self.technician.current_workload, 0)
        self.assertEqual(ResolutionReport.objects.filter(incident=incident, round_number=1).count(), 1)
        self.assertEqual(
            IncidentPhoto.objects.filter(incident=incident, kind=IncidentPhoto.Kind.TECHNICIAN_COMPLETION, round_number=1).count(),
            3,
        )

    def test_negative_feedback_allows_reopen_and_second_round(self):
        incident = self.create_incident()
        incident.assign_technician(operator=self.operator, technician=self.technician)
        incident.mark_resolved(technician=self.technician)
        CitizenFeedback.objects.create(
            incident=incident,
            citizen=self.citizen,
            is_resolved=False,
            reason='Muammo to`liq bartaraf etilmadi.',
            rating=2,
        )
        incident.assign_technician(operator=self.operator, technician=self.technician)
        incident.refresh_from_db()
        self.assertEqual(incident.status, Incident.Status.IN_PROGRESS)
        self.assertEqual(incident.workflow_round, 2)

    def test_auto_close_command_closes_only_feedbackless_resolved_incidents(self):
        incident = self.create_incident()
        incident.assign_technician(operator=self.operator, technician=self.technician)
        incident.mark_resolved(technician=self.technician)
        incident.resolved_at = timezone.now() - timedelta(days=8)
        incident.save(update_fields=['resolved_at'])

        with_feedback = self.create_incident()
        with_feedback.assign_technician(operator=self.operator, technician=self.technician)
        with_feedback.mark_resolved(technician=self.technician)
        with_feedback.resolved_at = timezone.now() - timedelta(days=8)
        with_feedback.save(update_fields=['resolved_at'])
        CitizenFeedback.objects.create(
            incident=with_feedback,
            citizen=self.citizen,
            is_resolved=True,
            rating=5,
            reason='',
        )

        call_command('auto_close_incidents')
        incident.refresh_from_db()
        with_feedback.refresh_from_db()
        self.assertEqual(incident.status, Incident.Status.CLOSED)
        self.assertEqual(with_feedback.status, Incident.Status.RESOLVED)

    def test_operator_can_close_after_reopened_round(self):
        incident = self.create_incident()
        incident.assign_technician(operator=self.operator, technician=self.technician)
        incident.mark_resolved(technician=self.technician)
        CitizenFeedback.objects.create(
            incident=incident,
            citizen=self.citizen,
            is_resolved=False,
            reason='Muammo qolgan.',
            rating=1,
        )
        incident.assign_technician(operator=self.operator, technician=self.technician)
        incident.mark_resolved(technician=self.technician)

        self.client.force_login(self.operator)
        response = self.client.post(reverse('incidents:operator_close_incident', kwargs={'pk': incident.pk}))
        self.assertEqual(response.status_code, 302)
        incident.refresh_from_db()
        self.assertEqual(incident.status, Incident.Status.CLOSED)
