from django.test import Client, TestCase
from django.urls import reverse
from .forms import CitizenRegistrationForm
from .models import CustomUser


class UserFlowTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.citizen = CustomUser.objects.create_user(
            username='citizen1',
            password='StrongPass123',
            first_name='Ali',
            last_name='Valiyev',
            phone='+998901111111',
            role=CustomUser.Role.CITIZEN,
            address='Toshkent shahar',
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
            specialization=CustomUser.Specialization.ELECTRICIAN,
        )
        self.admin = CustomUser.objects.create_user(
            username='admin1',
            password='StrongPass123',
            first_name='Admin',
            last_name='Boshqaruv',
            phone='+998904444444',
            role=CustomUser.Role.ADMIN,
        )

    def test_citizen_registration_form_creates_role_based_user(self):
        form = CitizenRegistrationForm(data={
            'username': 'newcitizen',
            'first_name': 'Hasan',
            'last_name': 'Aliyev',
            'email': 'citizen@example.com',
            'phone': '+998905555555',
            'password1': 'ComplexPass123',
            'password2': 'ComplexPass123',
            'address': 'Yunusobod tumani',
        })
        self.assertTrue(form.is_valid(), form.errors)
        user = form.save()
        self.assertEqual(user.role, CustomUser.Role.CITIZEN)
        self.assertEqual(user.address, 'Yunusobod tumani')

    def test_login_redirects_by_role(self):
        response = self.client.post(reverse('users:login'), {'username': 'operator1', 'password': 'StrongPass123'})
        self.assertRedirects(response, reverse('reports:operator_dashboard'))

        self.client.logout()
        response = self.client.post(reverse('users:login'), {'username': 'technician1', 'password': 'StrongPass123'})
        self.assertRedirects(response, reverse('incidents:technician_incident_list'))

    def test_home_and_register_pages_load(self):
        self.assertEqual(self.client.get(reverse('users:home')).status_code, 200)
        self.assertEqual(self.client.get(reverse('users:register')).status_code, 200)
