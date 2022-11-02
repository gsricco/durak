from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .serializers import CaseSerializer
from .models import Case


@api_view(['GET'])
def get_case_by_id(request, pk=None):
    """
    Returns specific case
    """
    if request.user.is_authenticated:
        cases = Case.objects.all()
        case = get_object_or_404(cases, pk=pk)
        serializer = CaseSerializer(case)
        return Response(serializer.data)

    return Response(status=401)


@api_view(['GET'])
def get_cases(request):
    """
    Returns cases for authenticated user
    """
    if request.user.is_authenticated:
        cases = Case.objects.all()
        serializer = CaseSerializer(cases, many=True)
        return Response(serializer.data)

    return Response(status=401)


