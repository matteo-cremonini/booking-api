from bookings.services import (
    book_slot as book_slot_service,
    cancel_booking as cancel_booking_service,
    SlotUnavailable,
)
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
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
    return render(request, 'web/partials/slot_list.html', {'service': service, 'slots': slots})



@login_required
@require_POST
def book_slot(request, slot_id):
    if request.user.role != 'client':
        return render(request, 'web/partials/booking_message.html',
                      {'message': 'Only clients can make bookings.', 'ok': False})
    try:
        book_slot_service(request.user, slot_id)
    except SlotUnavailable:
        return render(request, 'web/partials/booking_message.html',
                      {'message': 'This slot is no longer available.', 'ok': False})
    return render(request, 'web/partials/booking_message.html',
                  {'message': "Booking requested — pending confirmation.", 'ok': True})

@login_required
def my_bookings(request):
    bookings = (Booking.objects
                .filter(client=request.user)
                .select_related('slot__service'))
    return render(request, 'web/my_bookings.html', {'bookings': bookings})


@login_required
@require_POST
def cancel_booking(request, pk):
    booking = get_object_or_404(Booking, pk=pk, client=request.user)
    cancel_booking_service(booking)
    return render(request, 'web/partials/booking_row.html', {'booking': booking})

@login_required
def provider_dashboard(request):
    if request.user.role != 'provider':
        return redirect('home')
    bookings = (Booking.objects
                .filter(slot__service__owner=request.user)
                .select_related('slot__service', 'client'))
    return render(request, 'web/provider_dashboard.html', {'bookings': bookings})

@login_required
@require_POST
def confirm_booking(request, pk):
    booking = get_object_or_404(Booking, pk=pk, slot__service__owner=request.user)
    if booking.status == Booking.Status.PENDING:
        booking.status = Booking.Status.CONFIRMED
        booking.save()
    return render(request, 'web/partials/provider_booking_row.html', {'booking': booking})

@login_required
@require_POST
def provider_cancel_booking(request, pk):
    booking = get_object_or_404(Booking, pk=pk, slot__service__owner=request.user)
    cancel_booking_service(booking)
    return render(request, 'web/partials/provider_booking_row.html', {'booking': booking})
