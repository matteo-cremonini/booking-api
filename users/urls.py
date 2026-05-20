from django.urls import path
from .views import RegisterClientView, RegisterProviderView
from rest_framework_simplejwt.views import (
    TokenObtainPairView, 
     TokenRefreshView,
)

urlpatterns = [
    path('register/client/', RegisterClientView.as_view(), name='register_client'),
    path('register/provider/', RegisterProviderView.as_view(), name='register_provider'),
    path('login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]