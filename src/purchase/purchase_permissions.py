from rest_framework.permissions import BasePermission
from rest_framework.permissions import SAFE_METHODS


class PurchaseOrderSavePermission(BasePermission):
    def has_permission(self, request, view):
        if request.user.is_anonymous:
            return False
        if request.user.is_superuser is True:
            return True
        try:
            user_permissions = request.user.group.permissions.values_list('code_name', flat=True)
        except:
            return False
        if (request.method == 'POST' or request.method in SAFE_METHODS) and 'add_purchase_order' in user_permissions:
            return True
        return False


class PurchaseOrderViewPermission(BasePermission):
    def has_permission(self, request, view):
        if request.user.is_anonymous:
            return False
        if request.user.is_superuser is True:
            return True
        try:
            user_permissions = request.user.group.permissions.values_list('code_name', flat=True)
        except:
            return False
        if request.method in SAFE_METHODS and ('view_purchase_order' in user_permissions or
                                               'add_purchase_order' in user_permissions or
                                               'cancel_purchase_order' in user_permissions or
                                               'approve_purchase_order' in user_permissions):
            return True
        return False


class PurchaseOrderApprovePermission(BasePermission):
    def has_permission(self, request, view):
        if request.user.is_anonymous:
            return False
        if request.user.is_superuser is True:
            return True
        try:
            user_permissions = request.user.group.permissions.values_list('code_name', flat=True)
        except:
            return False
        if (request.method == 'POST' or request.method in SAFE_METHODS) and 'approve_purchase_order' in user_permissions:
            return True
        return False


class PurchaseOrderApprovedViewPermission(BasePermission):
    def has_permission(self, request, view):
        if request.user.is_anonymous:
            return False
        if request.user.is_superuser is True:
            return True
        try:
            user_permissions = request.user.group.permissions.values_list('code_name', flat=True)
        except:
            return False
        if request.method in SAFE_METHODS and ('view_purchase_order_approved' in user_permissions or
                                               'approve_purchase_order' in user_permissions):
            return True
        return False


class PurchaseOrderCancelPermission(BasePermission):
    def has_permission(self, request, view):
        if request.user.is_anonymous:
            return False
        if request.user.is_superuser is True:
            return True
        
        try:
            user_permissions = request.user.group.permissions.values_list('code_name', flat=True)
        except:
            return False

        if (request.method == 'POST' or request.method in SAFE_METHODS) and 'cancel_purchase_order' in user_permissions:
            return True
        return False


class PurchaseOrderCancelledViewPermission(BasePermission):
    def has_permission(self, request, view):
        if request.user.is_anonymous:
            return False
        if request.user.is_superuser is True:
            return True
        try:
            user_permissions = request.user.group.permissions.values_list('code_name', flat=True)
        except:
            return False
        if request.method in SAFE_METHODS and ('view_purchase_order_cancelled' in user_permissions or
                                               'cancel_purchase_order' in user_permissions):
            return True
        return False


# class PurchaseOrderPendingViewPermission(BasePermission):
#     def has_permission(self, request, view):
#         if request.user.is_superuser is True:
#             return True
#         user_permissions = request.user.group.permissions.values_list('code_name', flat=True)
#         if request.method in SAFE_METHODS and ('view_purchase_order_pending' in user_permissions or
#                                                'cancel_purchase_order' in user_permissions or
#                                                'approve_purchase_order' in user_permissions):
#             return True
#         return False


class PurchaseOrderDetailViewPermission(BasePermission):
    def has_permission(self, request, view):
        if request.user.is_anonymous:
            return False
        if request.user.is_superuser is True:
            return True
        # try:
        #     user_permissions = request.user.group.permissions.values_list('code_name', flat=True)
        # except:
        #     return False

        if PurchaseOrderViewPermission.has_permission(self, request, view):
            return True
        elif PurchaseOrderCancelledViewPermission.has_permission(self, request, view):
            return True
        elif PurchaseOrderApprovedViewPermission.has_permission(self, request, view):
            return True
        return False


'''---------------------- Permissions for Purchase ----------------------------------------------------'''


class PurchaseViewPermission(BasePermission):
    def has_permission(self, request, view):
        if request.user.is_anonymous:
            return False
        if request.user.is_superuser is True:
            return True
        try:
            user_permissions = request.user.group.permissions.values_list('code_name', flat=True)
        except:
            return False
        user_permissions = request.user.group.permissions.values_list('code_name', flat=True)
        if request.method in SAFE_METHODS and ('view_purchase' in user_permissions or
                                               'add_purchase' in user_permissions or
                                               'add_purchase_return' in user_permissions):
            return True
        return False


class PurchaseDirectPermission(BasePermission):
    def has_permission(self, request, view):
        if request.user.is_anonymous:
            return False
        if request.user.is_superuser is True:
            return True
        try:
            user_permissions = request.user.group.permissions.values_list('code_name', flat=True)
        except:
            return False
        if (request.method == 'POST' or request.method in SAFE_METHODS) and 'add_purchase' in user_permissions:
            return True
        return False


class PurchaseReturnedViewPermission(BasePermission):
    def has_permission(self, request, view):
        if request.user.is_anonymous:
            return False
        if request.user.is_superuser is True:
            return True
        try:
            user_permissions = request.user.group.permissions.values_list('code_name', flat=True)
        except:
            return False
        if request.method in SAFE_METHODS and ('view_purchase_return' in user_permissions or
                                               'add_purchase_return' in user_permissions):
            return True
        return False


class PurchaseReturnPermission(BasePermission):
    def has_permission(self, request, view):
        if request.user.is_anonymous:
            return False
        if request.user.is_superuser is True:
            return True
        try:
            user_permissions = request.user.group.permissions.values_list('code_name', flat=True)
        except:
            return False
        if (request.method == 'POST' or request.method in SAFE_METHODS) and 'add_purchase_return' in user_permissions:
            return True
        return False


class PurchaseAdditionPermission(BasePermission):
    def has_permission(self, request, view):
        if request.user.is_anonymous:
            return False
        if request.user.is_superuser is True:
            return True
        try:
            user_permissions = request.user.group.permissions.values_list('code_name', flat=True)
        except:
            return False
        if (request.method == 'POST' or request.method in SAFE_METHODS) and 'add_purchase_addition' in user_permissions:
            return True
        return False


class PurchaseDetailViewPermission(BasePermission):
    def has_permission(self, request, view):
        if request.user.is_anonymous:
            return False
        if request.user.is_superuser is True:
            return True
        # try:
        #     user_permissions = request.user.group.permissions.values_list('code_name', flat=True)
        # except:
        #     return False
        if PurchaseViewPermission.has_permission(self, request, view):
            return True
        elif PurchaseReturnedViewPermission.has_permission(self, request, view):
            return True
        return False