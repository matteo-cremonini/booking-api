from datetime import timedelta
from rest_framework import serializers
from services.models import Service, Slot


class ServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Service
        fields = ['id', 'name', 'description', 'owner', 'is_active', 'duration_minutes']
        read_only_fields = ['owner']


class SlotSerializer(serializers.ModelSerializer):
    service = ServiceSerializer(read_only=True)
    service_id = serializers.PrimaryKeyRelatedField(
        queryset=Service.objects.all(),
        source='service',
        write_only=True
    )

    class Meta:
        model = Slot
        fields = ['id', 'service', 'service_id', 'start_time', 'end_time', 'is_booked', 'price']
        read_only_fields = ['is_booked']

    def validate(self, data):
        request = self.context['request']
        service = data.get('service')
        start = data['start_time']
        end = data['end_time']

        if service and service.owner != request.user:
            raise serializers.ValidationError(
                {'service': 'You can only create slots for your own services'}
            )

        if end <= start:
            raise serializers.ValidationError(
                {'end_time': 'end_time must be after start_time'}
            )

        if service and service.duration_minutes:
            expected_end_time = start + timedelta(minutes=service.duration_minutes)
            if end != expected_end_time:
                raise serializers.ValidationError(
                    {'end_time': f'end_time must be exactly {service.duration_minutes} minutes after start_time'}
                )

        return data