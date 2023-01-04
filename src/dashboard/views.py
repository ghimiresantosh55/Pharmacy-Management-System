from itertools import chain
from re import S
from typing import Collection, cast
from django.db import models
from django.db.models import fields
from django.db.models.aggregates import Count
from django.db.models.expressions import ExpressionWrapper, RowRange, Value
from django.db.models.functions.comparison import Cast
from django.db.models.query import QuerySet
from django.db.models.query_utils import FilteredRelation
from django.db.models.sql import query
from django.db.models.sql.query import Query
from django.shortcuts import render

from django.db import connection
from django.utils.translation import activate

# Create your views here.
from rest_framework import viewsets
from django.db.models import Sum
from rest_framework import serializers

from rest_framework.response import Response
from rest_framework import status
from django.db.models import F, Q
from django.db import connection
from django.db.models.functions import Coalesce
from rest_framework.serializers import Serializer

from src.purchase.models import PurchaseMaster
from src.purchase.serializers import PurchaseMasterSerializer
from src.sale.models import SaleMaster
from src.sale.serializers import SaleMasterSerializer
from src.credit_management.models import CreditClearance
from src.credit_management.serializers import CreditPaymentMasterSerializer

from src.item.models import Item, ItemCategory
from src.item.serializers import ItemSerializer, ItemCategorySerializer
from .dashboard_permissions import DashboardStatisticalPermission, DashboardFinancialPermission

'''---------------------------------- Financial Dashboard ---------------------------------'''


class FinancialDashboardViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [DashboardFinancialPermission]
    queryset = PurchaseMaster.objects.all()
    serializer_class = PurchaseMasterSerializer

    def list(self, request):
        query_dict = {

        }
        for k, vals in request.GET.lists():
            print(k, vals[0])
            if vals[0] != '':
                k = str(k)
                query_dict[k] = vals[0]
        # query_dict['filter-class']=FilterForPurchase
        query_filter = {}
        if "date_after" in query_dict:
            query_filter['created_date_ad__date__gte'] = query_dict['date_after']
        if "date_before" in query_dict:
            query_filter['created_date_ad__date__lte'] = query_dict['date_before']

        # purchase data
        data = {}
        purchase_amount_data = PurchaseMaster.objects.filter(purchase_type=1, **query_filter) \
            .aggregate(total_purchase_amount=Coalesce(Sum('grand_total'), 0))
        purchase_return_data = PurchaseMaster.objects.filter(purchase_type=2, **query_filter) \
            .aggregate(total_purchase_return_amount=Coalesce(Sum('grand_total'), 0))
        data.update(purchase_amount_data)
        data.update(purchase_return_data)

        # Sale Data
        sale_amount_data = SaleMaster.objects.filter(sale_type=1, **query_filter) \
            .aggregate(total_sale_amount=Coalesce(Sum('grand_total'), 0))
        sale_return_data = SaleMaster.objects.filter(sale_type=2, **query_filter) \
            .aggregate(total_sale_return_amount=Coalesce(Sum('grand_total'), 0))
        data.update(sale_amount_data)
        data.update(sale_return_data)

        # Credit Sale Data
        credit_sale_data = SaleMaster.objects.filter(pay_type=2, **query_filter) \
            .aggregate(credit_sale_total=Coalesce(Sum('grand_total'), 0))
        credit_payment_data = CreditClearance.objects.filter(**query_filter) \
            .aggregate(credit_collection_total=Coalesce(Sum('total_amount'), 0))

        data.update(credit_sale_data)
        data.update(credit_payment_data)

        return Response(data, status=status.HTTP_200_OK)


class GetPurchaseViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [DashboardFinancialPermission]
    queryset = PurchaseMaster.objects.all()
    serializer_class = PurchaseMasterSerializer

    def list(self, request):
        query_dict = {

        }
        for k, vals in request.GET.lists():
            print(k, vals[0])
            if vals[0] != '':
                k = str(k)
                query_dict[k] = vals[0]
        # query_dict['filter-class']=FilterForPurchase
        query_filter = {}
        if "date_after" in query_dict:
            query_filter['created_date_ad__date__gte'] = query_dict['date_after']
        if "date_before" in query_dict:
            query_filter['created_date_ad__date__lte'] = query_dict['date_before']
        summary_data = {}
        data = {}
        # purchase_summary
        purchase_amount_data = PurchaseMaster.objects.filter(purchase_type=1, **query_filter) \
            .aggregate(total_purchase_amount=Coalesce(Sum('grand_total'), 0))
        purchase_return_data = PurchaseMaster.objects.filter(purchase_type=2, **query_filter) \
            .aggregate(total_purchase_return_amount=Coalesce(Sum('grand_total'), 0))
        summary_data.update(purchase_amount_data)
        summary_data.update(purchase_return_data)

        purchase_data = PurchaseMaster.objects.filter(**query_filter).values("created_date_ad__date") \
            .annotate(
            date_ad=Cast('created_date_ad', fields.DateField()),
            total_purchase=Coalesce(Sum('grand_total', filter=Q(purchase_type=1)), 0),
            total_purchase_return=Coalesce(Sum('grand_total', filter=Q(purchase_type=2)), 0)) \
            .values('total_purchase', 'total_purchase_return', 'date_ad').order_by('date_ad')
        data['summary'] = summary_data
        data['data'] = purchase_data
        return Response(data, status=status.HTTP_200_OK)


class GetSaleViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [DashboardFinancialPermission]
    queryset = SaleMaster.objects.all()
    serializer_class = SaleMasterSerializer

    def list(self, request):
        query_dict = {

        }
        for k, vals in request.GET.lists():
            print(k, vals[0])
            if vals[0] != '':
                k = str(k)
                query_dict[k] = vals[0]
        query_filter = {}
        if "date_after" in query_dict:
            query_filter['created_date_ad__date__gte'] = query_dict['date_after']
        if "date_before" in query_dict:
            query_filter['created_date_ad__date__lte'] = query_dict['date_before']
        summary_data = {}
        data = {}
        # sale summary data
        sale_amount_data = SaleMaster.objects.filter(sale_type=1, **query_filter) \
            .aggregate(total_sale_amount=Coalesce(Sum('grand_total'), 0))
        sale_return_data = SaleMaster.objects.filter(sale_type=2, **query_filter) \
            .aggregate(total_sale_return_amount=Coalesce(Sum('grand_total'), 0))
        summary_data.update(sale_amount_data)
        summary_data.update(sale_return_data)
        sale_data = SaleMaster.objects.filter(**query_filter).values("created_date_ad__date") \
            .annotate(
            date_ad=Cast('created_date_ad', fields.DateField()),
            total_sale=Coalesce(Sum('grand_total', filter=Q(sale_type=1)), 0),
            total_sale_return=Coalesce(Sum('grand_total', filter=Q(sale_type=2)), 0)) \
            .values('date_ad', 'total_sale', 'total_sale_return').order_by('date_ad')
        data['summary'] = summary_data
        data['data'] = sale_data
        return Response(data, status=status.HTTP_200_OK)


