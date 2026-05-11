# users/mixins.py (updated)
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect
from django.contrib import messages
from .models import CustomUser


class RoleRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    allowed_roles = ()

    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.role in self.allowed_roles

    def handle_no_permission(self):
        if not self.request.user.is_authenticated:
            return super().handle_no_permission()
        # Role mismatch – still raise 403
        raise PermissionDenied("Sizda bu sahifaga kirish huquqi yo'q.")


class CitizenRequiredMixin(RoleRequiredMixin):
    allowed_roles = (CustomUser.Role.CITIZEN,)


class OperatorRequiredMixin(RoleRequiredMixin):
    allowed_roles = (CustomUser.Role.OPERATOR,)

    def dispatch(self, request, *args, **kwargs):
        # First check authentication & role
        result = super().dispatch(request, *args, **kwargs)
        # If still here, role is correct; now check approval
        if request.user.is_authenticated and not request.user.is_approved:
            messages.warning(request, "Hisobingiz admin tomonidan tasdiqlanmagan.")
            return redirect('users:pending_approval')
        return result


class TechnicianRequiredMixin(RoleRequiredMixin):
    allowed_roles = (CustomUser.Role.TECHNICIAN,)

    def dispatch(self, request, *args, **kwargs):
        result = super().dispatch(request, *args, **kwargs)
        if request.user.is_authenticated and not request.user.is_approved:
            messages.warning(request, "Hisobingiz admin tomonidan tasdiqlanmagan.")
            return redirect('users:pending_approval')
        return result


class AdminRequiredMixin(RoleRequiredMixin):
    allowed_roles = (CustomUser.Role.ADMIN,)