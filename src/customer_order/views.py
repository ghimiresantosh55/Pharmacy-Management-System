from django.shortcuts import render
from rest_framework import viewsets
from django.db import transaction
from rest_framework.views import APIView
from rest_framework.decorators import action
# filter
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.response import Response
from rest_framework import status
from decimal import Decimal
# jwt
from rest_framework import generics, mixins, filters
from rest_framework.permissions import IsAuthenticated
from django_filters import DateFilter, CharFilter, NumberFilter

# importing Models needed in below classes
from src.item.models import Item
import django_filters
from django_filters import DateFilter
from .models import OrderMaster, OrderDetail
from .serializers import SaveOrderSerializer, OrderMasterSerializer, OrderDetailSerializer,\
     OrderSummaryMasterSerializer
# from .serializers import OrderMasterSerializer, OrderDetailSerializer, OrderListMasterSerializer
from .order_unique_id_generator import generate_customer_order_no
from src.customer.models import Customer
from src.customer.serializers import CustomerSerializer
from src.item.models import Item
from src.item.serializers import ItemSerializer
from src.core_app.models import DiscountScheme, AdditionalChargeType, PaymentMode
from src.core_app.serializers import DiscountSchemeSerializer, AdditionalChargeTypeSerializer,\
    PaymentModeSerializer
# permissions
from .customer_order_permissions import CustomerOrderSavePermission, CustomerOrderViewPermission,\
    CustomerOrderUpdatePermission, CustomerOrderCancelPermission
from src.advance_deposit.serializers import SaveAdvancedDepositSerializer


class RangeFilterForOrderMaster(django_filters.FilterSet):
    start_date_created_date_ad = DateFilter(field_name="created_date_ad__date", lookup_expr='gte')
    end_date_created_date_ad = DateFilter(field_name="created_date_ad__date", lookup_expr='lte')

    class Meta:
        model = OrderMaster
        fields = "__all__"


class OrderMasterViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [CustomerOrderViewPermission]
    queryset = OrderMaster.objects.all().select_related("customer","discount_scheme")
    serializer_class = OrderMasterSerializer
    filter_class = RangeFilterForOrderMaster
    filter_backends = [SearchFilter, OrderingFilter, DjangoFilterBackend]
    ordering_fields = ['id', 'order_no', 'delivery_date-ad', 'created_date_ad']
    search_fields = ['order_no', 'customer__first_name', 'customer__last_name']


class OrderDetailViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [CustomerOrderViewPermission]
    queryset = OrderDetail.objects.all().select_related("order","item")
    serializer_class = OrderDetailSerializer
    filter_backends = [SearchFilter, OrderingFilter, DjangoFilterBackend]
    common_filter = '__all__'
    search_filter = ['item', 'order']
    search_fields = search_filter
    ordering_fields = common_filter


class OrderSummaryViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [CustomerOrderViewPermission]
    queryset = OrderMaster.objects.all().select_related("customer","discount_scheme")
    serializer_class = OrderSummaryMasterSerializer
    filter_backends = (SearchFilter, OrderingFilter, DjangoFilterBackend)
    common_filter = "__all__"
    search_filter = "__all__"
    search_fields = search_filter
    ordering_fields = common_filter
    filterset_fields = common_filter