class GetCreditSaleReportViewset(viewsets.ReadOnlyModelViewSet):
    permission_classes = [DashboardFinancialPermission]
    queryset = CreditClearance.objects.all()
    serializer_class = CreditPaymentMasterSerializer

    def list(self, request):
        query_dict = {

        }
        for k, vals in request.GET.lists():
            if vals[0] != '':
                k = str(k)
                query_dict[k] = vals[0]
        query_filter = {}

        if query_dict:
            try:
                query_filter['created_date_ad__date__gte'] = query_dict['date_after']
                query_filter['created_date_ad__date__lte'] = query_dict['date_before']
            except KeyError:
                return Response("Please provide both date_after and date_before")
        summary_data = {}
        data = {}

        if query_filter:
            print("up")
            credit_sale_data = SaleMaster.objects.filter(pay_type=2, **query_filter) \
                .aggregate(credit_sale_total=Coalesce(Sum('grand_total'), 0))

            credit_payment_data = CreditClearance.objects.filter(payment_type=1, **query_filter) \
                .aggregate(credit_collection_total=Coalesce(Sum('total_amount'), 0))

            summary_data.update(credit_sale_data)
            summary_data.update(credit_payment_data)
            cursor = connection.cursor()
            cursor.execute('''select DATE(created_date_ad) created_date_ad, sum(credit_sale_amount) AS "credit_sale_amount", 
                                        sum (credit_coll) credit_clearance_amount from 
                                        (select DATE(created_date_ad) created_date_ad, sum(grand_total) credit_sale_amount, 0 as credit_coll from
                                                    sale_salemaster
                                        where sale_type = 1 and pay_type = 2 and DATE(created_date_ad)>= %s and DATE(created_date_ad)<= %s
                                        group by DATE(created_date_ad) 
                                        union all
                                        select DATE(created_date_ad) created_date_ad, 0 as credit_sale_amount, sum(total_amount) credit_coll from credit_management_creditclearance
                                        where payment_type = 1 and DATE(created_date_ad)>= %s and DATE(created_date_ad)<= %s
                                        group by DATE(created_date_ad)) R
                                        group by DATE(created_date_ad)''',
                           [query_filter["created_date_ad__date__gte"], query_filter["created_date_ad__date__lte"],
                            query_filter["created_date_ad__date__gte"], query_filter["created_date_ad__date__lte"]])
            columns = [col[0] for col in cursor.description]
            credit_data = [
                dict(zip(columns, row))
                for row in cursor.fetchall()
            ]
            data['summary'] = summary_data
            data['data'] = credit_data
            return Response(data, status=status.HTTP_200_OK)


        else:
            credit_sale_data = SaleMaster.objects.filter(pay_type=2) \
                .aggregate(credit_sale_total=Coalesce(Sum('grand_total'), 0))

            credit_payment_data = CreditClearance.objects.filter(payment_type=1) \
                .aggregate(credit_collection_total=Coalesce(Sum('total_amount'), 0))

            summary_data.update(credit_sale_data)
            summary_data.update(credit_payment_data)
            cursor = connection.cursor()
            cursor.execute('''select DATE(created_date_ad) created_date_ad, sum(credit_sale_amount) AS "credit_sale_amount", 
                                            sum (credit_coll) credit_clearance_amount from 
                                            (select DATE(created_date_ad) created_date_ad, sum(grand_total) credit_sale_amount, 0 as credit_coll from
                                                        sale_salemaster
                                            where sale_type = 1 and pay_type = 2 
                                            group by DATE(created_date_ad) 
                                            union all
                                            select DATE(created_date_ad) created_date_ad, 0 as credit_sale_amount, sum(total_amount) credit_coll from credit_management_creditclearance
                                            where payment_type = 1 
                                            group by DATE(created_date_ad)) R
                                            group by DATE(created_date_ad)''')
            columns = [col[0] for col in cursor.description]
            credit_data = [
                dict(zip(columns, row))
                for row in cursor.fetchall()
            ]
            data['summary'] = summary_data
            data['data'] = credit_data
        return Response(data, status=status.HTTP_200_OK)


''' ---------------------------------- Statistical Dashboard ---------------------------------------------------'''


class GetPurchaseCountViewSet(viewsets.ViewSet):
    permission_classes = [DashboardStatisticalPermission]
    serializer_class = PurchaseMaster
    queryset = PurchaseMaster.objects.all()

    def list(self, request):
        query_dict = {}
        for k, vals in request.GET.lists():
            print(k, vals[0])
            if vals[0] != '':
                k = str(k)
                query_dict[k] = vals[0]
        query_filter = {}
        if "date_after" in query_dict:
            query_filter['created_date_ad__date__gte'] = query_dict['date_after']
        if "date_before" in query_dict:
            query_filter['created_date_ad__date__lte'] = query_dict['date_before']

        summary_data = {}
        data = {}
        # for summary data
        total_purchase_count_data = PurchaseMaster.objects.filter(**query_filter) \
            .aggregate(overall_total_purchase=Count("id"))
        total_purchase_return_data = PurchaseMaster.objects.filter(purchase_type=2, **query_filter) \
            .aggregate(overall_total_purchase_return=Count("id"))
        summary_data.update(total_purchase_count_data)
        summary_data.update(total_purchase_return_data)

        purchase_data = PurchaseMaster.objects.filter(**query_filter).values("created_date_ad__date") \
            .annotate(
            date_ad=Cast('created_date_ad', fields.DateField()),
            total_purchase=Count("id"),
            total_purchase_return=Count("id", filter=Q(purchase_type=2))
        ).values('date_ad', 'total_purchase', 'total_purchase_return') \
            .order_by('created_date_ad__date')

        data['summary'] = summary_data
        data['data'] = purchase_data

        return Response(data, status=status.HTTP_200_OK)


