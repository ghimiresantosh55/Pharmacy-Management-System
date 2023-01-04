from rest_framework import viewsets
from rest_framework.response import Response
from django.db import transaction
from rest_framework.decorators import action
from rest_framework import status
from decimal import Decimal

# filter
import django_filters
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter, SearchFilter
from django_filters import DateFromToRangeFilter

# importing of models
from src.sale.models import SaleMaster
from src.customer.models import Customer
from .models import CreditClearance, CreditPaymentDetail

# importing of serializers
from .serializers import CreditPaymentMasterSerializer, CreditPaymentDetailSerializer, \
    CreditPaymentDetailSerializer, SaleCreditSerializer
from .serializers import SaveCreditClearanceSerializer
from src.customer.serializers import CustomerSerializer

# functions
from .reciept_unique_id_generator import get_receipt_no
from src.custom_lib.functions.credit_management import get_sale_credit_detail

# custom permissions
from .credit_management_permissions import CreditManagementSavePermission, CreditManagementViewPermission


# Create your views here.
class RangeFilterForCreditClearance(django_filters.FilterSet):
    # for date range filter
    date = DateFromToRangeFilter(field_name="created_date_ad")

    class Meta:
        model = CreditClearance
        fields = '__all__'


class CreditClearanceViewSet(viewsets.ReadOnlyModelViewSet):
    # permissions
    permission_classes = [CreditManagementViewPermission]
    queryset = CreditClearance.objects.all().select_related("sale_master","ref_credit_clearance")
    serializer_class = CreditPaymentMasterSerializer
    filter_class = RangeFilterForCreditClearance
    filter_backends = (SearchFilter, OrderingFilter, DjangoFilterBackend)
    common_filter = "__all__"
    search_filter = "__all__"
    search_fields = ['id']
    ordering_fields = ['id']


class CreditPaymentDetailViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [CreditManagementViewPermission]
    queryset = CreditPaymentDetail.objects.all().select_related("credit_clearance", "payment_mode")
    serializer_class = CreditPaymentDetailSerializer
    filter_backends = (SearchFilter, OrderingFilter, DjangoFilterBackend)
    filter_fields = ['credit_clearance__sale_master', 'id']
    ordering_fields = ['credit_clearance', 'id']


class CreditClearanceSummary(viewsets.ReadOnlyModelViewSet):
    permission_classes = [CreditManagementViewPermission]
    queryset = CreditClearance.objects.all().select_related("sale_master","ref_credit_clearance")
    serializer_class = SaveCreditClearanceSerializer
    filter_class = RangeFilterForCreditClearance
    filter_backends = (SearchFilter, OrderingFilter, DjangoFilterBackend)


class FilterForCreditReportSaleMaster(django_filters.FilterSet):
    date = django_filters.DateFromToRangeFilter(field_name="created_date_ad")

    class Meta:
        model = SaleMaster
        fields = ['id', 'sale_no', 'created_by', 'created_date_ad', 'sale_type', 'customer']


class GetCreditInvoice(viewsets.ReadOnlyModelViewSet):
    permission_classes = [CreditManagementViewPermission]
    queryset = SaleMaster.objects.filter(pay_type=2).select_related("discount_scheme","customer","ref_order_master")
    serializer_class = SaleCreditSerializer
    filter_class = FilterForCreditReportSaleMaster
    filter_backends = (SearchFilter, OrderingFilter, DjangoFilterBackend)
    search_fields = ['sale_no']
    ordering_fields = ['id', 'sale_id', 'created_date_ad']

    @action(detail=False, methods=['GET'])
    def customers(self, request):
        data = get_sale_credit_detail()
        id_list = data.values_list('customer', flat=True)
        # converting a list into set for removing repeated values
        customer_id_list = set(id_list)
        customers = Customer.objects.filter(id__in=customer_id_list)
        customers_serializer = CustomerSerializer(customers, many=True)
        return Response(customers_serializer.data, status=status.HTTP_200_OK)


