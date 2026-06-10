from datetime import timedelta
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from services.models import Service, Slot
from bookings.models import Booking

User = get_user_model()


class Command(BaseCommand):
    help = "Seed demo data: a provider, services, slots for the next 7 days, and a sample booking."

    def handle(self, *args, **options):
        # --- Users ---
        provider, _ = User.objects.get_or_create(
            username='testprovider', defaults={'role': 'provider'})
        provider.set_password('testpassword')
        provider.save()

        client, _ = User.objects.get_or_create(
            username='testclient', defaults={'role': 'client'})
        client.set_password('testpassword')
        client.save()

        # --- Service ---
        service, _ = Service.objects.get_or_create(
            owner=provider,
            name='Haircut',
            defaults={
                'description': 'Classic haircut — 30 minutes.',
                'duration_minutes': 30,
                'is_active': True,
            },
        )

        # --- Slots: next 7 days, 3 slots per day at 9:00 / 11:00 / 15:00 ---
        # Normalise "now" to the top of the current hour so slot times look clean.
        now = timezone.now().replace(minute=0, second=0, microsecond=0)
        slots_created = 0
        for day in range(7):
            for hour in (9, 11, 15):
                # Skip slots that would land in the past (today's hours already gone).
                if day == 0 and hour <= now.hour:
                    continue
                start = now + timedelta(days=day, hours=hour - now.hour)
                end = start + timedelta(minutes=service.duration_minutes)
                _, created = Slot.objects.get_or_create(
                    service=service,
                    start_time=start,
                    defaults={'end_time': end, 'price': 25},
                )
                if created:
                    slots_created += 1

        # --- Sample booking (first available slot) ---
        first_slot = (
            Slot.objects.filter(service=service, is_booked=False)
            .order_by('start_time')
            .first()
        )
        if first_slot and not Booking.objects.filter(slot=first_slot).exists():
            Booking.objects.create(client=client, slot=first_slot)
            first_slot.is_booked = True
            first_slot.save()
            self.stdout.write(f"  Sample booking created for slot {first_slot.start_time}.")

        self.stdout.write(self.style.SUCCESS(
            f"Demo data ready. "
            f"Slots created: {slots_created}. "
            f"Credentials: testprovider / testclient — password: testpassword"
        ))
