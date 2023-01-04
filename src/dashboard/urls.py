from django.urls.conf import path
from rest_framework import routers
from .views import GetPurchaseViewSet, GetSaleViewSet, GetCreditSaleReportViewset,\
    FinancialDashboardViewSet, GetPurchaseCountViewSet, GetSaleCountViewSet, GetActiveItemCountViewSet,\
    GetCreditSaleCountViewSet, StaticalDashboardViewSet

# for pdf and excel
# from .views import MyExcelViewSet,SaleMasterPDFView
#  MyExcelViewSet

router = routers.DefaultRouter(trailing_slash=False)
router.register('financial-dashboard', FinancialDashboardViewSet)
router.register('statical-dashboard', StaticalDashboardViewSet)
router.register('purchase-dashboard', GetPurchaseViewSet)
router.register('sale-dashboard', GetSaleViewSet)
router.register('credit-sale-dashboard', GetCreditSaleReportViewset)
router.register('purchase-count', GetPurchaseCountViewSet)
router.register('sale-count', GetSaleCountViewSet)
router.register('credit-sale-count', GetCreditSaleCountViewSet)
router.register('active-item', GetActiveItemCountViewSet)
# router.register('excel',MyExcelViewSet)
# router.register('pdf',SaleMasterPDFView)

urlpatterns = [
    # path('pdf',SaleMasterPDFView.as_view(), name='pdf')
              ] + router.urls
