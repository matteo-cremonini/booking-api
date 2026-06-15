from django.contrib import admin
from .models import Service, Slot


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ['name', 'owner', 'duration_minutes', 'is_active']
    list_filter = ['is_active']
    search_fields = ['name', 'owner__username']


@admin.register(Slot)
class SlotAdmin(admin.ModelAdmin):
    list_display = ['service', 'start_time', 'end_time', 'price', 'is_booked']
    list_filter = ['is_booked']
    search_fields = ['service__name']
