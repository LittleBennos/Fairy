from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import InvoiceViewSet, InvoiceLineItemViewSet, PaymentViewSet, PaymentPlanViewSet

router = DefaultRouter()
router.register(r'invoices', InvoiceViewSet, basename='invoice')
router.register(r'invoice-line-items', InvoiceLineItemViewSet, basename='invoicelineitem')
router.register(r'payments', PaymentViewSet, basename='payment')
router.register(r'payment-plans', PaymentPlanViewSet, basename='paymentplan')

urlpatterns = [
    path('', include(router.urls)),
]
