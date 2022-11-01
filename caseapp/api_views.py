from rest_framework.generics import ListAPIView
from .serializers import CaseSerializer
from .models import Case


class CaseListAPIView(ListAPIView):
    """API View for getting cases on profile page"""
    serializer_class = CaseSerializer

    def get_queryset(self):
        return Case.objects.all()