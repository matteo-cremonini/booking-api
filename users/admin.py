from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from services.models import Service, Slot
from bookings.models import Booking
from users.models import CustomUser

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = ['username', 'email', 'role', 'is_staff', 'is_active']
    list_filter = ['role', 'is_staff', 'is_active']
    fieldsets = UserAdmin.fieldsets + (
        ('Role', {'fields': ('role',)}),
    )

admin.site.register(Service)
admin.site.register(Booking)
admin.site.register(Slot)