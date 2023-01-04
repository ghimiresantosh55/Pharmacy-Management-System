# from custom
from src.custom_lib.functions import stock

import django_filters
from rest_framework import viewsets, status
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.response import Response
from django.db import models, transaction
from decimal import Decimal
from decimal import Decimal


# imported serializers
from src.purchase.serializers import GetItemSerializer, GetSupplierSerializer, GetPackingTypeDetailSerializer
from src.purchase.models import PurchaseMaster
from src.item.models import Item, PackingTypeDetail
from src.supplier.models import Supplier

# custom files
from src.purchase.purchase_unique_id_generator import generate_purchase_no, generate_purchase_no

# Puchase Stock Addition
from src.supplier.models import Supplier
from .serializers import PurchaseAdjustmentSerializer, SavePurchaseAdjustmentSerializer

# Permission
from .stock_adjustment_permissions import PurchaseStockAdditionPermission, PurchaseStockSubtractionPermission


# for read only
class PurchaseMasterAdditionViewSet(viewsets.ModelViewSet):
    permission_classes = [PurchaseStockAdditionPermission]
    queryset = PurchaseMaster.objects.filter(purchase_type=4)
    serializer_class = PurchaseAdjustmentSerializer
    filter_backends = (SearchFilter, OrderingFilter, DjangoFilterBackend)
    search_fields = ['purchase_no', 'bill_no', 'chalan_no', 'supplier__first_name',
                     "supplier__middle_name", 'supplier__last_name']
    ordering_fields = ['id', 'created_date_ad__date', 'pay_type', 'purchase_no']
    filter_fields = ['id', 'created_date_ad', 'created_date_bs', 'pay_type', 'supplier']


# For read only 
class PurchaseMasterSubtractionViewSet(viewsets.ModelViewSet):
    permission_classes = [PurchaseStockSubtractionPermission]
    queryset = PurchaseMaster.objects.filter(purchase_type=5)
    serializer_class = PurchaseAdjustmentSerializer
    filter_backends = (SearchFilter, OrderingFilter, DjangoFilterBackend)
    search_fields = ['purchase_no', 'bill_no', 'chalan_no', 'supplier__first_name',
                     "supplier__middle_name", 'supplier__last_name']
    ordering_fields = ['id', 'created_date_ad__date', 'pay_type', 'purchase_no']
    filter_fields = ['id', 'created_date_ad', 'created_date_bs', 'pay_type', 'purchase_type', 'supplier']


# For Purchase Adjustment i.e. when purchase_type = 4 (where 4=STOCK-Addition) 
class SavePurchaseAdditionView(viewsets.ModelViewSet):
    permission_classes = [PurchaseStockAdditionPermission]
    serializer_class = SavePurchaseAdjustmentSerializer
    http_method_names = ['post', 'head', 'get']
    queryset = PurchaseMaster.objects.all()

    def list(self, request, **kwargs):
        item_key = request.GET.get("item", None)
        data = {}
        if item_key:
            packing_type_data = list()
            packing_type_data.append
            packing_type_details = PackingTypeDetail.objects.filter(active=True, item=item_key).select_related("item", "packing_type")
            packing_type_detail_serializer = GetPackingTypeDetailSerializer(packing_type_details, many=True)
            return Response(packing_type_detail_serializer.data, status=status.HTTP_200_OK)

        suppliers = Supplier.objects.filter(active=True).order_by('first_name')
        suppliers_serializer = GetSupplierSerializer(suppliers, many=True, read_only=True)
        items = Item.objects.filter(active=True).order_by('name')
        item_serializer = GetItemSerializer(items, many=True, read_only=True) 
        data['items'] = item_serializer.data
        data['suppliers'] = suppliers_serializer.data
        return Response(data, status=status.HTTP_200_OK)

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        purchase_detail = request.data['purchase_details']
        # validation for datetime field end
        for detail in purchase_detail:
            try:
                if detail['expiry_date_ad'] == "":
                    detail['expiry_date_ad'] = None
            except KeyError:
                return Response({"key_error": "provide expiry_date_ad key"},
                                status=status.HTTP_400_BAD_REQUEST)

        # setting pay type = 1 i.e CASH for stock addition
        request.data['pay_type'] = 1

        # validation for date time fields with blank values start
        try:
            if request.data['bill_date_ad'] == "":
                request.data['bill_date_ad'] = None
        except KeyError:
            return Response({'key_error': 'please provide bill_date_ad Keys'},
                            status=status.HTTP_400_BAD_REQUEST)
        try:
            if request.data['due_date_ad'] == "":
                request.data['due_date_ad'] = None
        except KeyError:
            return Response({'key_error': 'please provide due_date_ad Keys'},
                            status=status.HTTP_400_BAD_REQUEST)
        # validation for datetime field end

        # getting unique purchase addition id
        request.data['purchase_no'] = generate_purchase_no(4)

        # saving purchase type to 4 i.e addition
        request.data['purchase_type'] = 4
        serializer = SavePurchaseAdjustmentSerializer(data=request.data, context={'request': request})
        if not serializer.is_valid(raise_exception=True):
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def retrieve(self, request, *args, **kwargs):
        return Response({"method not allowed"}, status=status.HTTP_405_METHOD_NOT_ALLOWED)


# For Purchase Adjustment i.e. when purchase_type = 5 (where 5=STOCK-Subtration)
class SavePurchaseSubtractionView(viewsets.ModelViewSet):
    permission_classes = [PurchaseStockSubtractionPermission]
    serializer_class = SavePurchaseAdjustmentSerializer
    http_method_names = ['post', 'head', 'get']
    queryset = PurchaseMaster.objects.all()

    def list(self, request, **kwargs):
        item_key = request.GET.get("item", None)
        data = {}
        if item_key:
            packing_type_data = list()
            packing_type_data.append
            packing_type_details = PackingTypeDetail.objects.filter(active=True, item=item_key).select_related("item", "packing_type")
            packing_type_detail_serializer = GetPackingTypeDetailSerializer(packing_type_details, many=True)
            return Response(packing_type_detail_serializer.data, status=status.HTTP_200_OK)

        suppliers = Supplier.objects.filter(active=True).order_by('first_name')
        suppliers_serializer = GetSupplierSerializer(suppliers, many=True, read_only=True)
        items = Item.objects.filter(active=True).order_by('name')
        item_serializer = GetItemSerializer(items, many=True, read_only=True) 
        data['items'] = item_serializer.data
        data['suppliers'] = suppliers_serializer.data
        return Response(data, status=status.HTTP_200_OK)

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        purchase_detail = request.data['purchase_details']
        # validation for Date fields being empty

        # setting pay type = 1 i.e CASH for stock addition
        request.data['pay_type'] = 1
        
        # validation for date time fields with blank values start
        try:
            if request.data['bill_date_ad'] == "":
                request.data['bill_date_ad'] = None
        except KeyError:
            return Response({'key_error': 'please provide bill_date_ad Keys'},
                            status=status.HTTP_400_BAD_REQUEST)
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

        request.data['purchase_no'] = generate_purchase_no(5)
        request.data['purchase_type'] = 5
        serializer = SavePurchaseAdjustmentSerializer(data=request.data, context={'request': request})
        if not serializer.is_valid(raise_exception=True):
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def retrieve(self, request, *args, **kwargs):
        return Response({"method not allowed"}, status=status.HTTP_405_METHOD_NOT_ALLOWED)


