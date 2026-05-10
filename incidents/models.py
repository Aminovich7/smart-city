from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone
from users.models import Operator, Technician, Citizen, Admin
import os
from django.conf import settings

class Category(models.Model):

    PRIORITY_CHOICES= [
        ('low', 'Past'),
        ('medium', 'O`rta'),
        ('high', 'Yuqori'),
    ]

    name = models.CharField(max_length=100)
    description = models.TextField()
    priority_level = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='medium')

    class Meta:
        db_table = 'incidents_category'
        ordering = ['name']
        indexes = [
            models.Index(fields=['priority_level']),
        ]

    def __str__(self):
        return self.name



class Incident(models.Model):
    STATUS_CHOICES = [
        ('NEW', 'Yangi'),
        ('IN_PROGRESS', 'Jarayonda'),
        ('RESOLVED', 'Tugallangan'),
        ('CLOSED', 'Yopilgan'),
    ]

    PRIORITY_CHOICES = [
        ('low', 'Past'),
        ('medium', "O`rta"),
        ('high', 'Yuqori'),
    ]

    UZBEKISTAN_GEOGRAPHY_CHOICES = [
        ('Tashkent City', (
            ('toshkent_city_bektemir', 'Bektemir tumani'),
            ('toshkent_city_chilonzor', 'Chilonzor tumani'),
            ('toshkent_city_mirobod', 'Mirobod tumani'),
            ('toshkent_city_mirzo_ulugbek', 'Mirzo Ulugʻbek tumani'),
            ('toshkent_city_olmazor', 'Olmazor tumani'),
            ('toshkent_city_sergeli', 'Sergeli tumani'),
            ('toshkent_city_shayxontohur', 'Shayxontohur tumani'),
            ('toshkent_city_uhtepa', 'Uchtepa tumani'),
            ('toshkent_city_yakkasaroy', 'Yakkasaroy tumani'),
            ('toshkent_city_yashnobod', 'Yashnobod tumani'),
            ('toshkent_city_yunusobod', 'Yunusobod tumani'),
            ('toshkent_city_yangihayot', 'Yangihayot tumani'),
        )),
        ('Andijon', (
            ('andijon_city', 'Andijon shahri'),
            ('andijon_tuman', 'Andijon tumani'),
            ('asaka', 'Asaka tumani'),
            ('baliqchi', 'Baliqchi tumani'),
            ('boz', 'Boʻz tumani'),
            ('buloqboshi', 'Buloqboshi tumani'),
            ('izboskan', 'Izboskan tumani'),
            ('jalaquduq', 'Jalaquduq tumani'),
            ('marhamat', 'Marhamat tumani'),
            ('oltinkol', 'Oltinkoʻl tumani'),
            ('paxtaobod', 'Paxtaobod tumani'),
            ('qorgontepa', 'Qoʻrgʻontepa tumani'),
            ('shaxrixon', 'Shahrixon tumani'),
            ('ulugnor', 'Ulugʻnor tumani'),
            ('xojaobod', 'Xoʻjaobod tumani'),
        )),
        ('Buxoro', (
            ('buxoro_city', 'Buxoro shahri'),
            ('buxoro_tuman', 'Buxoro tumani'),
            ('gijduvon', 'Gʻijduvon tumani'),
            ('jondor', 'Jondor tumani'),
            ('kogon_city', 'Kogon shahri'),
            ('kogon_tuman', 'Kogon tumani'),
            ('qorakol', 'Qorakoʻl tumani'),
            ('qorovulbozor', 'Qorovulbozor tumani'),
            ('olot', 'Olot tumani'),
            ('peshku', 'Peshku tumani'),
            ('shofirkon', 'Shofirkon tumani'),
            ('vobkent', 'Vobkent tumani'),
        )),
        ('Fargʻona', (
            ('fargona_city', 'Fargʻona shahri'),
            ('margilon_city', 'Margʻilon shahri'),
            ('qoqon_city', 'Qoʻqon shahri'),
            ('quva_city', 'Quva shahri'),
            ('oltiariq', 'Oltiariq tumani'),
            ('bagdod', 'Bagʻdod tumani'),
            ('beshariq', 'Beshariq tumani'),
            ('buvayda', 'Buvayda tumani'),
            ('dangara', 'Dangʻara tumani'),
            ('fargona_tuman', 'Fargʻona tumani'),
            ('furqat', 'Furqat tumani'),
            ('quva_tuman', 'Quva tumani'),
            ('rishton', 'Rishton tumani'),
            ('sox', 'Soʻx tumani'),
            ('toshloq', 'Toshloq tumani'),
            ('uchkoprik', 'Uchkunda tumani'),
            ('yozvovon', 'Yozvovon tumani'),
        )),
        ('Jizzax', (
            ('jizzax_city', 'Jizzax shahri'),
            ('arnasoy', 'Arnasoy tumani'),
            ('baxtmal', 'Baxtmal tumani'),
            ('dostlik', 'Doʻstlik tumani'),
            ('forish', 'Forish tumani'),
            ('gallaorol', 'Gʻallaorol tumani'),
            ('sharof_rashidov', 'Sharof Rashidov tumani'),
            ('mirzachol', 'Mirzachoʻl tumani'),
            ('paxtakor', 'Paxtakor tumani'),
            ('yangiobod', 'Yangiobod tumani'),
            ('zamin', 'Zamin tumani'),
            ('zafarobod', 'Zafarobod tumani'),
            ('zarbdor', 'Zarbdor tumani'),
        )),
        ('Namangan', (
            ('namangan_city', 'Namangan shahri'),
            ('chortoq', 'Chortoq tumani'),
            ('chust', 'Chust tumani'),
            ('kosonsoy', 'Kosonsoy tumani'),
            ('mingbuloq', 'Mingbuloq tumani'),
            ('namangan_tuman', 'Namangan tumani'),
            ('norin', 'Norin tumani'),
            ('pop', 'Pop tumani'),
            ('toraqorgon', 'Toʻraqoʻrgʻon tumani'),
            ('uchqorgon', 'Uchqoʻrgʻon tumani'),
            ('uychi', 'Uychi tumani'),
            ('yangiqorgon', 'Yangiqoʻrgʻon tumani'),
        )),
        ('Navoiy', (
            ('navoiy_city', 'Navoiy shahri'),
            ('zarafshon_city', 'Zarafshon shahri'),
            ('karmana', 'Karmana tumani'),
            ('konimex', 'Konimex tumani'),
            ('navbahor', 'Navbahor tumani'),
            ('nurota', 'Nurota tumani'),
            ('qiziltepa', 'Qiziltepa tumani'),
            ('tomdi', 'Tomdi tumani'),
            ('uchquduq', 'Uchquduq tumani'),
            ('xatirchi', 'Xatirchi tumani'),
        )),
        ('Qashqadaryo', (
            ('qarshi_city', 'Qarshi shahri'),
            ('shaxrisabz_city', 'Shahrisabz shahri'),
            ('chiroqchi', 'Chiroqchi tumani'),
            ('dehqonobod', 'Dehqonobod tumani'),
            ('kamashi', 'Kamashi tumani'),
            ('kasbi', 'Kasbi tumani'),
            ('kitob', 'Kitob tumani'),
            ('koson', 'Koson tumani'),
            ('mirishkor', 'Mirishkor tumani'),
            ('muborak', 'Muborak tumani'),
            ('nishon', 'Nishon tumani'),
            ('qarshi_tuman', 'Qarshi tumani'),
            ('shaxrisabz_tuman', 'Shahrisabz tumani'),
            ('yakkabog', 'Yakkabogʻ tumani'),
            ('guzor', 'Gʻuzor tumani'),
        )),
        ('Samarqand', (
            ('samarqand_city', 'Samarqand shahri'),
            ('oqdaryo', 'Oqdaryo tumani'),
            ('bulungur', 'Bulungʻur tumani'),
            ('ishtixon', 'Ishtixon tumani'),
            ('jomboy', 'Jomboy tumani'),
            ('kattaqorgon_city', 'Kattaqoʻrgʻon shahri'),
            ('kattaqorgon_tuman', 'Kattaqoʻrgʻon tumani'),
            ('narpay', 'Narpay tumani'),
            ('nurabod', 'Nurabod tumani'),
            ('payariq', 'Payariq tumani'),
            ('pasdargom', 'Pastdargʻom tumani'),
            ('paxtachi', 'Paxtachi tumani'),
            ('samarqand_tuman', 'Samarqand tumani'),
            ('toyloq', 'Toyloq tumani'),
            ('urgut', 'Urgut tumani'),
        )),
        ('Sirdaryo', (
            ('guliston_city', 'Guliston shahri'),
            ('shirin_city', 'Shirin shahri'),
            ('yangiyer_city', 'Yangiyer shahri'),
            ('boyovut', 'Boyovut tumani'),
            ('guliston_tuman', 'Guliston tumani'),
            ('oqoltin', 'Oqoltin tumani'),
            ('mirzaobod', 'Mirzaobod tumani'),
            ('sayxunobod', 'Sayxunobod tumani'),
            ('sardoba', 'Sardoba tumani'),
            ('sirdaryo_tuman', 'Sirdaryo tumani'),
            ('xovos', 'Xovos tumani'),
        )),
        ('Surxondaryo', (
            ('termiz_city', 'Termiz shahri'),
            ('angor', 'Angor tumani'),
            ('boysun', 'Boysun tumani'),
            ('denov', 'Denov tumani'),
            ('jarqorgon', 'Jarqoʻrgʻon tumani'),
            ('muzrobot', 'Muzrobot tumani'),
            ('oltinsoy', 'Oltinsoy tumani'),
            ('qiziriq', 'Qiziriq tumani'),
            ('qumqorgon', 'Qumqoʻrgʻon tumani'),
            ('shorchi', 'Shoʻrchi tumani'),
            ('sherobod', 'Sherobod tumani'),
            ('termiz_tuman', 'Termiz tumani'),
            ('uzun', 'Uzun tumani'),
            ('sariosiyo', 'Sariosiyo tumani'),
        )),
        ('Tashkent Region', (
            ('nurafshon_city', 'Nurafshon shahri'),
            ('olmaliq_city', 'Olmaliq shahri'),
            ('angren_city', 'Angren shahri'),
            ('chirchiq_city', 'Chirchiq shahri'),
            ('bekobod_city', 'Bekobod shahri'),
            ('bekobod_tuman', 'Bekobod tumani'),
            ('bostonliq', 'Boʻstonliq tumani'),
            ('chinoz', 'Chinoz tumani'),
            ('qibray', 'Qibray tumani'),
            ('oxangaron', 'Ohangaron tumani'),
            ('oqtosh', 'Oqtosh tumani'),
            ('parkent', 'Parkent tumani'),
            ('piskent', 'Piskent tumani'),
            ('quyichirchiq', 'Quyi Chirchiq tumani'),
            ('ortachirchiq', 'Oʻrta Chirchiq tumani'),
            ('yangiyol_city', 'Yangiyoʻl shahri'),
            ('yuqorichirchiq', 'Yuqori Chirchiq tumani'),
            ('zangiota', 'Zangiota tumani'),
        )),
        ('Xorazm', (
            ('urganch_city', 'Urganch shahri'),
            ('xiva_city', 'Xiva shahri'),
            ('bogot', 'Bogʻot tumani'),
            ('gurlan', 'Gurlan tumani'),
            ('shovot', 'Shovot tumani'),
            ('tuproqqala', 'Tuproqqala tumani'),
            ('urganch_tuman', 'Urganch tumani'),
            ('xazarasp', 'Xazarasp tumani'),
            ('xantqa', 'Xonqa tumani'),
            ('xiva_tuman', 'Xiva tumani'),
            ('yangiariq', 'Yangiariq tumani'),
            ('yangibozor', 'Yangibozor tumani'),
        )),
        ('Qoraqalpogʻiston', (
            ('nukus_city', 'Nukus shahri'),
            ('amudaryo', 'Amudaryo tumani'),
            ('beruniy', 'Beruniy tumani'),
            ('ellikqala', 'Ellikqala tumani'),
            ('kegeyli', 'Kegeyli tumani'),
            ('mojnoq', 'Moʻynoq tumani'),
            ('nukus_tuman', 'Nukus tumani'),
            ('qonlikol', 'Qonlikoʻl tumani'),
            ('qongirot', 'Qoʻngʻirot tumani'),
            ('qoraozaq', 'Qoraoʻzak tumani'),
            ('shumanay', 'Shumanay tumani'),
            ('taxtakopir', 'Taxtakoʻpir tumani'),
            ('tortkol', 'Toʻrtkoʻl tumani'),
            ('xojayli', 'Xoʻjayli tumani'),
            ('chimboy', 'Chimboy tumani'),
        )),
    ]

    citizen = models.ForeignKey(
        Citizen,
        on_delete=models.PROTECT,
        related_name='incidents',
        help_text="Citizen who reported the incident"
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name='incidents',
    )
    location_area = models.CharField(
        max_length=50,
        choices=UZBEKISTAN_GEOGRAPHY_CHOICES,
        verbose_name="Region/District"
    )
    title = models.CharField(max_length=200)
    description = models.TextField()
    street = models.CharField(help_text="Ko`cha nomi")
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='medium')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='NEW')
    operator = models.ForeignKey(
        Operator,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name='assigned_incidents',
        help_text="Operator responsible for this incident"
    )
    technician = models.ForeignKey(
        Technician,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name='assigned_incidents',
        help_text="Technician assigned to resolve this incident"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    closed_at = models.DateTimeField(null=True, blank=True)


    class Meta:
        db_table = 'incident'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['category']),
            models.Index(fields=['priority']),
            models.Index(fields=['status', 'priority']),
        ]


    def __str__(self):
        return f"Incident #{self.id}: {self.title}"


    def mark_resolved(self):
        """Mark incident as resolved"""
        self.status = 'RESOLVED'
        self.resolved_at = timezone.now()
        self.save()


    def mark_closed(self):
        """Mark incident as closed"""
        self.status = 'CLOSED'
        self.closed_at = timezone.now()
        self.save()


    def assign_operator(self, operator):
        """Assign operator to incident"""
        self.operator = operator
        self.save()


    def assign_technician(self, technician):
        """Assign technician to incident"""
        self.technician = technician
        if technician:
            technician.current_workload += 1
            technician.save()
            self.status = 'IN_PROGRESS'

        self.save()

