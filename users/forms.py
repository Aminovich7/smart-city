from django import forms
from django.contrib.auth.forms import UserChangeForm, UserCreationForm
from .models import CustomUser


class StyledFormMixin:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            css_class = field.widget.attrs.get('class', '')
            field.widget.attrs['class'] = f'{css_class} form-control'.strip()


class CustomUserChangeForm(StyledFormMixin, UserChangeForm):
    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'phone', 'is_active')


class BaseRegistrationForm(StyledFormMixin, UserCreationForm):
    first_name = forms.CharField(max_length=150, label='Ism')
    last_name = forms.CharField(max_length=150, label='Familiya')
    email = forms.EmailField(label='Elektron pochta')
    phone = forms.CharField(max_length=15, label='Telefon raqami')

    class Meta:
        model = CustomUser
        fields = ('username', 'first_name', 'last_name', 'email', 'phone')

    role = None

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = self.role
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.email = self.cleaned_data['email']
        user.phone = self.cleaned_data['phone']
        if commit:
            user.full_clean()
            user.save()
        return user


class CitizenRegistrationForm(BaseRegistrationForm):
    address = forms.CharField(max_length=255, label='Manzil')
    role = CustomUser.Role.CITIZEN

    def save(self, commit=True):
        user = super().save(commit=False)
        user.address = self.cleaned_data['address']
        if commit:
            user.full_clean()
            user.save()
        return user


class TechnicianRegistrationForm(BaseRegistrationForm):
    specialization = forms.ChoiceField(
        choices=CustomUser.Specialization.choices,
        label='Mutaxassislik',
        help_text='Incident kategoriyalariga mos yo`nalishni tanlang.',
    )
    role = CustomUser.Role.TECHNICIAN

    def save(self, commit=True):
        user = super().save(commit=False)
        user.specialization = self.cleaned_data['specialization']
        if commit:
            user.full_clean()
            user.save()
        return user


class OperatorRegistrationForm(BaseRegistrationForm):
    department = forms.CharField(max_length=255, label='Bo`lim')
    role = CustomUser.Role.OPERATOR

    def save(self, commit=True):
        user = super().save(commit=False)
        user.department = self.cleaned_data['department']
        if commit:
            user.full_clean()
            user.save()
        return user


class AdminRegistrationForm(BaseRegistrationForm):
    role = CustomUser.Role.ADMIN

    def save(self, commit=True):
        user = super().save(commit=False)
        user.is_staff = True
        if commit:
            user.full_clean()
            user.save()
        return user
