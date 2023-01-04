from rest_framework.permissions import BasePermission
from rest_framework.permissions import SAFE_METHODS


# permission for viewing of credit
class CreditManagementViewPermission(BasePermission):
    def has_permission(self, request, view):
        if request.user.is_anonymous:
            return False
        if request.user.is_superuser is True:
            return True
        try:
            user_permissions = request.user.group.permissions.values_list('code_name', flat=True)
        except:
            return False
        
        if request.method in SAFE_METHODS and 'view_credit_management' in user_permissions:
            return True
        return False

# permission for post operation in credit management
class CreditManagementSavePermission(BasePermission):
    def has_permission(self, request, view):
        if request.user.is_anonymous:
            return False
        if request.user.is_superuser is True:
            return True
        try:
            user_permissions = request.user.group.permissions.values_list('code_name', flat=True)
        except:
            return False
        if (request.method == 'POST' or request.method in SAFE_METHODS) and 'add_credit_management' in user_permissions:
            return True
        return False