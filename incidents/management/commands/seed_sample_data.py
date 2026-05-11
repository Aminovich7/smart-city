from datetime import timedelta
from itertools import cycle
from pathlib import Path
from random import Random
from urllib.parse import quote
from urllib.request import Request, urlopen

from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from incidents.models import CitizenFeedback, Incident, IncidentPhoto, ResolutionReport
from users.models import CustomUser


IMAGE_LIBRARY = {
    Incident.Category.SANITATION: {
        'initial': ['garbage,street', 'trash,city'],
        'completion': ['garbage,truck', 'cleaning,worker'],
    },
    Incident.Category.ELECTRICITY: {
        'initial': ['electricity,cable', 'electrical,repair'],
        'completion': ['electrician,worker', 'electric,maintenance'],
    },
    Incident.Category.WATER: {
        'initial': ['water,pipe,leak', 'plumbing,leak'],
        'completion': ['plumber,repair', 'water,maintenance'],
    },
    Incident.Category.LIGHTING: {
        'initial': ['streetlight,broken', 'lamp,street'],
        'completion': ['streetlight,repair', 'lighting,maintenance'],
    },
    Incident.Category.ROAD: {
        'initial': ['pothole,road', 'damaged,asphalt'],
        'completion': ['road,repair', 'asphalt,worker'],
    },
    Incident.Category.DRAINAGE: {
        'initial': ['drain,blocked', 'sewer,street'],
        'completion': ['sewer,repair', 'drainage,worker'],
    },
    Incident.Category.LANDSCAPING: {
        'initial': ['tree,street', 'bush,city'],
        'completion': ['tree,trimming', 'landscaping,worker'],
    },
    Incident.Category.SIGNAL: {
        'initial': ['traffic,light', 'road,sign'],
        'completion': ['traffic,maintenance', 'signal,repair'],
    },
    Incident.Category.OTHER: {
        'initial': ['city,infrastructure', 'urban,problem'],
        'completion': ['maintenance,worker', 'repair,city'],
    },
}


