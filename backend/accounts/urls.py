from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    StudentViewSet,
    GuardianViewSet,
    BillingContactViewSet,
    StaffViewSet,
    AccountViewSet,
)

router = DefaultRouter()
router.register(r'students', StudentViewSet, basename='student')
router.register(r'guardians', GuardianViewSet, basename='guardian')
router.register(r'billing-contacts', BillingContactViewSet, basename='billingcontact')
router.register(r'staff', StaffViewSet, basename='staff')
router.register(r'accounts', AccountViewSet, basename='account')

urlpatterns = router.urls