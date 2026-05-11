from datetime import timedelta
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone
from users.models import CustomUser


def incident_photo_path(instance, filename):
    return f'incident_photos/incident_{instance.incident_id}/{instance.kind}/{filename}'


class Incident(models.Model):
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

    class Status(models.TextChoices):
        NEW = 'NEW', 'Yangi'
        IN_PROGRESS = 'IN_PROGRESS', 'Jarayonda'
        RESOLVED = 'RESOLVED', 'Hal qilindi'
        CLOSED = 'CLOSED', 'Yopildi'

    class Category(models.TextChoices):
        SANITATION = 'sanitation', 'Tozalik va chiqindi'
        ELECTRICITY = 'electricity', 'Elektr tarmoqlari'
        WATER = 'water', 'Suv ta`minoti va quvurlar'
        LIGHTING = 'lighting', 'Ko`cha yoritish'
        ROAD = 'road', 'Yo`l va trotuar'
        DRAINAGE = 'drainage', 'Kanalizatsiya va drenaj'
        LANDSCAPING = 'landscaping', 'Ko`kalamzorlashtirish va daraxtlar'
        SIGNAL = 'signal', 'Svetofor va xavfsizlik belgilari'
        OTHER = 'other', 'Boshqa'

    CATEGORY_TECHNICIAN_MAP = {
        Category.SANITATION: CustomUser.Specialization.CLEANER,
        Category.ELECTRICITY: CustomUser.Specialization.ELECTRICIAN,
        Category.WATER: CustomUser.Specialization.PLUMBER,
        Category.LIGHTING: CustomUser.Specialization.LIGHTING_TECH,
        Category.ROAD: CustomUser.Specialization.ROAD_WORKER,
        Category.DRAINAGE: CustomUser.Specialization.DRAINAGE_TECH,
        Category.LANDSCAPING: CustomUser.Specialization.LANDSCAPER,
        Category.SIGNAL: CustomUser.Specialization.SIGNAL_TECH,
        Category.OTHER: CustomUser.Specialization.MULTI_SKILLED,
    }

    class Priority(models.TextChoices):
        LOW = 'low', 'Past'
        MEDIUM = 'medium', 'O`rta'
        HIGH = 'high', 'Yuqori'



    citizen = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='citizen_incidents')
    operator = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='operator_incidents',
        blank=True,
        null=True,
    )
    technician = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='technician_incidents',
        blank=True,
        null=True,
    )
    title = models.CharField(max_length=200)
    description = models.TextField()
    category = models.CharField(max_length=32, choices=Category.choices)
    other_category_note = models.CharField(max_length=255, blank=True)
    priority = models.CharField(max_length=16, choices=Priority.choices, default=Priority.MEDIUM)
    region = models.CharField(max_length=100, choices=UZBEKISTAN_GEOGRAPHY_CHOICES)
    address = models.CharField(max_length=255)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.NEW)
    workflow_round = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    assigned_at = models.DateTimeField(blank=True, null=True)
    resolved_at = models.DateTimeField(blank=True, null=True)
    closed_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'#{self.pk} {self.title}'

    @property
    def preferred_specialization(self):
        return self.CATEGORY_TECHNICIAN_MAP[self.category]

    @property
    def matching_specializations(self):
        preferred = self.preferred_specialization
        return [preferred, CustomUser.Specialization.MULTI_SKILLED]

    def clean(self):
        super().clean()
        if self.citizen_id and self.citizen.role != CustomUser.Role.CITIZEN:
            raise ValidationError({'citizen': "Incident egasi fuqaro bo'lishi kerak."})
        if self.operator_id and self.operator.role != CustomUser.Role.OPERATOR:
            raise ValidationError({'operator': "Biriktiruvchi foydalanuvchi operator bo'lishi kerak."})
        if self.technician_id and self.technician.role != CustomUser.Role.TECHNICIAN:
            raise ValidationError({'technician': "Ijrochi texnik bo'lishi kerak."})
        if self.category == self.Category.OTHER and not self.other_category_note.strip():
            raise ValidationError({'other_category_note': "`Boshqa` tanlanganda izoh yozish majburiy."})
        if self.category != self.Category.OTHER:
            self.other_category_note = ''

    def add_update(self, *, actor=None, from_status=None, to_status=None, note=''):
        IncidentUpdate.objects.create(
            incident=self,
            actor=actor,
            from_status=from_status or self.status,
            to_status=to_status or self.status,
            note=note,
        )

    def can_reopen(self):
        feedback = getattr(self, 'feedback_entry', None)
        return self.status == self.Status.RESOLVED and feedback is not None and not feedback.is_resolved

    def assign_technician(self, *, operator, technician, note=''):
        if operator.role != CustomUser.Role.OPERATOR:
            raise ValidationError("Incidentni faqat operator biriktira oladi.")
        if technician.role != CustomUser.Role.TECHNICIAN:
            raise ValidationError("Tanlangan foydalanuvchi texnik emas.")
        if technician.specialization not in self.matching_specializations:
            raise ValidationError("Tanlangan texnik incident kategoriyasiga mos emas.")

        if self.status == self.Status.NEW:
            self.workflow_round = max(self.workflow_round, 1)
            action_note = note or "Yangi incident texnikka biriktirildi."
        elif self.can_reopen():
            self.workflow_round += 1
            self.resolved_at = None
            action_note = note or "Fuqaro rad etgan incident qayta ishga tushirildi."
        else:
            raise ValidationError("Bu incidentni hozir texnikka biriktirib bo'lmaydi.")

        previous_status = self.status
        self.operator = operator
        self.technician = technician
        self.status = self.Status.IN_PROGRESS
        self.assigned_at = timezone.now()
        self.closed_at = None
        self.save(
            update_fields=[
                'operator',
                'technician',
                'status',
                'assigned_at',
                'resolved_at',
                'closed_at',
                'workflow_round',
                'updated_at',
            ]
        )
        technician.current_workload += 1
        technician.save(update_fields=['current_workload'])
        self.add_update(actor=operator, from_status=previous_status, to_status=self.Status.IN_PROGRESS, note=action_note)

    def mark_resolved(self, *, technician, note=''):
        if self.status != self.Status.IN_PROGRESS:
            raise ValidationError("Faqat jarayondagi incident hal qilinishi mumkin.")
        if self.technician_id != technician.id:
            raise ValidationError("Bu incident sizga biriktirilmagan.")
        previous_status = self.status
        self.status = self.Status.RESOLVED
        self.resolved_at = timezone.now()
        self.save(update_fields=['status', 'resolved_at', 'updated_at'])
        if technician.current_workload > 0:
            technician.current_workload -= 1
            technician.save(update_fields=['current_workload'])
        self.add_update(
            actor=technician,
            from_status=previous_status,
            to_status=self.Status.RESOLVED,
            note=note or "Texnik yechim hisobotini yubordi.",
        )

    def mark_closed(self, *, actor=None, note=''):
        if self.status != self.Status.RESOLVED:
            raise ValidationError("Faqat hal qilingan incident yopilishi mumkin.")
        previous_status = self.status
        self.status = self.Status.CLOSED
        self.closed_at = timezone.now()
        self.save(update_fields=['status', 'closed_at', 'updated_at'])
        self.add_update(
            actor=actor,
            from_status=previous_status,
            to_status=self.Status.CLOSED,
            note=note or "Incident yopildi.",
        )

    def close_if_overdue(self, *, now=None):
        now = now or timezone.now()
        if self.status != self.Status.RESOLVED or not self.resolved_at:
            return False
        if hasattr(self, 'feedback_entry'):
            return False
        if self.resolved_at + timedelta(days=7) > now:
            return False
        self.mark_closed(actor=None, note="7 kun ichida fikr bildirilmagani uchun tizim avtomatik yopdi.")
        return True


