from .serializers import CustomGroupSerializer, CustomPermissionSerializer, PermissionCategorySerializer
from .models import CustomGroup, CustomPermission, PermissionCategory
from rest_framework.viewsets import ModelViewSet
from rest_framework.filters import OrderingFilter, SearchFilter

from django_filters.rest_framework import DjangoFilterBackend, DateFromToRangeFilter, FilterSet
import django_filters
from .group_permissions import GroupPermission, PermissionPermission, PermissionCategoryPermission


class FilterForCustomGroup(FilterSet):
    date = DateFromToRangeFilter(field_name="created_date_ad")
    name = django_filters.CharFilter(lookup_expr='iexact')

    class Meta:
        model = CustomGroup
        fields = ['is_active', 'id',
                  'date', 'name']


class CustomGroupViewSet(ModelViewSet):
    permission_classes = [GroupPermission]
    queryset = CustomGroup.objects.all()
    serializer_class = CustomGroupSerializer
    filter_class = FilterForCustomGroup
    filter_backends = (SearchFilter, OrderingFilter, DjangoFilterBackend)
    search_fields = ['name']
    ordering_fields = ['id', 'name']


class CustomPermissionViewSet(ModelViewSet):
    permission_classes = [PermissionPermission]
    queryset = CustomPermission.objects.all()
    serializer_class = CustomPermissionSerializer
    filter_backends = (SearchFilter, OrderingFilter, DjangoFilterBackend)
    search_fields = ['name', 'code_name']
    ordering_fields = ['id', 'name']
    filter_fields = ['id', 'category']


class PermissionCategoryViewSet(ModelViewSet):
    permission_classes = [PermissionCategoryPermission]
    queryset = PermissionCategory.objects.all()
    serializer_class = PermissionCategorySerializer
    filter_backends = (SearchFilter, OrderingFilter, DjangoFilterBackend)
    search_fields = ['name']
    ordering_fields = ['id', 'name']
    filter_fields = ['id']
