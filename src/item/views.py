# Django-Rest_framework
from rest_framework import viewsets, status
from django_filters.rest_framework import DjangoFilterBackend, DateFromToRangeFilter
from rest_framework.filters import OrderingFilter, SearchFilter
from django_filters.rest_framework import FilterSet
import django_filters
from rest_framework.response import Response
# imported serializers
from .serializers import UnitSerializer, ManufacturerSerializer, GenericNameSerializer, ItemCategorySerializer, ItemSerializer, PackingTypeSerializer
from .serializers import GetPackingTypeDetailSerializer, GetGenericNameSerializer, GetItemCategorySerializer, GetManufactureSerializer
from .serializers import GetUnitSerializer, PackingTypeDetailSerializer
# imported models
from .models import Unit, Manufacturer, GenericName, ItemCategory, Item, PackingType, PackingTypeDetail
from .item_permissions import UnitPermission, ManufacturerPermission, GenericNamePermission, ItemPermission, ItemCategoryPermission, PackingTypePermission
from .item_permissions import PackingTypeDetailPermission
# for log

from simple_history.utils import update_change_reason
from rest_framework.decorators import action
from django.db import transaction
# views
# custom filter for Unit model

class FilterForPackingType(FilterSet):
    date = DateFromToRangeFilter(field_name="created_date_ad")
    name = django_filters.CharFilter(lookup_expr='iexact')
    class Meta:
        model = PackingType
        fields = ['name','short_name' ]

class PackingTypeViewSet(viewsets.ModelViewSet):
    permission_classes = [PackingTypePermission]
    queryset = PackingType.objects.all()
    serializer_class = PackingTypeSerializer
    filter_class = FilterForPackingType
    filter_backends = (SearchFilter, OrderingFilter, DjangoFilterBackend)
    search_fields = ['name', 'short_name']
    ordering_fields = ['id', 'name']
    http_method_names = ['get', 'head', 'post', 'patch']
    
    def partial_update(self, request, *args, **kwargs):
        try:
            remarks = str(request.data['remarks']).strip()
            if len(remarks) <= 0:
                return Response({'remarks': 'Please give at least one word for remarks'}, status=status.HTTP_400_BAD_REQUEST)
        except KeyError:
            return Response({'remarks': 'Please Provide remarks'}, status=status.HTTP_400_BAD_REQUEST)
        instance = self.get_object()
        serializer = self.serializer_class(instance, data=request.data, partial=True)

        if serializer.is_valid(raise_exception=True):
            serializer.save()
            # for log history. Atleast one reason must be given if update is made
            update_change_reason(instance, remarks)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class FilterForUnit(FilterSet):
    date = DateFromToRangeFilter(field_name="created_date_ad")
    name = django_filters.CharFilter(lookup_expr='iexact')
    class Meta:
        model = Unit
        fields = ['name','active', 'short_form']

class UnitViewSet(viewsets.ModelViewSet):
    permission_classes = [UnitPermission]
    queryset = Unit.objects.all()
    serializer_class = UnitSerializer
    filter_class = FilterForUnit
    filter_backends = (SearchFilter, OrderingFilter, DjangoFilterBackend)
    search_fields = ['name', 'short_form']
    ordering_fields = ['id', 'name', 'short_form']
    http_method_names = ['get', 'head', 'post', 'patch']


# custom filter for Manufacturer model
class FilterForManufacturer(FilterSet):
    date = DateFromToRangeFilter(field_name="created_date_ad")
    name = django_filters.CharFilter(lookup_expr='iexact') 
    class Meta:
        model = Manufacturer
        fields = ['name', 'active']

class ManufacturerViewSet(viewsets.ModelViewSet):
    permission_classes = [ManufacturerPermission]
    queryset = Manufacturer.objects.all()
    # print(queryset.query)
    serializer_class = ManufacturerSerializer
    filter_class = FilterForManufacturer
    filter_backends = (SearchFilter, OrderingFilter, DjangoFilterBackend)
    search_fields = ['name']
    ordering_fields = ['id', 'name']
    http_method_names = ['get', 'head', 'post', 'patch']


# custom filter for Genericname model
class FilterForGenericName(FilterSet):
    date = DateFromToRangeFilter(field_name="created_date_ad")
    name = django_filters.CharFilter(lookup_expr='iexact')
    class Meta:
        model = GenericName
        fields = ['name','active']

class GenericNameViewSet(viewsets.ModelViewSet):
    permission_classes = [GenericNamePermission]
    queryset = GenericName.objects.all()
    serializer_class = GenericNameSerializer
    filter_class = FilterForGenericName
    filter_backends = (SearchFilter, OrderingFilter, DjangoFilterBackend)
    search_fields = ['name']
    ordering_fields = ['id', 'name']
    http_method_names = ['get', 'head', 'post', 'patch']


# custom filter for Item model
class FilterForItem(FilterSet):
    date = DateFromToRangeFilter(field_name="created_date_ad")
    name = django_filters.CharFilter(lookup_expr='iexact')
    
    class Meta:
        model = Item
        fields = ['code', 'item_category__name', 'manufacturer', 'generic_name',
                  'location', 'taxable', 'discountable']


