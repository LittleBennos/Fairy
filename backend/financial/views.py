from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .models import Invoice, InvoiceLineItem, Payment, PaymentPlan
from .serializers import (
    InvoiceSerializer, InvoiceListSerializer,
    InvoiceLineItemSerializer,
    PaymentSerializer, PaymentListSerializer,
    PaymentPlanSerializer, PaymentPlanListSerializer
)


class InvoiceViewSet(viewsets.ModelViewSet):
    """ViewSet for Invoice CRUD operations"""
    queryset = Invoice.objects.select_related(
        'account__student__person',
        'account__guardian__person',
        'account__billing_contact__person',
        'term'
    ).prefetch_related('line_items').all()
    serializer_class = InvoiceSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['account', 'status', 'term', 'issue_date', 'due_date']
    search_fields = [
        'invoice_number',
        'account__account_code',
        'account__student__person__given_name',
        'account__student__person__family_name',
        'billing_contact_name'
    ]
    ordering_fields = ['issue_date', 'due_date', 'total', 'amount_paid', 'created_at']
    ordering = ['-issue_date']

    def get_serializer_class(self):
        if self.action == 'list':
            return InvoiceListSerializer
        return InvoiceSerializer

    @action(detail=True, methods=['post'])
    def calculate_totals(self, request, pk=None):
        """Recalculate invoice totals from line items"""
        invoice = self.get_object()
        invoice.calculate_totals()
        invoice.save()
        serializer = self.get_serializer(invoice)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def send(self, request, pk=None):
        """Mark invoice as sent"""
        invoice = self.get_object()
        if invoice.status == 'draft':
            invoice.status = 'sent'
            invoice.save()
            return Response({'status': 'Invoice marked as sent'})
        return Response(
            {'error': 'Only draft invoices can be sent'},
            status=status.HTTP_400_BAD_REQUEST
        )

    @action(detail=False, methods=['get'])
    def overdue(self, request):
        """List all overdue invoices"""
        from django.utils import timezone
        overdue_invoices = self.get_queryset().filter(
            status__in=['sent', 'partially_paid'],
            due_date__lt=timezone.now().date()
        )
        serializer = self.get_serializer(overdue_invoices, many=True)
        return Response(serializer.data)


class InvoiceLineItemViewSet(viewsets.ModelViewSet):
    """ViewSet for InvoiceLineItem CRUD operations"""
    queryset = InvoiceLineItem.objects.select_related(
        'invoice__account',
        'enrollment__class_instance__class_type'
    ).all()
    serializer_class = InvoiceLineItemSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['invoice', 'item_type', 'enrollment']
    search_fields = ['description', 'invoice__invoice_number']
    ordering_fields = ['created_at', 'total']
    ordering = ['invoice', 'item_type']


class PaymentViewSet(viewsets.ModelViewSet):
    """ViewSet for Payment CRUD operations"""
    queryset = Payment.objects.select_related(
        'invoice__account__student__person',
        'received_by__person'
    ).all()
    serializer_class = PaymentSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['invoice', 'status', 'payment_method', 'payment_date', 'received_by']
    search_fields = [
        'payment_reference',
        'invoice__invoice_number',
        'invoice__account__account_code',
        'transaction_id',
        'notes'
    ]
    ordering_fields = ['payment_date', 'amount', 'created_at']
    ordering = ['-payment_date']

    def get_serializer_class(self):
        if self.action == 'list':
            return PaymentListSerializer
        return PaymentSerializer

    def perform_create(self, serializer):
        """Automatically set received_by to current staff member"""
        # Try to get staff object from current user
        if hasattr(self.request.user, 'person') and hasattr(self.request.user.person, 'staff'):
            serializer.save(received_by=self.request.user.person.staff)
        else:
            serializer.save()

    @action(detail=False, methods=['get'])
    def recent(self, request):
        """List recent payments (last 30 days)"""
        from django.utils import timezone
        from datetime import timedelta
        thirty_days_ago = timezone.now().date() - timedelta(days=30)
        recent_payments = self.get_queryset().filter(
            payment_date__gte=thirty_days_ago,
            status='completed'
        )
        serializer = self.get_serializer(recent_payments, many=True)
        return Response(serializer.data)


class PaymentPlanViewSet(viewsets.ModelViewSet):
    """ViewSet for PaymentPlan CRUD operations"""
    queryset = PaymentPlan.objects.select_related(
        'account__student__person',
        'invoice',
        'approved_by__person'
    ).all()
    serializer_class = PaymentPlanSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['account', 'status', 'frequency', 'invoice', 'approved_by']
    search_fields = [
        'account__account_code',
        'account__student__person__given_name',
        'account__student__person__family_name',
        'notes'
    ]
    ordering_fields = ['start_date', 'end_date', 'total_amount', 'created_at']
    ordering = ['-created_at']

    def get_serializer_class(self):
        if self.action == 'list':
            return PaymentPlanListSerializer
        return PaymentPlanSerializer

    def perform_create(self, serializer):
        """Automatically set approved_by to current staff member"""
        # Try to get staff object from current user
        if hasattr(self.request.user, 'person') and hasattr(self.request.user.person, 'staff'):
            serializer.save(approved_by=self.request.user.person.staff)
        else:
            serializer.save()

    @action(detail=False, methods=['get'])
    def active(self, request):
        """List all active payment plans"""
        active_plans = self.get_queryset().filter(status='active')
        serializer = self.get_serializer(active_plans, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def defaulted(self, request):
        """List all defaulted payment plans"""
        defaulted_plans = self.get_queryset().filter(status='defaulted')
        serializer = self.get_serializer(defaulted_plans, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def record_payment(self, request, pk=None):
        """Record an installment payment for this payment plan"""
        plan = self.get_object()

        if plan.status not in ['active', 'defaulted']:
            return Response(
                {'error': 'Cannot record payment for completed or cancelled plans'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Update payment plan
        plan.amount_paid += plan.installment_amount
        plan.installments_paid += 1
        plan.update_status()
        plan.save()

        return Response({
            'status': 'Payment recorded',
            'amount_paid': plan.amount_paid,
            'installments_paid': plan.installments_paid,
            'installments_remaining': plan.installments_remaining,
            'plan_status': plan.status
        })
