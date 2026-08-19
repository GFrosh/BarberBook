"""Seed BarberBook with demo data: admin + customer + barbers + services."""
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from services.models import Service, Barber

User = get_user_model()

SERVICES = [
    {'name': 'Classic Haircut',       'category': 'haircut', 'price': 28, 'duration_minutes': 30,
     'description': 'Scissor & clipper work — washed, cut and finished.'},
    {'name': 'Signature Fade',        'category': 'haircut', 'price': 38, 'duration_minutes': 45,
     'description': 'A precision skin or taper fade tailored to your face shape.'},
    {'name': 'Buzz Cut',              'category': 'haircut', 'price': 18, 'duration_minutes': 20,
     'description': 'Single-guard all-over clipper cut. Quick and sharp.'},
    {'name': 'Beard Trim & Shape',    'category': 'beard',   'price': 18, 'duration_minutes': 20,
     'description': 'Outline, sculpt and condition. Hot towel finish.'},
    {'name': 'Hot Towel Shave',       'category': 'shave',   'price': 32, 'duration_minutes': 35,
     'description': 'Traditional straight razor shave with hot towels and balm.'},
    {'name': 'Cut & Beard Combo',     'category': 'combo',   'price': 45, 'duration_minutes': 55,
     'description': 'Our most popular service — full haircut plus beard sculpting.'},
    {'name': 'Kids Cut (Under 12)',   'category': 'kids',    'price': 20, 'duration_minutes': 25,
     'description': 'A patient cut for young clients. Includes a lollipop.'},
    {'name': 'Wash, Style & Blow-Dry','category': 'styling', 'price': 22, 'duration_minutes': 25,
     'description': 'Deep shampoo, condition, style and finish.'},
]

BARBERS = [
    {
        'display_name': 'Marcus "The Razor" Hill',
        'specialty': 'Skin fades & beard sculpting',
        'years_experience': 12, 'rating': 4.9,
        'work_start': '09:00', 'work_end': '19:00', 'days_off': '6',  # Sun off
        'bio': "Twelve years behind the chair. Marcus is famous for razor-perfect fades and a tight beard line.",
        'avatar_url': 'https://images.unsplash.com/photo-1622286342621-4bd786c2447c?w=600&q=80',
        'services': ['Classic Haircut', 'Signature Fade', 'Buzz Cut', 'Beard Trim & Shape',
                     'Hot Towel Shave', 'Cut & Beard Combo'],
    },
    {
        'display_name': 'Diego Alvarez',
        'specialty': 'Classic cuts & hot towel shaves',
        'years_experience': 8, 'rating': 4.8,
        'work_start': '10:00', 'work_end': '20:00', 'days_off': '0',  # Mon off
        'bio': "Old-school barber trained in Barcelona. Master of the classic shave and traditional pomp.",
        'avatar_url': 'https://images.unsplash.com/photo-1599351431202-1e0f0137899a?w=600&q=80',
        'services': ['Classic Haircut', 'Beard Trim & Shape', 'Hot Towel Shave',
                     'Cut & Beard Combo', 'Wash, Style & Blow-Dry'],
    },
    {
        'display_name': 'Tariq Bello',
        'specialty': 'Textured cuts & afros',
        'years_experience': 6, 'rating': 4.95,
        'work_start': '09:30', 'work_end': '18:30', 'days_off': '6',  # Sun off
        'bio': "Specialist in textured hair — afros, twists, line-ups and sponge curls.",
        'avatar_url': 'https://images.unsplash.com/photo-1583195764036-6dc248ac07d9?w=600&q=80',
        'services': ['Classic Haircut', 'Signature Fade', 'Buzz Cut', 'Beard Trim & Shape',
                     'Cut & Beard Combo', 'Wash, Style & Blow-Dry'],
    },
    {
        'display_name': 'Jamie Park',
        'specialty': 'Modern styles & kids cuts',
        'years_experience': 5, 'rating': 4.85,
        'work_start': '11:00', 'work_end': '20:00', 'days_off': '1,2',  # Tue+Wed off
        'bio': "Modern-style specialist with infinite patience for first-time clients and young kids.",
        'avatar_url': 'https://images.unsplash.com/photo-1503951914875-452162b0f3f1?w=600&q=80',
        'services': ['Classic Haircut', 'Signature Fade', 'Kids Cut (Under 12)',
                     'Wash, Style & Blow-Dry', 'Buzz Cut'],
    },
]


class Command(BaseCommand):
    help = 'Seed BarberBook demo data.'

    def handle(self, *args, **options):
        # Admin
        admin, created = User.objects.get_or_create(
            username='admin',
            defaults={'email': 'admin@barberbook.test', 'role': User.Role.ADMIN,
                      'is_staff': True, 'is_superuser': True},
        )
        if created:
            admin.set_password('admin123'); admin.save()
            self.stdout.write(self.style.SUCCESS('✓ Created admin (admin / admin123)'))

        # Customer
        cust, created = User.objects.get_or_create(
            username='demo',
            defaults={'email': 'demo@barberbook.test', 'first_name': 'Demo', 'last_name': 'Regular'},
        )
        if created:
            cust.set_password('demo1234'); cust.save()
            self.stdout.write(self.style.SUCCESS('✓ Created customer (demo / demo1234)'))

        # Services
        svc_map = {}
        for entry in SERVICES:
            obj, _ = Service.objects.get_or_create(name=entry['name'], defaults=entry)
            svc_map[entry['name']] = obj
        self.stdout.write(self.style.SUCCESS(f'✓ {Service.objects.count()} services total'))

        # Barbers
        for entry in BARBERS:
            services = entry.pop('services', [])
            obj, was_created = Barber.objects.get_or_create(
                display_name=entry['display_name'], defaults=entry,
            )
            if not was_created:
                continue
            obj.services.set([svc_map[name] for name in services if name in svc_map])
        self.stdout.write(self.style.SUCCESS(f'✓ {Barber.objects.count()} barbers total'))

        self.stdout.write(self.style.SUCCESS(
            '\n💈  Seed complete — login as admin/admin123 or demo/demo1234'))
