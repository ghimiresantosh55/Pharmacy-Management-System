from rest_framework.permissions import BasePermission
from rest_framework.permissions import SAFE_METHODS


class SaleSavePermission(BasePermission):
    def has_permission(self, request, view):
        if request.user.is_anonymous:
            return False
        if request.user.is_superuser is True:
            return True
        try:
            user_permissions = request.user.group.permissions.values_list('code_name', flat=True)
        except:
            return False
        if (request.method == 'POST' or request.method in SAFE_METHODS) and 'add_sale' in user_permissions:
            return True
        return False


class SaleViewPermission(BasePermission):
    def has_permission(self, request, view):
        if request.user.is_anonymous:
            return False
        if request.user.is_superuser is True:
            return True
        try:
            user_permissions = request.user.group.permissions.values_list('code_name', flat=True)
        except:
            return False
        if request.method in SAFE_METHODS and ('view_sale' in user_permissions or 'add_sale' in user_permissions or
                                               'add_sale_return' in user_permissions):
            return True
        return False


class SaleReturnViewPermission(BasePermission):
    def has_permission(self, request, view):
        if request.user.is_anonymous:
            return False
        if request.user.is_superuser is True:
            return True
        try:
            user_permissions = request.user.group.permissions.values_list('code_name', flat=True)
        except:
            return False
        if request.method in SAFE_METHODS and ('view_sale_return' in user_permissions or
                                               'add_sale_return' in user_permissions):
            return True
        return False


class SaleDetailViewPermission(BasePermission):
    def has_permission(self, request, view):
        if request.user.is_anonymous:
            return False
        if SaleViewPermission.has_permission(self, request, view):
            return True
        elif SaleReturnViewPermission.has_permission(self, request, view):
            return True
        return False


class SaleReturnPermission(BasePermission):
    def has_permission(self, request, view):
        if request.user.is_anonymous:
            return False
        if request.user.is_superuser is True:
            return True
        try:
            user_permissions = request.user.group.permissions.values_list('code_name', flat=True)
        except:
            return False
        if (request.method == 'POST' or request.method in SAFE_METHODS) and 'add_sale_return' in user_permissions:
            return True
        return False

class SalePrintLogPermission(BasePermission):
    def has_permission(self, request, view):
        if request.user.is_anonymous:
            return False
        if request.user.is_superuser is True:
            return True
        try:
            user_permissions = request.user.group.permissions.values_list('code_name', flat=True)
        except:
            return False
        if request.method in SAFE_METHODS and 'view_sale_print_log' in user_permissions:
            return True
        if (request.method == 'POST' or request.method in SAFE_METHODS) and 'add_sale_print_log' in user_permissions:
            return True
        return False