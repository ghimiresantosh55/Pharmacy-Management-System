from django.urls import path, include
from src.custom_lib.views.stock_views import StockAnalysisView, ItemLedgerView, ExpiredItemView
urlpatterns = [
    path('user-app/', include('src.user.urls')),
    path('core-app/', include('src.core_app.urls')),
    path('item-app/', include('src.item.urls')),
    path('supplier-app/', include('src.supplier.urls')),
    path('purchase-app/', include('src.purchase.urls')),
    path('opening-stock-app/', include('src.opening_stock.urls')),
    path('stock-adjustment-app/', include('src.stock_adjustment.urls')),
    path('customer-app/', include('src.customer.urls')),
    path('financial-report/', include('src.financial_report.urls')),
    path('sale-app/', include('src.sale.urls')),
    path('customer-order-app/', include('src.customer_order.urls')),
    path('advance-deposit-app/', include('src.advance_deposit.urls')),
    path('credit-management-app/', include('src.credit_management.urls')),
    path('stock/stock-analysis', StockAnalysisView.as_view({'get': 'list'})),
    path('stock/item-ledger', ItemLedgerView.as_view()),
    path('stock/expired-item-report', ExpiredItemView.as_view({'get': 'list'})),
    path('party-payment-app/', include('src.party_payment.urls')),
    path('dashboard/', include('src.dashboard.urls')),
    path('group-app/', include('src.user_group.urls')),
    path('ird-report-app/', include('src.ird_report.urls'))
]
