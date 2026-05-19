from django.db import models

from django.conf import settings

class Booking(models.Model):
    class Status(models.TextChoices):
        PENDING = 'pending', 'Pending'
        CONFIRMED = 'confirmed', 'Confirmed'
        CANCELLED = 'cancelled', 'Cancelled'

    client = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='bookings')
    slot = models.ForeignKey(
        'services.Slot', 
        on_delete=models.CASCADE)
    status = models.CharField(
        max_length=20, 
        choices=Status.choices,
        default=Status.PENDING)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f" {self.client.username} - {self.slot} - {self.status}"