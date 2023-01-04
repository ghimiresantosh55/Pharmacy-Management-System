from rest_framework import routers

from django.urls import path, include

from .views import UnitViewSet, ManufacturerViewSet, GenericNameViewSet, ItemViewSet, ItemCategoryViewSet, PackingTypeViewSet
from .views import PackingTypeDetailViewSet

router = routers.DefaultRouter(trailing_slash=False)
router.register("unit", UnitViewSet)
router.register("manufacturer", ManufacturerViewSet)
router.register("generic-name", GenericNameViewSet)
router.register("item", ItemViewSet)
router.register("item-category", ItemCategoryViewSet)
router.register("packing-type", PackingTypeViewSet)
router.register("packing-type-detail", PackingTypeDetailViewSet)

urlpatterns = [
    path('', include(router.urls))
]
