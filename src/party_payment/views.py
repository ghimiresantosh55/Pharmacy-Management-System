from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework import status
from src.supplier.models import Supplier
from src.supplier.serializers import SupplierSerializer
from decimal import Decimal
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter, SearchFilter
import django_filters
from django_filters import DateFromToRangeFilter
from django.db import transaction
from src.purchase.models import PurchaseMaster

# filter
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter, SearchFilter
import django_filters
from django_filters import DateFromToRangeFilter
from django_filters.filterset import FilterSet


from .serializers import PartyPaymentMasterSerializer, PartyPaymentDetailSerializer, PurchaseCreditSerializer,BasicPartyPaymentDetailSerializer
from .serializers import SavePartyPaymentDetailSerializer, SavePartyPaymentSerializer, SaveBasicPartyPaymentSerializer
from .models import BasicPartyPayment, PartyPayment,PartyPaymentDetail, BasicPartyPaymentDetail
from src.custom_lib.functions.party_payment import get_purchase_credit_detail
from src.custom_lib.functions.current_user import get_created_by
from django.utils import timezone

# Custom
from .reciept_unique_id_generator import get_receipt_no
from .party_payment_permissions import PartyPaymentSavePermission, PartyPaymentViewPermission, BasicPartyPaymentPermission

# for log
from simple_history.utils import update_change_reason


# Create your views here.
class RangeFilterForPartyPayment(django_filters.FilterSet):
    date = DateFromToRangeFilter(field_name="created_date_ad")

    class Meta:
        model = PartyPayment
        fields = '__all__'


class PartyPaymentViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [PartyPaymentViewPermission]
    queryset = PartyPayment.objects.all()
    serializer_class = PartyPaymentMasterSerializer
    filter_class = RangeFilterForPartyPayment
    filter_backends = (SearchFilter, OrderingFilter, DjangoFilterBackend)
    common_filter = "__all__"
    search_filter = "__all__"
    search_fields = search_filter
    ordering_fields = common_filter
    filterset_fields = common_filter


class PartyPaymentDetailViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [PartyPaymentViewPermission]
    queryset = PartyPaymentDetail.objects.all()
    serializer_class = PartyPaymentDetailSerializer
    filter_backends = (SearchFilter, OrderingFilter, DjangoFilterBackend)
    filter_fields = ['id','party_payment__purchase_master']
    ordering_fields = ['party_clearance', 'id']


class PartyPaymentSummaryViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [PartyPaymentViewPermission]
    queryset = PartyPayment.objects.all()
    serializer_class = SavePartyPaymentSerializer
    filter_class = RangeFilterForPartyPayment
    filter_backends = (SearchFilter, OrderingFilter, DjangoFilterBackend)


class FilterForCreditReportPurchaseMaster(django_filters.FilterSet):
    date = django_filters.DateFromToRangeFilter(field_name="created_date_ad")

    class Meta:
        model = PurchaseMaster
        fields = ['id', 'purchase_no', 'created_by', 'created_date_ad', 'pay_type', 'supplier']


class GetPartyInvoice(viewsets.ReadOnlyModelViewSet):
    permission_classes = [PartyPaymentViewPermission]
    queryset = PurchaseMaster.objects.filter(pay_type=2).select_related().select_related("discount_scheme","supplier","ref_purchase_order")
    serializer_class = PurchaseCreditSerializer
    filter_class = FilterForCreditReportPurchaseMaster
    filter_backends = (SearchFilter, OrderingFilter, DjangoFilterBackend)
    search_fields = ['purchase_no']
    ordering_fields = ['purchase_id', 'created_date_ad']

    @action(detail=False, methods=['GET'])
    def suppliers(self, request):
        data = get_purchase_credit_detail()
        id_list = data.values_list('supplier', flat=True)
        # converting a list into set for removing repeated values
        supplier_id_list = set(id_list)
        suppliers = Supplier.objects.filter(id__in=supplier_id_list)
        suppliers_serializer = SupplierSerializer(suppliers, many=True)
        return Response(suppliers_serializer.data, status=status.HTTP_200_OK)


