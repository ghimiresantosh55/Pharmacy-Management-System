from rest_framework.permissions import BasePermission, SAFE_METHODS


class GroupPermission(BasePermission):
    def has_permission(self, request, view):
        if request.user.is_anonymous:
            return False
        if request.user.is_superuser is True:
            return True
        user_permissions = request.user.group.permissions.values_list('code_name', flat=True)
        if request.method == 'POST' and 'add_group' in user_permissions:
            return True
        if request.method in SAFE_METHODS and 'view_group' in user_permissions:
            return True
        if request.method == 'PATCH' and 'update_group' in user_permissions:
            return True

        return False


class PermissionPermission(BasePermission):
    def has_permission(self, request, view):
        if request.user.is_anonymous:
            return False
        if request.user.is_superuser is True:
            return True
        user_permissions = request.user.group.permissions.values_list('code_name', flat=True)
        if request.method in SAFE_METHODS and 'add_group' in user_permissions:
            return True
        if request.method in SAFE_METHODS and 'update_group' in user_permissions:
            return True
        return False


class PermissionCategoryPermission(BasePermission):
    def has_permission(self, request, view):
        if request.user.is_anonymous:
            return False
        if request.user.is_superuser is True:
            return True
        user_permissions = request.user.group.permissions.values_list('code_name', flat=True)
        if request.method in SAFE_METHODS and 'add_group' in user_permissions:
            return True
        if request.method in SAFE_METHODS and 'update_group' in user_permissions:
            return True
        return False
