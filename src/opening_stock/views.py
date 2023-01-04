import re
from django.db.models.expressions import Exists
from django.shortcuts import render
from rest_framework import viewsets
from src.purchase.models import PurchaseDetail, PurchaseMaster
from .serializers import OpeningStockSerializer, SaveOpeningStockSerializer, UpdateOpeningStockSerializer, OpeningStockSummarySerializer
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework import viewsets, status
from rest_framework.response import Response
from src.purchase.purchase_unique_id_generator import generate_purchase_no
from django.db import models, transaction
from .opening_stock_permissions import OpeningStockPermission

from src.item.serializers import ItemSerializer
from src.supplier.serializers import SupplierSerializer
from src.purchase.serializers import GetPackingTypeDetailSerializer, GetItemSerializer, GetSupplierSerializer

from src.purchase.models import PurchaseMaster
from src.item.models import PackingTypeDetail, Item
from src.supplier.models import Supplier

# Create your views here.
class OpeningStockViewset(viewsets.ReadOnlyModelViewSet):
    permission_classes = [OpeningStockPermission]
    # we need to display only opening stock so purchase_type=3
    queryset = PurchaseMaster.objects.filter(purchase_type=3)
    serializer_class = OpeningStockSerializer
    filter_backends = (SearchFilter, OrderingFilter, DjangoFilterBackend)
    search_fields = ['id']
    ordering_fields = ['id']
    filter_fields = ['id']


# for patch operation
class OpeningStockSummaryViewset(viewsets.ReadOnlyModelViewSet):
    permission_classes = [OpeningStockPermission]
    queryset = PurchaseMaster.objects.filter(purchase_type=3)
    serializer_class = OpeningStockSummarySerializer
    filter_backends = (SearchFilter, OrderingFilter, DjangoFilterBackend)
    search_fields = ['id']
    ordering_fields = ['id']
    filter_fields = ['id']


class SaveOpeningStockViewset(viewsets.ModelViewSet):
    permission_classes = [OpeningStockPermission]
    queryset = PurchaseMaster.objects.filter(purchase_type=3)
    serializer_class = SaveOpeningStockSerializer
    http_method_names = ['get', 'list', 'head','post']

    def list(self, request, **kwargs):
        item_key = request.GET.get("item", None)
        data = {}
        if item_key:
            packing_type_data = list()
            packing_type_data.append
            packing_type_details = PackingTypeDetail.objects.filter(active=True, item=item_key).select_related("item", "packing_type")
            packing_type_detail_serializer = GetPackingTypeDetailSerializer(packing_type_details, many=True)
            
            return Response(packing_type_detail_serializer.data, status=status.HTTP_200_OK)
        suppliers =Supplier.objects.filter(active=True).order_by('first_name')
        suppliers_serializer = GetSupplierSerializer(suppliers, many=True)
        items = Item.objects.filter(active=True).order_by('name')
        item_serializer = GetItemSerializer(items, many=True)
        data['items'] = item_serializer.data
        data['suppliers'] = suppliers_serializer.data
        
        return Response(data, status=status.HTTP_200_OK)

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        purchase_detail = request.data['purchase_details']
        # pay_type = 1 i.e CASH for opening Stock
        request.data['pay_type'] = 1
         # validation for purchase detail for blank value
        if not purchase_detail:
            return Response({"key_error": "Provide purchase_detail"}, status=status.HTTP_400_BAD_REQUEST)
        
        
        # validation for date time fields with blank values start
        try:
            if request.data['bill_date_ad'] == "":
                request.data['bill_date_ad'] = None
        except KeyError:
            return Response({'key_error': 'please provide bill_date_ad Keys'},
                            status=status.HTTP_400_BAD_REQUEST)
        # checking due_date_ad
        try:
            if request.data['due_date_ad'] == "":
                request.data['due_date_ad'] = None
        except KeyError:
            return Response({'key_error': 'please provide due_date_ad Keys'},
                            status=status.HTTP_400_BAD_REQUEST)

        # validation for datetime field end
        for detail in purchase_detail:
            try:
                if detail['expiry_date_ad'] == "":
                    detail['expiry_date_ad'] = None
            except KeyError:
                return Response({"key_error": "provide expiry_date_ad key"},
                                status=status.HTTP_400_BAD_REQUEST)

        # purchase number generated is passed in purchase_no
        request.data['purchase_no'] = generate_purchase_no(3)
        # passing purchase_type=3
        request.data['purchase_type'] = 3
        serializer = SaveOpeningStockSerializer(data=request.data, context={'request': request})
    
        if not serializer.is_valid(raise_exception=True):
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

# performing of patch operation for Opening Stock
class UpdateOpeningStockViewset(viewsets.ModelViewSet):
    permission_classes = [OpeningStockPermission]
    queryset = PurchaseMaster.objects.filter(purchase_type=3)
    serializer_class = UpdateOpeningStockSerializer
    http_method_names = ['patch']
    
    # we are allowed to perform patch operation in purchase_type=3 only 
    def get_purchase_master(self, pk):
        try:
            return PurchaseMaster.objects.get(id=pk,purchase_type=3)
        except PurchaseMaster.DoesNotExist:
            return False
    
    @transaction.atomic
    def partial_update(self, request, pk):
        purchase_master = self.get_purchase_master(pk)

        # checking if the purchase_master have value or not
        if purchase_master is not False:
            # for passing of blank value in expiry_date_ad
            purchase_details = request.data['purchase_details']
            for purchase_detail in purchase_details:
                try:
                    if purchase_detail['expiry_date_ad'] == "":
                        purchase_detail['expiry_date_ad'] = None
                except KeyError:
                    return Response({'key_error': 'please provide expiry_date_ad Keys'},
                                    status=status.HTTP_400_BAD_REQUEST)
            try:
                request.data['grand_total']
                if request.data['grand_total'] == "":
                    request.data['grand_total'] = None
            except KeyError:
                return Response({'key_error': 'please provide grand_total Keys'},
                                status=status.HTTP_400_BAD_REQUEST)
        
            
            opening_stock_serializer = UpdateOpeningStockSerializer(purchase_master, data=request.data, partial=True, context={'request': request})
            
            if opening_stock_serializer.is_valid(raise_exception=True):
                opening_stock_serializer.save()
                return Response(opening_stock_serializer.data, status=status.HTTP_201_CREATED)
            else:
                return Response(opening_stock_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
                
        return Response(data="To perform patch operation value for purchase_type must be 3",
                        status=status.HTTP_404_NOT_FOUND)

