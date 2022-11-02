from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .serializers import CaseSerializer, ItemSerializer, OwnedCaseSerializer
from .models import Case, Item, ItemForCase, OwnedCase

from random import choices


@api_view(['GET'])
def open_case(request, owned_case_id):
    """Opens owned case and returns dropped item"""
    if not request.user.is_authenticated:
        return Response(status=401)

    owned_case = OwnedCase.objects.get(pk=owned_case_id)

    if owned_case is None:
        return Response({"details": f"cannot find case with id={owned_case_id}"}, status=404)

    if owned_case.owner != request.user.pk:
        return Response({"details": "Access forbidden"}, status=403)

    case = owned_case.case
    case_items = ItemForCase.objects.filter(case=case)

    weights = case_items.values('chance')
    chosen_item_in_case = choices(case_items, weights=weights, k=1)[0]
    chosen_item = Item.objects.get(pk=chosen_item_in_case.item)

    serializer = ItemSerializer(chosen_item)

    return Response(serializer.data)


@api_view(['GET'])
def get_user_cases(request):
    """Returns cases for the user"""
    if not request.user.is_authenticated:
        return Response(status=401)

    cases = OwnedCase.objects.filter(owner=request.user)
    serializer = OwnedCaseSerializer(cases, many=True)

    return Response(serializer.data)


@api_view(['GET'])
def get_items_in_case(request, case_pk=None):
    """Returns list of items for the case"""
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
    """Returns specific case"""
    if not request.user.is_authenticated:
        return Response(status=401)

    cases = Case.objects.all()
    case = get_object_or_404(cases, pk=pk)
    serializer = CaseSerializer(case)

    return Response(serializer.data)


@api_view(['GET'])
def get_cases(request):
    """Returns cases for authenticated user"""
    if not request.user.is_authenticated:
        return Response(status=401)

    cases = Case.objects.all()
    serializer = CaseSerializer(cases, many=True)

    return Response(serializer.data)
