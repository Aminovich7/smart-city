from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.db import models


class CustomUser(AbstractUser):
    class Role(models.TextChoices):
        CITIZEN = 'citizen', 'Fuqaro'
        OPERATOR = 'operator', 'Operator'
        TECHNICIAN = 'technician', 'Texnik'
        ADMIN = 'admin', 'Admin'

    class Specialization(models.TextChoices):
        CLEANER = 'cleaner', 'Tozalovchi'
        ELECTRICIAN = 'electrician', 'Elektrik'
        PLUMBER = 'plumber', 'Santexnik'
        LIGHTING_TECH = 'lighting_tech', 'Yoritish texnigi'
        ROAD_WORKER = 'road_worker', 'Yo`l ustasi'
        DRAINAGE_TECH = 'drainage_tech', 'Kanalizatsiya ustasi'
        LANDSCAPER = 'landscaper', 'Ko`kalamzorlashtirish ustasi'
        SIGNAL_TECH = 'signal_tech', 'Svetofor va belgi ustasi'
        MULTI_SKILLED = 'multi_skilled', 'Universal texnik'

    role = models.CharField(max_length=20, choices=Role.choices)
    phone = models.CharField(max_length=15, unique=True)
    address = models.CharField(max_length=255, blank=True)
    department = models.CharField(max_length=255, blank=True)
    specialization = models.CharField(max_length=255, blank=True)
    current_workload = models.PositiveIntegerField(default=0)
    is_approved = models.BooleanField(default=False)   # <-- NEW FIELD

    class Meta:
        db_table = 'custom_user'

    def clean(self):
        super().clean()
        if self.role == self.Role.CITIZEN and not self.address.strip():
            raise ValidationError({'address': "Fuqaro uchun manzil kiritilishi shart."})
        if self.role == self.Role.OPERATOR and not self.department.strip():
            raise ValidationError({'department': "Operator uchun bo'lim kiritilishi shart."})
        if self.role == self.Role.TECHNICIAN and not self.specialization.strip():
            raise ValidationError({'specialization': "Texnik uchun mutaxassislik kiritilishi shart."})

    def save(self, *args, **kwargs):
        self.is_staff = self.role == self.Role.ADMIN or self.is_staff
        # Auto-approve citizens
        if self.role == self.Role.CITIZEN:
            self.is_approved = True
        self.address = self.address.strip()
        self.department = self.department.strip()
        self.specialization = self.specialization.strip()
        super().save(*args, **kwargs)

    @property
    def is_citizen(self):
        return self.role == self.Role.CITIZEN

    @property
    def is_operator(self):
        return self.role == self.Role.OPERATOR

    @property
    def is_technician(self):
        return self.role == self.Role.TECHNICIAN

    @property
    def is_admin_role(self):
        return self.role == self.Role.ADMIN

    @property
    def specialization_label(self):
        return self.specialization_choices_map().get(self.specialization, self.specialization)

    @classmethod
    def specialization_choices_map(cls):
        return {value: label for value, label in cls.Specialization.choices}

    def __str__(self):
        return self.get_full_name() or self.username