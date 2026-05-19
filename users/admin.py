from django.contrib import admin

from services.models import Service, Slot
from bookings.models import Booking
from users.models import CustomUser

admin.site.register(CustomUser)
admin.site.register(Service)
admin.site.register(Booking)
admin.site.register(Slot)