class GetSaleCountViewSet(viewsets.ViewSet):
    permission_classes = [DashboardStatisticalPermission]
    serializers_class = SaleMasterSerializer
    queryset = SaleMaster.objects.all()

    def list(self, request):
        query_dict = {}
        for k, vals in request.GET.lists():
            if vals[0] != '':
                k = str(k)
                query_dict[k] = vals[0]
        query_filter = {}
        if "date_after" in query_dict:
            query_filter['created_date_ad__date__gte'] = query_dict['date_after']
        if "date_before" in query_dict:
            query_filter['created_date_ad__date__lte'] = query_dict['date_before']

        summary_data = {}
        data = {}
        # for summary data
        total_sale_count_data = SaleMaster.objects.filter(**query_filter) \
            .aggregate(overall_total_sale=Count("id"))
        total_sale_return_data = SaleMaster.objects.filter(sale_type=2, **query_filter) \
            .aggregate(overall_total_sale_return=Count("id"))
        summary_data.update(total_sale_count_data)
        summary_data.update(total_sale_return_data)

        sale_count_data = SaleMaster.objects.filter(**query_filter).values('created_date_ad__date') \
            .annotate(
            date_ad=Cast('created_date_ad', fields.DateField()),
            total_sale=Count("sale_no"),
            total_sale_return=Count("sale_no", filter=Q(sale_type=2))
        ).values("date_ad", "total_sale", "total_sale_return") \
            .order_by("date_ad")
        data["summary_data"] = summary_data
        data["data"] = sale_count_data
        return Response(data, status=status.HTTP_200_OK)


class GetCreditSaleCountViewSet(viewsets.ViewSet):
    permission_classes = [DashboardStatisticalPermission]
    serializers_class = SaleMasterSerializer
    queryset = SaleMaster.objects.all()

    def list(self, request):
        query_dict = {}
        for k, vals in request.GET.lists():
            if vals[0] != '':
                k = str(k)
                query_dict[k] = vals[0]
        query_filter = {}
        if "date_after" in query_dict:
            query_filter['created_date_ad__date__gte'] = query_dict['date_after']
        if "date_before" in query_dict:
            query_filter['created_date_ad__date__lte'] = query_dict['date_before']

        summary_data = {}
        data = {}
        # for summary data
        total_sale_count_data = SaleMaster.objects.filter(**query_filter, pay_type=2) \
            .aggregate(overall_total_credit_sales=Count("id"))
        total_sale_return_data = SaleMaster.objects.filter(pay_type=2, **query_filter) \
            .aggregate(overall_total_credit_sale_return=Count("id", filter=Q(sale_type=2) & Q(pay_type=2)))
        summary_data.update(total_sale_count_data)
        summary_data.update(total_sale_return_data)

        credit_sale_data = SaleMaster.objects.filter(**query_filter, pay_type=2).values("created_date_ad__date") \
            .annotate(
            date_ad=Cast("created_date_ad", fields.DateField()),
            total_credit_sales=Count('sale_no'),
            total_credit_sale_return=Count('sale_no', filter=Q(sale_type=2) & Q(pay_type=2))
        ).values('date_ad', 'total_credit_sales', 'total_credit_sale_return') \
            .order_by('date_ad')
        data["summary_data"] = summary_data
        data["data"] = credit_sale_data
        return Response(data, status=status.HTTP_200_OK)


class GetActiveItemCountViewSet(viewsets.ViewSet):
    permission_classes = [DashboardStatisticalPermission]
    serializers_class = ItemSerializer
    queryset = Item.objects.all()

    def list(self, request):
        query_dict = {}
        for k, vals in request.GET.lists():
            if vals[0] != '':
                k = str(k)
                query_dict[k] = vals[0]

        data = Item.objects.filter(**query_dict) \
            .aggregate(
            total_items=Count('name'),
            total_active_items=Count('name', filter=Q(active=True)),
            total_deactivated_items=Count('name', filter=Q(active=False))
        )

        return Response(data, status=status.HTTP_200_OK)