class ItemViewSet(viewsets.ModelViewSet):
    permission_classes = [ItemPermission]
    queryset = Item.objects.all().select_related("item_category", "manufacturer", "generic_name", "unit")
    serializer_class = ItemSerializer
    filter_class = FilterForItem
    filter_backends = (SearchFilter, OrderingFilter, DjangoFilterBackend)
    search_fields = ['name', 'code']
    ordering_fields = ['id', 'name', 'code']
    http_method_names = ['get', 'head', 'post', 'patch']


    @transaction.atomic
    def create(self, request, *args, **kwargs):
        return super(ItemViewSet, self).create(request, *args, *kwargs)

    @transaction.atomic
    def partial_update(self, request, *args, **kwargs):
        try:
            remarks = str(request.data['remarks']).strip()
            if len(remarks) <= 0:
                return Response({'remarks': 'Please give at least one word for remarks'},
                                status=status.HTTP_400_BAD_REQUEST)
        except KeyError:
            return Response({'remarks': 'Please Provide remarks'}, status=status.HTTP_400_BAD_REQUEST)
        instance = self.get_object()
        serializer = self.serializer_class(instance, data=request.data, partial=True, context={'request': request})
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            update_change_reason(instance, remarks)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(url_path="get-data", detail=False)
    def get_data(self, request):
            data = {}
            item_categories = ItemCategory.objects.filter(active=True)
            item_category_serializer = GetItemCategorySerializer(item_categories, many=True, context={"request": request})
            manufactures = Manufacturer.objects.filter(active=True)
            manufacture_serializer =  GetManufactureSerializer(manufactures, many=True,  context={"request": request})
            generic_names = GenericName.objects.filter(active=True)
            generic_name_serializer = GetGenericNameSerializer( generic_names, many=True,  context={"request": request})
            units = Unit.objects.filter(active=True)
            unit_serializer = GetUnitSerializer( units, many=True,context={"request": request})
            packing_type_details = PackingTypeDetail.objects.filter(active=True)
            packing_type_detail_serializer = GetPackingTypeDetailSerializer(packing_type_details, many=True, context={"request": request})
            data['item_categories'] = item_category_serializer.data
            data['packing_type_details'] = packing_type_detail_serializer.data
            data['manufactures'] = manufacture_serializer.data
            data['generic_names'] = generic_name_serializer.data
            data['units'] = unit_serializer.data
            return Response(data, status=status.HTTP_200_OK)


class FilterForItemCategory(FilterSet):
    date = DateFromToRangeFilter(field_name="created_date_ad")
    name = django_filters.CharFilter(lookup_expr='iexact')

    class Meta:
        model = ItemCategory
        fields = ['display_order', 'active', 'code', 'date', 'name']


class ItemCategoryViewSet(viewsets.ModelViewSet):
    permission_classes = [ItemCategoryPermission]
    queryset = ItemCategory.objects.all()
    serializer_class = ItemCategorySerializer
    filter_class = FilterForItemCategory
    filter_backends = (SearchFilter, OrderingFilter, DjangoFilterBackend)
    search_fields = ['name', 'code']
    ordering_fields = ['id', 'name', 'code', 'display_order']
    http_method_names = ['get', 'head', 'post', 'patch']

    def partial_update(self, request, *args, **kwargs):
        try:
            remarks = str(request.data['remarks']).strip()
            if len(remarks) <= 0:
                return Response({'remarks': 'Please give at least one word for remarks'},
                                status=status.HTTP_400_BAD_REQUEST)
        except KeyError:
            return Response({'remarks': 'Please Provide remarks'}, status=status.HTTP_400_BAD_REQUEST)
        instance = self.get_object()
        serializer = self.serializer_class(instance, data=request.data, partial=True)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            update_change_reason(instance, remarks)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class FilterForPackingTypeDetail(FilterSet):
    date = DateFromToRangeFilter(field_name="created_date_ad")
    item__name = django_filters.CharFilter(lookup_expr='iexact')
    packing_type__name =django_filters.CharFilter(lookup_expr='iexact')
    class Meta:
        model = PackingTypeDetail
        fields = ['id', 'item', 'packing_type']

class PackingTypeDetailViewSet(viewsets.ModelViewSet):
    permission_classes = [PackingTypeDetailPermission]
    queryset = PackingTypeDetail.objects.all().select_related("item","packing_type")
    serializer_class = PackingTypeDetailSerializer
    filter_class = FilterForPackingTypeDetail
    filter_backends = (SearchFilter, OrderingFilter, DjangoFilterBackend)
    search_fields = ['item__name','packing_type__name']
    ordering_fields = ['id','item' ]
    http_method_names = ['get', 'head', 'post', 'patch']

    def partial_update(self, request, *args, **kwargs):
        try:
            remarks = str(request.data['remarks']).strip()
            if len(remarks) <= 0:
                return Response({'remarks': 'Please give at least one word for remarks'}, status=status.HTTP_400_BAD_REQUEST)
        except KeyError:
            return Response({'remarks': 'Please Provide remarks'}, status=status.HTTP_400_BAD_REQUEST)
        instance = self.get_object()
        serializer = self.serializer_class(instance, data=request.data, partial=True)

        if serializer.is_valid(raise_exception=True):
            serializer.save()
            # for log history. Atleast one reason must be given if update is made
            update_change_reason(instance, remarks)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)