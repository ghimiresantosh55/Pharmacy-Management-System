import django_filters

# IPAddress

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics
from rest_framework import status
from rest_framework import viewsets
from rest_framework.filters import OrderingFilter, SearchFilter
# imported permissions
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
# third-party
from rest_framework.views import APIView
from rest_framework_simplejwt.views import (
    TokenRefreshView,
)

# imported models
from .models import User
# imported serializers
from .serializers import ChangePasswordSerializer, UpdateUserSerializer
from .serializers import RegisterUserSerializer, LoginSerializer, \
    UserListSerializer, LogoutSerializer
from .user_permissions import UserViewPermissions, UserRegisterPermission, UserChangePasswordPermissions, \
    UserUpdatePermissions, UserRetrievePermission
from .user_login_log import save_user_log

class NewTokenRefreshView(TokenRefreshView):
    permission_classes = (AllowAny,)


class UserRegisterView(APIView):
    permission_classes = [UserRegisterPermission]
    serializer_class = RegisterUserSerializer

    def get_queryset(self):
        return User.objects.all()

    def post(self, request):
        user = request.data
        serializer = self.serializer_class(data=user, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        user_data = serializer.data
        return Response(user_data, status=status.HTTP_201_CREATED)


class UserLoginView(APIView):
    permission_classes = [AllowAny]
    serializer_class = LoginSerializer

    def get_queryset(self):
        return User.objects.all()

    def post(self, request):
        serializer = self.serializer_class(data=request.data, context={'request': request})
        if serializer.is_valid(raise_exception=True):

            # saving user login information to log database
            save_user_log(request, serializer.data['id'])
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserLogout(APIView):
    permission_classes = [AllowAny]
    serializer_class = LogoutSerializer

    def get_queryset(self):
        return User.objects.all()

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response({"Logout successful"}, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UpdateProfileView(generics.UpdateAPIView):
    permission_classes = [UserUpdatePermissions]
    queryset = User.objects.all()
    serializer_class = UpdateUserSerializer

    def patch(self, request, pk, **kwargs):
        # if pk != request.user.id:
        #     return Response("invalid id, Please choose the pk you are logged in with")
        # validation for date time fields with blank values
        user_object = self.get_object()
        serializer = UpdateUserSerializer(user_object, data=request.data, partial=True, context={'request': request,
                                                                                                 'pk': pk})  # set partial=True to update a data partially
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ChangePasswordView(generics.UpdateAPIView):
    permission_classes = [UserChangePasswordPermissions]
    queryset = User.objects.all()
    serializer_class = ChangePasswordSerializer


class FilterForUsers(django_filters.FilterSet):
    user_name = django_filters.CharFilter(lookup_expr='iexact')

    class Meta:
        model = User
        fields = ['id', 'user_name', 'group']


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [UserViewPermissions]
    queryset = User.objects.all()
    serializer_class = UserListSerializer
    filter_class = FilterForUsers
    filter_backends = (SearchFilter, OrderingFilter, DjangoFilterBackend)
    search_fields = ["mobile_no", "user_name", 'email']
    ordering_fields = ['id']

    def get_permissions(self):
        if self.action == 'list':
            self.permission_classes = [UserViewPermissions]
        elif self.action == 'retrieve':
            self.permission_classes = [UserRetrievePermission]
        return super(self.__class__, self).get_permissions()
