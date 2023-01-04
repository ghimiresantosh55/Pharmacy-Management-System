from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from django.db import connection
from .models import Tenant
from .serializer import TenantSerializer

class TenantMapView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        connection.cursor().execute(f"SET search_path to public")
        tenant_map = Tenant.objects.all()
        tenant_serialzier = TenantSerializer(tenant_map, many=True)

        # tenants_map = [{
        #     'id': 1,
        #     'sub_domain_address': 'customer1.pims-backend.staging.merakitechs.com',
        #     'branch_name': 'customer1',
        # },
        # {
        #     'id': 2,
        #     'sub_domain_address': 'customer2.pims-backend.staging.merakitechs.com',
        #     'branch_name': 'customer2',
        # }]
        return Response(tenant_serialzier.data, status=status.HTTP_200_OK)