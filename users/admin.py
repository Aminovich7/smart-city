from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ("Rol ma'lumotlari", {
            'fields': ('role', 'phone', 'address', 'department',
                       'specialization', 'current_workload', 'is_approved'),
        }),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ("Rol ma'lumotlari", {
            'fields': ('role', 'phone', 'address', 'department', 'specialization'),
        }),
    )
    list_display = ('username', 'role', 'phone', 'email', 'current_workload',
                    'is_approved', 'is_staff')
    list_filter = ('role', 'is_approved', 'is_staff', 'is_active')
    list_editable = ('is_approved',)