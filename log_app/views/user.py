from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter, SearchFilter
import django_filters
from django_filters import DateFromToRangeFilter
from rest_framework import serializers, viewsets
from django_filters.filterset import FilterSet
from log_app.serializers.user import UserHistorySerializer
from src.user.models import User
from log_app.permissions.user_log_permissions import UserHistoryPermission


class FilterForUserHistory(FilterSet):
    date = DateFromToRangeFilter(field_name='history_date', label='History date ad')
    class Meta:
        model = User.history.model
        fields = ['id','history_type','history_date_bs']

class UserHistoryViewset(viewsets.ReadOnlyModelViewSet):
    permission_classes = [UserHistoryPermission]
    queryset = User.history.all()
    serializer_class = UserHistorySerializer
    filter_class = FilterForUserHistory
    http_method_names = ['get', 'option', 'head']