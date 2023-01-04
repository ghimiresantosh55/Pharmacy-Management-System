from rest_framework import serializers
from src.purchase.models import PurchaseDetail
from src.custom_lib.functions import stock
from src.item.models import Item


# purchase detail serializer for write_only views
class PurchaseDetailStockSerializer(serializers.ModelSerializer):
    item_name = serializers.ReadOnlyField(source='item.name')
    code_name = serializers.ReadOnlyField(source='item.code')
    unit_name =  serializers.ReadOnlyField(source='item.unit.name', allow_null=True)
    unit_short_form = serializers.ReadOnlyField(source='item.unit.short_form', allow_null=True)
    packing_type_name =  serializers.ReadOnlyField(source='packing_type.name', allow_null=True)
    remaining_qty = serializers.SerializerMethodField()
    return_qty = serializers.SerializerMethodField()
    sale_qty = serializers.SerializerMethodField()
    sale_return_qty = serializers.SerializerMethodField()

    # def get_qty(self, product):
    #     PurchaseDetail.objects.filter(rem_qty__gt=0.00)
    #     ref_purchase_detail = purchase_detail.id
    #     serializer = stock.get_remaining_qty_of_purchase(ref_purchase_detail)
    #     return serializer.data
    class Meta:
        model = PurchaseDetail
        exclude = ['discount_amount', 'gross_amount', 'tax_amount', 'net_amount', 'created_date_ad',
                   'created_date_bs', 'created_by']
      

    def get_remaining_qty(self, purchase_detail):
        ref_purchase_detail = purchase_detail.id
        purchase_rem_qty = stock.get_remaining_qty_of_purchase(ref_purchase_detail)

        return purchase_rem_qty

    def get_return_qty(self, purchase_detail):
        ref_purchase_detail = purchase_detail.id
        return_rem_qty = stock.get_purchase_return_qty(ref_purchase_detail)
        return return_rem_qty


    def get_sale_qty(self, purchase_detail):
        ref_purchase_detail = purchase_detail.id
        sale_rem_qty = stock.get_purchase_sale_qty(ref_purchase_detail)
        return sale_rem_qty

    def get_sale_return_qty(self, purchase_detail):
        ref_purchase_detail = purchase_detail.id
        rem_qty = stock.get_purchase_sale_return_qty(ref_purchase_detail)
        return rem_qty


class StockAnalysisSerializer(serializers.ModelSerializer):
    # item_name = serializers.ReadOnlyField(source='item.name')
    # chalan_no = serializers.ReadOnlyField(source='purchase.chalan_no')
    item_category_name = serializers.ReadOnlyField(source='item_category.name')
    item_type_name = serializers.ReadOnlyField(source='get_item_type_display', allow_null=True)
    remaining_qty = serializers.SerializerMethodField()
    return_qty = serializers.SerializerMethodField()
    sale_qty = serializers.SerializerMethodField()
    sale_return_qty = serializers.SerializerMethodField()
    purchase_qty = serializers.SerializerMethodField()

    class Meta:
        model = Item
        fields = "__all__"

    def get_remaining_qty(self, item):
        item_id = item.id
        rem_qty = stock.get_remaining_qty_of_item(item_id)
        return rem_qty

    def get_return_qty(self, item):
        item_id = item.id
        rem_qty = stock.get_purchase_return_qty_of_item(item_id)
        return rem_qty


    def get_sale_qty(self, item):
        item_id = item.id
        rem_qty = stock.get_sale_qty_of_item(item_id)
        return rem_qty

    def get_sale_return_qty(self, item):
        item_id = item.id
        rem_qty = stock.get_sale_return_qty_of_item(item_id)
        return rem_qty

    def get_purchase_qty(self, item):
        item_id = item.id
        rem_qty = stock.get_purchase_qty_of_item(item_id)
        return rem_qty
