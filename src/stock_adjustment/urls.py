
from django.urls import path, include
from django.urls.resolvers import URLPattern
from rest_framework.routers import DefaultRouter
# from .views import StockAdditionViewset, StockSubtractionView
from .views import PurchaseMasterAdditionViewSet, PurchaseMasterSubtractionViewSet, SavePurchaseAdditionView, SavePurchaseSubtractionView

router = DefaultRouter(trailing_slash=False)
router.register("stock-addition", PurchaseMasterAdditionViewSet)
router.register("stock-subtraction", PurchaseMasterSubtractionViewSet)
router.register("save-stock-addition", SavePurchaseAdditionView)
router.register("save-stock-subtraction", SavePurchaseSubtractionView)

urlpatterns = [
    path('', include(router.urls))
]
