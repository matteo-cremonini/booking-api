from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase
from datetime import datetime, timezone
from services.models import Service, Slot
from .models import Booking

User = get_user_model()


class BookingTests(APITestCase):

    def setUp(self):
        self.provider = User.objects.create_user(
            username='provider1', password='pass1234', role='provider'
        )
        self.client_user = User.objects.create_user(
            username='client1', password='pass1234', role='client'
        )
        self.client_user2 = User.objects.create_user(
            username='client2', password='pass1234', role='client'
        )
        self.client.force_authenticate(user=self.client_user)
        self.service = Service.objects.create(
            owner=self.provider,
            name='Haircut',
            description='A haircut service',
            duration_minutes=30,
            is_active=True,
        )
        self.slot = Slot.objects.create(
            service=self.service,
            start_time=datetime(2026, 7, 1, 9, 0, tzinfo=timezone.utc),
            end_time=datetime(2026, 7, 1, 9, 30, tzinfo=timezone.utc),
            price='25.00',
        )
        self.list_url = '/api/bookings/'

    def test_client_creates_booking(self):
        data = {'slot_id': self.slot.id}

        response = self.client.post(self.list_url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Booking.objects.count(), 1)
        self.slot.refresh_from_db()
        self.assertTrue(self.slot.is_booked)

    def test_provider_cannot_create_booking(self):
        self.client.force_authenticate(user=self.provider)
        data = {'slot_id': self.slot.id}

        response = self.client.post(self.list_url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_unauthenticated_cannot_create_booking(self):
        self.client.force_authenticate(user=None)
        data = {'slot_id': self.slot.id}

        response = self.client.post(self.list_url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_same_slot_cannot_be_booked_twice(self):
        Booking.objects.create(
            client=self.client_user, slot=self.slot, status=Booking.Status.PENDING
        )
        self.slot.is_booked = True
        self.slot.save()
        self.client.force_authenticate(user=self.client_user2)
        data = {'slot_id': self.slot.id}

        response = self.client.post(self.list_url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Booking.objects.count(), 1)

    def test_provider_confirms_pending_booking(self):
        booking = Booking.objects.create(
            client=self.client_user, slot=self.slot, status=Booking.Status.PENDING
        )
        self.client.force_authenticate(user=self.provider)

        response = self.client.post(f'/api/bookings/{booking.id}/confirm/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        booking.refresh_from_db()
        self.assertEqual(booking.status, Booking.Status.CONFIRMED)

    def test_cancel_frees_slot(self):
        booking = Booking.objects.create(
            client=self.client_user, slot=self.slot, status=Booking.Status.PENDING
        )
        self.slot.is_booked = True
        self.slot.save()

        response = self.client.post(f'/api/bookings/{booking.id}/cancel/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.slot.refresh_from_db()
        self.assertFalse(self.slot.is_booked)

    def test_client_cannot_see_other_client_bookings(self):
        Booking.objects.create(
            client=self.client_user, slot=self.slot, status=Booking.Status.PENDING
        )
        self.client.force_authenticate(user=self.client_user2)

        response = self.client.get(self.list_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 0)

    def test_provider_sees_only_own_slot_bookings(self):
        other_provider = User.objects.create_user(
            username='provider2', password='pass1234', role='provider'
        )
        other_slot = Slot.objects.create(
            service=Service.objects.create(
                owner=other_provider, name='Massage', description='',
                duration_minutes=60, is_active=True,
            ),
            start_time=datetime(2026, 7, 1, 10, 0, tzinfo=timezone.utc),
            end_time=datetime(2026, 7, 1, 11, 0, tzinfo=timezone.utc),
            price='50.00',
        )
        Booking.objects.create(
            client=self.client_user, slot=other_slot, status=Booking.Status.PENDING
        )
        Booking.objects.create(
            client=self.client_user, slot=self.slot, status=Booking.Status.PENDING
        )
        self.client.force_authenticate(user=self.provider)

        response = self.client.get(self.list_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)