from django_filters import rest_framework as filters
from .models import Message
from django.contrib.auth.models import User

class MessageFilter(filters.FilterSet):
    """
    Filter messages by conversation participants or time range.
    """
    user = filters.ModelChoiceFilter(
        queryset=User.objects.all(),
        field_name='conversation__participants',
        label='Participant'
    )
    start_date = filters.DateTimeFilter(
        field_name='created_at',
        lookup_expr='gte',
        label='Start Date'
    )
    end_date = filters.DateTimeFilter(
        field_name='created_at',
        lookup_expr='lte',
        label='End Date'
    )

    class Meta:
        model = Message
        fields = ['user', 'start_date', 'end_date']


