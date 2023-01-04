  
from rest_framework import routers

from django.urls import path, include

from .views import GetPartyInvoice,SavePartyPaymentViewSet, PartyPaymentViewSet,\
     PartyPaymentDetailViewSet, PartyPaymentSummaryViewSet, SaveBasicPartyPaymentViewset, BasicPartyPaymentDetailViewset

router = routers.DefaultRouter(trailing_slash=False)
router.register("party-payment", PartyPaymentViewSet)
router.register("party-payment-payment-detail", PartyPaymentDetailViewSet)
router.register("party-payment-summary", PartyPaymentSummaryViewSet)
router.register("get-party-invoice", GetPartyInvoice)
router.register("clear-party-invoice", SavePartyPaymentViewSet)
router.register("save-basic-party-payment", SaveBasicPartyPaymentViewset)
router.register("basic-party-payment-detail", BasicPartyPaymentDetailViewset)


urlpatterns = [
    path('', include(router.urls))
]
