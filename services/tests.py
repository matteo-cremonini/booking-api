from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase
from datetime import datetime, timezone
from .models import Service, Slot

User = get_user_model()


class ServiceTests(APITestCase):

    def setUp(self):
        self.provider = User.objects.create_user(
            username='provider1', password='pass1234', role='provider'
        )
        self.other_provider = User.objects.create_user(
            username='provider2', password='pass1234', role='provider'
        )
        self.client_user = User.objects.create_user(
            username='client1', password='pass1234', role='client'
        )
        self.client.force_authenticate(user=self.provider)
        self.service = Service.objects.create(
            owner=self.provider,
            name='Haircut',
            description='A haircut service',
            duration_minutes=30,
            is_active=True,
        )
        self.other_service = Service.objects.create(
            owner=self.other_provider,
            name='Massage',
            description='A massage service',
            duration_minutes=60,
            is_active=True,
        )
        self.list_url = '/api/services/'

    def test_provider_creates_service(self):
        data = {
            'name': 'New Service',
            'description': 'Description',
            'duration_minutes': 45,
            'is_active': True,
        }

        response = self.client.post(self.list_url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Service.objects.count(), 3)
        self.assertEqual(response.data['owner'], self.provider.username)

    def test_client_cannot_create_service(self):
        self.client.force_authenticate(user=self.client_user)
        data = {
            'name': 'New Service',
            'description': 'Description',
            'duration_minutes': 45,
            'is_active': True,
        }

        response = self.client.post(self.list_url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_unauthenticated_cannot_list_services(self):
        self.client.force_authenticate(user=None)

        response = self.client.get(self.list_url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_provider_sees_only_own_services(self):
        response = self.client.get(self.list_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        ids = [s['id'] for s in response.data['results']]
        self.assertIn(self.service.id, ids)
        self.assertNotIn(self.other_service.id, ids)

    def test_client_sees_all_active_services(self):
        self.client.force_authenticate(user=self.client_user)

        response = self.client.get(self.list_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        ids = [s['id'] for s in response.data['results']]
        self.assertIn(self.service.id, ids)
        self.assertIn(self.other_service.id, ids)

    def test_provider_cannot_access_other_provider_service(self):
        response = self.client.get(f'/api/services/{self.other_service.id}/')

        self.assertIn(
            response.status_code,
            [status.HTTP_403_FORBIDDEN, status.HTTP_404_NOT_FOUND]
        )


class SlotTests(APITestCase):

    def setUp(self):
        self.provider = User.objects.create_user(
            username='provider1', password='pass1234', role='provider'
        )
        self.client_user = User.objects.create_user(
            username='client1', password='pass1234', role='client'
        )
        self.client.force_authenticate(user=self.provider)
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
        self.list_url = '/api/slots/'

    def test_provider_creates_slot(self):
        data = {
            'service_id': self.service.id,
            'start_time': '2026-07-01T10:00:00Z',
            'end_time': '2026-07-01T10:30:00Z',
            'price': '25.00',
        }

        response = self.client.post(self.list_url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Slot.objects.count(), 2)

    def test_invalid_duration(self):
        data = {
            'service_id': self.service.id,
            'start_time': '2026-07-01T10:00:00Z',
            'end_time': '2026-07-01T10:45:00Z',
            'price': '25.00',
        }

        response = self.client.post(self.list_url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_overlap(self):
        data = {
            'service_id': self.service.id,
            'start_time': '2026-07-01T09:00:00Z',
            'end_time': '2026-07-01T09:30:00Z',
            'price': '25.00',
        }

        response = self.client.post(self.list_url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_client_cannot_create_slot(self):
        self.client.force_authenticate(user=self.client_user)
        data = {
            'service_id': self.service.id,
            'start_time': '2026-07-01T10:00:00Z',
            'end_time': '2026-07-01T10:30:00Z',
            'price': '25.00',
        }

        response = self.client.post(self.list_url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_unauthenticated_cannot_list_slots(self):
        self.client.force_authenticate(user=None)

        response = self.client.get(self.list_url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_provider_cannot_modify_booked_slot(self):
        self.slot.is_booked = True
        self.slot.save()

        response = self.client.patch(
            f'/api/slots/{self.slot.id}/', {'price': '30.00'}, format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_provider_cannot_delete_booked_slot(self):
        self.slot.is_booked = True
        self.slot.save()

        response = self.client.delete(f'/api/slots/{self.slot.id}/')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)