from rest_framework.routers import DefaultRouter
from django.urls import path, include
from .views import PurchaseOrderDetailViewSet, \
    PurchaseMasterViewSet, PurchaseDetailViewSet
from .views import SavePurchaseOrderView, CancelPurchaseOrderView, ApprovePurchaseOrderView, DirectApprovePurchaseView,\
    ReturnPurchaseView, GetUnAppUnCanPurchaseOrderMasterView, PurchaseMasterReturnedViewSet,\
    PurchaseMasterPurchaseViewSet, PurchaseOrderMasterViewSet, PurchasePaymentDetailsViewSet, \
    PurchaseAdditionalChargeViewSet
from src.custom_lib.views.stock_views import PurchaseDetailStockViewSet
router = DefaultRouter(trailing_slash=False)

# ViewSet registration from purchase
router.register("purchase-order-master", PurchaseOrderMasterViewSet)
router.register("purchase-order-detail", PurchaseOrderDetailViewSet)
router.register('get-orders', GetUnAppUnCanPurchaseOrderMasterView)
router.register("save-purchase-order", SavePurchaseOrderView)
router.register('cancel-purchase-order', CancelPurchaseOrderView)
router.register('approve-purchase-order', ApprovePurchaseOrderView)
router.register("purchase-master", PurchaseMasterViewSet)
router.register("purchase-master-purchase", PurchaseMasterPurchaseViewSet)
router.register("purchase-master-returned", PurchaseMasterReturnedViewSet)
router.register("purchase-detail", PurchaseDetailViewSet)
# router.register('direct-purchase', DirectApprovePurchaseView)
router.register('return-purchase', ReturnPurchaseView)
router.register('get-stock-by-purchase', PurchaseDetailStockViewSet)
router.register('purchase-payment-detail', PurchasePaymentDetailsViewSet)
router.register('purchase-additional-charge', PurchaseAdditionalChargeViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('direct-purchase', DirectApprovePurchaseView.as_view({'get': 'list','post':'create'}))
]
