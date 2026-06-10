from django.db import transaction
from services.models import Slot
from .models import Booking


class SlotUnavailable(Exception):
    pass


def book_slot(client, slot_id):
    with transaction.atomic():
        try:
            slot = Slot.objects.select_for_update().get(pk=slot_id)
        except Slot.DoesNotExist:
            raise SlotUnavailable()
        if slot.is_booked:
            raise SlotUnavailable()
        slot.is_booked = True
        slot.save()
        return Booking.objects.create(client=client, slot=slot)


def cancel_booking(booking):
    if booking.status == Booking.Status.CANCELLED:
        return booking
    with transaction.atomic():
        booking.status = Booking.Status.CANCELLED
        booking.slot.is_booked = False
        booking.slot.save()
        booking.save()
    return booking