from rest_framework import routers

from django.urls import path, include

from .views import CustomGroupViewSet, CustomPermissionViewSet, PermissionCategoryViewSet

router = routers.DefaultRouter(trailing_slash=False)
router.register("group", CustomGroupViewSet)
router.register("permission", CustomPermissionViewSet)
router.register("permission-category", PermissionCategoryViewSet)



urlpatterns = [
    path('', include(router.urls))
]
