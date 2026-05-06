from django.db import models
from django.utils import timezone
from users.models import Operator, Technician, Citizen, Admin


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





