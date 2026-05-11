from django.contrib import admin
from .models import CitizenFeedback, Incident, IncidentPhoto, IncidentUpdate, ResolutionReport


class IncidentPhotoInline(admin.TabularInline):
    model = IncidentPhoto
    extra = 0


class IncidentUpdateInline(admin.TabularInline):
    model = IncidentUpdate
    extra = 0
    readonly_fields = ('actor', 'from_status', 'to_status', 'note', 'created_at')


@admin.register(Incident)
class IncidentAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'status', 'category', 'priority', 'citizen', 'technician')
    list_filter = ('status', 'category', 'priority', 'region')
    search_fields = ('title', 'description', 'address')
    inlines = [IncidentPhotoInline, IncidentUpdateInline]


@admin.register(ResolutionReport)
class ResolutionReportAdmin(admin.ModelAdmin):
    list_display = ('incident', 'technician', 'completed_at')


@admin.register(CitizenFeedback)
class CitizenFeedbackAdmin(admin.ModelAdmin):
    list_display = ('incident', 'citizen', 'is_resolved', 'rating', 'created_at')
