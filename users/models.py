from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    phone = models.PositiveIntegerField(max_length=15, unique=True)
    role = models.CharField()


class Citizen(CustomUser):
    address = models.CharField(max_length=255)
    feedback_count = models.PositiveIntegerField(default=0)
    avatar = models.ImageField(upload_to='avatars/', default='avatars/default.jpg')


class Operator(CustomUser):
    department = models.CharField(max_length=255)
    assigned_incidents_count= models.PositiveIntegerField(default=0)


class Technician(CustomUser):
    specialization = models.CharField(max_length=255)
    current_workload = models.PositiveIntegerField(default=0)


class Admin(CustomUser):
    permissions = models.ManyToManyField(CustomUser, related_name='admin_user')