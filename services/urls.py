from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ServiceViewSet, SlotViewSet

router = DefaultRouter()
router.register('services', ServiceViewSet, basename='service')
router.register('slots', SlotViewSet, basename='slot')

urlpatterns = [
    path('', include(router.urls)),
]