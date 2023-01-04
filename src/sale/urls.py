from rest_framework.routers import DefaultRouter
from django.urls import path, include
from .views import SaleMasterView, SaleDetailView, SaveSaleView, ReturnSaleView, SaleDetailForReturnViewSet, \
    SalePaymentDetailView, SaleMasterSaleView, SaleMasterReturnView, SaleAdditionalChargeViewSet,\
        SalePrintLogViewset
router = DefaultRouter(trailing_slash=False)

# ViewSet registration from purchase
router.register("sale-master", SaleMasterView)
router.register("sale-master-sale", SaleMasterSaleView)
router.register("sale-master-return", SaleMasterReturnView)
router.register("sale-detail", SaleDetailView)
router.register("get-sale-info", SaleDetailForReturnViewSet)
router.register("save-sale", SaveSaleView)
router.register("save-sale-return", ReturnSaleView)
router.register("sale-payment-detail", SalePaymentDetailView)
router.register("sale-additional-charge", SaleAdditionalChargeViewSet)
router.register("sale-print-log",SalePrintLogViewset)


urlpatterns = [
    path('', include(router.urls)),

]