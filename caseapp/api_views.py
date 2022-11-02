from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .serializers import CaseSerializer, ItemSerializer
from .models import Case, Item, ItemForCase


@api_view(['POST'])
def open_case(request, owned_case_id):
    """Opens owned case and returns dropped item"""
    pass


@api_view(['GET'])
def get_user_cases(request):
    """Returns cases for the user"""
    pass


@api_view(['GET'])
def get_items_in_case(request, case_pk=None):
    """
    Returns list of items for the case
    """
    items_for_case = ItemForCase.objects.filter(case=case_pk)
    items = Item.objects.filter(pk__in=items_for_case.values('item'))
    serializer = ItemSerializer(items, many=True)
    return Response(serializer.data)


@api_view(['GET'])
def get_items(request):
    """Returns list of all items"""
    items = Item.objects.all()
    serializer = ItemSerializer(items, many=True)

    return Response(serializer.data)


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


