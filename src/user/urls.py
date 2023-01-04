
from django.urls import path, re_path, include
from rest_framework import routers
from src.user.views import UserLoginView, UserRegisterView,\
    UserLogout, ChangePasswordView, UpdateProfileView
from .views import UserViewSet, NewTokenRefreshView

router = routers.DefaultRouter(trailing_slash=False)
router.register("users", UserViewSet)
# router.register("user-groups", UserGroupViewSet)
# router.register("user-permissions", PermissionViewSet)
# router.register("user-models", ModelTypeViewSet)
urlpatterns = [
    path('register', UserRegisterView.as_view(), name="register"),
    path('login', UserLoginView.as_view(), name='UserLogin'),
    path('logout', UserLogout.as_view(), name="logout"),
    path('login/refresh', NewTokenRefreshView.as_view(), name='token_refresh'),
    path('change-password/<int:pk>', ChangePasswordView.as_view(),
         name='auth_change_password'),
    path('update-profile/<int:pk>', UpdateProfileView.as_view(),
         name='auth_update_profile'),
    re_path(r'password-reset/', include('django_rest_resetpassword.urls',
            namespace='password_reset')),
] + router.urls

'''
1 - submit email form       //PasswordResetView.as_view()
2 - email sent success message //PasswordResetDoneView.as_view()
3 - Link to password reset form in email  //PasswordResetConfirmView.as_view()
4 - Password successfully changed message //PasswordResetCompleteView.as_view()
'''