class SaveCreditClearanceViewSet(viewsets.ModelViewSet):
    permission_classes = [CreditManagementSavePermission]
    queryset = CreditClearance.objects.all().select_related("sale_master","ref_credit_clearance")
    serializer_class = SaveCreditClearanceSerializer

    @transaction.atomic
    def create(self, request):
        quantize_places = Decimal(10) ** -2

        try:
            customer_id = request.data.pop('customer_id')
            sale_master_id_list = request.data.pop('sale_masters')
            remarks = request.data.pop('remarks')
            payment_details = request.data.pop('payment_details')
        except KeyError:
            return Response("provide customer_id, sale_master, remarks and payment_details keys",
                            status=status.HTTP_400_BAD_REQUEST)

        # calculating total amount
        total_amount = Decimal('0.00')
        for detail in payment_details:
            amount = Decimal(str(detail['amount']))
            total_amount = total_amount + amount

        total_due_amount = Decimal('0.00')
        for sale_id in sale_master_id_list:
            # Get due_amount of the given customer
            data = get_sale_credit_detail(customer=customer_id, sale_master=sale_id)
            # print(data, "this")
            if data[0]['due_amount'] <= 0:
                return Response('This invoice id ({}) has zero due_amount please unselect it'.format(sale_id))
            total_due_amount += data[0]['due_amount']

        total_due_amount = total_due_amount.quantize(quantize_places)
        total_amount = total_amount.quantize(quantize_places)

        if total_amount > total_due_amount:
            return Response("Paying amount {} greater than Due amount {}".format(total_amount, total_due_amount),
                            status=status.HTTP_400_BAD_REQUEST)
        response_data = []
        for sale_id in sale_master_id_list:

            # check if payment_details have any amount left
            total_sum = Decimal('0.00')
            for detail in payment_details:
                total_sum = total_sum + Decimal(str(detail['amount']))
            if total_sum <= 0:
                break

            # Get due_amount of the given customer
            data = get_sale_credit_detail(customer=customer_id, sale_master=sale_id)
            due_amount = data[0]['due_amount']
            credit_payment_details = []

            # calculate credit_payment_details
            for detail in payment_details:
                if Decimal(detail['amount']) > Decimal(0):
                    if Decimal(due_amount) <= Decimal(detail['amount']):
                        credit_payment_detail = {
                            "payment_mode": detail['payment_mode'],
                            "amount": due_amount,
                            "remarks": detail['remarks']
                        }
                        detail['amount'] = detail['amount'] - due_amount
                        due_amount = 0
                        credit_payment_details.append(credit_payment_detail)
                        break
                    else:
                        credit_payment_detail = {
                            "payment_mode": detail['payment_mode'],
                            "amount": detail['amount'],
                            "remarks": detail['remarks']
                        }
                        detail['amount'] = 0
                        due_amount = due_amount - detail['amount']
                        credit_payment_details.append(credit_payment_detail)
            # Calculate Total Amount for credit payment master
            total_payment = Decimal('0.00')
            for payment in credit_payment_details:
                total_payment = total_payment + Decimal(str(payment['amount']))

            # 1. save Credit payment Master,
            request.data['payment_type'] = 1
            request.data['sale_master'] = sale_id
            # generate unique receipt no for the CreditClearance
            request.data['receipt_no'] = get_receipt_no()
            request.data['total_amount'] = total_payment
            request.data['remarks'] = remarks

            # # 2. save Credit Payment Detail
            # credit_clearance_detail_data = [{
            #
            #     'amount': total_payment,
            # }]
            # request.data['credit_clearance_details'] = credit_clearance_detail_data

            # 3. save Credit Payment Model Detail
            request.data['credit_payment_details'] = credit_payment_details

            credit_master_serializer = SaveCreditClearanceSerializer(data=request.data,
                                                                     context={'request': request})

            if credit_master_serializer.is_valid(raise_exception=True):
                credit_master_serializer.save()
                response_data.append(credit_master_serializer.data)
            else:
                return Response(
                    credit_master_serializer.errors, status=status.HTTP_400_BAD_REQUEST
                )
        return Response(response_data, status=status.HTTP_201_CREATED)

    def update(self, request, pk=None):
        return Response("method not allowed")

    def partial_update(self, request, pk=None):
        return Response("Method not allowed")