class SavePartyPaymentViewSet(viewsets.ModelViewSet):
    permission_classes = [PartyPaymentSavePermission]
    queryset = PartyPayment.objects.all().select_related("purchase_master")
    serializer_class = SavePartyPaymentSerializer

    @transaction.atomic
    def create(self, request):
        quantize_places = Decimal(10) ** -2

        try:
            supplier_id = request.data.pop('supplier_id')
            purchase_master_id_list = request.data.pop('purchase_masters')
            remarks = request.data.pop('remarks')
            payment_details = request.data.pop('payment_details')
        except KeyError:
            return Response("Please provide supplier_id, purchase_master, remarks and payment_details values",
                            status=status.HTTP_400_BAD_REQUEST)

        # calculating total amount
        total_paying_amount = Decimal('0.00')
        for detail in payment_details:
            amount = Decimal(str(detail['amount']))
            total_paying_amount = total_paying_amount + amount

        total_due_amount = Decimal('0.00')
        for purchase_id in purchase_master_id_list:
            # Get due_amount of the given supplier
            data = get_purchase_credit_detail(supplier=supplier_id, purchase_master=purchase_id)
            if data[0]['due_amount'] <= 0:
                return Response('This invoice id ({}) has zero due_amount please unselect it'.format(purchase_id))
            total_due_amount += data[0]['due_amount']

        total_due_amount = total_due_amount.quantize(quantize_places)
        total_paying_amount = total_paying_amount.quantize(quantize_places)

        if total_paying_amount > total_due_amount:
            return Response("Your paying amount is {}, due amount is {}. Payment amount must be less than due amount".format(total_paying_amount, total_due_amount),
                            status=status.HTTP_400_BAD_REQUEST)
        response_data = []
        for purchase_id in purchase_master_id_list:

            # check if payment_details have any amount left
            sum = Decimal('0.00')
            for detail in payment_details:
                sum = sum + Decimal(str(detail['amount']))
            if sum <= 0:
                break

            # Get due_amount for given supplier
            data = get_purchase_credit_detail(supplier=supplier_id, purchase_master=purchase_id)
            due_amount = data[0]['due_amount']
            party_payment_details = []

            # calcaulate credit_payment_details
            for detail in payment_details:
                if detail['amount'] > 0:
                    if due_amount <= detail['amount']:
                        party_payment_detail = {
                            "payment_mode": detail['payment_mode'],
                            "amount": due_amount,
                            "remarks": detail['remarks']
                        }
                        detail['amount'] = detail['amount'] - due_amount
                        due_amount = 0
                        party_payment_details.append(party_payment_detail)
                        break
                    else:
                        party_payment_detail = {
                            "payment_mode": detail['payment_mode'],
                            "amount": detail['amount'],
                            "remarks": detail['remarks']
                        }
                        detail['amount'] = 0
                        due_amount = due_amount - detail['amount']
                        party_payment_details.append(party_payment_detail)
            # Calculate Total Amount for credit payment master
            total_payment = Decimal('0.00')
            for payment in party_payment_details:
                total_payment = total_payment + Decimal(str(payment['amount']))


            # 1. save Credit payment Master,
            request.data['payment_type'] = 1
            
            request.data['purchase_master'] = purchase_id
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
            request.data['party_payment_details'] = party_payment_details

            party_master_serializer = SavePartyPaymentSerializer(data=request.data,
                                                                     context={'request': request})

            if party_master_serializer.is_valid(raise_exception=True):
                party_master_serializer.save()
                response_data.append(party_master_serializer.data)
            else:
                return Response(
                    party_master_serializer.errors, status=status.HTTP_400_BAD_REQUEST
                )
        return Response(response_data, status=status.HTTP_201_CREATED)

    def update(self, request, pk=None):
        return Response("method not allowed")

    def partial_update(self, request, pk=None):
        return Response("Method not allowed")


class FilterForBasicPartyPaymentDetail(FilterSet):
    date = DateFromToRangeFilter(field_name="created_date_ad")
    class Meta:
        model = BasicPartyPaymentDetail
        fields = ['amount',]

class BasicPartyPaymentDetailViewset(viewsets.ModelViewSet):
    queryset = BasicPartyPaymentDetail.objects.all()
    serializer_class = BasicPartyPaymentDetailSerializer
    http_method_names = ['get']
    filter_backends = [SearchFilter, OrderingFilter, DjangoFilterBackend]
    filter_class = FilterForBasicPartyPaymentDetail
    ordering_fields = ['id','amount']
    search_fields = ['amount',]

