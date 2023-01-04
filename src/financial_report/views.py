from django.conf.urls import url
import django_filters
from rest_framework import  viewsets, status
from django.core import serializers
from django.db import connection

from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q
from rest_framework.decorators import permission_classes
from .CustomSerializer import BasicPartyPaymentSummaryReportSerializer
from rest_framework.filters import OrderingFilter, SearchFilter
# from core_app.models import FiscalSessionAD
from src.party_payment.models import BasicPartyPayment, BasicPartyPaymentDetail
from src.purchase.serializers import PurchaseMasterSerializer
from src.purchase.models import PurchaseMaster, PurchaseDetail, PurchasePaymentDetail, PurchaseAdditionalCharge
from src.purchase.models import PurchaseOrderMaster, PurchaseOrderDetail
from src.sale.models import SaleMaster, SaleDetail, SalePaymentDetail
from src.customer_order.models import OrderMaster, OrderDetail
from src.core_app.models import FiscalSessionAD,FiscalSessionBS

from src.supplier.models import Supplier
from .serializers import SummaryPurchaseOrderMasterSerializer, ReportPurchaseOrderMasterSerializer, ItemwisePurchaseReportSerializer,\
    ReportPurchaseOrderDetailSerializer, GetFiscalSessionADSerializer, GetSupplierSerializer, GetFiscalSessionBSSerializer
from .serializers import ReportPurchaseMasterSerializer, ReportPurchaseDetailSerializer, \
    ReportPurchasePaymentDetailSerializer, ReportBasicPartyPaymentSerializer, \
    ReportPurchaseAdditionalChargeSerializer, SummaryPurchaseMasterSerializer
from .serializers import ReportSaleDetailSerializer, ReportSaleMasterSerializer, ReportSalePaymentDetailSerializer, \
    SummarySaleMasterSerializer, SaleCreditReportSerializer, StockAdjustmentSummarySerializer, SummaryBasicPartyPaymentSerializer
from .serializers import CustomerOrderSummarySerializer, CustomerOrderMasterReportSerializer, \
    CustomerOrderDetailReportSerializer, ReportBasicPartyPaymentDetailSerializer
from rest_framework.decorators import action
from rest_framework.response import Response
from .financial_report_permissions import PurchaseOrderReportPermission, PurchaseReportPermission, BasicPartyPaymentDetailReportPermission,\
    SaleReportPermission, SaleCreditReportPermission, CustomerOrderReportPermission, StockAdjustmentReportPermission, BasicPartyPaymentReportPermission

"""_______________________________ views for purchase order__________________________________________________________"""


class FilterForPurchaseOrderMaster(django_filters.FilterSet):
    date = django_filters.DateFromToRangeFilter(field_name="created_date_ad")

    class Meta:
        model = PurchaseOrderMaster
        fields = ['id', 'order_no', 'created_date_ad', 'supplier',
                  'created_by', 'discount_scheme', 'order_type', 'ref_purchase_order']


class FilterForPurchaseOrderDetail(django_filters.FilterSet):
    date = django_filters.DateFromToRangeFilter(field_name="created_date_ad")

    class Meta:
        model = PurchaseOrderDetail
        fields = ['id', 'created_by', 'created_date_ad', 'item', 'item_category', 'purchase_order',
                  'taxable', 'discountable', 'ref_purchase_order_detail']


class PurchaseOrderMasterReportViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [PurchaseOrderReportPermission]
    queryset = PurchaseOrderMaster.objects.all()
    serializer_class = ReportPurchaseOrderMasterSerializer
    filter_class = FilterForPurchaseOrderMaster
    filter_backends = (SearchFilter, OrderingFilter, DjangoFilterBackend)
    search_fields = ['order_no', 'supplier__first_name', 'supplier__last_name',
                     'created_by__user_name', 'discount_scheme__name', 'order_type', 'remarks']
    ordering_fields = ['id']


class PurchaseOrderDetailReportViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [PurchaseOrderReportPermission]
    queryset = PurchaseOrderDetail.objects.all()
    serializer_class = ReportPurchaseOrderDetailSerializer
    filter_class = FilterForPurchaseOrderDetail
    filter_backends = (SearchFilter, OrderingFilter, DjangoFilterBackend)
    search_fields = ['id']
    ordering_fields = ['id']


class PurchaseOrderSummaryReportViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [PurchaseOrderReportPermission]
    queryset = PurchaseOrderMaster.objects.all()
    serializer_class = SummaryPurchaseOrderMasterSerializer
    filter_class = FilterForPurchaseOrderMaster
    filter_backends = (SearchFilter, OrderingFilter, DjangoFilterBackend)
    search_fields = ['order_no', 'supplier__first_name', 'supplier__last_name',
                     'created_by__user_name', 'discount_scheme__name', 'order_type', 'remarks']
    ordering_fields = ['id']


"""_______________________________ views for purchase order__________________________________________________________"""


class FilterForPurchaseMaster(django_filters.FilterSet):
    date = django_filters.DateFromToRangeFilter(field_name="created_date_ad")
    # item = django_filters.NumberFilter(field_name="purchase_details__item")

    class Meta:
        model = PurchaseMaster
        fields = ['id', 'purchase_no', 'created_by', 'created_date_ad', 'bill_date_ad', 'due_date_ad', 'purchase_type',
                  'supplier', 'purchase_details__item',
                  'discount_scheme', 'ref_purchase', 'ref_purchase_order']


class FilterForPurchaseDetail(django_filters.FilterSet):
    date = django_filters.DateFromToRangeFilter(field_name="created_date_ad")

    class Meta:
        model = PurchaseDetail
        fields = ['id', 'created_by', 'created_date_ad', 'item', 'item_category', 
                  'taxable', 'discountable', 'ref_purchase_order_detail', 'ref_purchase_detail']


class PurchaseMasterReportViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [PurchaseReportPermission]
    queryset = PurchaseMaster.objects.all()
    serializer_class = ReportPurchaseMasterSerializer
    filter_class = FilterForPurchaseMaster
    filter_backends = (SearchFilter, OrderingFilter, DjangoFilterBackend)
    search_fields = ['purchase_no', 'supplier__first_name', 'supplier__last_name',
                     'created_by__user_name', 'discount_scheme__name', 'purchase_type', 'chalan_no', 'remarks']
    ordering_fields = ['id']


class PurchaseDetailReportViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [PurchaseReportPermission]
    queryset = PurchaseDetail.objects.all()
    serializer_class = ReportPurchaseDetailSerializer
    filter_class =  FilterForPurchaseDetail
    filter_class = FilterForPurchaseDetail
    filter_backends = (SearchFilter, OrderingFilter, DjangoFilterBackend)
    search_fields = ['id', 'item__name', 'item_category__name']
    ordering_fields = ['id']


# itemwise purchase report
class ItemwisePurchaseReportViewset(viewsets.ReadOnlyModelViewSet):
    queryset = PurchaseDetail.objects.all()
    serializer_class = ItemwisePurchaseReportSerializer
    filter_class =  FilterForPurchaseDetail
    filter_backends = (SearchFilter, OrderingFilter, DjangoFilterBackend)
    search_fields = ['id', 'item__name']
    ordering_fields = ['id']


class PurchasePaymentDetailReportViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [PurchaseReportPermission]
    queryset = PurchasePaymentDetail.objects.all()
    serializer_class = ReportPurchasePaymentDetailSerializer
    filter_backends = (SearchFilter, OrderingFilter, DjangoFilterBackend)
    filter_fields = ['id', 'purchase_master', 'payment_mode']
    search_fields = ['id']
    ordering_fields = ['id']


class PurchaseAdditionalChargeReportViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [PurchaseReportPermission]
    queryset = PurchaseAdditionalCharge.objects.all()
    serializer_class = ReportPurchaseAdditionalChargeSerializer
    filter_backends = (SearchFilter, OrderingFilter, DjangoFilterBackend)
    filter_fields = ['id', 'purchase_master', 'charge_type']
    search_fields = ['id']
    ordering_fields = ['id']


class PurchaseSummaryReportViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [PurchaseReportPermission]
    queryset = PurchaseMaster.objects.all()
    serializer_class = SummaryPurchaseMasterSerializer
    filter_class = FilterForPurchaseMaster
    filter_backends = (SearchFilter, OrderingFilter, DjangoFilterBackend)
    search_fields = ['purchase_no', 'supplier__first_name', 'supplier__last_name',
                     'created_by__user_name', 'discount_scheme__name', 'purchase_type', 'chalan_no', 'remarks']
    ordering_fields = ['id']


