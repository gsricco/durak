from django.urls import path
from .api_views import (
    get_cases,
    get_case_by_id,
    get_items,
    get_items_in_case,
    open_case,
    get_user_cases,
)

urlpatterns = [
    path('cases/', get_cases, name='api_cases'),
    path('cases/<int:pk>/', get_case_by_id, name='api_case'),
    path('items/', get_items, name='api_items'),
    path('items_for_case/<int:case_pk>/', get_items_in_case, name='api_items_in_case'),
    path('get_user_cases/', get_user_cases, name='api_get_user_cases'),
    path('open/<int:owned_case_id>', open_case, name="api_open_case"),
]
