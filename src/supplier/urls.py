from rest_framework import routers

from django.urls import path, include

from .views import SupplierViewSet

router = routers.DefaultRouter(trailing_slash=False)
router.register("supplier", SupplierViewSet)


urlpatterns = [
    path('', include(router.urls))
]