class IncidentPhoto(models.Model):
    class Kind(models.TextChoices):
        INITIAL = 'initial', 'Boshlang`ich foto'
        TECHNICIAN_COMPLETION = 'technician_completion', 'Texnik yakuniy foto'
        OPERATOR_COMPLETION = 'operator_completion', 'Operator qo`shimcha foto'

    incident = models.ForeignKey(Incident, on_delete=models.CASCADE, related_name='photos')
    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='incident_photos')
    kind = models.CharField(max_length=32, choices=Kind.choices)
    round_number = models.PositiveIntegerField(default=0)
    image = models.FileField(upload_to=incident_photo_path)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def clean(self):
        super().clean()
        count = IncidentPhoto.objects.filter(
            incident=self.incident,
            kind=self.kind,
            round_number=self.round_number,
        ).exclude(pk=self.pk).count()
        if self.kind == self.Kind.INITIAL:
            if self.incident.status != Incident.Status.NEW:
                raise ValidationError("Boshlang`ich fotolar faqat yangi incident uchun yuklanadi.")
            if self.uploaded_by_id != self.incident.citizen_id:
                raise ValidationError("Boshlang`ich fotoni faqat incident egasi yuklaydi.")
            if self.round_number != 0:
                raise ValidationError("Boshlang`ich foto round 0 ga tegishli bo`lishi kerak.")
            if count >= 3:
                raise ValidationError("Fuqaro aynan 3 ta boshlang`ich foto yuklashi kerak.")
        elif self.kind == self.Kind.TECHNICIAN_COMPLETION:
            if self.incident.status != Incident.Status.IN_PROGRESS:
                raise ValidationError("Yakuniy texnik fotolar faqat jarayondagi incident uchun yuklanadi.")
            if self.incident.technician_id != self.uploaded_by_id:
                raise ValidationError("Bu fotolarni faqat biriktirilgan texnik yuklay oladi.")
            if self.round_number != self.incident.workflow_round:
                raise ValidationError("Texnik fotosi joriy workflow sikliga mos emas.")
            if count >= 3:
                raise ValidationError("Texnik aynan 3 ta yakuniy foto yuklay oladi.")
        elif self.kind == self.Kind.OPERATOR_COMPLETION:
            if self.incident.status != Incident.Status.RESOLVED:
                raise ValidationError("Operator qo`shimcha fotolarni faqat hal qilingan incidentga yuklaydi.")
            if self.uploaded_by.role != CustomUser.Role.OPERATOR:
                raise ValidationError("Qo`shimcha fotolarni faqat operator yuklay oladi.")
            if self.round_number != self.incident.workflow_round:
                raise ValidationError("Operator fotosi joriy workflow sikliga mos emas.")
            if count >= 2:
                raise ValidationError("Operator ko`pi bilan 2 ta qo`shimcha foto yuklay oladi.")

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)


