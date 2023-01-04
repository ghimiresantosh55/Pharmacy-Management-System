import django_filters
from django.core import serializers
from rest_framework import  viewsets, status
from src.financial_report.CustomSerializer import BasicPartyPaymentSummaryReportSerializer
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from src.party_payment.models import BasicPartyPaymentDetail, BasicPartyPayment, PartyPayment
from src.financial_report.serializers.party_payment_report_serializer import ReportBasicPartyPaymentDetailSerializer, ReportBasicPartyPaymentSerializer
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.decorators import permission_classes
from rest_framework.decorators import action
from src.core_app.models import FiscalSessionAD,FiscalSessionBS
from src.supplier.models import Supplier
from src.financial_report.serializers import GetSupplierSerializer, GetFiscalSessionADSerializer
from src.financial_report.serializers.party_payment_report_serializer import SummaryBasicPartyPaymentSerializer
from src.financial_report.permission.party_payment_permission import BasicPartyPaymentDetailReportPermission, BasicPartyPaymentReportPermission
from src.financial_report.permission.party_payment_permission import BasicPartyPaymentDetailReportPermission
from src.financial_report.serializers import GetFiscalSessionBSSerializer



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

class BasicPartyPaymentDetailReportViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [BasicPartyPaymentDetailReportPermission]
    queryset = BasicPartyPaymentDetail.objects.all()
    serializer_class = ReportBasicPartyPaymentDetailSerializer

 

class BasicPartyPaymentSummaryReportViewSet(viewsets.ReadOnlyModelViewSet):
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
        if request.GET.get("id", None) is None:
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
                        chinari_dang.purchase_purchasemaster pm
                    join chinari_dang.supplier_supplier sr on
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
                        chinari_dang.purchase_purchasemaster pm
                    join chinari_dang.supplier_supplier sr on
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
                        chinari_dang.purchase_purchasemaster pm
                    join chinari_dang.supplier_supplier sr on
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
                        chinari_dang.purchase_purchasemaster pm
                    join chinari_dang.supplier_supplier sr on
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
                        chinari_dang.party_payment_basicpartypayment pp
                    join chinari_dang.supplier_supplier sr on
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
                        chinari_dang.party_payment_basicpartypayment pp
                    join chinari_dang.supplier_supplier sr on
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
                        chinari_dang.purchase_purchasemaster pm
                    join chinari_dang.supplier_supplier sr on
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
                        chinari_dang.purchase_purchasemaster pm
                    join chinari_dang.supplier_supplier sr on
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
                        chinari_dang.purchase_purchasemaster pm
                    join chinari_dang.supplier_supplier sr on
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
                        chinari_dang.purchase_purchasemaster pm
                    join chinari_dang.supplier_supplier sr on
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
                        chinari_dang.party_payment_basicpartypayment pp
                    join chinari_dang.supplier_supplier sr on
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
                        chinari_dang.party_payment_basicpartypayment pp
                    join chinari_dang.supplier_supplier sr on
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