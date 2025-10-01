from django.db import models
from django.core.validators import MinValueValidator
from decimal import Decimal
import uuid


def generate_invoice_number():
    """Generate unique invoice number like INV-XXXXX"""
    return f"INV-{uuid.uuid4().hex[:8].upper()}"


def generate_payment_reference():
    """Generate unique payment reference like PAY-XXXXX"""
    return f"PAY-{uuid.uuid4().hex[:8].upper()}"


class Invoice(models.Model):
    """
    Invoice for an account. Can contain multiple line items (enrollments, fees, etc.).
    Generated per billing cycle (usually per term).
    """

    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('sent', 'Sent'),
        ('paid', 'Paid'),
        ('partially_paid', 'Partially Paid'),
        ('overdue', 'Overdue'),
        ('cancelled', 'Cancelled'),
    ]

    # Invoice identification
    invoice_number = models.CharField(
        max_length=20,
        unique=True,
        default=generate_invoice_number,
        help_text="Unique invoice number (auto-generated)"
    )

    # Link to Account
    account = models.ForeignKey(
        'accounts.Account',
        on_delete=models.PROTECT,
        related_name='invoices',
        help_text="The account being invoiced"
    )

    # Billing information (snapshot from account at invoice generation time)
    billing_contact_name = models.CharField(max_length=200, help_text="Billing contact name at time of invoice")
    billing_email = models.EmailField(help_text="Email for invoice delivery")
    billing_address = models.TextField(help_text="Full billing address")

    # Invoice dates
    issue_date = models.DateField(help_text="Date invoice was issued")
    due_date = models.DateField(help_text="Payment due date")

    # Term reference (optional - invoices can be for specific terms)
    term = models.ForeignKey(
        'scheduling.Term',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='invoices',
        help_text="Term this invoice is for (optional)"
    )

    # Amounts
    subtotal = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        help_text="Subtotal before tax"
    )
    tax_rate = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0.00,
        validators=[MinValueValidator(0)],
        help_text="Tax rate as percentage (e.g., 10.00 for 10%)"
    )
    tax_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        help_text="Tax amount"
    )
    total = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        help_text="Total amount due (subtotal + tax)"
    )
    amount_paid = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00,
        validators=[MinValueValidator(0)],
        help_text="Amount paid so far"
    )

    # Status
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='draft',
        help_text="Invoice status"
    )

    # Late fees
    late_fee_applied = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00,
        validators=[MinValueValidator(0)],
        help_text="Late fees applied to this invoice"
    )

    # Additional information
    notes = models.TextField(blank=True, help_text="Internal notes about this invoice")
    customer_notes = models.TextField(blank=True, help_text="Notes visible to customer on invoice")

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-issue_date', '-invoice_number']
        indexes = [
            models.Index(fields=['invoice_number']),
            models.Index(fields=['account', 'status']),
            models.Index(fields=['status']),
            models.Index(fields=['issue_date']),
            models.Index(fields=['due_date']),
            models.Index(fields=['term']),
        ]

    def __str__(self):
        return f"{self.invoice_number} - {self.account.account_code} (${self.total})"

    @property
    def amount_outstanding(self):
        """Returns the outstanding balance"""
        return max(Decimal('0.00'), self.total - self.amount_paid)

    @property
    def is_paid(self):
        """Returns True if invoice is fully paid"""
        return self.amount_paid >= self.total

    @property
    def is_overdue(self):
        """Returns True if invoice is overdue"""
        from django.utils import timezone
        return (
            self.status not in ['paid', 'cancelled']
            and self.due_date < timezone.now().date()
        )

    def calculate_totals(self):
        """Calculate subtotal, tax, and total from line items"""
        line_items = self.line_items.all()
        self.subtotal = sum(item.total for item in line_items)
        self.tax_amount = (self.subtotal * self.tax_rate / Decimal('100.00')).quantize(Decimal('0.01'))
        self.total = self.subtotal + self.tax_amount + self.late_fee_applied

    def update_status(self):
        """Update invoice status based on payment amount"""
        if self.status == 'cancelled':
            return

        if self.amount_paid >= self.total:
            self.status = 'paid'
        elif self.amount_paid > 0:
            self.status = 'partially_paid'
        elif self.is_overdue:
            self.status = 'overdue'
        elif self.status == 'draft':
            pass  # Keep as draft
        else:
            self.status = 'sent'

    def save(self, *args, **kwargs):
        """Override save to auto-update status"""
        self.update_status()
        super().save(*args, **kwargs)