class ResolutionReport(models.Model):
    incident = models.ForeignKey(Incident, on_delete=models.CASCADE, related_name='resolution_reports')
    technician = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='resolution_reports')
    round_number = models.PositiveIntegerField(default=1)
    description = models.TextField()
    materials_used = models.TextField(blank=True)
    completed_at = models.DateTimeField(default=timezone.now)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        constraints = [
            models.UniqueConstraint(fields=['incident', 'round_number'], name='unique_resolution_report_per_round'),
        ]

    def clean(self):
        super().clean()
        if not self.technician_id or not self.incident_id:
            return
        if self.technician.role != CustomUser.Role.TECHNICIAN:
            raise ValidationError({'technician': "Hisobotni faqat texnik yuboradi."})
        if self.round_number != self.incident.workflow_round:
            raise ValidationError({'round_number': "Hisobot joriy workflow sikliga tegishli bo`lishi kerak."})


class CitizenFeedback(models.Model):
    incident = models.OneToOneField(Incident, on_delete=models.CASCADE, related_name='feedback_entry')
    citizen = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='incident_feedbacks')
    is_resolved = models.BooleanField()
    reason = models.TextField(blank=True)
    rating = models.PositiveSmallIntegerField(blank=True, null=True, choices=[(i, str(i)) for i in range(1, 6)])
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def clean(self):
        super().clean()
        if self.citizen.role != CustomUser.Role.CITIZEN:
            raise ValidationError({'citizen': "Fikrni faqat fuqaro qoldira oladi."})
        if self.incident.citizen_id != self.citizen_id:
            raise ValidationError("Faqat incident egasi fikr qoldira oladi.")
        if self.incident.status != Incident.Status.RESOLVED:
            raise ValidationError("Fikr faqat hal qilingan incident uchun qabul qilinadi.")
        if not self.is_resolved and not self.reason.strip():
            raise ValidationError({'reason': "Muammo hal bo'lmagan bo'lsa, sabab yozilishi shart."})


class IncidentUpdate(models.Model):
    incident = models.ForeignKey(Incident, on_delete=models.CASCADE, related_name='updates')
    actor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='incident_updates', blank=True, null=True)
    from_status = models.CharField(max_length=20, blank=True)
    to_status = models.CharField(max_length=20)
    note = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def actor_name(self):
        if not self.actor:
            return 'Tizim'
        return self.actor.get_full_name() or self.actor.username
