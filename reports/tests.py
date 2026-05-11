from django.test import TestCase
from django.urls import reverse
from incidents.models import Incident
from users.models import CustomUser


class DashboardTests(TestCase):
    def setUp(self):
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
            specialization=CustomUser.Specialization.ROAD_WORKER,
        )
        self.admin = CustomUser.objects.create_user(
            username='admin1',
            password='StrongPass123',
            first_name='Admin',
            last_name='Boshqaruv',
            phone='+998904444444',
            role=CustomUser.Role.ADMIN,
        )
        Incident.objects.create(
            citizen=self.citizen,
            title='Yo`l buzilgan',
            description='Asfalt yorilgan.',
            category=Incident.Category.ROAD,
            priority=Incident.Priority.LOW,
            region=Incident.Region.TOSHKENT,
            address='Chilonzor',
        )

    def test_citizen_dashboard_loads(self):
        self.client.force_login(self.citizen)
        response = self.client.get(reverse('reports:citizen_dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['total_incidents'], 1)

    def test_operator_dashboard_loads(self):
        self.client.force_login(self.operator)
        response = self.client.get(reverse('reports:operator_dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['total_incidents'], 1)

    def test_admin_dashboard_shows_totals(self):
        self.client.force_login(self.admin)
        response = self.client.get(reverse('reports:admin_system_reports'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['total_operators'], 1)
        self.assertEqual(response.context['total_technicians'], 1)
