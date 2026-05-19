from django.db import models
from django.contrib.auth.models import AbstractUser

class CustomUser(AbstractUser):
   class Role(models.TextChoices):
      PROVIDER = 'provider', 'Provider'
      CLIENT = 'client', 'Client'

   role = models.CharField(
      max_length=10, 
      choices=Role.choices, 
      default=Role.CLIENT)