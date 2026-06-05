from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import redirect, render, get_object_or_404
from django.views.decorators.http import require_POST
from services.models import Service, Slot
from bookings.models import Booking



from .forms import RegistrationForm


def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
    else:
        form = RegistrationForm()
    return render(request, 'web/register.html', {'form': form})


@login_required
def home(request):
    return render(request, 'web/home.html')

@login_required
def service_list(request):
    if request.user.role == 'provider':
        services = Service.objects.filter(owner=request.user)
    else:
        services = Service.objects.filter(is_active=True)
    return render(request, 'web/service_list.html', {'services': services})


@login_required
def available_slots(request, pk):
    service = get_object_or_404(Service, pk=pk, is_active=True)
    slots = Slot.objects.filter(service=service, is_booked=False)
    return render(request, 'web/partials/slot_list.html',
                  {'service': service, 'slots': slots})


@login_required
@require_POST
def book_slot(request, slot_id):
    if request.user.role != 'client':
        return render(request, 'web/partials/booking_message.html',
                      {'message': 'Only clients can make bookings.', 'ok': False})
    # TODO week 3: wrap with select_for_update() to prevent race conditions on concurrent bookings.
    slot = get_object_or_404(Slot, pk=slot_id)
    if slot.is_booked:
        return render(request, 'web/partials/booking_message.html',
                      {'message': 'This slot is no longer available.', 'ok': False})
    with transaction.atomic():
        Booking.objects.create(client=request.user, slot=slot)
        slot.is_booked = True
        slot.save()
    return render(request, 'web/partials/booking_message.html',
                  {'message': 'Booking confirmed!', 'ok': True})


@login_required
def my_bookings(request):
    bookings = Booking.objects.filter(client=request.user).select_related('slot__service')
    return render(request, 'web/my_bookings.html', {'bookings': bookings})


@login_required
@require_POST
def cancel_booking(request, pk):
    booking = get_object_or_404(Booking, pk=pk, client=request.user)
    if booking.status != Booking.Status.CANCELLED:
        with transaction.atomic():
            booking.status = Booking.Status.CANCELLED
            booking.slot.is_booked = False
            booking.slot.save()
            booking.save()
    return render(request, 'web/partials/booking_row.html', {'booking': booking})


