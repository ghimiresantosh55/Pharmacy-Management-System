from rest_framework.permissions import BasePermission
from rest_framework.permissions import SAFE_METHODS


class CountryPermission(BasePermission):
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

        # add_country is checked in user_permissions if add_country keyword is present permissions is provided for insert operations
        if (request.method == 'POST' or request.method in SAFE_METHODS) and 'add_country' in user_permissions:
            return True
        # update_country is checked in user_permissions if update_country keyword is present provided for update operations
        if (request.method == 'PATCH' or request.method in SAFE_METHODS) and 'update_country' in user_permissions:
            return True
        # view_country is checked in user_permissions if view_country keyword is present provided for view operations
        if request.method in SAFE_METHODS and 'view_country' in user_permissions:
            return True
        return False


class ProvincePermission(BasePermission):
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

        # add_province is checked in user_permissions if add_province keyword is present, permission provided for add operations
        if (request.method == 'POST' or request.method in SAFE_METHODS) and 'add_province' in user_permissions:
            return True
        # update_province is checked in user_permissions if update_province keyword is present, permission provided for update operations
        if (request.method == 'PATCH' or request.method in SAFE_METHODS) and 'update_province' in user_permissions:
            return True
        # view_province is checked in user_permissions if view_province keyword is present, permission provided for view operations
        if request.method in SAFE_METHODS and 'view_province' in user_permissions:
            return True
        return False


class DistrictPermission(BasePermission):
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
        # add_district is checked in user_permissions if match permissions is provided for view operations
        if (request.method == 'POST' or request.method in SAFE_METHODS) and 'add_district' in user_permissions:
            return True
        # update_district is checked in user_permissions if match permissions is provided for view operations
        if (request.method == 'PATCH' or request.method in SAFE_METHODS) and 'update_district' in user_permissions:
            return True
        # view_district is checked in user_permissions if match permissions is provided for view operations
        if request.method in SAFE_METHODS and 'view_district' in user_permissions:
            return True
        return False


class OrganizationRulePermission(BasePermission):
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

        # add_organization_rule is checked in user_permissions if match permissions is provided for post operations
        if (request.method in SAFE_METHODS or request.method == 'POST') and 'add_organization_rule' in user_permissions:
            return True

        # view_organization_rule is checked in user_permissions if match permissions is provided for view operations
        if request.method in SAFE_METHODS and 'view_organization_rule' in user_permissions:
            return True

        # update_organization_rule is checked in user_permissions if match permissions is provided for update operations
        if (request.method in SAFE_METHODS or request.method == 'PATCH') and 'update_organization_rule' in user_permissions:
            return True
        return False


class OrganizationSetupPermission(BasePermission):
    def has_permission(self, request, view):
        # if unknown user then permission is denied
        if request.user.is_anonymous:
            return False
        
        # if user is superuser then permission is allowed.
        if request.user.is_superuser is True:
            return True
        user_permissions = request.user.group.permissions.values_list('code_name', flat=True)
        # add_organization_setup is checked in user_permissions if match permissions is provided for post operations
        if request.method == 'POST' and 'add_organization_setup' in user_permissions:
            return True
        if request.method in SAFE_METHODS and ('view_organization_setup' in user_permissions or
                                               'add_organization_setup' in user_permissions or
                                               'update_organization_setup' in user_permissions):
            return True
        # update_organization_setup is checked in user_permissions if match permissions is provided for update operations
        if request.method == 'PATCH' and 'update_organization_setup' in user_permissions:
            return True
        return False


class BankPermission(BasePermission):
    def has_permission(self, request, view):
        # if unknown user then permission is denied
        if request.user.is_anonymous:
            return False

        # if user is superuser then permission is allowed.
        if request.user.is_superuser is True:
            return True
        user_permissions = request.user.group.permissions.values_list('code_name', flat=True)
        if request.method == 'POST' and 'add_bank' in user_permissions:
            return True
        if request.method in SAFE_METHODS and ('view_bank' in user_permissions or
                                               'update_bank' in user_permissions or
                                               'add_bank' in user_permissions):
            return True
        if request.method == 'PATCH' and 'update_bank' in user_permissions:
            return True
        return False


class BankDepositPermission(BasePermission):
    def has_permission(self, request, view):
        # if user is unkown then permission is denied
        if request.user.is_anonymous:
            return False
        
        # if user is superuser then permission is allowed.
        if request.user.is_superuser is True:
            return True
        user_permissions = request.user.group.permissions.values_list('code_name', flat=True)
        if request.method == 'POST' and 'add_bank_deposit' in user_permissions:
            return True
        if request.method in SAFE_METHODS and ('view_bank_deposit' in user_permissions or
                                               'add_bank_deposit' in user_permissions or
                                               'update_bank_deposit' in user_permissions):
            return True
        if request.method == 'PATCH' and 'update_bank_deposit' in user_permissions:
            return True
        return False


