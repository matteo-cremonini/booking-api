from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from bookings.permissions import IsProvider, IsSlotOwner
from .models import Service, Slot
from .serializers import ServiceSerializer, SlotSerializer
from rest_framework.response import Response
from rest_framework import status 
from datetime import timedelta
from .filters import ServiceFilter, SlotFilter   



class ServiceViewSet(ModelViewSet):
    serializer_class = ServiceSerializer
    filterset_class = ServiceFilter

    def get_queryset(self):
        user = self.request.user
        if user.role == 'provider':
            return Service.objects.filter(owner=user)
        return Service.objects.filter(is_active=True)

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsProvider()]
        return [IsAuthenticated()]

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    def destroy(self, request, *args, **kwargs):
        service = self.get_object()
        if service.slot_set.filter(is_booked=True).exists():
            return Response(
                {'detail': 'Cannot delete a service that has active bookings.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        return super().destroy(request, *args, **kwargs)
    
    def perform_update(self, serializer):
        old_duration = serializer.instance.duration_minutes
        service = serializer.save()
        if service.duration_minutes != old_duration:
            for slot in service.slot_set.filter(is_booked=False):
                slot.end_time = slot.start_time + timedelta(minutes=service.duration_minutes)
                slot.save()


class SlotViewSet(ModelViewSet):
    serializer_class = SlotSerializer
    filterset_class = SlotFilter

    def get_queryset(self):
        user = self.request.user
        if user.role == 'provider':
            return Slot.objects.filter(service__owner=user)
        return Slot.objects.filter(is_booked=False)

    def get_permissions(self):
        if self.action == 'create':
            return [IsProvider()]
        if self.action in ['update', 'partial_update', 'destroy']:
            return [IsProvider(), IsSlotOwner()]
        return [IsAuthenticated()]
    
    def destroy(self, request, *args, **kwargs):
        slot = self.get_object()
        if slot.is_booked:
            return Response(
                {'detail': 'Cannot delete a slot that has an active booking.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        return super().destroy(request, *args, **kwargs)