class FilterForBasicPartyPayment(FilterSet):
    date = DateFromToRangeFilter(field_name="created_date_ad")
    class Meta:
        model = BasicPartyPayment
        fields = ['supplier','receipt_no']

class SaveBasicPartyPaymentViewset(viewsets.ModelViewSet):
    queryset = BasicPartyPayment.objects.all()
    permission_classes = [BasicPartyPaymentPermission]
    serializer_class = SaveBasicPartyPaymentSerializer
    http_method_names = ['get', 'head', 'post','patch']
    filter_backends = [SearchFilter, OrderingFilter, DjangoFilterBackend]
    filter_class = FilterForBasicPartyPayment
    ordering_fields = ['id','amount']
    search_fields = ['receipt_no','supplier__first_name']

     

    @transaction.atomic
    def create(self, request):
        # print(request.data)
            basic_party_payment_serializers = SaveBasicPartyPaymentSerializer(data=request.data, context={'request': request})
       
            if   basic_party_payment_serializers.is_valid(raise_exception = True):
                    basic_party_payment_serializers.save()
                    return Response( basic_party_payment_serializers.data, status=status.HTTP_201_CREATED)
            return Response( basic_party_payment_serializers.errors, status=status.HTTP_400_BAD_REQUEST)

    @transaction.atomic
    
    def partial_update(self, request, pk, *args, **kwargs):
        date_now = timezone.now()
        current_user_id = get_created_by({"request":request}).id  

        basic_party_payment_instance = BasicPartyPayment.objects.get(id=pk)
        basic_party_payment_details_update_data = list()
        basic_party_payment_details_create_data = list()

        basic_party_payment_details_data = request.data.pop('basic_party_payment_details')
        for basic_party_payment_detail_data in basic_party_payment_details_data:
            if "id" in  basic_party_payment_detail_data:
                basic_party_payment_details_update_data.append(basic_party_payment_detail_data)
            else: 
                basic_party_payment_details_create_data.append(basic_party_payment_detail_data)

        
        # print(basic_party_payment_details_update_data,"basic_party_payment_details_update_data")
        for  basic_party_payment_detail_update_data in  basic_party_payment_details_update_data:
                basic_party_payment_details_instance = BasicPartyPaymentDetail.objects.get(id = int( basic_party_payment_detail_update_data['id']))
                basic_party_payment_details_update_serializer = BasicPartyPaymentDetailSerializer( basic_party_payment_details_instance,context={"request":request}, data= basic_party_payment_detail_update_data, partial=True)
                if  basic_party_payment_details_update_serializer.is_valid():
                     basic_party_payment_details_update_serializer.save()
                else: 
                    return Response( basic_party_payment_details_update_serializer.errors, status= status.HTTP_400_BAD_REQUEST)


        for  basic_party_payment_detail_create_data in  basic_party_payment_details_create_data:
                basic_party_payment_detail_create_data['basic_party_payment'] = basic_party_payment_instance.id
                basic_party_payment_detail_create_data['created_by'] = current_user_id
                basic_party_payment_detail_create_data['created_date_ad'] =  date_now
                
                basic_party_payment_details_create_serializer = BasicPartyPaymentDetailSerializer(data=basic_party_payment_detail_create_data, context={"request":request})
                if  basic_party_payment_details_create_serializer.is_valid(raise_exception=True):
                     basic_party_payment_details_create_serializer.save()
                else: 
                    return Response( basic_party_payment_details_create_serializer.errors, status= status.HTTP_400_BAD_REQUEST)
     
           
        basic_party_payment_serializer = SaveBasicPartyPaymentSerializer(basic_party_payment_instance, data=request.data, partial=True)
        if basic_party_payment_serializer.is_valid(raise_exception=True):
             basic_party_payment_serializer.save()
             return Response(basic_party_payment_serializer.data, status= status.HTTP_200_OK)
        else:
            return Response(basic_party_payment_serializer.errors, status= status.HTTP_400_BAD_REQUEST)     
             