class InvoiceLineItem(models.Model):
    """
    Individual line item on an invoice.
    Can represent enrollment fees, late fees, discounts, etc.
    """

    ITEM_TYPE_CHOICES = [
        ('enrollment', 'Enrollment Fee'),
        ('late_fee', 'Late Fee'),
        ('discount', 'Discount'),
        ('adjustment', 'Adjustment'),
        ('other', 'Other'),
    ]

    invoice = models.ForeignKey(
        Invoice,
        on_delete=models.CASCADE,
        related_name='line_items',
        help_text="Invoice this line item belongs to"
    )

    # Item details
    item_type = models.CharField(
        max_length=20,
        choices=ITEM_TYPE_CHOICES,
        help_text="Type of line item"
    )
    description = models.CharField(max_length=500, help_text="Description of the item")

    # Optional link to enrollment (if this line item is for an enrollment)
    enrollment = models.ForeignKey(
        'scheduling.Enrollment',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='invoice_line_items',
        help_text="Enrollment this line item is for (optional)"
    )

    # Pricing
    quantity = models.IntegerField(
        default=1,
        validators=[MinValueValidator(1)],
        help_text="Quantity"
    )
    unit_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Price per unit"
    )
    total = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Total for this line item (quantity × unit_price)"
    )

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['invoice', 'item_type', 'description']
        indexes = [
            models.Index(fields=['invoice']),
            models.Index(fields=['enrollment']),
            models.Index(fields=['item_type']),
        ]

    def __str__(self):
        return f"{self.invoice.invoice_number} - {self.description} (${self.total})"

    def save(self, *args, **kwargs):
        """Calculate total before saving"""
        self.total = Decimal(str(self.quantity)) * self.unit_price
        super().save(*args, **kwargs)


class Payment(models.Model):
    """
    Payment record for an invoice.
    Tracks individual payments made toward invoices.
    """

    PAYMENT_METHOD_CHOICES = [
        ('cash', 'Cash'),
        ('check', 'Check'),
        ('credit_card', 'Credit Card'),
        ('debit_card', 'Debit Card'),
        ('bank_transfer', 'Bank Transfer'),
        ('paypal', 'PayPal'),
        ('stripe', 'Stripe'),
        ('other', 'Other'),
    ]

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
        ('cancelled', 'Cancelled'),
    ]

    # Payment identification
    payment_reference = models.CharField(
        max_length=20,
        unique=True,
        default=generate_payment_reference,
        help_text="Unique payment reference (auto-generated)"
    )

    # Link to Invoice
    invoice = models.ForeignKey(
        Invoice,
        on_delete=models.PROTECT,
        related_name='payments',
        help_text="Invoice this payment is for"
    )

    # Payment details
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0.01)],
        help_text="Payment amount"
    )
    payment_date = models.DateField(help_text="Date payment was received")
    payment_method = models.CharField(
        max_length=20,
        choices=PAYMENT_METHOD_CHOICES,
        help_text="Payment method used"
    )

    # Status
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='completed',
        help_text="Payment status"
    )

    # External transaction reference (e.g., Stripe transaction ID)
    transaction_id = models.CharField(
        max_length=200,
        blank=True,
        help_text="External transaction ID (e.g., from payment gateway)"
    )

    # Staff tracking
    received_by = models.ForeignKey(
        'accounts.Staff',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='payments_received',
        help_text="Staff member who received/processed this payment"
    )

    # Additional information
    notes = models.TextField(blank=True, help_text="Notes about this payment")

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-payment_date', '-payment_reference']
        indexes = [
            models.Index(fields=['payment_reference']),
            models.Index(fields=['invoice', 'status']),
            models.Index(fields=['payment_date']),
            models.Index(fields=['status']),
            models.Index(fields=['transaction_id']),
        ]

    def __str__(self):
        return f"{self.payment_reference} - {self.invoice.invoice_number} (${self.amount})"

    def save(self, *args, **kwargs):
        """Update invoice amount_paid when payment is saved"""
        super().save(*args, **kwargs)

        # Recalculate invoice amount_paid from all completed payments
        if self.status == 'completed':
            completed_payments = self.invoice.payments.filter(status='completed')
            self.invoice.amount_paid = sum(p.amount for p in completed_payments)
            self.invoice.save()


