from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import OpeningStockViewset, SaveOpeningStockViewset, UpdateOpeningStockViewset, OpeningStockSummaryViewset

router = DefaultRouter(trailing_slash=False)
router.register('opening-stock', OpeningStockViewset)
router.register('opening-stock-summary', OpeningStockSummaryViewset)
router.register('save-opening-stock', SaveOpeningStockViewset)
router.register('update-opening-stock', UpdateOpeningStockViewset)


urlpatterns = [

] + router.urls