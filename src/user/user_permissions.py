from rest_framework.permissions import BasePermission


class UserRegisterPermission(BasePermission):

    def has_permission(self, request, view):
        if request.user.is_anonymous:
            return False

        if request.user.is_superuser is True:
            return True
        try:
            permissions_list = request.user.group.permissions.values_list('code_name', flat=True)
        except:
            return False
        permissions_list = request.user.group.permissions.values_list('code_name', flat=True)
        if request.method == 'POST' and 'add_user' in permissions_list:
            return True
        return False


class UserUpdatePermissions(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.user.is_anonymous:
            return False
        if request.user.is_superuser is True:
            return True
        permissions_list = request.user.group.permissions.values_list('code_name', flat=True)
        if request.method == 'PATCH' and 'update_user' in permissions_list:
            return True
        return False


class UserChangePasswordPermissions(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.user.is_anonymous:
            return False
        if request.user.is_superuser is True:
            return True
        permissions_list = request.user.group.permissions.values_list('code_name', flat=True)
        if request.method == 'PATCH' and 'change_user_password' in permissions_list:
            return True
        elif request.user.id == obj.id:
            return True
        return False


class UserViewPermissions(BasePermission):

    def has_permission(self, request, view):
        if request.user.is_anonymous:
            return False
        if request.user.is_superuser is True:
            return True
        try:
            permissions_list = request.user.group.permissions.values_list('code_name', flat=True)
        except:
            return False
        if 'view_user' in permissions_list or 'add_user' in permissions_list or 'update_user' in permissions_list:
            return True
        return False


class UserRetrievePermission(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.user.is_anonymous:
            return False
        if request.user.is_superuser is True:
            return True
        if request.user.id == obj.id:
            return True
        return False
