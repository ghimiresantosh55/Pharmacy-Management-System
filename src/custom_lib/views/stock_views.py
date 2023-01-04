from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status
from src.purchase.models import PurchaseDetail
from src.custom_lib.serializers.stock_serializers import PurchaseDetailStockSerializer, StockAnalysisSerializer
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter, SearchFilter
from src.item.models import Item
from src.custom_lib.functions.stock import get_item_ledger
from rest_framework.decorators import action
from rest_framework.views import APIView
from django.utils import timezone
import django_filters
from rest_framework.permissions import BasePermission, SAFE_METHODS
from src.custom_lib.functions import stock

class FilterForPurchaseDetailStock(django_filters.FilterSet):
    date = django_filters.DateFromToRangeFilter(field_name="created_date_ad")
    expiry_date = django_filters.DateFromToRangeFilter(field_name="expiry_date_ad")

    class Meta:
        model = PurchaseDetail
        fields = ['id', 'purchase', 'purchase__supplier', 'item']


class PurchaseDetailStockViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = PurchaseDetail.objects.filter(ref_purchase_detail__isnull=True).select_related('item','purchase','item_category','packing_type_detail')
    serializer_class = PurchaseDetailStockSerializer
    filter_class = FilterForPurchaseDetailStock 
    filter_backends = (SearchFilter, OrderingFilter, DjangoFilterBackend)
    ordering_fields = ['id', 'expiry_date_ad', 'item__name']
    search_fields = ['item__name','item__code']


    # def list(self, request):
    #     remaining_qty = PurchaseDetail.objects.filter(remaining_qty__gt=0.00)
    #     return Response(remaining_qty, status=status.HTTP_200_OK)
  

class StockAnalysisPermission(BasePermission):
    def has_permission(self, request, view):
        if request.user.is_anonymous:
            return False
        if request.user.is_superuser is True:
            return True
        try:
            user_permissions = request.user.group.permissions.values_list('code_name', flat=True)
        except:
            return False
        if request.method in SAFE_METHODS and 'view_stock_analysis' in user_permissions:
            return True
        return False


class StockAnalysisView(viewsets.ReadOnlyModelViewSet):
    permission_classes = [StockAnalysisPermission]
    queryset = Item.objects.all()
    serializer_class = StockAnalysisSerializer
    filter_backends = (OrderingFilter, SearchFilter, DjangoFilterBackend)
    search_fields = ['name', 'code', 'item_category__name', 'location']
    ordering_fields = ['id', '']
    filter_fields = ['id', 'name']


class ItemLedgerPermission(BasePermission):
    def has_permission(self, request, view):
        if request.user.is_anonymous:
            return False
        if request.user.is_superuser is True:
            return True
        try:
            user_permissions = request.user.group.permissions.values_list('code_name', flat=True)
        except:
            return False
        if request.method in SAFE_METHODS and 'view_item_ledger' in user_permissions:
            return True
        return False


class ItemLedgerView(APIView):
    permission_classes = [ItemLedgerPermission]
    queryset = PurchaseDetail.objects.all()

    def get(self, request):
        query_dict = {

        }
        for k, vals in request.GET.lists():
            if vals[0] != '':
                k = str(k)
                if k == 'date_after':
                    k = 'created_date_ad__date__gte'
                elif k == 'date_before':
                    k = 'created_date_ad__date__lte'
                query_dict[k] = vals[0]
        data = get_item_ledger(query_dict)
        return Response(data, status=status.HTTP_200_OK)


class ExpiredItemReportPermission(BasePermission):
    def has_permission(self, request, view):
        if request.user.is_anonymous:
            return False
        if request.user.is_superuser is True:
            return True
        try:
            user_permissions = request.user.group.permissions.values_list('code_name', flat=True)
        except:
            return False
        if request.method in SAFE_METHODS and 'view_expired_item_report' in user_permissions:
            return True
        return False


class ExpiredItemView(viewsets.ReadOnlyModelViewSet):
    permission_classes = [ExpiredItemReportPermission]
    queryset = PurchaseDetail.objects.filter(ref_purchase_detail__isnull=True)
    serializer_class = PurchaseDetailStockSerializer
    filter_class = FilterForPurchaseDetailStock
    filter_backends = (SearchFilter, OrderingFilter, DjangoFilterBackend)
    ordering_fields = ['id']
    search_fields = ['item__name']
    filter_fields = ['id', 'purchase', 'purchase__supplier', 'item']