from rest_framework.permissions import BasePermission
from django.contrib.auth import get_user_model

User = get_user_model()

class IsProvider(BasePermission):
    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            request.user.role == User.Role.PROVIDER
        )

class IsClient(BasePermission):
    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            request.user.role == User.Role.CLIENT
        )

class IsSlotOwner(BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.service.owner == request.user