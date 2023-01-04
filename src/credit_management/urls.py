from rest_framework import routers

from django.urls import path, include

from .views import GetCreditInvoice, SaveCreditClearanceViewSet, CreditClearanceViewSet,\
     CreditPaymentDetailViewSet, CreditClearanceSummary

router = routers.DefaultRouter(trailing_slash=False)
router.register("credit-clearance", CreditClearanceViewSet)
router.register("credit-clearance-payment-detail", CreditPaymentDetailViewSet)
router.register("credit-clearance-summary", CreditClearanceSummary)
router.register("get-credit-invoice", GetCreditInvoice)
router.register("clear-credit-invoice", SaveCreditClearanceViewSet)


urlpatterns = [
    path('', include(router.urls))
]
