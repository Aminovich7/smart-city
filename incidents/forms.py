from django import forms
from .models import CitizenFeedback, Incident, ResolutionReport


class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True


class MultipleFileField(forms.FileField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault('widget', MultipleFileInput(attrs={'multiple': True}))
        super().__init__(*args, **kwargs)

    def clean(self, data, initial=None):
        single_file_clean = super().clean
        if isinstance(data, (list, tuple)):
            result = [single_file_clean(d, initial) for d in data]
        else:
            result = single_file_clean(data, initial)
        return result


class IncidentCreationForm(forms.ModelForm):
    photos = MultipleFileField(label='3 ta boshlang`ich foto')

    class Meta:
        model = Incident
        fields = ('title', 'description', 'category', 'other_category_note', 'priority', 'region', 'address')
        labels = {
            'title': 'Sarlavha',
            'description': 'Tavsif',
            'category': 'Kategoriya',
            'other_category_note': '`Boshqa` bo`lsa izoh',
            'priority': 'Muhimlik darajasi',
            'region': 'Hudud',
            'address': 'Aniq manzil',
        }
        widgets = {
            'description': forms.Textarea(attrs={'rows': 5}),
            'other_category_note': forms.TextInput(attrs={'placeholder': 'Masalan: Lift buzilgan, kamera ishlamaydi'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data.get('category') == Incident.Category.OTHER and not (cleaned_data.get('other_category_note') or '').strip():
            self.add_error('other_category_note', "`Boshqa` tanlansa izoh kiritilishi shart.")
        return cleaned_data


class AssignTechnicianForm(forms.ModelForm):
    class Meta:
        model = Incident
        fields = ('technician',)
        labels = {'technician': 'Texnik'}


class ResolutionForm(forms.ModelForm):
    photos = MultipleFileField(label='3 ta yakuniy foto')

    class Meta:
        model = ResolutionReport
        fields = ('description', 'materials_used', 'completed_at')
        labels = {
            'description': 'Bajarilgan ish tavsifi',
            'materials_used': 'Ishlatilgan materiallar',
            'completed_at': 'Bajarilgan vaqt',
        }
        widgets = {
            'description': forms.Textarea(attrs={'rows': 5}),
            'materials_used': forms.Textarea(attrs={'rows': 3}),
            'completed_at': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }


class AdditionalCompletionPhotosForm(forms.Form):
    photos = MultipleFileField(label='Ko`pi bilan 2 ta qo`shimcha foto', required=True)


class FeedbackForm(forms.ModelForm):
    class Meta:
        model = CitizenFeedback
        fields = ('is_resolved', 'reason', 'rating')
        labels = {
            'is_resolved': 'Muammo to`liq hal bo`ldimi?',
            'reason': 'Agar hal bo`lmagan bo`lsa, sabab',
            'rating': 'Baholash',
        }
        widgets = {
            'reason': forms.Textarea(attrs={'rows': 4}),
        }

    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data.get('is_resolved') is False and not (cleaned_data.get('reason') or '').strip():
            self.add_error('reason', "Muammo hal bo'lmagan bo'lsa, sabab kiritilishi kerak.")
        return cleaned_data


class PriorityUpdateForm(forms.ModelForm):
    class Meta:
        model = Incident
        fields = ('priority',)
        labels = {'priority': 'Muhimlik darajasi'}