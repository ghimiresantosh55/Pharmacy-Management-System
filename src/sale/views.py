# Django-rest-framework
from rest_framework import serializers, viewsets, status
from rest_framework.response import Response
from django.db import transaction
from decimal import Decimal
from rest_framework.decorators import api_view
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter, SearchFilter
from src.custom_lib.functions.fiscal_year import get_fiscal_year_code_bs
# from requests library
import requests
from django.utils import timezone
import threading
from django.db import connection
from tenant.utils import tenant_schema_from_request

from src.sale.models import SaleDetail, SaleMaster, SalePaymentDetail, IRDUploadLog, SaleAdditionalCharge, SalePrintLog
from .sale_unique_id_generator import generate_sale_no

# import core files
from src.custom_lib.functions import stock

# filter
from django_filters import DateFromToRangeFilter, FilterSet

# import serializer
from src.sale.serializers import SaleMasterSerializer, SaleDetailSerializer, SaveSaleMasterSerializer, \
    SaleDetailForSaleReturnSerializer, SalePaymentDetailSerializer, GetAdditionalChargeTypeSerializer
from src.sale.serializers import GetDiscountSchemeSerializer, GetPaymentModeSerializer, GetCustomerSerializer
from src.customer.serializers import CustomerSerializer
from src.core_app.models import DiscountScheme, AdditionalChargeType, PaymentMode, OrganizationSetup
from src.core_app.serializers import DiscountSchemeSerializer, AdditionalChargeTypeSerializer, PaymentModeSerializer
from src.customer.models import Customer
from .sale_permissions import SaleSavePermission, SaleViewPermission, SaleReturnViewPermission, SaleReturnPermission, \
    SaleDetailViewPermission, SalePrintLogPermission
from .serializers import SalePrintLogSerializer, UpdateCustomerOrderMsterSerializer, SaleAdditionalChargeSerializer
from src.customer_order.models import OrderMaster


class SaleMasterView(viewsets.ReadOnlyModelViewSet):
    permission_classes = [SaleViewPermission]
    queryset = SaleMaster.objects.all().select_related("discount_scheme","customer","ref_order_master")
    serializer_class = SaleMasterSerializer
    filter_backends = (SearchFilter, OrderingFilter, DjangoFilterBackend)
    search_fields = ["sale_no", "customer__first_name"]
    filter_fields = ["customer", "sale_type"]
    ordering_fields = ["id", "sale_no"]


class SaleMasterSaleView(viewsets.ReadOnlyModelViewSet):
    permission_classes = [SaleViewPermission]
    queryset = SaleMaster.objects.filter(sale_type=1).select_related("discount_scheme","customer","ref_order_master")
    serializer_class = SaleMasterSerializer
    filter_backends = (SearchFilter, OrderingFilter, DjangoFilterBackend)
    search_fields = ["sale_no", "customer__first_name"]
    filter_fields = ["customer", "sale_type"]
    ordering_fields = ["id", "sale_no"]


class SaleMasterReturnView(viewsets.ReadOnlyModelViewSet):
    permission_classes = [SaleReturnViewPermission]
    queryset = SaleMaster.objects.filter(sale_type=2).select_related("discount_scheme","customer","ref_order_master")
    serializer_class = SaleMasterSerializer
    filter_backends = (SearchFilter, OrderingFilter, DjangoFilterBackend)
    search_fields = ["sale_no", "customer__first_name"]
    filter_fields = ["customer", "sale_type"]
    ordering_fields = ["id", "sale_no"]


class SaleDetailView(viewsets.ReadOnlyModelViewSet):
    permission_classes = [SaleDetailViewPermission]
    queryset = SaleDetail.objects.all().select_related("sale_master","item","item_category","packing_type","packing_type_detail")
    serializer_class = SaleDetailSerializer
    filter_backends = (SearchFilter, OrderingFilter, DjangoFilterBackend)
    search_fields = ["item", "sale_master__customer"]
    filter_fields = ["sale_master", "item", "item_category"]
    ordering_fields = ["id", "sale_master", "sale_master__sale_no"]


class SalePaymentDetailView(viewsets.ReadOnlyModelViewSet):
    permission_classes = [SaleDetailViewPermission]
    queryset = SalePaymentDetail.objects.all().select_related("sale_master","payment_mode")
    serializer_class = SalePaymentDetailSerializer
    filter_backends = (SearchFilter, OrderingFilter, DjangoFilterBackend)
    search_fields = ["sale_master__customer"]
    filter_fields = ["sale_master", "id", "payment_mode"]
    ordering_fields = ["id"]


class SaleAdditionalChargeViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [SaleDetailViewPermission]
    queryset = SaleAdditionalCharge.objects.all().select_related("charge_type","sale_master")
    serializer_class = SaleAdditionalChargeSerializer
    filter_backends = (SearchFilter, OrderingFilter, DjangoFilterBackend)
    search_fields = ["remarks"]
    filter_fields = ["sale_master", "id", "charge_type"]
    ordering_fields = ["id", 'charge_type', 'sale_master', 'amount']


class SaleDetailForReturnViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [SaleViewPermission]
    queryset = SaleDetail.objects.filter(ref_sale_detail__isnull=True).select_related("sale_master","item","item_category","packing_type","packing_type_detail")
    serializer_class = SaleDetailForSaleReturnSerializer
    filter_backends = (SearchFilter, OrderingFilter, DjangoFilterBackend)
    search_fields = ["item", "customer","item__code"]
    filter_fields = ["sale_master", "item", "item_category"]
    ordering_fields = ["id", "sale_master"]


class SaveSaleView(viewsets.ModelViewSet):
    permission_classes = [SaleSavePermission]
    queryset = SaleMaster.objects.all().select_related("discount_scheme","customer","ref_order_master")
    serializer_class = SaveSaleMasterSerializer

    def list(self, request, **kwargs):
        data = {}
        customer = Customer.objects.filter(active=True)
        customer_serializer = GetCustomerSerializer(customer, many=True)
        discount_scheme = DiscountScheme.objects.filter(active=True)
        discount_scheme_serializer = GetDiscountSchemeSerializer(
            discount_scheme, many=True)
        additional_charge = AdditionalChargeType.objects.filter(active=True)
        additional_charge_serializer = GetAdditionalChargeTypeSerializer(
            additional_charge, many=True)
        payment_modes = PaymentMode.objects.filter(active=True)
        payment_mode_serializer = GetPaymentModeSerializer(
            payment_modes, many=True)
        data["payment_modes"] = payment_mode_serializer.data
        data["customers"] = customer_serializer.data
        data["discount_schemes"] = discount_scheme_serializer.data
        data["additional_charges"] = additional_charge_serializer.data
        return Response(data, status=status.HTTP_200_OK)

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        if OrganizationSetup.objects.first() is None:
            return Response({'organization setup': 'Please insert Organization setup before making any sale'})
        try:
            sale_details = request.data["sale_details"]
        except KeyError:
            return Response({"key_error": "Provide sale_details"}, status=status.HTTP_400_BAD_REQUEST)
        for sale in sale_details:
            ref_purchase_detail = int(sale["ref_purchase_detail"])

            stock_data = stock.get_remaining_qty_of_purchase(
                ref_purchase_detail)
            qty = Decimal(sale["qty"])
            if stock_data < qty:
                return Response("Given qty ({}) greater than stock qty ({})".format(qty, stock_data),
                                status=status.HTTP_400_BAD_REQUEST)
        request.data["sale_no"] = generate_sale_no(1)
        request.data["sale_type"] = 1

        serializer = SaveSaleMasterSerializer(
            data=request.data, context={"request": request})
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            if request.data["ref_order_master"] is not None:
                order_master = request.data["ref_order_master"]
                order_master_object = OrderMaster.objects.get(id=order_master)
                order_serializer = UpdateCustomerOrderMsterSerializer(
                    order_master_object, data={"status": 2}, partial=True)
                if order_serializer.is_valid(raise_exception=True):
                    order_serializer.save()
                else:
                    return Response(order_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

            # send data to IRD
            sale_master_id = serializer.data['id']
            ird_thread = threading.Thread(target=save_data_to_ird, args=(sale_master_id, request), kwargs={})
            ird_thread.setDaemon = True
            ird_thread.start()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, *args, **kwargs):
        return Response({"method not allowed"}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

def save_data_to_ird(sale_master_id, request):
    api_url = "http://103.1.92.174:9050/api/bill"
    with connection.cursor() as cursor:
        cursor.execute(f"set search_path to {tenant_schema_from_request(request)}")
        sale_master = SaleMaster.objects.get(id=sale_master_id)
        customer = sale_master.customer
        organization_setup = OrganizationSetup.objects.first()
        fiscal_year = str(get_fiscal_year_code_bs()).replace("/", ".")
        customer_name = str(f"{customer.first_name} {customer.middle_name} {customer.last_name}").replace("  ", " ")
        data = {
            "username": "Test_CBMS",
            "password": "test@321",
            "seller_pan": str(organization_setup.pan_no),  # from organization setup
            "buyer_pan": str(customer.pan_vat_no),  # from customer
            "fiscal_year": fiscal_year,  # get_fiscal year function e.g 77.78
            "buyer_name": customer_name,  # from customer first name, middle name, last name
            "invoice_number": sale_master.sale_no,  # Sale no
            "invoice_date": sale_master.created_date_bs,  # created_data_bs of sale
            "total_sale": float(sale_master.sub_total),  # Sub Total of sale
            "taxable_sale_vat": float(sale_master.total_tax),  # Tax amount of sale
            "vat": "0",  # vat of sale
            "excisable_amount": 0,  # zero 0
            "excise": 0,  # zero 0
            "taxable_sale_hst": 0,  # zero 0
            "hst": 0,  # zero 0
            "amount_for_esf": 0,  # zero 0
            "esf": 0,  # zero 0
            "export_sales": 0,  # zero 0
            "tax_exempted_sale": 0,  # zero 0
            "isrealtime": True,
            "datetimeClient": str(timezone.now().strftime("%Y-%m-%d %H:%M:%S"))  # date('Y-m-d h:i:s');

        }
        try:
            response = requests.post(api_url, data=data)

        except:
            ird_update = IRDUploadLog.objects.create(sale_master=sale_master, status_code=504,
                                                     response_message="server time out",
                                                     created_by=sale_master.created_by,
                                                     created_date_bs=sale_master.created_date_ad)
            ird_update.save()
            print("server not Found")
        else:
            if response.status_code == "200":
                ird_update = IRDUploadLog.objects.create(sale_master=sale_master, status_code=response.status_code,
                                                         response_message="Log saved to IRD",
                                                         created_by=sale_master.created_by,
                                                         created_date_bs=sale_master.created_date_ad)
                ird_update.save()
                sale_master.is_real_time_upload = True
                sale_master.synced_with_ird = True
                sale_master.save()
            else:
                ird_update = IRDUploadLog.objects.create(sale_master=sale_master, status_code=response.status_code,
                                                         response_message="Log Not saved to IRD",
                                                         created_by=sale_master.created_by,
                                                         created_date_bs=sale_master.created_date_ad)
                ird_update.save()


class ReturnSaleView(viewsets.ModelViewSet):
    permission_classes = [SaleReturnPermission]
    queryset = SaleMaster.objects.all().select_related("discount_scheme","customer","ref_order_master")
    serializer_class = SaveSaleMasterSerializer

    def list(self, request, **kwargs):
        data = {}
        customer = Customer.objects.filter(active=True)
        customer_serializer = GetCustomerSerializer(customer, many=True)
        discount_scheme = DiscountScheme.objects.filter(active=True)
        discount_scheme_serializer = GetDiscountSchemeSerializer(
            discount_scheme, many=True)
        additional_charge = AdditionalChargeType.objects.filter(active=True)
        additional_charge_serializer = GetAdditionalChargeTypeSerializer(
            additional_charge, many=True)
        payment_modes = PaymentMode.objects.filter(active=True)
        payment_mode_serializer = GetPaymentModeSerializer(
            payment_modes, many=True)
        data["payment_modes"] = payment_mode_serializer.data
        data["customers"] = customer_serializer.data
        data["discount_schemes"] = discount_scheme_serializer.data
        data["additional_charges"] = additional_charge_serializer.data
        return Response(data, status=status.HTTP_200_OK)

    @transaction.atomic
    def create(self, request, *args, **kwargs):

        try:
            sale_details = request.data["sale_details"]
        except KeyError:
            return Response({"key_error": "Provide sale_details"}, status=status.HTTP_400_BAD_REQUEST)
        for sale in sale_details:
            ref_id_sale = int(sale["ref_sale_detail"])
            total_quantity = SaleDetail.objects.values_list(
                "qty", flat=True).get(pk=ref_id_sale)
            return_quantity = sum(SaleDetail.objects.filter(ref_sale_detail=ref_id_sale)
                                  .values_list("qty", flat=True)) + Decimal(sale["qty"])

            if total_quantity < return_quantity:
                return Response("Return items ({}) more than sale items({})".format(return_quantity, total_quantity),
                                status=status.HTTP_400_BAD_REQUEST)

        request.data["sale_no"] = generate_sale_no(2)
        request.data["sale_type"] = 2
        serializer = SaveSaleMasterSerializer(
            data=request.data, context={"request": request})
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, *args, **kwargs):
        return Response({"method not allowed"}, status=status.HTTP_405_METHOD_NOT_ALLOWED)


class SalePrintLogViewset(viewsets.ModelViewSet):
    permission_classes = [SalePrintLogPermission]
    queryset = SalePrintLog.objects.all().select_related("sale_master")
    serializer_class = SalePrintLogSerializer
    filter_backends = (SearchFilter, OrderingFilter, DjangoFilterBackend)
    search_fields = ["sale_master"]
    filter_fields = ["id"]
    ordering_fields = ["id"]
