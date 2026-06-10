from datetime import timedelta
from rest_framework import serializers
from bookings.models import Booking
from services.models import Slot
from services.serializers import SlotSerializer


class BookingSerializer(serializers.ModelSerializer):
    client = serializers.StringRelatedField()
    slot = SlotSerializer(read_only=True)
    slot_id = serializers.PrimaryKeyRelatedField(
        queryset=Slot.objects.all(),
        source='slot',
        write_only=True
    )

    class Meta:
        model = Booking
        fields = ['id', 'client', 'slot', 'slot_id', 'created_at', 'updated_at', 'status']
        read_only_fields = ['created_at', 'updated_at', 'status']

    