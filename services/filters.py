import django_filters
from .models import Service, Slot


class ServiceFilter(django_filters.FilterSet):

    class Meta:
        model = Service
        fields = ['is_active']

class SlotFilter(django_filters.FilterSet):
    start_date = django_filters.DateFilter(
        field_name='start_time', 
        lookup_expr='date'
        )
    
    class Meta:
        model = Slot
        fields = ['service', 'is_booked', 'start_date']