from django.contrib import admin
from .models import Operator, Technician, Citizen, Admin
# Register your models here.
admin.site.register(Operator)
admin.site.register(Technician)
admin.site.register(Citizen)
admin.site.register(Admin)  