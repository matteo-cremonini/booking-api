from django.contrib.auth import views as auth_views
from django.urls import path

from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('login/', auth_views.LoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('services/', views.service_list, name='service_list'),
    path('services/<int:pk>/slots/', views.available_slots, name='available_slots'),
    path('book/<int:slot_id>/', views.book_slot, name='book_slot'),
    path('bookings/', views.my_bookings, name='my_bookings'),
    path('bookings/<int:pk>/cancel/', views.cancel_booking, name='cancel_booking'),
]