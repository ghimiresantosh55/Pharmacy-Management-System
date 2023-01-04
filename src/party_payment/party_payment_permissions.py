from rest_framework.permissions import BasePermission
from rest_framework.permissions import SAFE_METHODS


class PartyPaymentViewPermission(BasePermission):
    def has_permission(self, request, view):
        if request.user.is_anonymous:
            return False
        if request.user.is_superuser is True:
            return True
        try:
            user_permissions = request.user.group.permissions.values_list('code_name', flat=True)
        except:
            return False
        if request.method in SAFE_METHODS and 'view_party_payment' in user_permissions:
            return True
        return False


class PartyPaymentSavePermission(BasePermission):
    def has_permission(self, request, view):
        if request.user.is_anonymous:
            return False
        if request.user.is_superuser is True:
            return True
        try:
            user_permissions = request.user.group.permissions.values_list('code_name', flat=True)
        except:
            return False
        if (request.method == 'POST' or request.method in SAFE_METHODS) and 'add_party_payment' in user_permissions:
            return True
        return False

class BasicPartyPaymentPermission(BasePermission):
    def has_permission(self, request, view):
        if request.user.is_anonymous:
            return False
        if request.user.is_superuser is True:
            return True
        try:
            user_permissions = request.user.group.permissions.values_list('code_name', flat=True)
        except:
            return False
        if request.method in SAFE_METHODS and 'view_basic_party_payment' in user_permissions:
            return True
        if (request.method == 'POST' or request.method in SAFE_METHODS) and 'add_basic_part_payment' in user_permissions:
            return True
        if (request.method == 'PATCH' or request.method in SAFE_METHODS) and 'update_basic_party_payment' in user_permissions:
            return True
        return False
