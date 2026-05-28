from datetime import timedelta
from rest_framework import serializers
from services.models import Service, Slot


class ServiceSerializer(serializers.ModelSerializer):
    owner = serializers.StringRelatedField()

    class Meta:
        model = Service
        fields = ['id', 'name', 'description', 'owner', 'is_active', 'duration_minutes']

    def validate(self, data):
        if self.instance and 'duration_minutes' in data:
            new_duration = data['duration_minutes']
            if new_duration != self.instance.duration_minutes:
                if self.instance.slot_set.filter(is_booked=True).exists():
                    raise serializers.ValidationError({
                        'duration_minutes': 'Cannot change duration while active bookings exist.'
                    })
        return data


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

        if self.instance and self.instance.is_booked:
            raise serializers.ValidationError(
                'Cannot modify a slot that has an active booking.'
            )

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
        
        overlapping = Slot.objects.filter(
            service=service,
            start_time__lt=end,
            end_time__gt=start
        )

        if self.instance:
            overlapping = overlapping.exclude(id=self.instance.id)
        if overlapping.exists():
            raise serializers.ValidationError(
                {'start_time': 'A slot already exists for this service at this time.'}
        )

        return data
    