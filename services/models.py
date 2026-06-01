from django.db import models

from django.conf import settings



class Service(models.Model):
    class Meta:
        ordering = ['-id']

    name = models.CharField(max_length=255)
    description = models.TextField()
    is_active = models.BooleanField(default=True)
    duration_minutes = models.PositiveIntegerField()
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='services')
    
    def __str__(self):
        return self.name

class Slot(models.Model):
    class Meta:
        ordering = ['start_time']
        
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    is_booked = models.BooleanField(default=False)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.service.name} - {self.start_time}"
    
    