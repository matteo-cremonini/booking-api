from datetime import timedelta
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from services.models import Service, Slot
from bookings.models import Booking

User = get_user_model()

SERVICES = [
    {
        'username': 'testprovider',
        'name': 'Haircut',
        'description': 'Classic scissor cut, finished with a hot towel.',
        'duration_minutes': 30,
        'price': 25,
    },
    {
        'username': 'testprovider',
        'name': 'Beard Trim',
        'description': 'Shape and clean-up with straight razor finish.',
        'duration_minutes': 20,
        'price': 15,
    },
    {
        'username': 'testprovider2',
        'name': 'Massage',
        'description': 'Full-body relaxing massage, Swedish technique.',
        'duration_minutes': 60,
        'price': 50,
    },
]


class Command(BaseCommand):
    help = 'Seed demo data: 2 providers, 3 services, 6 slots each, 1 sample booking.'

    def handle(self, *args, **options):
        # --- Users ---
        provider, _ = User.objects.get_or_create(
            username='testprovider', defaults={'role': 'provider'})
        provider.set_password('testpassword')
        provider.save()

        provider2, _ = User.objects.get_or_create(
            username='testprovider2', defaults={'role': 'provider'})
        provider2.set_password('testpassword')
        provider2.save()

        client, _ = User.objects.get_or_create(
            username='testclient', defaults={'role': 'client'})
        client.set_password('testpassword')
        client.save()

        users = {'testprovider': provider, 'testprovider2': provider2}

        # --- Services and slots ---
        # 6 slots per service: day 1 and day 2 from today, at 09:00 / 13:00 / 17:00
        today = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
        first_slot = None

        for svc_data in SERVICES:
            owner = users[svc_data['username']]
            service, _ = Service.objects.get_or_create(
                owner=owner,
                name=svc_data['name'],
                defaults={
                    'description': svc_data['description'],
                    'duration_minutes': svc_data['duration_minutes'],
                    'is_active': True,
                },
            )
            for day in (1, 2):
                for hour in (9, 13, 17):
                    start = today + timedelta(days=day, hours=hour)
                    end = start + timedelta(minutes=service.duration_minutes)
                    slot, _ = Slot.objects.get_or_create(
                        service=service,
                        start_time=start,
                        defaults={'end_time': end, 'price': svc_data['price']},
                    )
                    if first_slot is None and svc_data['name'] == 'Haircut':
                        first_slot = slot

        # --- Sample booking on first Haircut slot ---
        if first_slot and not Booking.objects.filter(slot=first_slot).exists():
            Booking.objects.create(client=client, slot=first_slot)
            first_slot.is_booked = True
            first_slot.save()
            self.stdout.write(f'  Sample booking created on slot {first_slot.start_time}.')

        self.stdout.write(self.style.SUCCESS(
            'Demo data ready. '
            'Providers: testprovider, testprovider2 | Client: testclient | Password: testpassword'
        ))
