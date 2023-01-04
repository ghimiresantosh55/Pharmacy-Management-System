from rest_framework import routers

from django.urls import path, include

from .views import SaveOrderView, OrderMasterViewSet, OrderDetailViewSet, OrderSummaryViewSet

router = routers.DefaultRouter(trailing_slash=False)
router.register("save-order", SaveOrderView)

# Check where this URL is used???
router.register("order-master", OrderMasterViewSet)
router.register("order-detail", OrderDetailViewSet)
router.register("order-summary", OrderSummaryViewSet)

urlpatterns = [
    path('', include(router.urls))
]
