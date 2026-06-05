from django.db import transaction
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from bookings.permissions import IsProvider, IsClient
from .models import Booking
from .serializers import BookingSerializer
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from bookings.filters import BookingFilter


class BookingViewSet(ModelViewSet):
    serializer_class = BookingSerializer
    filterset_class = BookingFilter
    http_method_names = ['get', 'post', 'head', 'options']
    
    def get_queryset(self):
        user = self.request.user
        if user.role == 'provider':
            return Booking.objects.filter(slot__service__owner=user).select_related('slot__service')
        return Booking.objects.filter(client=user).select_related('slot__service')

    def get_permissions(self):
        if self.action == 'create':
            return [IsClient()]
        if self.action == 'confirm':
            return [IsProvider()]
        if self.action in ['cancel', 'retrieve', 'list']:
            return [IsAuthenticated()]
        return [IsAuthenticated()]

    def perform_create(self, serializer):
        with transaction.atomic():
            booking = serializer.save(client=self.request.user)
            booking.slot.is_booked = True
            booking.slot.save()

    @action(detail=True, methods=['post'], permission_classes=[IsProvider])
    def confirm(self, request, pk=None):
        booking = self.get_object()
        if booking.status != Booking.Status.PENDING:
            return Response(
                {'detail': 'Only pending bookings can be confirmed.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        booking.status = Booking.Status.CONFIRMED
        booking.save()
        return Response({'detail': 'Booking confirmed.'}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def cancel(self, request, pk=None):
        booking = self.get_object()
        if booking.status == Booking.Status.CANCELLED:
            return Response(
                {'detail': 'Booking is already cancelled.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        with transaction.atomic():
            booking.status = Booking.Status.CANCELLED
            booking.slot.is_booked = False
            booking.slot.save()
            booking.save()
        return Response({'detail': 'Booking cancelled.'}, status=status.HTTP_200_OK)