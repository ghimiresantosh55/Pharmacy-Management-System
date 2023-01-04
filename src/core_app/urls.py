from rest_framework import routers

from django.urls import path, include

from .views import OrganizationSetupViewSet, OrganizationRuleViewSet,\
    CountryViewSet, ProvinceViewset, DistrictViewset, AppAccessLogViewset
from .views import BankViewSet, BankDepositViewSet, PaymentModeViewSet, DiscountSchemeViewSet, AdditionalChargeTypeViewSet,  StoreViewSet, FiscalSessionADViewSet, FiscalSessionBSViewSet

router = routers.DefaultRouter(trailing_slash=False)
router.register("country", CountryViewSet)
router.register("province", ProvinceViewset)
router.register("district", DistrictViewset)
router.register("organization-setup", OrganizationSetupViewSet)
router.register("organization-rule", OrganizationRuleViewSet)
router.register("bank", BankViewSet)
router.register("bank-deposit", BankDepositViewSet)
router.register("payment-mode", PaymentModeViewSet)
router.register("discount-scheme", DiscountSchemeViewSet)
router.register("additional-charge-type", AdditionalChargeTypeViewSet)
router.register("app-access-log", AppAccessLogViewset)
router.register("store", StoreViewSet)
router.register("fiscal-session-ad", FiscalSessionADViewSet)
router.register("fiscal-session-bs", FiscalSessionBSViewSet)

urlpatterns = [
    path('', include(router.urls))
]