class PaymentModePermission(BasePermission):
    def has_permission(self, request, view):
        # if user is unkown then permission is denied
        if request.user.is_anonymous:
            return False
        # if user is superuser then permission is allowed.
        if request.user.is_superuser is True:
            return True
        user_permissions = request.user.group.permissions.values_list('code_name', flat=True)
        if request.method == 'POST' and 'add_payment_mode' in user_permissions:
            return True
        elif request.method in SAFE_METHODS and ('view_payment_mode' in user_permissions or
                                                 'add_payment_mode' in user_permissions or
                                                 'update_payment_mode' in user_permissions):
            return True
        elif request.method in SAFE_METHODS and 'approve_purchase_order' in user_permissions:
            return True
        elif request.method in SAFE_METHODS and 'add_purchase' in user_permissions:
            return True
        elif request.method in SAFE_METHODS and 'add_sale' in user_permissions:
            return True
        elif request.method in SAFE_METHODS and 'add_sale_return' in user_permissions:
            return True
        elif request.method == 'PATCH' and 'update_payment_mode' in user_permissions:
            return True
        return False


class DiscountSchemePermission(BasePermission):
    def has_permission(self, request, view):
        # if user is unkown then permission is denied
        if request.user.is_anonymous:
            return False

        # if user is superuser then permission is allowed.
        if request.user.is_superuser is True:
            return True
        user_permissions = request.user.group.permissions.values_list('code_name', flat=True)
        if request.method == 'POST' and 'add_discount_scheme' in user_permissions:
            return True
        if request.method in SAFE_METHODS and ('view_discount_scheme' in user_permissions or
                                               'add_discount_scheme' in user_permissions or
                                               'update_discount_scheme' in user_permissions ):
            return True
        if request.method == 'PATCH' and 'update_discount_scheme' in user_permissions:
            return True
        return False


class AdditionalChargeTypePermission(BasePermission):
    def has_permission(self, request, view):
        # if user is unkown then permission is denied
        if request.user.is_anonymous:
            return False

        # if user is superuser then permission is allowed.
        if request.user.is_superuser is True:
            return True
        user_permissions = request.user.group.permissions.values_list('code_name', flat=True)
        if (request.method == 'POST' or request.method in SAFE_METHODS) and 'add_additional_charge' in user_permissions:
            return True

        if request.method in SAFE_METHODS and ('view_additional_charge' in user_permissions or
                                               'approve_purchase_order' in user_permissions or
                                               'add_purchase' in user_permissions):
            return True
        if(request.method == 'PATCH' or request.method in SAFE_METHODS) and 'update_additional_charge' in user_permissions:
            return True
        return False


class AppAccessLogPermission(BasePermission):
    def has_permission(self, request, view):
        # if user is unkown then permission is denied
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
        
        # add_app_access_log is checked in user_permissions if match permissions is provided for add operations
        if (request.method == 'POST' or request.method in SAFE_METHODS) and 'add_app_access_log' in user_permissions:
            return True
        # view_app_access_log is checked in user_permissions if match permissions is provided for view operations
        if request.method in SAFE_METHODS and 'view_app_access_log' in user_permissions:
            return True
        return False


class StorePermission(BasePermission):
    def has_permission(self, request, view):
        # if user is unkown then permission is denied
        if request.user.is_anonymous:
            return False
        
        # if user is superuser then permission is allowed.
        if request.user.is_superuser is True:
            return True
        user_permissions = request.user.group.permissions.values_list('code_name', flat=True)
        if request.method == 'POST' and 'add_store' in user_permissions:
            return True
        if request.method in SAFE_METHODS and ('view_store' in user_permissions or
                                               'add_store' in user_permissions or
                                               'update_store' in user_permissions):
            return True
        if request.method == 'PATCH' and 'update_store' in user_permissions:
            return True
        return False

class  FiscalSessionADPermission(BasePermission):
    def has_permission(self, request, view):
        # if user is unkown then permission is denied
        if request.user.is_anonymous:
            return False
        
        # if user is superuser then permission is allowed.
        if request.user.is_superuser is True:
            return True
        user_permissions = request.user.group.permissions.values_list('code_name', flat=True)
        if request.method == 'POST' and 'add_store' in user_permissions:
            return True
        if request.method in SAFE_METHODS and ('view_fiscal_session_ad' in user_permissions or
                                               'add_fiscal_session_ad' in user_permissions or
                                               'update_fiscal_session_ad' in user_permissions):
            return True
        if request.method == 'PATCH' and 'update_fiscal_session_ad' in user_permissions:
            return True
        return False


class  FiscalSessionBSPermission(BasePermission):
    def has_permission(self, request, view):
        # if user is unkown then permission is denied
        if request.user.is_anonymous:
            return False
        
        # if user is superuser then permission is allowed.
        if request.user.is_superuser is True:
            return True
        user_permissions = request.user.group.permissions.values_list('code_name', flat=True)
        if request.method == 'POST' and 'add_store' in user_permissions:
            return True
        if request.method in SAFE_METHODS and ('view_fiscal_session_bs' in user_permissions or
                                               'add_fiscal_session_bs' in user_permissions or
                                               'update_fiscal_session_bs' in user_permissions):
            return True
        if request.method == 'PATCH' and 'update_fiscal_session_bs' in user_permissions:
            return True
        return False