from rest_framework.routers import DefaultRouter
from django.urls import path, include

from src.party_payment.models import BasicPartyPaymentDetail
from .views import PurchaseOrderMasterReportViewSet, PurchaseOrderSummaryReportViewSet,\
     PurchaseOrderDetailReportViewSet, StockAdjustmentReportViewSet, StockAdjustmentSummaryReportViewSet
from .views import PurchaseMasterReportViewSet, PurchaseDetailReportViewSet, PurchaseSummaryReportViewSet, ItemwisePurchaseReportViewset
from .views import SaleMasterReportViewSet, SaleDetailReportViewSet, SaleSummaryReportViewSet, SaleCreditReportViewSet
from .views import CustomerOrderSummaryViewSet, CustomerOrderDetailReportViewSet, CustomerOrderMasterReportViewSet, BasicPartyPaymentReportViewset,\
    BasicPartyPaymentDetailReportViewSet, BasicPartyPaymentSummaryReportViewSet
router = DefaultRouter(trailing_slash=False)


# ViewSet registration from purchase
router.register("purchase-order", PurchaseOrderMasterReportViewSet)
router.register("purchase-order-summary", PurchaseOrderSummaryReportViewSet)
router.register("purchase-order-detail", PurchaseOrderDetailReportViewSet)
router.register("purchase", PurchaseMasterReportViewSet)
router.register("itemwise-purchase-report",ItemwisePurchaseReportViewset)
router.register("stock-adjustment",StockAdjustmentReportViewSet)
router.register("stock-adjustment-summary",StockAdjustmentSummaryReportViewSet)
router.register("purchase-detail", PurchaseDetailReportViewSet)
router.register("purchase-summary", PurchaseSummaryReportViewSet)
router.register("sale", SaleMasterReportViewSet)
router.register("sale-detail", SaleDetailReportViewSet)
router.register("sale-summary", SaleSummaryReportViewSet)
router.register("credit", SaleCreditReportViewSet) # change to credit-sale
router.register("order-master", CustomerOrderMasterReportViewSet)
router.register("order-detail", CustomerOrderDetailReportViewSet)
router.register("order-summary", CustomerOrderSummaryViewSet)
router.register("party-payment", BasicPartyPaymentReportViewset)
router.register("party-payment-detail", BasicPartyPaymentDetailReportViewSet)
router.register("party-payment-summary", BasicPartyPaymentSummaryReportViewSet)


# router.register("party-payment", BasicPartyPaymentReportViewset, basename="party-payment")
# router.register("party-payment-detail", BasicPartyPaymentDetailReportViewSet, basename="party-payment-report-detail")
router.register("party-payment", BasicPartyPaymentDetailReportViewSet)


urlpatterns = [
    path('', include(router.urls))
    

]