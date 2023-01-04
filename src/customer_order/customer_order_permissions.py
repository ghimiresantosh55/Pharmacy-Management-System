from rest_framework.permissions import BasePermission
from rest_framework.permissions import SAFE_METHODS


# permission for customer order view
class CustomerOrderViewPermission(BasePermission):
    
    def has_permission(self, request, view):
        # if unknown user then permission is denied
        if request.user.is_anonymous:
            return False
        
        # if user is superuser then permission is allowed.
        if request.user.is_superuser is True:
            return True
        
        # exception handling
        # first try block is checked if condition doesnot match error is passed
        try:
            # value from permissions model (i.e. code name) is saved in user_permissions
            user_permissions = request.user.group.permissions.values_list('code_name', flat=True)
        except:
            return False
        # check if view_customer_order is in user_permissions or not. If yes permissions is provided
        if request.method in SAFE_METHODS and 'view_customer_order' in user_permissions:
            return True
        return False


# permission for adding customer_order 
class CustomerOrderSavePermission(BasePermission):
    # if unknown user then permission is denied
    def has_permission(self, request, view):
        if request.user.is_anonymous:
            return False

        # if user is superuser then permission is allowed.
        if request.user.is_superuser is True:
            return True
        
        # exception handling
        # first try block is checked if condition doesnot match error is passed
        try:
            # value from permissions model (i.e. code name) is saved in user_permissions
            user_permissions = request.user.group.permissions.values_list('code_name', flat=True)
        except:
            return False
        
        # add_customer_order is checked in user_permissions. If present then permission is provided
        if (request.method == 'POST' or request.method in SAFE_METHODS) and 'add_customer_order' in user_permissions:
            return True
        return False


# permission for customer_order update 
class CustomerOrderUpdatePermission(BasePermission):
    def has_permission(self, request, view):
        # if unknown user then permission is denied
        if request.user.is_anonymous:
            return False

        # if user is superuser then permission is allowed.
        if request.user.is_superuser is True:
            return True
        
        # exception handling
        # first try block is checked if condition doesnot match error is passed
        try:
            # value from permissions model (i.e. code name) is saved in user_permissions
            user_permissions = request.user.group.permissions.values_list('code_name', flat=True)
        except:
            return False
        #  user_permissions and update_customer_order is compared if yes, permissions is provided
        if (request.method == 'PATCH' or request.method in SAFE_METHODS) and 'update_customer_order' in user_permissions:
            return True
        return False


# permission for customer_order cancellation
class CustomerOrderCancelPermission(BasePermission):
    
    def has_permission(self, request, view):
        # if unknown user then permission is denied
        if request.user.is_anonymous:
            return False
        # if user is superuser then permission is allowed.
        if request.user.is_superuser is True:
            return True
        # exception handling
        # first try block is checked if condition doesnot match error is passed
        try:
            # value from permissions model (i.e. code name) is saved in user_permissions
            user_permissions = request.user.group.permissions.values_list('code_name', flat=True)
        except:
            return False
        #  check of cancel_customer_order is in user_permissions or not if yes, permissions is provided.
        if (request.method == 'PATCH' or request.method in SAFE_METHODS) and 'cancel_customer_order' in user_permissions:
            return True
        return False
