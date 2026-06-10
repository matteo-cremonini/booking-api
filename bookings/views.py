from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import ValidationError
from bookings.permissions import IsProvider, IsClient
from bookings.services import (
    book_slot as book_slot_service,
    cancel_booking as cancel_booking_service,
    SlotUnavailable,
)
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
        slot = serializer.validated_data['slot']
        try:
            serializer.instance = book_slot_service(self.request.user, slot.pk)
        except SlotUnavailable:
            raise ValidationError({'slot_id': 'This slot is no longer available.'})

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
        cancel_booking_service(booking)
        return Response({'detail': 'Booking cancelled.'}, status=status.HTTP_200_OK)