from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    phone = models.CharField(max_length=15, unique=True)
    avatar = models.ImageField(upload_to='avatars/', default='avatars/default.jpg')
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'custom_user'



class Citizen(CustomUser):
    address = models.CharField(max_length=255)
    feedback_count = models.PositiveIntegerField(default=0)

    class Meta:
        db_table = 'citizen'

    def __str__(self):
        return self.username



class Operator(CustomUser):
    department = models.CharField(max_length=255)
    assigned_incidents_count= models.PositiveIntegerField(default=0)

    class Meta:
        db_table = 'operator'

    def __str__(self):
        return self.username

class Technician(CustomUser):
    specialization = models.CharField(max_length=255)
    current_workload = models.PositiveIntegerField(default=0)

    class Meta:
        db_table = 'technician'

    def __str__(self):
        return self.username

class Admin(CustomUser):
    # Operator bilan Technicianni activate qilishi kerak ular ro`yxatdan o`tgandan keyin.
    # Bo`lmasa access berilmaydi programmaga.
    class Admin(CustomUser):

        managed_operators = models.ForeignKey(
            Operator,
            on_delete=models.PROTECT,
            related_name='operators_approved_by_admin',
            null=True, blank=True
        )
        managed_technicians = models.ForeignKey(
            Technician,
            on_delete=models.PROTECT,
            related_name='technicians_approved_by_admin',
            null=True, blank=True
        )

        class Meta:
            db_table = 'admin'

        def __str__(self):
            return self.username