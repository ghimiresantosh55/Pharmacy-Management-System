from .models import PurchaseMaster, PurchaseOrderMaster
from src.custom_lib.functions.fiscal_year import get_fiscal_year_code_bs
# format order_no according to given digits
PURCHASE_ORDER_LENGTH = 7

fiscal_year_code = get_fiscal_year_code_bs()

# generate unique order_no for purchase_order_master
def generate_order_no(order_type):

    # for Purchase order
    if order_type == 1:
        cancel_count = PurchaseOrderMaster.objects.filter(order_type=order_type).count()
        max_id = str(cancel_count + 1)
        # generate id = PO-77/78-0000000001, PO-77/78-0000000002 ...
        #  zfill() method adds zeros (0) at the beginning of the string, until it reaches the specified length
        unique_id = "PO-" + fiscal_year_code + "-" + max_id.zfill(PURCHASE_ORDER_LENGTH)
        return unique_id

    # for Purchase cancelled
    elif order_type == 2:
        cancel_count = PurchaseOrderMaster.objects.filter(order_type=order_type).count()
        max_id = str(cancel_count + 1)
        # generate id = PC-77/78-0000000001, PC-77/78-0000000002 ...
        #  zfill() method adds zeros (0) at the beginning of the string, until it reaches the specified length
        unique_id = "PC-" + fiscal_year_code + "-" + max_id.zfill(PURCHASE_ORDER_LENGTH)
        return unique_id

    # for Purchase approved
    elif order_type == 3:
        cancel_count = PurchaseOrderMaster.objects.filter(order_type=order_type).count()
        max_id = str(cancel_count + 1)
        # generate id = PA-77/78-0000000001, PA-77/78-0000000002 ...
        #  zfill() method adds zeros (0) at the beginning of the string, until it reaches the specified length
        unique_id = "PA-" + fiscal_year_code + "-" + max_id.zfill(PURCHASE_ORDER_LENGTH)
        return unique_id

    else:
        return ValueError


# generate unique order_no for purchase_master
def generate_purchase_no(purchase_type):

    # for Purchase /Direct Purchase
    if purchase_type == 1:
        cancel_count = PurchaseMaster.objects.filter(purchase_type=purchase_type).count()
        max_id = str(cancel_count + 1)
        # generate id = PU-77/78-0000000001, PU-77/78-0000000002 ...
        #  zfill() method adds zeros (0) at the beginning of the string, until it reaches the specified length
        unique_id = "PU-" + fiscal_year_code + "-" + max_id.zfill(PURCHASE_ORDER_LENGTH)
        return unique_id

    # for Purchase Returned
    elif purchase_type == 2:
        cancel_count = PurchaseMaster.objects.filter(purchase_type=purchase_type).count()
        max_id = str(cancel_count + 1)
        # generate id = PR-77/78-0000000001, PR-77/78-0000000002 ...
        #  zfill() method adds zeros (0) at the beginning of the string, until it reaches the specified length
        unique_id = "PR-" + fiscal_year_code + "-" + max_id.zfill(PURCHASE_ORDER_LENGTH)
        return unique_id

    # for Stock Opening
    elif purchase_type == 3:
        cancel_count = PurchaseMaster.objects.filter(purchase_type=purchase_type).count()
        max_id = str(cancel_count + 1)
        # generate id = OS-77/78-0000000001, OS-77/78-0000000002
        #  zfill() method adds zeros (0) at the beginning of the string, until it reaches the specified length
        unique_id = "OS-" + fiscal_year_code + "-" + max_id.zfill(PURCHASE_ORDER_LENGTH)
        return unique_id

    elif purchase_type == 4:
        cancel_count = PurchaseMaster.objects.filter(purchase_type=purchase_type).count()
        max_id = str(cancel_count + 1)
        # generate AD = PO-77/78-0000000001, AD-77/78-0000000002 ...
        #  zfill() method adds zeros (0) at the beginning of the string, until it reaches the specified length
        unique_id = "AD-" + fiscal_year_code + "-" + max_id.zfill(PURCHASE_ORDER_LENGTH)
        return unique_id

    elif purchase_type == 5:
        cancel_count = PurchaseMaster.objects.filter(purchase_type=purchase_type).count()
        max_id = str(cancel_count + 1)
        # generate id = SU-77/78-0000000001, SU-77/78-0000000002 ...
        #  zfill() method adds zeros (0) at the beginning of the string, until it reaches the specified length
        unique_id = "SU-" + fiscal_year_code + "-" + max_id.zfill(PURCHASE_ORDER_LENGTH)
        return unique_id