"""_______________________________ views for sale __________________________________________________________"""


class FilterForSaleMaster(django_filters.FilterSet):
    date = django_filters.DateFromToRangeFilter(field_name="created_date_ad")

    class Meta:
        model = SaleMaster
        fields = ['id', 'sale_no', 'created_by', 'created_date_ad', 'sale_type', 'customer',
                  'discount_scheme', 'ref_sale_master']


class FilterForSaleDetail(django_filters.FilterSet):
    date = django_filters.DateFromToRangeFilter(field_name="created_date_ad")

    class Meta:
        model = SaleDetail
        fields = ['id', 'created_by', 'created_date_ad', 'item', 'item_category', 'sale_master',
                  'taxable', 'discountable', 'ref_sale_detail']


class SaleMasterReportViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [SaleReportPermission]
    queryset = SaleMaster.objects.all()
    serializer_class = ReportSaleMasterSerializer
    filter_class = FilterForSaleMaster
    filter_backends = (SearchFilter, OrderingFilter, DjangoFilterBackend)
    search_fields = ['sale_no', 'customer__first_name', 'customer__last_name',
                     'created_by__user_name', 'discount_scheme__name', 'sale_type', 'ref_by', 'remarks']
    ordering_fields = ['id']


class SaleDetailReportViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [SaleReportPermission]
    queryset = SaleDetail.objects.all()
    serializer_class = ReportSaleDetailSerializer
    filter_class = FilterForSaleDetail
    filter_backends = (SearchFilter, OrderingFilter, DjangoFilterBackend)
    search_fields = ['id', 'item__name', 'item_category__name']
    ordering_fields = ['id']


class SalePaymentDetailReportViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [SaleReportPermission]
    queryset = SalePaymentDetail.objects.all()
    serializer_class = ReportSalePaymentDetailSerializer
    filter_backends = (SearchFilter, OrderingFilter, DjangoFilterBackend)
    filter_fields = ['id', 'sale_master', 'payment_mode']
    search_fields = ['id']
    ordering_fields = ['id']


class SaleSummaryReportViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [SaleReportPermission]
    queryset = SaleMaster.objects.all()
    serializer_class = SummarySaleMasterSerializer
    filter_class = FilterForSaleMaster
    filter_backends = (SearchFilter, OrderingFilter, DjangoFilterBackend)
    search_fields = ['sale_no', 'customer__first_name', 'customer__last_name',
                     'created_by__user_name', 'discount_scheme__name', 'sale_type', 'ref_by', 'remarks']
    ordering_fields = ['id']


"""________________________ views for credit report __________________________________________"""


class FilterForCreditSaleMaster(django_filters.FilterSet):
    date = django_filters.DateFromToRangeFilter(field_name="created_date_ad")

    class Meta:
        model = SaleMaster
        fields = ['id', 'sale_no', 'created_by', 'created_date_ad', 'sale_type', 'customer']


class SaleCreditReportViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [SaleCreditReportPermission]
    queryset = SaleMaster.objects.filter(pay_type=2)
    serializer_class = SaleCreditReportSerializer
    filter_class = FilterForCreditSaleMaster
    filter_backends = (SearchFilter, OrderingFilter, DjangoFilterBackend)
    search_fields = ['sale_no']
    ordering_fields = ['sale_id', 'created_date_ad']


"""___________________________________ views for customer orders _____________________________________________"""


class FilterForCustomerOrderMaster(django_filters.FilterSet):
    date = django_filters.DateFromToRangeFilter(field_name="created_date_ad")

    class Meta:
        model = OrderMaster
        fields = ['id', 'customer', 'discount_scheme', 'created_date_ad', 'status', 'created_by']


class FilterForCustomerOrderDetail(django_filters.FilterSet):
    date = django_filters.DateFromToRangeFilter(field_name="created_date_ad")

    class Meta:
        model = OrderDetail
        fields = ['order', 'id', 'item', 'created_by']


class CustomerOrderSummaryViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [CustomerOrderReportPermission]
    queryset = OrderMaster.objects.all()
    serializer_class = CustomerOrderSummarySerializer
    filter_class = FilterForCustomerOrderMaster
    filter_backends = (SearchFilter, OrderingFilter, DjangoFilterBackend)
    search_fields = ['order_no']
    ordering_fields = ['id', 'created_date_ad', 'status']


class CustomerOrderMasterReportViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [CustomerOrderReportPermission]
    queryset = OrderMaster.objects.all()
    serializer_class = CustomerOrderMasterReportSerializer
    filter_class = FilterForCustomerOrderMaster
    filter_backends = (SearchFilter, OrderingFilter, DjangoFilterBackend)
    search_fields = ['order_no']
    ordering_fields = ['id', 'created_date_ad', 'status']


class CustomerOrderDetailReportViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [CustomerOrderReportPermission]
    queryset = OrderDetail.objects.all()
    serializer_class = CustomerOrderDetailReportSerializer
    filter_class = FilterForCustomerOrderDetail
    filter_backends = (SearchFilter, OrderingFilter, DjangoFilterBackend)
    search_fields = ['item']
    ordering_fields = ['id', 'created_date_ad', 'order']


class FilterForStockAdjustment(django_filters.FilterSet):
    date = django_filters.DateFromToRangeFilter(field_name="created_date_ad")

    class Meta:
        model = PurchaseMaster
        fields = ['id', 'created_by', 'date', 'purchase_type', 'supplier']


class StockAdjustmentReportViewSet(viewsets.ReadOnlyModelViewSet):
    # permission_classes = [PurchaseReportPermission]
    queryset = PurchaseMaster.objects.filter(Q(purchase_type=4) | Q(purchase_type=5))
    serializer_class = PurchaseMasterSerializer
    filter_class = FilterForStockAdjustment
    filter_backends = (SearchFilter, OrderingFilter, DjangoFilterBackend)
    search_fields = ['purchase_no', 'supplier__first_name', 'supplier__last_name',
                     'created_by__user_name','purchase_type']
    ordering_fields = ['id']


class StockAdjustmentSummaryReportViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [StockAdjustmentReportPermission]
    queryset = PurchaseMaster.objects.filter(Q(purchase_type=4) | Q(purchase_type=5))
    serializer_class = StockAdjustmentSummarySerializer
    filter_class = FilterForStockAdjustment


class FilterForBasicPartyPayment(django_filters.FilterSet):
    date = django_filters.DateFromToRangeFilter(field_name="created_date_ad")
    
    class Meta:
        model = BasicPartyPayment
        fields = ['id', 'supplier', 'created_by', 'created_date_ad', 'payment_type', 'amount',
                  'receipt_no', 'payment_date_ad','payment_date_bs','fiscal_session_ad','fiscal_session_bs']

class BasicPartyPaymentReportViewset(viewsets.ReadOnlyModelViewSet):
    permission_classes = [BasicPartyPaymentReportPermission]
    queryset = BasicPartyPayment.objects.all()
    serializer_class = ReportBasicPartyPaymentSerializer
    filter_class = FilterForBasicPartyPayment
    filter_backends = (SearchFilter, OrderingFilter, DjangoFilterBackend)
    search_fields = ['supplier', 'supplier__first_name','amount','recipt_no',
                     'created_by__user_name', 'payment_date_ad','payment_date_bs', 'fiscal_session_ad','fiscal_session_bs','payment_type', 'remarks']
    ordering_fields = ['id','created_date_ad','fiscal_session_ad','fiscal_session_bs']


class FilterForBasicPartyPaymentSummaryReport(django_filters.FilterSet):
    date = django_filters.DateFromToRangeFilter(field_name="created_date_ad")
    supplier= django_filters.CharFilter(field_name="basic_party_payment__supplier__id")
 
    class Meta:
        model = BasicPartyPaymentDetail
        fields = ['id', 'created_by', 'supplier','created_date_ad', 'payment_mode', 'amount']  


class BasicPartyPaymentSummaryReportViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [BasicPartyPaymentDetailReportPermission]
    queryset = BasicPartyPaymentDetail.objects.all()
    serializer_class = ReportBasicPartyPaymentDetailSerializer
    filter_class = FilterForBasicPartyPaymentSummaryReport
    filter_backends = (SearchFilter, OrderingFilter, DjangoFilterBackend)


class BasicPartyPaymentDetailReportViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [BasicPartyPaymentReportPermission]
    queryset =  BasicPartyPayment.objects.all()
    serializer_class = SummaryBasicPartyPaymentSerializer
    filter_class =  FilterForBasicPartyPayment
    filter_backends = (SearchFilter, OrderingFilter, DjangoFilterBackend)
    search_fields = ['supplier__first_name', 'supplier__last_name',
                     'created_by__user_name', 'payment_type', 'receipt_no', 'payment_date_ad','payment_date_bs','fiscal_session_ad','fiscal_session_bs']
    ordering_fields = ['id']

    @action(url_path="get-data", detail=False)
    def get_data(self, request):
    # def list(self, request, **kwargs):
        data = {}
        fiscal_session_ad = FiscalSessionAD.objects.all()
        fiscal_session_ad_serializer = GetFiscalSessionADSerializer(fiscal_session_ad, many=True)
        fiscal_session_bs = FiscalSessionBS.objects.all()
        fiscal_session_bs_serializer = GetFiscalSessionBSSerializer(fiscal_session_bs, many=True)
        suppliers = Supplier.objects.filter(active=True)
        supplier_serializer = GetSupplierSerializer(suppliers, many=True)
        data['fiscal_session_ad'] =  fiscal_session_ad_serializer.data
        data['fiscal_session_bs'] = fiscal_session_bs_serializer.data
        data['suppliers'] = supplier_serializer.data
        return Response(data, status=status.HTTP_200_OK)


    @action(url_path="summary", detail=False)
    def summary(self, request):    
        if request.GET.get("supplier", None) is None:
            summary_queryset = BasicPartyPayment.objects.raw(f'''select id, first_name, middle_name, last_name, total_purchase_cash, 
                total_purchase_credit, total_purchase_return_cash,
                total_purchase_return_credit, party_payment_payment, party_payment_payment_return, 
                total_purchase_cash + total_purchase_credit - total_purchase_return_cash - total_purchase_return_credit to_be_paid,
                total_purchase_cash + party_payment_payment - party_payment_payment_return paid_amount,
                (total_purchase_cash + total_purchase_credit - total_purchase_return_cash - total_purchase_return_credit) -
                (total_purchase_cash + party_payment_payment - party_payment_payment_return)
                 adv_due_amount
                from (select
                    id, first_name, middle_name, last_name, 
                    sum(total_purchase_cash) as total_purchase_cash,
                        sum(total_purchase_credit) as total_purchase_credit,
                        sum(total_purchase_return_cash) as total_purchase_return_cash,
                        sum(total_purchase_return_credit) as total_purchase_return_credit,
                        sum(party_payment_payment) as party_payment_payment,
                        sum(party_payment_payment_return) as party_payment_payment_return
                from
                    (
                    select
                        sr.id,
                        sr.first_name ,
                        sr.middle_name ,
                        sr.last_name ,
                        sum(grand_total) as total_purchase_cash,
                        0 as total_purchase_credit,
                        0 as total_purchase_return_cash,
                        0 as total_purchase_return_credit,
                        0 as party_payment_payment,
                        0 as party_payment_payment_return
                    from
                        customer.purchase_purchasemaster pm
                    join customer.supplier_supplier sr on
                        pm.supplier_id = sr.id
                    where
                        purchase_type = 1
                        and pay_type = 1
                    group by
                        sr.id,
                        sr.first_name ,
                        sr.middle_name ,
                        sr.last_name
                union all
                    select
                        sr.id,
                        sr.first_name ,
                        sr.middle_name ,
                        sr.last_name ,
                        0 as total_purchase_cash,
                        sum(grand_total) as total_purchase_credit,
                        0 as total_purchase_return_cash,
                        0 as total_purchase_return_credit,
                        0 as party_payment_payment,
                        0 as party_payment_payment_return
                    from
                        customer.purchase_purchasemaster pm
                    join customer.supplier_supplier sr on
                        pm.supplier_id = sr.id
                    where
                        purchase_type = 1
                        and pay_type = 2
                    group by
                        sr.id,
                        sr.first_name ,
                        sr.middle_name ,
                        sr.last_name
                union all
                    select
                        sr.id,
                        sr.first_name ,
                        sr.middle_name ,
                        sr.last_name ,
                        0 as total_purchase_cash,
                        0 as total_purchase_credit,
                        sum(grand_total) as total_purchase_return_cash,
                        0 as total_purchase_return_credit,
                        0 as party_payment_payment,
                        0 as party_payment_payment_return
                    from
                        customer.purchase_purchasemaster pm
                    join customer.supplier_supplier sr on
                        pm.supplier_id = sr.id
                    where
                        purchase_type = 2
                        and pay_type = 1
                    group by
                        sr.id,
                        sr.first_name ,
                        sr.middle_name ,
                        sr.last_name
                union all
                    select
                        sr.id,
                        sr.first_name ,
                        sr.middle_name ,
                        sr.last_name ,
                        0 as total_purchase_cash,
                        0 as total_purchase_credit,
                        0 as total_purchase_return_cash,
                        sum(grand_total) as total_purchase_return_credit,
                        0 as party_payment_payment,
                        0 as party_payment_payment_return
                    from
                        customer.purchase_purchasemaster pm
                    join customer.supplier_supplier sr on
                        pm.supplier_id = sr.id
                    where
                        purchase_type = 2
                        and pay_type = 2
                    group by
                        sr.id,
                        sr.first_name ,
                        sr.middle_name ,
                        sr.last_name
                union all
                    select
                        sr.id,
                        sr.first_name ,
                        sr.middle_name ,
                        sr.last_name ,
                        0 as total_purchase_cash,
                        0 as total_purchase_credit,
                        0 as total_purchase_return_cash,
                        0 as total_purchase_return_credit,
                        sum(amount) as party_payment_payment,
                        0 as party_payment_payment_return
                    from
                        customer.party_payment_basicpartypayment pp
                    join customer.supplier_supplier sr on
                        pp.supplier_id = sr.id
                    where
                        payment_type = 1
                    group by
                        sr.id,
                        sr.first_name ,
                        sr.middle_name ,
                        sr.last_name
                union all
                    select
                        sr.id,
                        sr.first_name ,
                        sr.middle_name ,
                        sr.last_name ,
                        0 as total_purchase_cash,
                        0 as total_purchase_credit,
                        0 as total_purchase_return_cash,
                        0 as total_purchase_return_credit,
                        0 as party_payment_payment,
                        sum(amount) as party_payment_payment_return
                    from
                        customer.party_payment_basicpartypayment pp
                    join customer.supplier_supplier sr on
                        pp.supplier_id = sr.id
                    where
                        payment_type = 2
                    group by
                        sr.id,
                        sr.first_name ,
                        sr.middle_name ,
                        sr.last_name ) R
                        group by id, first_name, middle_name, last_name
                        order by id) S''')
            
        else:
            supplier_filter = tuple()
            supplier_filter = request.GET.get("supplier", None)
            summary_queryset = BasicPartyPayment.objects.raw(f'''select id, first_name, middle_name, last_name, total_purchase_cash, 
                total_purchase_credit, total_purchase_return_cash,
                total_purchase_return_credit, party_payment_payment, party_payment_payment_return, 
                total_purchase_cash + total_purchase_credit - total_purchase_return_cash - total_purchase_return_credit to_be_paid,
                total_purchase_cash + party_payment_payment - party_payment_payment_return paid_amount,
                (total_purchase_cash + total_purchase_credit - total_purchase_return_cash - total_purchase_return_credit) -
                (total_purchase_cash + party_payment_payment - party_payment_payment_return)
                adv_due_amount
                from (select
                    id, first_name, middle_name, last_name, 
                    sum(total_purchase_cash) as total_purchase_cash,
                        sum(total_purchase_credit) as total_purchase_credit,
                        sum(total_purchase_return_cash) as total_purchase_return_cash,
                        sum(total_purchase_return_credit) as total_purchase_return_credit,
                        sum(party_payment_payment) as party_payment_payment,
                        sum(party_payment_payment_return) as party_payment_payment_return
                from
                    (
                    select
                        sr.id,
                        sr.first_name ,
                        sr.middle_name ,
                        sr.last_name ,
                        sum(grand_total) as total_purchase_cash,
                        0 as total_purchase_credit,
                        0 as total_purchase_return_cash,
                        0 as total_purchase_return_credit,
                        0 as party_payment_payment,
                        0 as party_payment_payment_return
                    from
                        customer.purchase_purchasemaster pm
                    join customer.supplier_supplier sr on
                        pm.supplier_id = sr.id
                    where
                        purchase_type = 1
                        and pay_type = 1
                    group by
                        sr.id,
                        sr.first_name ,
                        sr.middle_name ,
                        sr.last_name
                union all
                    select
                        sr.id,
                        sr.first_name ,
                        sr.middle_name ,
                        sr.last_name ,
                        0 as total_purchase_cash,
                        sum(grand_total) as total_purchase_credit,
                        0 as total_purchase_return_cash,
                        0 as total_purchase_return_credit,
                        0 as party_payment_payment,
                        0 as party_payment_payment_return
                    from
                        customer.purchase_purchasemaster pm
                    join customer.supplier_supplier sr on
                        pm.supplier_id = sr.id
                    where
                        purchase_type = 1
                        and pay_type = 2
                    group by
                        sr.id,
                        sr.first_name ,
                        sr.middle_name ,
                        sr.last_name
                union all
                    select
                        sr.id,
                        sr.first_name ,
                        sr.middle_name ,
                        sr.last_name ,
                        0 as total_purchase_cash,
                        0 as total_purchase_credit,
                        sum(grand_total) as total_purchase_return_cash,
                        0 as total_purchase_return_credit,
                        0 as party_payment_payment,
                        0 as party_payment_payment_return
                    from
                        customer.purchase_purchasemaster pm
                    join customer.supplier_supplier sr on
                        pm.supplier_id = sr.id
                    where
                        purchase_type = 2
                        and pay_type = 1
                    group by
                        sr.id,
                        sr.first_name ,
                        sr.middle_name ,
                        sr.last_name
                union all
                    select
                        sr.id,
                        sr.first_name ,
                        sr.middle_name ,
                        sr.last_name ,
                        0 as total_purchase_cash,
                        0 as total_purchase_credit,
                        0 as total_purchase_return_cash,
                        sum(grand_total) as total_purchase_return_credit,
                        0 as party_payment_payment,
                        0 as party_payment_payment_return
                    from
                        customer.purchase_purchasemaster pm
                    join customer.supplier_supplier sr on
                        pm.supplier_id = sr.id
                    where
                        purchase_type = 2
                        and pay_type = 2
                    group by
                        sr.id,
                        sr.first_name ,
                        sr.middle_name ,
                        sr.last_name
                union all
                    select
                        sr.id,
                        sr.first_name ,
                        sr.middle_name ,
                        sr.last_name ,
                        0 as total_purchase_cash,
                        0 as total_purchase_credit,
                        0 as total_purchase_return_cash,
                        0 as total_purchase_return_credit,
                        sum(amount) as party_payment_payment,
                        0 as party_payment_payment_return
                    from
                        customer.party_payment_basicpartypayment pp
                    join customer.supplier_supplier sr on
                        pp.supplier_id = sr.id
                    where
                        payment_type = 1
                    group by
                        sr.id,
                        sr.first_name ,
                        sr.middle_name ,
                        sr.last_name
                union all
                    select
                        sr.id,
                        sr.first_name ,
                        sr.middle_name ,
                        sr.last_name ,
                        0 as total_purchase_cash,
                        0 as total_purchase_credit,
                        0 as total_purchase_return_cash,
                        0 as total_purchase_return_credit,
                        0 as party_payment_payment,
                        sum(amount) as party_payment_payment_return
                    from
                        customer.party_payment_basicpartypayment pp
                    join customer.supplier_supplier sr on
                        pp.supplier_id = sr.id
                    where
                        payment_type = 2
                    group by
                        sr.id,
                        sr.first_name ,
                        sr.middle_name ,
                        sr.last_name ) R
                        group by id, first_name, middle_name, last_name
                        order by id) S where id = {supplier_filter}; ''')


        basicSerializer = BasicPartyPaymentSummaryReportSerializer(summary_queryset, many=True)     
        return Response(basicSerializer.data, status=status.HTTP_200_OK)