class StaticalDashboardViewSet(viewsets.ViewSet):
    permission_classes = [DashboardStatisticalPermission]
    serializers_class = ItemSerializer
    queryset = Item.objects.all()

    def list(self, request):
        query_dict = {}
        for k, vals in request.GET.lists():
            print(k, vals[0])
            if vals[0] != '':
                k = str(k)
                query_dict[k] = vals[0]

        query_filter = {}
        if "date_after" in query_dict:
            query_filter['created_date_ad__date__gte'] = query_dict['date_after']
        if "date_before" in query_dict:
            query_filter['created_date_ad__date__lte'] = query_dict['date_before']
        data = {}

        purchase_count = PurchaseMaster.objects.filter(**query_filter).values() \
            .aggregate(total_purchase=Count("id"))
        purchase_return = PurchaseMaster.objects.filter(**query_filter, purchase_type=2).values() \
            .aggregate(total_purchase_return=Count("id"))
        sale_count = SaleMaster.objects.filter(**query_filter).values() \
            .aggregate(total_sale=Count("id"))
        sale_return = SaleMaster.objects.filter(**query_filter, sale_type=2).values() \
            .aggregate(total_sale_return=Count("id"))
        credit_sale = SaleMaster.objects.filter(**query_filter, pay_type=2).values() \
            .aggregate(total_credit_sale=Count("id"))
        credit_sale_return = SaleMaster.objects.filter(Q(**query_filter) & Q(pay_type=2) & Q(sale_type=2)).values() \
            .aggregate(total_credit_sale_return=Count("id"))
        items = Item.objects.values() \
            .aggregate(total_items=Count("id"))
        active_items = Item.objects.filter(active=True).values() \
            .aggregate(total_active_items=Count("id"))

        data.update(purchase_count)
        data.update(purchase_return)
        data.update(sale_count)
        data.update(sale_return)
        data.update(credit_sale)
        data.update(credit_sale_return)
        data.update(items)
        data.update(active_items)

        return Response(data, status=status.HTTP_200_OK)


# for pdf and excel

# from rest_framework.viewsets import ReadOnlyModelViewSet
# from rest_framework.renderers import JSONRenderer
# from drf_renderer_xlsx.renderers import XLSXRenderer
# from drf_renderer_xlsx.mixins import XLSXFileMixin
# from rest_framework.renderers import JSONRenderer
# from rest_framework.response import Response
# from rest_framework.views import APIView




# class MyExcelViewSet(XLSXFileMixin, ReadOnlyModelViewSet):
#     queryset = Item.objects.all()
#     serializer_class = ItemSerializer
#     xlsx_ignore_headers = [
#         'created_date_bs','created_date_ad','stock_alert_qty','location','image','expirable',\
#         'item_category','taxable', 'discountable', 'item_type_display', 'basic_info', 'item_type_display',\
#             'created_by', 'active','item_type'
#         ]
#     column_header = {
#         'titles': [
#             "S.N.",
#             "Category",
#             "Name", "Code", "TAX %", 'Purchase cost', "Sale cost","Profit"
#         ],}

#     renderer_classes = [XLSXRenderer]
#     filename = 'file.xlsx'

#     def get_queryset(self):
#         queryset = Item.objects.all()
#         code = self.request.query_params.get('code', None)
#         if code is not None:
#             queryset = queryset.filter(code=code)
#         return queryset
#     def get_header(self):
#         return {
#             'tab_title': 'Item Report',
#             'header_title': 'Item Report',
#             'height': 20,
#             'style': {
#                 'fill': {
#                     'fill_type': 'solid',
#                     'start_color': 'FFFFFFFF',
#                 },
#                 'alignment': {
#                     'horizontal': 'center',
#                     'vertical': 'center',
#                     'wrapText': True,
#                     'shrink_to_fit': True,
#                 },
#                 'border_side': {
#                     'border_style': 'thin',
#                     'color': 'FF000000',
#                 },
#                 'font': {
#                     'name': 'Arial',
#                     'size': 14,
#                     'bold': True,
#                     'color': 'FF000000',
#                 }
#             }
#         }
    


# from django.views.generic import ListView
# from django.http import HttpResponse
# from django.template.loader import get_template 
# from xhtml2pdf import pisa
# from django.views.generic import View

# class SaleMasterPDFView(View):
#     def get(self, request, *args, **kwargs):
#         template_name = 'sale.html'
#         purchase_master = PurchaseMaster.objects.all()
#         total =  PurchaseMaster.objects.aggregate(
#             total_discount=Coalesce(Sum('total_discount'), 0),
#             grand_total =Coalesce(Sum('grand_total'),0)
#         )
#         print(total)
        
#         context = {
#             "purchase_masters": purchase_master,
#             "totals": total
            
#         }
       
#         # Create a Django response object, and specify content_type as pdf
#         response = HttpResponse(content_type='application/pdf')
#         response['Content-Disposition'] = 'filename="report.pdf"'
#         # find the template and render it.
#         template = get_template(template_name)
#         html = template.render(context)

#         # create a pdf
#         pisa_status = pisa.CreatePDF(html, dest=response)
#         # if error then show some funy view
#         if pisa_status.err:
#             return HttpResponse('We had some errors <pre>' + html + '</pre>')
#         return response
            
       