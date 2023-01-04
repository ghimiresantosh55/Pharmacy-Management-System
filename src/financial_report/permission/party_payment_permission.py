from rest_framework.permissions import BasePermission
from rest_framework.permissions import SAFE_METHODS

class BasicPartyPaymentReportPermission(BasePermission):
    def has_permission(self, request, view):
        if request.user.is_anonymous:
            return False
        if request.user.is_superuser is True:
            return True
        try:
            user_permissions = request.user.group.permissions.values_list('code_name', flat=True)
        except:
            return False
        if request.method in SAFE_METHODS and 'view_basic_party_payment_report' in user_permissions:
            return True
        return False

class BasicPartyPaymentDetailReportPermission(BasePermission):
    def has_permission(self, request, view):
        if request.user.is_anonymous:
            return False
        if request.user.is_superuser is True:
            return True
        try:
            user_permissions = request.user.group.permissions.values_list('code_name', flat=True)
        except:
            return False
        if request.method in SAFE_METHODS and 'view_basic_party_payment_detail_report' in user_permissions:
            return True
        return False