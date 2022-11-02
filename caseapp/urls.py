from django.urls import path
from .api_views import get_cases, get_case_by_id

urlpatterns = [
    path('cases/', get_cases, name='api_cases'),
    path('cases/<int:pk>', get_case_by_id, name='api_case'),

]