class SaveOrderView(viewsets.ModelViewSet):
    queryset = OrderMaster.objects.all().select_related("customer","discount_scheme")
    serializer_class = SaveOrderSerializer

    def get_permissions(self):
        if self.action == 'create':
            self.permission_classes = [CustomerOrderSavePermission]
        elif self.action == 'partial_update':
            self.permission_classes = [CustomerOrderUpdatePermission]
        elif self.action == 'cancel_order' or self.action == 'cancel_single_order':
            self.permission_classes = [CustomerOrderCancelPermission]

        elif self.action == 'list' or self.action == 'retrieve':
            # for GET operation user must have save customer order Permission
            self.permission_classes = [CustomerOrderSavePermission]
        return super(self.__class__, self).get_permissions()

    def list(self, request):
        items_data = {}
        customer_data = {}
        discount_scheme_data = {}
        additional_charge_data = {}
        payment_mode_data = {}
        items_query = Item.objects.filter(active=True)
        serializer_food = ItemSerializer(items_query, many=True)
        items_data['items'] = serializer_food.data

        customer_query = Customer.objects.filter(active=True)
        serializer_customer = CustomerSerializer(customer_query, many=True)
        customer_data['customers'] = serializer_customer.data
        items_data.update(customer_data)

        additional_charge_query = AdditionalChargeType.objects.filter(active=True)
        additional_charge_serializer = AdditionalChargeTypeSerializer(additional_charge_query, many=True)
        additional_charge_data['additional_charges'] = additional_charge_serializer.data
        items_data.update(additional_charge_data)

        payment_mode_query = PaymentMode.objects.filter(active=True)
        serializer_payment_mode = PaymentModeSerializer(payment_mode_query, many=True)
        payment_mode_data['payment_modes'] = serializer_payment_mode.data
        items_data.update(payment_mode_data)

        discount_scheme_query = DiscountScheme.objects.filter(active=True)
        serializer_discount_scheme = DiscountSchemeSerializer(discount_scheme_query, many=True)
        discount_scheme_data['discount_schemes'] = serializer_discount_scheme.data
        items_data.update(discount_scheme_data)
        return Response(items_data)

    @transaction.atomic
    def create(self, request):

        request.data['order_no'] = generate_customer_order_no()
        request.data['status'] = 1

        # validation for date time fields with blank values
        try:
            request.data['delivery_date_ad']
            if request.data['delivery_date_ad'] == "":
                request.data['delivery_date_ad'] = None
        except KeyError:
            return Response({'key_error': 'please provide delivery_date_ad and delivery_date_ad Keys'},
                            status=status.HTTP_400_BAD_REQUEST)
        advanced_deposit = {}
        # Accept Advanced Deposit
        if 'advanced_deposit' in request.data:
            advanced_deposit = request.data['advanced_deposit']


        # inserting order master and detail
        order_serializer = SaveOrderSerializer(data=request.data, context={'request': request})
        if order_serializer.is_valid(raise_exception=True):
            order_serializer.save()
            data = order_serializer.data
            order_master_id = data["id"]

            # save advanced deposit
            advanced_deposit_data = {}
            if advanced_deposit:
                if Decimal(request.data['grand_total']) < Decimal(advanced_deposit['amount']):
                    return Response("grand_total {} less than advanced deposit {}".format(request.data['grand_total'],
                                                                                          advanced_deposit['amount']),
                                    status=status.HTTP_400_BAD_REQUEST)
                # advanced_deposit['deposit_no'] = generate_advanced_deposit_no()
                advanced_deposit['order_master'] = order_master_id
                advanced_deposit_serializer = SaveAdvancedDepositSerializer(data=advanced_deposit,
                                                                            context={'request': request})
                if advanced_deposit_serializer.is_valid(raise_exception=True):
                    advanced_deposit_serializer.save()
                    advanced_deposit_data = advanced_deposit_serializer.data
                else:
                    return Response(advanced_deposit_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            data['advanced_deposit'] = advanced_deposit_data
            return Response(data, status=status.HTTP_201_CREATED)
        else:
            return Response(order_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get_order_master(self, pk):
        return OrderMaster.objects.get(id=pk)

    def get_order_detail(self, pk):
        return OrderDetail.objects.get(pk=pk)

    # partial_update is used to  add item to already saved customer order
    @transaction.atomic
    def partial_update(self, request, pk):
        order_master = self.get_order_master(pk)
        # validation for date time fields with blank values
        try:
            request.data['delivery_date_ad']
            if request.data['delivery_date_ad'] == "":
                request.data['delivery_date_ad'] = None
        except KeyError:
            return Response({'key_error': 'please provide delivery_date_ad and delivery_date_ad Keys'},
                            status=status.HTTP_400_BAD_REQUEST)
        # check order exist or not
        if not order_master:
            return Response(
                'Order does not exist', status=status.HTTP_400_BAD_REQUEST
            )
        # check order is CLEARED or CANCELLED
        if order_master.status == 2:
            return Response(
                'order is already BILLED', status=status.HTTP_400_BAD_REQUEST
            )
        elif order_master.status == 3:
            return Response(
                'order is already CANCELLED',
                status=status.HTTP_400_BAD_REQUEST
            )

        # inserting order master and detail
        order_serializer = SaveOrderSerializer(
            order_master, data=request.data, partial=True, context={'request': request}
        )
        if order_serializer.is_valid(raise_exception=True):
            order_serializer.save()
            return Response(
                order_serializer.data, status=status.HTTP_201_CREATED
            )
        else:
            return Response(
                order_serializer.errors, status=status.HTTP_400_BAD_REQUEST
            )

    @transaction.atomic
    @action(detail=True, methods=['PATCH'])
    def cancel_order(self, request, pk=None):
        customer_order_master = self.get_order_master(pk)

        # check order exist or not
        if not customer_order_master:
            return Response('Order does not exist', status=status.HTTP_400_BAD_REQUEST)
        # check order is CLEARED or CANCELLED
        if customer_order_master.status == 2:
            return Response('order is already BILLED', status=status.HTTP_400_BAD_REQUEST)
        elif customer_order_master.status == 3:
            return Response('order is already CANCELLED', status=status.HTTP_400_BAD_REQUEST)

        # inserting status = 3 (CANCELLED) in  order master
        order_master_updated_data = {
            'status': 3,
            'total_discount': Decimal('0.00'),
            'total_tax': Decimal('0.00'),
            'sub_total': Decimal('0.00'),
            'total_discountable_amount': Decimal('0.00'),
            'total_taxable_amount': Decimal('0.00'),
            'total_non_taxable_amount': Decimal('0.00'),
            'grand_total': Decimal('0.00')

        }

        order_master_serializer = OrderMasterSerializer(customer_order_master,
                                                        data=order_master_updated_data, partial=True)

        # inserting cancelled = True in order Detail

        order_detail_id_list = OrderDetail.objects.filter(order=pk).values_list('id', flat=True)
        for order_id in order_detail_id_list:
            order_detail_object = OrderDetail.objects.get(id=order_id)
            order_detail_object.cancelled = True
            order_detail_object.save()
        order_details = OrderDetail.objects.filter(order=pk)
        order_details_serializer = OrderDetailSerializer(order_details, many=True)
        order_detail_instances = order_details_serializer.data
        if order_master_serializer.is_valid(raise_exception=True):
            order_master_serializer.save()
            data = order_master_serializer.data
            data['order_details'] = order_detail_instances
            return Response(data, status=status.HTTP_201_CREATED)
        else:
            return Response(order_master_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @transaction.atomic
    @action(detail=True, methods=['PATCH'])
    def cancel_single_order(self, request, pk=None):
        customer_order_detail = self.get_order_detail(pk)
        order_master_id = customer_order_detail.order.id
        order_master_instance = OrderMaster.objects.get(id=order_master_id)

        if order_master_instance.status == 3 or order_master_instance.status == 2:
            return Response('Order master for current order is already cancelled',
                            status=status.HTTP_400_BAD_REQUEST)
        # check order detail exist or not
        if not customer_order_detail:
            return Response('Order detail does not exist', status=status.HTTP_400_BAD_REQUEST)
        # check if already cancelled
        if customer_order_detail.cancelled is True:
            return Response('Order detail is already cancelled', status=status.HTTP_400_BAD_REQUEST)

        # inserting order master and detail
        order_detail_serializer = OrderDetailSerializer(customer_order_detail, data={'cancelled': True}, partial=True)
        if order_detail_serializer.is_valid(raise_exception=True):
            order_detail_serializer.save()
            uncancelled_orders = OrderDetail.objects.filter(order=order_master_id, cancelled=False)

            """____________________ Calculate and Update order master_______________________"""
            quantize_places = Decimal(10) ** -2
            # initialize variables to check
            sub_total = Decimal('0.00')
            total_discount = Decimal('0.00')
            total_discountable_amount = Decimal('0.00')
            total_taxable_amount = Decimal('0.00')
            total_nontaxable_amount = Decimal('0.00')
            total_tax = Decimal('0.00')
            grand_total = Decimal('0.00')
            for orders in uncancelled_orders:
                sub_total += orders.gross_amount
                if orders.discountable is True:
                    total_discountable_amount += orders.gross_amount
                    total_discount += orders.discount_amount
                probable_taxable_amount = orders.gross_amount - orders.discount_amount
                if orders.taxable is True:
                    total_taxable_amount += probable_taxable_amount
                    total_tax += orders.tax_amount
                else:
                    total_nontaxable_amount += probable_taxable_amount
                grand_total += orders.net_amount

            sub_total = sub_total.quantize(quantize_places)
            total_discount = total_discount.quantize(quantize_places)
            total_discountable_amount = total_discountable_amount.quantize(quantize_places)
            total_tax = total_tax.quantize(quantize_places)
            total_taxable_amount = total_taxable_amount.quantize(quantize_places)
            total_nontaxable_amount = total_nontaxable_amount.quantize(quantize_places)
            grand_total = grand_total.quantize(quantize_places)
            order_master_updated_data = {
                'total_discount': total_discount,
                'total_tax': total_tax,
                'sub_total': sub_total,
                'total_discountable_amount': total_discountable_amount,
                'total_taxable_amount': total_taxable_amount,
                'total_non_taxable_amount': total_nontaxable_amount,
                'grand_total': grand_total

            }
            order_master_serializer = OrderMasterSerializer(order_master_instance,
                                                            data=order_master_updated_data, partial=True)
            if order_master_serializer.is_valid(raise_exception=True):
                order_master_serializer.save()
                return Response(order_detail_serializer.data, status=status.HTTP_201_CREATED)
            else:
                return Response(order_master_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        else:
            return Response(order_detail_serializer.errors, status=status.HTTP_400_BAD_REQUEST)