## RASM TUSHIRISH LOGIKASIDA FOYDALANUVCHI BOSHQA LOKATSIYADAN TURIB RASM QOSHIB BOLMAYDIGAN QILISHNI OYLAB KOR.


def incident_photo_path(instance, filename):
    return os.path.join('incident_photos',
                        f'incident_{instance.incident.id}',
                        instance.upload_type,filename
                        )

class IncidentPhoto(models.Model):
    UPLOAD_TYPE_CHOICES = [
        ('initial', 'Initial report'),
        ('completion', 'Completion report'),
    ]

    incident = models.ForeignKey(
        Incident,
        on_delete=models.CASCADE,
        related_name='photos'
    )

    image = models.ImageField(upload_to=incident_photo_path)
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,   # CustomUser
        on_delete=models.PROTECT,
        related_name='uploaded_photos'
    )
    upload_type = models.CharField(
        max_length=20,
        choices=UPLOAD_TYPE_CHOICES
    )
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'incident_photo'
        ordering = ['uploaded_at']

    def clean(self):
        super().clean()
        user = self.uploaded_by
        incident = self.incident
        stage = self.upload_type

        # ----------------------------------------------------------
        # Determine user role (multi-table inheritance)
        # ----------------------------------------------------------
        is_citizen = hasattr(user, 'citizen')
        is_operator = hasattr(user, 'operator')
        is_technician = hasattr(user, 'technician')

        # ----------------------------------------------------------
        # Validations for INITIAL stage
        # ----------------------------------------------------------
        if stage == 'initial':
            # Initial photos are only allowed when the incident is NEW
            if incident.status != 'NEW':
                raise ValidationError(
                    'Initial photos can only be uploaded while the incident is NEW.'
                )
            if not (is_citizen or is_operator):
                raise ValidationError(
                    'Only the citizen or an operator can upload initial photos.'
                )
            # --- Citizen must upload exactly 3 initial photos, operator up to 2 ---
            # Count photos already uploaded in this stage, per role
            if is_citizen:
                citizen_initial_count = incident.photos.filter(
                    upload_type='initial',
                    uploaded_by=user   # same citizen
                ).count()
                if citizen_initial_count >= 3:
                    raise ValidationError('A citizen can upload at most 3 initial photos.')
            elif is_operator:
                operator_initial_count = incident.photos.filter(
                    upload_type='initial',
                    uploaded_by=user
                ).count()
                if operator_initial_count >= 2:
                    raise ValidationError('An operator can upload at most 2 initial photos.')

            # Optional: total initial photos per incident ≤ 5
            total_initial = incident.photos.filter(upload_type='initial').count()
            if total_initial >= 5:
                raise ValidationError('Maximum 5 initial photos allowed per incident.')

        # ----------------------------------------------------------
        # Validations for COMPLETION stage
        # ----------------------------------------------------------
        elif stage == 'completion':
            # No uploads allowed when CLOSED
            if incident.status == 'CLOSED':
                raise ValidationError('Cannot upload photos to a closed incident.')

            if is_technician:
                # Technician uploads only while incident is IN_PROGRESS
                if incident.status != 'IN_PROGRESS':
                    raise ValidationError('Technician can upload completion photos only while incident is IN_PROGRESS.')
                count = incident.photos.filter(upload_type='completion', uploaded_by=user).count()
                if count >= 3:
                    raise ValidationError('Technician can upload at most 3 completion photos.')
            elif is_operator:
                # Operator can add photos only when incident is RESOLVED
                if incident.status != 'RESOLVED':
                    raise ValidationError(
                        'Operator can upload additional completion photos only when incident is RESOLVED.')
                count = incident.photos.filter(upload_type='completion', uploaded_by=user).count()
                if count >= 2:
                    raise ValidationError('Operator can upload at most 2 additional completion photos.')
            else:
                raise ValidationError('Only technician or operator can upload completion photos.')

            total = incident.photos.filter(upload_type='completion').count()
            if total >= 5:
                raise ValidationError('Max 5 completion photos per incident.')

        def save(self, *args, **kwargs):
            self.full_clean()
            super().save(*args, **kwargs)


