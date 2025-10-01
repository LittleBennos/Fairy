from rest_framework import serializers
from .models import Invoice, InvoiceLineItem, Payment, PaymentPlan


class InvoiceLineItemSerializer(serializers.ModelSerializer):
    """Serializer for InvoiceLineItem model"""
    enrollment_details = serializers.CharField(
        source='enrollment.class_instance.class_type.name',
        read_only=True
    )

    class Meta:
        model = InvoiceLineItem
        fields = [
            'id', 'invoice', 'item_type', 'description', 'enrollment',
            'enrollment_details', 'quantity', 'unit_price', 'total',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'total', 'created_at', 'updated_at']


class InvoiceSerializer(serializers.ModelSerializer):
    """Full serializer for Invoice model"""
    account_code = serializers.CharField(source='account.account_code', read_only=True)
    student_name = serializers.CharField(source='account.student.person.full_name', read_only=True)
    term_name = serializers.CharField(source='term.name', read_only=True)
    line_items = InvoiceLineItemSerializer(many=True, read_only=True)
    amount_outstanding = serializers.ReadOnlyField()
    is_paid = serializers.ReadOnlyField()
    is_overdue = serializers.ReadOnlyField()

    class Meta:
        model = Invoice
        fields = [
            'id', 'invoice_number', 'account', 'account_code', 'student_name',
            'billing_contact_name', 'billing_email', 'billing_address',
            'issue_date', 'due_date', 'term', 'term_name',
            'subtotal', 'tax_rate', 'tax_amount', 'total', 'amount_paid',
            'amount_outstanding', 'status', 'is_paid', 'is_overdue',
            'late_fee_applied', 'line_items', 'notes', 'customer_notes',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'invoice_number', 'amount_paid', 'created_at', 'updated_at']

    def validate(self, data):
        """Validate invoice dates"""
        if 'due_date' in data and 'issue_date' in data:
            if data['due_date'] < data['issue_date']:
                raise serializers.ValidationError({
                    'due_date': 'Due date must be on or after issue date'
                })
        return data


class InvoiceListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for listing invoices"""
    account_code = serializers.CharField(source='account.account_code', read_only=True)
    student_name = serializers.CharField(source='account.student.person.full_name', read_only=True)
    amount_outstanding = serializers.ReadOnlyField()
    is_overdue = serializers.ReadOnlyField()

    class Meta:
        model = Invoice
        fields = [
            'id', 'invoice_number', 'account_code', 'student_name',
            'issue_date', 'due_date', 'total', 'amount_outstanding',
            'status', 'is_overdue'
        ]


class PaymentSerializer(serializers.ModelSerializer):
    """Full serializer for Payment model"""
    invoice_number = serializers.CharField(source='invoice.invoice_number', read_only=True)
    account_code = serializers.CharField(source='invoice.account.account_code', read_only=True)
    received_by_name = serializers.CharField(source='received_by.person.full_name', read_only=True)

    class Meta:
        model = Payment
        fields = [
            'id', 'payment_reference', 'invoice', 'invoice_number', 'account_code',
            'amount', 'payment_date', 'payment_method', 'status',
            'transaction_id', 'received_by', 'received_by_name', 'notes',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'payment_reference', 'created_at', 'updated_at']

    def validate(self, data):
        """Validate payment amount doesn't exceed invoice outstanding"""
        if not self.instance and data.get('invoice') and data.get('amount'):
            invoice = data['invoice']
            if data['amount'] > invoice.amount_outstanding:
                raise serializers.ValidationError({
                    'amount': f'Payment amount (${data["amount"]}) exceeds outstanding balance (${invoice.amount_outstanding})'
                })
        return data


class PaymentListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for listing payments"""
    invoice_number = serializers.CharField(source='invoice.invoice_number', read_only=True)
    account_code = serializers.CharField(source='invoice.account.account_code', read_only=True)

    class Meta:
        model = Payment
        fields = [
            'id', 'payment_reference', 'invoice_number', 'account_code',
            'amount', 'payment_date', 'payment_method', 'status'
        ]


class PaymentPlanSerializer(serializers.ModelSerializer):
    """Full serializer for PaymentPlan model"""
    account_code = serializers.CharField(source='account.account_code', read_only=True)
    student_name = serializers.CharField(source='account.student.person.full_name', read_only=True)
    invoice_number = serializers.CharField(source='invoice.invoice_number', read_only=True)
    approved_by_name = serializers.CharField(source='approved_by.person.full_name', read_only=True)
    amount_outstanding = serializers.ReadOnlyField()
    is_completed = serializers.ReadOnlyField()
    installments_remaining = serializers.ReadOnlyField()

    class Meta:
        model = PaymentPlan
        fields = [
            'id', 'account', 'account_code', 'student_name', 'invoice',
            'invoice_number', 'total_amount', 'installment_amount', 'frequency',
            'number_of_installments', 'start_date', 'end_date', 'first_payment_date',
            'status', 'amount_paid', 'installments_paid', 'amount_outstanding',
            'is_completed', 'installments_remaining', 'notes', 'approved_by',
            'approved_by_name', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def validate(self, data):
        """Validate payment plan dates and amounts"""
        errors = {}

        # Validate dates
        if 'end_date' in data and 'start_date' in data:
            if data['end_date'] <= data['start_date']:
                errors['end_date'] = 'End date must be after start date'

        if 'first_payment_date' in data and 'start_date' in data:
            if data['first_payment_date'] < data['start_date']:
                errors['first_payment_date'] = 'First payment date must be on or after start date'

        # Validate installment amount
        if 'installment_amount' in data and 'total_amount' in data and 'number_of_installments' in data:
            total_installments = data['installment_amount'] * data['number_of_installments']
            if total_installments < data['total_amount']:
                errors['installment_amount'] = (
                    f'Installment amount × number of installments (${total_installments}) '
                    f'is less than total amount (${data["total_amount"]})'
                )

        if errors:
            raise serializers.ValidationError(errors)

        return data


class PaymentPlanListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for listing payment plans"""
    account_code = serializers.CharField(source='account.account_code', read_only=True)
    student_name = serializers.CharField(source='account.student.person.full_name', read_only=True)
    amount_outstanding = serializers.ReadOnlyField()
    installments_remaining = serializers.ReadOnlyField()

    class Meta:
        model = PaymentPlan
        fields = [
            'id', 'account_code', 'student_name', 'total_amount',
            'installment_amount', 'frequency', 'status', 'amount_outstanding',
            'installments_remaining'
        ]