class PaymentPlan(models.Model):
    """
    Payment plan for an account.
    Allows customers to pay invoices in installments.
    """

    STATUS_CHOICES = [
        ('active', 'Active'),
        ('completed', 'Completed'),
        ('defaulted', 'Defaulted'),
        ('cancelled', 'Cancelled'),
    ]

    FREQUENCY_CHOICES = [
        ('weekly', 'Weekly'),
        ('biweekly', 'Bi-Weekly'),
        ('monthly', 'Monthly'),
    ]

    # Plan identification
    account = models.ForeignKey(
        'accounts.Account',
        on_delete=models.PROTECT,
        related_name='payment_plans',
        help_text="Account this payment plan belongs to"
    )

    # Optional link to specific invoice
    invoice = models.ForeignKey(
        Invoice,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='payment_plans',
        help_text="Invoice this payment plan is for (optional)"
    )

    # Plan details
    total_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0.01)],
        help_text="Total amount to be paid"
    )
    installment_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0.01)],
        help_text="Amount per installment"
    )
    frequency = models.CharField(
        max_length=20,
        choices=FREQUENCY_CHOICES,
        help_text="Payment frequency"
    )
    number_of_installments = models.IntegerField(
        validators=[MinValueValidator(2)],
        help_text="Total number of installments"
    )

    # Dates
    start_date = models.DateField(help_text="Date payment plan starts")
    end_date = models.DateField(help_text="Expected completion date")
    first_payment_date = models.DateField(help_text="Date of first installment")

    # Status
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='active',
        help_text="Payment plan status"
    )
    amount_paid = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00,
        validators=[MinValueValidator(0)],
        help_text="Amount paid so far"
    )
    installments_paid = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0)],
        help_text="Number of installments paid"
    )

    # Additional information
    notes = models.TextField(blank=True, help_text="Notes about this payment plan")

    # Approval
    approved_by = models.ForeignKey(
        'accounts.Staff',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='payment_plans_approved',
        help_text="Staff member who approved this payment plan"
    )

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['account', 'status']),
            models.Index(fields=['status']),
            models.Index(fields=['start_date']),
            models.Index(fields=['invoice']),
        ]

    def __str__(self):
        return f"Payment Plan for {self.account.account_code} - ${self.total_amount} ({self.status})"

    @property
    def amount_outstanding(self):
        """Returns the outstanding balance"""
        return max(Decimal('0.00'), self.total_amount - self.amount_paid)

    @property
    def is_completed(self):
        """Returns True if payment plan is fully paid"""
        return self.amount_paid >= self.total_amount

    @property
    def installments_remaining(self):
        """Returns number of installments remaining"""
        return max(0, self.number_of_installments - self.installments_paid)

    def update_status(self):
        """Update payment plan status based on payments"""
        if self.is_completed:
            self.status = 'completed'
        elif self.status == 'active':
            # Check if defaulted (missed payment)
            from django.utils import timezone
            from dateutil.relativedelta import relativedelta

            today = timezone.now().date()

            # Calculate expected payment date based on frequency
            if self.frequency == 'weekly':
                delta = relativedelta(weeks=self.installments_paid)
            elif self.frequency == 'biweekly':
                delta = relativedelta(weeks=self.installments_paid * 2)
            else:  # monthly
                delta = relativedelta(months=self.installments_paid)

            expected_payment_date = self.first_payment_date + delta

            # If expected payment date is more than 7 days past and not paid, mark as defaulted
            if expected_payment_date < today and self.installments_paid < self.number_of_installments:
                grace_period_end = expected_payment_date + relativedelta(days=7)
                if today > grace_period_end:
                    self.status = 'defaulted'

    def save(self, *args, **kwargs):
        """Override save to auto-update status"""
        self.update_status()
        super().save(*args, **kwargs)
