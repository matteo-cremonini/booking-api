from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from bookings.permissions import IsProvider, IsSlotOwner
from .models import Service, Slot
from .serializers import ServiceSerializer, SlotSerializer


class ServiceViewSet(ModelViewSet):
    serializer_class = ServiceSerializer

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


class SlotViewSet(ModelViewSet):
    serializer_class = SlotSerializer

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