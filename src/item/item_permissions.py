from rest_framework.permissions import BasePermission
from rest_framework.permissions import SAFE_METHODS


class PackingTypePermission(BasePermission):
    def has_permission(self, request, view):
        if request.user.is_anonymous:
            return False
        if request.user.is_superuser is True:
            return True
        try:
            user_permissions = request.user.group.permissions.values_list('code_name', flat=True)
        except:
            return False
        if request.method in SAFE_METHODS and 'view_packing_type' in user_permissions:
            return True
        if (request.method == 'POST' or request.method in SAFE_METHODS) and 'add_packing_type' in user_permissions:
            return True
        if (request.method == 'PATCH' or request.method in SAFE_METHODS) and 'update_packing_type' in user_permissions:
            return True
        return False

class UnitPermission(BasePermission):
    def has_permission(self, request, view):
        if request.user.is_anonymous:
            return False
        if request.user.is_superuser is True:
            return True
        try:
            user_permissions = request.user.group.permissions.values_list('code_name', flat=True)
        except:
            return False
        if request.method in SAFE_METHODS and 'view_unit' in user_permissions:
            return True
        if (request.method == 'POST' or request.method in SAFE_METHODS) and 'add_unit' in user_permissions:
            return True
        if (request.method == 'PATCH' or request.method in SAFE_METHODS) and 'update_unit' in user_permissions:
            return True
        return False


class ManufacturerPermission(BasePermission):
    def has_permission(self, request, view):
        if request.user.is_anonymous:
            return False
        if request.user.is_superuser is True:
            return True
        try:
            user_permissions = request.user.group.permissions.values_list('code_name', flat=True)
        except:
            return False
        if request.method in SAFE_METHODS and 'view_manufacturer' in user_permissions:
            return True
        if (request.method == 'POST' or request.method in SAFE_METHODS) and 'add_manufacturer' in user_permissions:
            return True
        if (request.method == 'PATCH' or request.method in SAFE_METHODS) and 'update_manufacturer' in user_permissions:
            return True
        return False


class GenericNamePermission(BasePermission):
    def has_permission(self, request, view):
        if request.user.is_anonymous:
            return False
        if request.user.is_superuser is True:
            return True
        try:
            user_permissions = request.user.group.permissions.values_list('code_name', flat=True)
        except:
            return False
        if request.method in SAFE_METHODS and 'view_generic_name' in user_permissions:
            return True
        if (request.method == 'POST' or request.method in SAFE_METHODS) and 'add_generic_name' in user_permissions:
            return True
        if (request.method == 'PATCH' or request.method in SAFE_METHODS) and 'update_generic_name' in user_permissions:
            return True
        return False


class ItemPermission(BasePermission):
    def has_permission(self, request, view):
        if request.user.is_anonymous:
            return False
        if request.user.is_superuser is True:
            return True
        try:
            user_permissions = request.user.group.permissions.values_list('code_name', flat=True)
        except:
            return False
        if (request.method == 'POST' or request.method in SAFE_METHODS) and 'add_item' in user_permissions:
            return True
        if request.method in SAFE_METHODS and 'view_item' in user_permissions:
            return True
        if (request.method == 'PATCH' or request.method in SAFE_METHODS) and 'update_item' in user_permissions:
            return True
        return False


class ItemCategoryPermission(BasePermission):
    def has_permission(self, request, view):
        if request.user.is_anonymous:
            return False
        if request.user.is_superuser is True:
            return True
        try:
            user_permissions = request.user.group.permissions.values_list('code_name', flat=True)
        except:
            return False
        if (request.method == 'POST' or request.method in SAFE_METHODS) and 'add_item_category' in user_permissions:
            return True
        if request.method in SAFE_METHODS and 'view_item_category' in user_permissions:
            return True
        if (request.method == 'PATCH' or request.method in SAFE_METHODS) and 'update_item_category' in user_permissions:
            return True
        return False


class PackingTypeDetailPermission(BasePermission):
    def has_permission(self, request, view):
        if request.user.is_anonymous:
            return False
        if request.user.is_superuser is True:
            return True
        try:
            user_permissions = request.user.group.permissions.values_list('code_name', flat=True)
        except:
            return False
        if (request.method == 'POST' or request.method in SAFE_METHODS) and 'add_packing_type_detail' in user_permissions:
            return True
        if request.method in SAFE_METHODS and 'view_packing_type_detail' in user_permissions:
            return True
        if (request.method == 'PATCH' or request.method in SAFE_METHODS) and 'update_packing_type_detail' in user_permissions:
            return True
        return False