class Command(BaseCommand):
    help = "150 ta Uzbekcha sample data va real suratlar bilan demo muhit yaratadi."

    first_names = [
        'Ali', 'Vali', 'Hasan', 'Husan', 'Bekzod', 'Jasur', 'Temur', 'Sardor', 'Aziza', 'Madina',
        'Dilnoza', 'Shahzoda', 'Malika', 'Umida', 'Nigora', 'Kamola', 'Ziyoda', 'Bobur', 'Sherzod', 'Nodira',
    ]
    last_names = [
        'Karimov', 'Ismoilov', 'Tursunov', 'Rahimov', 'Qodirov', 'Sodiqov', 'Xudoyberdiyev', 'Yo`ldoshev',
        'Abdullayeva', 'Toshpo`latova', 'Rustamova', 'Aliyeva', 'Zokirov', 'Ergashev', 'Mamatqulov',
    ]
    districts = [
        'Yunusobod', 'Chilonzor', 'Olmazor', 'Sergeli', 'Yakkasaroy', 'Mirzo Ulug`bek',
        'Shayxontohur', 'Mirobod', 'Uchtepa', 'Yashnobod', 'Qo`qon', 'Samarqand markazi',
    ]
    streets = [
        'Amir Temur ko`chasi', 'Bobur shoh ko`chasi', 'Istiqlol ko`chasi', 'Navro`z ko`chasi',
        'Mustaqillik shoh ko`chasi', 'Do`stlik ko`chasi', 'Al-Xorazmiy ko`chasi', 'Beruniy ko`chasi',
    ]
    operator_departments = [
        'Shahar dispetcherlik markazi', 'Infratuzilma koordinatsiyasi', 'Tuman xizmatlari bo`limi',
    ]
    other_notes = [
        'Lift eshigi yopilmayapti',
        'Kuzatuv kamerasi ishlamayapti',
        'Bolalar maydonchasi jihozi sinib qolgan',
        'Bekat peshtoqi qulab tushgan',
    ]
    category_phrases = {
        Incident.Category.SANITATION: (
            ['Chiqindi konteyneri to`lib ketgan', 'Axlat vaqtida olib ketilmagan', 'Noqonuniy chiqindi tashlangan'],
            ['Hududda chiqindi to`planib qolgan.', 'Konteyner atrofi tozalanmagan.', 'Aholi yuradigan joyda sanitariya muammosi yuzaga kelgan.'],
        ),
        Incident.Category.ELECTRICITY: (
            ['Elektr qutisidan uchqun chiqmoqda', 'Mahalliy kabel uzilgan', 'Transformator qutisi shikastlangan'],
            ['Elektr tarmog`ida xavfli holat kuzatildi.', 'Kabel liniyasi ochiq holda qolgan.', 'Aholi uchun xavf tug`diruvchi elektr nosozligi bor.'],
        ),
        Incident.Category.WATER: (
            ['Suv quvuri yorilgan', 'Ichimlik suvi sizib chiqmoqda', 'Ko`cha chetida suv oqimi kuchaygan'],
            ['Quvurdan suv chiqib yo`lni bosmoqda.', 'Suv bosimi sabab qoplama shikastlanmoqda.', 'Nosozlik tezkor santexnik aralashuvini talab qiladi.'],
        ),
        Incident.Category.LIGHTING: (
            ['Ko`cha chirog`i yonmayapti', 'Ustun lampasi miltillab o`chmoqda', 'Yoritish tarmog`i ishlamay qoldi'],
            ['Kechki payt hudud qorong`i qolmoqda.', 'Jamoat xavfsizligi uchun yoritish kerak.', 'Yoritish tizimi izdan chiqqan.'],
        ),
        Incident.Category.ROAD: (
            ['Asfaltda chuqur paydo bo`lgan', 'Trotuar plitasi ko`chib ketgan', 'Yo`l qoplamasi yorilgan'],
            ['Transport harakati uchun noqulaylik tug`ilmoqda.', 'Piyodalar yurish qismi xavfli holatga kelgan.', 'Ta`mirlash ishlari zarur.'],
        ),
        Incident.Category.DRAINAGE: (
            ['Drenaj teshigi tiqilib qolgan', 'Kanalizatsiya qudug`i toshib chiqmoqda', 'Yomg`ir suvi oqmayapti'],
            ['Suv yig`ilib qolgan va oqim ketmayapti.', 'Drenaj tizimi tozalanishi kerak.', 'Kanalizatsiya bilan bog`liq nosozlik mavjud.'],
        ),
        Incident.Category.LANDSCAPING: (
            ['Daraxt shoxlari yo`lga osilib qolgan', 'Qurigan daraxt kesilmagan', 'Butalar o`tish joyini to`sib qo`ygan'],
            ['Ko`kalamzor hudud tartibga keltirilishi kerak.', 'Shox-shabba transport va piyodalarga xalaqit bermoqda.', 'Daraxt parvarishi talab qilinadi.'],
        ),
        Incident.Category.SIGNAL: (
            ['Svetofor ishlamay qoldi', 'Yo`l belgisi yiqilgan', 'Piyodalar tugmasi javob bermayapti'],
            ['Yo`l harakati xavfsizligi buzilgan.', 'Svetofor signalizatsiyasi nosoz.', 'Belgilash uskunasi ta`mirtalab.'],
        ),
        Incident.Category.OTHER: (
            ['Infratuzilma bo`yicha boshqa muammo', 'Ro`yxatga kirmagan nosozlik', 'Qo`shimcha xizmat talab qilinadi'],
            ['Mazkur muammo standart kategoriyalarga to`g`ri kelmadi.', 'Qo`shimcha izoh asosida ko`rib chiqish talab qilinadi.', 'Universal xizmat guruhi ko`rib chiqishi kerak.'],
        ),
    }

    def add_arguments(self, parser):
        parser.add_argument('--count', type=int, default=150)
        parser.add_argument('--reset', action='store_true')

    def handle(self, *args, **options):
        self.random = Random(42)
        self.cache = {}
        count = options['count']

        with transaction.atomic():
            if options['reset']:
                self.reset_existing_data()
            admin_user = self.ensure_admin()
            operators = self.create_operators(12)
            technicians = self.create_technicians(27)
            citizens = self.create_citizens(max(110, count - len(operators) - len(technicians) - 1))
            self.create_incidents(count, citizens, operators, technicians)

        self.stdout.write(
            self.style.SUCCESS(
                f"Sample data tayyor: admin=1, operator={len(operators)}, texnik={len(technicians)}, fuqaro={len(citizens)}, incident={count}"
            )
        )
        self.stdout.write(f"Admin login: {admin_user.username} / SamplePass123")

    def reset_existing_data(self):
        Incident.objects.all().delete()
        CustomUser.objects.exclude(role=CustomUser.Role.ADMIN).delete()

    def ensure_admin(self):
        admin, _ = CustomUser.objects.get_or_create(
            username='admin_demo',
            defaults={
                'first_name': 'Bosh',
                'last_name': 'Admin',
                'role': CustomUser.Role.ADMIN,
                'phone': '+998990000001',
                'email': 'admin@smartcity.uz',
            },
        )
        admin.set_password('SamplePass123')
        admin.save()
        return admin

    def create_operators(self, count):
        result = []
        for index in range(count):
            operator, _ = CustomUser.objects.get_or_create(
                username=f'operator_{index + 1}',
                defaults={
                    'first_name': self.first_names[index % len(self.first_names)],
                    'last_name': self.last_names[index % len(self.last_names)],
                    'role': CustomUser.Role.OPERATOR,
                    'phone': f'+99897{index + 1000000:07d}',
                    'email': f'operator{index + 1}@smartcity.uz',
                    'department': self.operator_departments[index % len(self.operator_departments)],
                },
            )
            operator.set_password('SamplePass123')
            operator.save()
            result.append(operator)
        return result

    def create_technicians(self, count):
        specs = list(CustomUser.Specialization.values)
        result = []
        for index in range(count):
            technician, _ = CustomUser.objects.get_or_create(
                username=f'technician_{index + 1}',
                defaults={
                    'first_name': self.first_names[(index + 3) % len(self.first_names)],
                    'last_name': self.last_names[(index + 5) % len(self.last_names)],
                    'role': CustomUser.Role.TECHNICIAN,
                    'phone': f'+99895{index + 1000000:07d}',
                    'email': f'technician{index + 1}@smartcity.uz',
                    'specialization': specs[index % len(specs)],
                },
            )
            technician.set_password('SamplePass123')
            technician.current_workload = 0
            technician.save()
            result.append(technician)
        return result

    def create_citizens(self, count):
        result = []
        for index in range(count):
            district = self.districts[index % len(self.districts)]
            street = self.streets[index % len(self.streets)]
            citizen, _ = CustomUser.objects.get_or_create(
                username=f'citizen_{index + 1}',
                defaults={
                    'first_name': self.first_names[(index + 7) % len(self.first_names)],
                    'last_name': self.last_names[(index + 2) % len(self.last_names)],
                    'role': CustomUser.Role.CITIZEN,
                    'phone': f'+99890{index + 1000000:07d}',
                    'email': f'citizen{index + 1}@smartcity.uz',
                    'address': f'{district}, {street}, {index + 10}-uy',
                },
            )
            citizen.set_password('SamplePass123')
            citizen.save()
            result.append(citizen)
        return result

    def create_incidents(self, count, citizens, operators, technicians):
        status_cycle = (
            [Incident.Status.NEW] * 30
            + [Incident.Status.IN_PROGRESS] * 40
            + [Incident.Status.RESOLVED] * 35
            + [Incident.Status.CLOSED] * 45
        )
        categories = list(Incident.Category.values)
        operator_cycle = cycle(operators)
        citizen_cycle = cycle(citizens)

        for index in range(count):
            category = categories[index % len(categories)]
            citizen = next(citizen_cycle)
            operator = next(operator_cycle)
            title_options, desc_options = self.category_phrases[category]
            district = self.districts[(index * 3) % len(self.districts)]
            street = self.streets[(index * 5) % len(self.streets)]
            incident = Incident.objects.create(
                citizen=citizen,
                title=f"{title_options[index % len(title_options)]} - {district}",
                description=f"{desc_options[index % len(desc_options)]} Manzil: {district}, {street}.",
                category=category,
                other_category_note=self.other_notes[index % len(self.other_notes)] if category == Incident.Category.OTHER else '',
                priority=[Incident.Priority.LOW, Incident.Priority.MEDIUM, Incident.Priority.HIGH][index % 3],
                region=list(Incident.Region.values)[index % len(Incident.Region.values)],
                address=f"{district}, {street}, {20 + index}-uy",
                created_at=timezone.now() - timedelta(days=self.random.randint(1, 40)),
            )
            incident.save(update_fields=['created_at'])
            self.attach_initial_photos(incident)
            incident.add_update(actor=citizen, from_status=Incident.Status.NEW, to_status=Incident.Status.NEW, note="Sample data orqali incident yaratildi.")

            target_status = status_cycle[index]
            if target_status == Incident.Status.NEW:
                continue

            technician = self.pick_technician(technicians, incident.matching_specializations, offset=index)
            incident.assign_technician(operator=operator, technician=technician, note="Operator sample ma`lumotlar uchun texnik biriktirdi.")

            if target_status == Incident.Status.IN_PROGRESS:
                continue

            self.resolve_incident(incident, technician, index)

            if target_status == Incident.Status.RESOLVED:
                if index % 4 == 0:
                    self.attach_operator_completion_photos(incident, operator, limit=1)
                continue

            if index % 5 == 0:
                CitizenFeedback.objects.create(
                    incident=incident,
                    citizen=citizen,
                    is_resolved=False,
                    reason="Birinchi ta`mirdan keyin muammo qisman saqlanib qoldi.",
                    rating=2,
                )
                reopened_technician = self.pick_technician(technicians, incident.matching_specializations, offset=index + 3)
                incident.assign_technician(operator=operator, technician=reopened_technician, note="Fuqaro rad javobidan so`ng incident qayta biriktirildi.")
                self.resolve_incident(incident, reopened_technician, index + 200)
                incident.mark_closed(actor=operator, note="Ikkinchi ta`mirdan keyin operator incidentni yopdi.")
            elif index % 3 == 0:
                incident.resolved_at = timezone.now() - timedelta(days=8)
                incident.save(update_fields=['resolved_at'])
                incident.close_if_overdue(now=timezone.now())
            else:
                CitizenFeedback.objects.create(
                    incident=incident,
                    citizen=citizen,
                    is_resolved=True,
                    reason='',
                    rating=5,
                )
                if index % 2 == 0:
                    self.attach_operator_completion_photos(incident, operator, limit=2)
                incident.mark_closed(actor=operator, note="Fuqaro ijobiy baho bergach operator incidentni yopdi.")

    def resolve_incident(self, incident, technician, seed_index):
        report = ResolutionReport.objects.create(
            incident=incident,
            technician=technician,
            round_number=incident.workflow_round,
            description=self.resolution_text(incident.category, seed_index),
            materials_used=self.materials_text(incident.category),
            completed_at=timezone.now() - timedelta(days=self.random.randint(0, 7)),
        )
        for photo_index in range(3):
            self.attach_photo(
                incident=incident,
                uploaded_by=technician,
                kind=IncidentPhoto.Kind.TECHNICIAN_COMPLETION,
                round_number=incident.workflow_round,
                source_group='completion',
                slot=photo_index,
            )
        incident.mark_resolved(technician=technician, note=f"Texnik {report.description.lower()}")

    def attach_initial_photos(self, incident):
        for photo_index in range(3):
            self.attach_photo(
                incident=incident,
                uploaded_by=incident.citizen,
                kind=IncidentPhoto.Kind.INITIAL,
                round_number=0,
                source_group='initial',
                slot=photo_index,
            )

    def attach_operator_completion_photos(self, incident, operator, limit=2):
        for photo_index in range(limit):
            self.attach_photo(
                incident=incident,
                uploaded_by=operator,
                kind=IncidentPhoto.Kind.OPERATOR_COMPLETION,
                round_number=incident.workflow_round,
                source_group='completion',
                slot=photo_index,
            )

    def attach_photo(self, *, incident, uploaded_by, kind, round_number, source_group, slot):
        image_key = self.photo_key_for_category(incident.category, source_group, slot)
        content = ContentFile(self.download_image(image_key))
        photo = IncidentPhoto(
            incident=incident,
            uploaded_by=uploaded_by,
            kind=kind,
            round_number=round_number,
        )
        photo.image.save(
            f"sample_{incident.pk}_{kind}_{round_number}_{slot}.jpg",
            content,
            save=False,
        )
        photo.save()

    def photo_key_for_category(self, category, source_group, slot):
        choices = IMAGE_LIBRARY[category][source_group]
        return choices[slot % len(choices)]

    def download_image(self, image_key):
        if image_key not in self.cache:
            image_url = f"https://loremflickr.com/1280/960/{quote(image_key, safe=',')}"
            request = Request(image_url, headers={'User-Agent': 'SmartCitySeed/1.0'})
            with urlopen(request, timeout=30) as response:
                self.cache[image_key] = response.read()
        return self.cache[image_key]

    def pick_technician(self, technicians, specializations, offset=0):
        matches = [item for item in technicians if item.specialization in specializations]
        return matches[offset % len(matches)]

    def resolution_text(self, category, index):
        texts = {
            Incident.Category.SANITATION: [
                'hudud tozalandi va chiqindi olib chiqildi',
                'konteyner atrofi maxsus brigada tomonidan tartibga keltirildi',
            ],
            Incident.Category.ELECTRICITY: [
                'elektr liniyasi tiklandi va xavfsiz holatga keltirildi',
                'kabel ulanishlari qayta ko`rib chiqilib izolyatsiya qilindi',
            ],
            Incident.Category.WATER: [
                'quvur qismi almashtirildi va sizib chiqish to`xtatildi',
                'nosoz ventil yopilib quvur birikmasi mustahkamlandi',
            ],
            Incident.Category.LIGHTING: [
                'chiroq moduli va kontakt qismi yangilandi',
                'ustun ichidagi nosoz ulanish tiklandi',
            ],
            Incident.Category.ROAD: [
                'asfalt qoplama yamalib tekislandi',
                'trotuar qismi qayta yotqizildi',
            ],
            Incident.Category.DRAINAGE: [
                'drenaj yo`li ochildi va quduq tozalandi',
                'kanalizatsiya oqimi maxsus uskuna bilan tiklandi',
            ],
            Incident.Category.LANDSCAPING: [
                'xalaqit berayotgan shoxlar kesildi va hudud tartibga keltirildi',
                'qurigan daraxt bo`laklari olib chiqildi',
            ],
            Incident.Category.SIGNAL: [
                'svetofor boshqaruv qutisi tekshirilib qayta ishga tushirildi',
                'yo`l belgisi ustuni mustahkamlandi va ko`rinarli holatga keltirildi',
            ],
            Incident.Category.OTHER: [
                'universal texnik guruh muammoni bartaraf etdi',
                'nosoz obyekt bo`yicha vaqtinchalik va yakuniy chora ko`rildi',
            ],
        }
        options = texts[category]
        return options[index % len(options)].capitalize() + '.'

    def materials_text(self, category):
        materials = {
            Incident.Category.SANITATION: 'Maxsus chiqindi qoplami, tozalash anjomlari',
            Incident.Category.ELECTRICITY: 'Izolyatsiya lenta, kabel, avtomat qismlari',
            Incident.Category.WATER: 'Mufta, quvur bo`lagi, ventil',
            Incident.Category.LIGHTING: 'LED lampa, kontakt ulagich, sug`urta',
            Incident.Category.ROAD: 'Asfalt aralashmasi, shag`al, sement',
            Incident.Category.DRAINAGE: 'Tozalash trosi, nasos, himoya vositalari',
            Incident.Category.LANDSCAPING: 'Arra, xavfsizlik arqoni, tozalash anjomi',
            Incident.Category.SIGNAL: 'Signal moduli, mahkamlash detali, kabel',
            Incident.Category.OTHER: 'Universal ta`mirlash to`plami',
        }
        return materials[category]