# -------------------------------------------------------------------
# IncidentUpdate – status change history
# -------------------------------------------------------------------
class IncidentUpdate(models.Model):
    incident = models.ForeignKey(
        Incident,
        on_delete=models.CASCADE,
        related_name='updates'
    )
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='incident_updates'
    )
    old_status = models.CharField(max_length=20, blank=True, null=True)
    new_status = models.CharField(max_length=20)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'incident_update'
        ordering = ['-created_at']

    def __str__(self):
        return f"Update #{self.id} for Incident #{self.incident_id}"


class Feedback(models.Model):
    incident = models.ForeignKey(
        Incident,
        on_delete=models.CASCADE,
        related_name='feedback'
    )
    citizen = models.ForeignKey(
        'users.Citizen',
        on_delete=models.PROTECT,
        related_name='feedback_entries'
    )
    rating = models.PositiveSmallIntegerField(
        choices=[(i, str(i)) for i in range(1, 6)],
        help_text="Rating from 1 (worst) to 5 (best)"
    )
    is_resolved = models.BooleanField(
        help_text="Citizen confirms if the incident was actually resolved"
    )
    reason = models.TextField(
        blank=True,
        help_text="If not resolved, the citizen must provide a reason"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'feedback'
        ordering = ['-created_at']
        unique_together = [['incident', 'citizen']]  # one feedback per incident per citizen

    def __str__(self):
        return f"Feedback for Incident #{self.incident_id} by {self.citizen.username}"

    def clean(self):
        super().clean()
        # Reason is required if is_resolved is False
        if not self.is_resolved and not self.reason.strip():
            raise ValidationError({
                'reason': 'You must provide a reason if the incident is not resolved.'
            })

    def save(self, *args, **kwargs):
        self.full_clean()
        # Increment citizen's feedback count
        if self._state.adding:  # only on creation
            self.citizen.feedback_count = F('feedback_count') + 1
            self.citizen.save(update_fields=['feedback_count'])
        super().save(*args, **kwargs)


class ResolutionReport(models.Model):
    incident = models.OneToOneField(
        Incident,
        on_delete=models.CASCADE,
        related_name='resolution_report'
    )
    technician = models.ForeignKey(
        'users.Technician',
        on_delete=models.PROTECT,
        related_name='resolved_incidents'
    )
    description = models.TextField(
        help_text="Detailed description of how the incident was resolved"
    )
    materials_used = models.TextField(
        blank=True,
        help_text="Optional: list of materials or equipment used"
    )
    completed_at = models.DateTimeField(
        default=timezone.now,
        help_text="When the work was actually completed"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'resolution_report'
        ordering = ['-created_at']

    def __str__(self):
        return f"Resolution Report for Incident #{self.incident_id}"



