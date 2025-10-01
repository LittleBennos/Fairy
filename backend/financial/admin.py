from django.contrib import admin
from .models import Invoice, InvoiceLineItem, Payment, PaymentPlan


class InvoiceLineItemInline(admin.TabularInline):
    model = InvoiceLineItem
    extra = 1
    fields = ['item_type', 'description', 'enrollment', 'quantity', 'unit_price', 'total']
    readonly_fields = ['total']


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = [
        'invoice_number', 'account', 'issue_date', 'due_date',
        'total', 'amount_paid', 'amount_outstanding', 'status', 'is_overdue'
    ]
    list_filter = ['status', 'issue_date', 'due_date', 'term']
    search_fields = [
        'invoice_number',
        'account__account_code',
        'account__student__person__given_name',
        'account__student__person__family_name',
        'billing_contact_name'
    ]
    readonly_fields = [
        'invoice_number', 'amount_paid', 'amount_outstanding',
        'is_paid', 'is_overdue', 'created_at', 'updated_at'
    ]
    autocomplete_fields = ['account', 'term']
    inlines = [InvoiceLineItemInline]
    date_hierarchy = 'issue_date'

    fieldsets = (
        ('Invoice Details', {
            'fields': ('invoice_number', 'account', 'term', 'status')
        }),
        ('Billing Information', {
            'fields': ('billing_contact_name', 'billing_email', 'billing_address')
        }),
        ('Dates', {
            'fields': ('issue_date', 'due_date')
        }),
        ('Amounts', {
            'fields': (
                'subtotal', 'tax_rate', 'tax_amount', 'late_fee_applied',
                'total', 'amount_paid', 'amount_outstanding'
            )
        }),
        ('Status', {
            'fields': ('is_paid', 'is_overdue')
        }),
        ('Notes', {
            'fields': ('notes', 'customer_notes')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    actions = ['mark_as_sent', 'calculate_totals']

    def mark_as_sent(self, request, queryset):
        updated = queryset.filter(status='draft').update(status='sent')
        self.message_user(request, f'{updated} invoices marked as sent')
    mark_as_sent.short_description = 'Mark selected invoices as sent'

    def calculate_totals(self, request, queryset):
        for invoice in queryset:
            invoice.calculate_totals()
            invoice.save()
        self.message_user(request, f'{queryset.count()} invoices recalculated')
    calculate_totals.short_description = 'Recalculate totals from line items'


@admin.register(InvoiceLineItem)
class InvoiceLineItemAdmin(admin.ModelAdmin):
    list_display = ['invoice', 'item_type', 'description', 'enrollment', 'quantity', 'unit_price', 'total']
    list_filter = ['item_type']
    search_fields = ['invoice__invoice_number', 'description']
    readonly_fields = ['total', 'created_at', 'updated_at']
    autocomplete_fields = ['invoice', 'enrollment']

    fieldsets = (
        ('Line Item Details', {
            'fields': ('invoice', 'item_type', 'description', 'enrollment')
        }),
        ('Pricing', {
            'fields': ('quantity', 'unit_price', 'total')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = [
        'payment_reference', 'invoice', 'amount', 'payment_date',
        'payment_method', 'status', 'received_by'
    ]
    list_filter = ['status', 'payment_method', 'payment_date']
    search_fields = [
        'payment_reference',
        'invoice__invoice_number',
        'invoice__account__account_code',
        'transaction_id'
    ]
    readonly_fields = ['payment_reference', 'created_at', 'updated_at']
    autocomplete_fields = ['invoice', 'received_by']
    date_hierarchy = 'payment_date'

    fieldsets = (
        ('Payment Details', {
            'fields': ('payment_reference', 'invoice', 'amount', 'payment_date')
        }),
        ('Payment Method', {
            'fields': ('payment_method', 'transaction_id')
        }),
        ('Status', {
            'fields': ('status',)
        }),
        ('Staff Tracking', {
            'fields': ('received_by',)
        }),
        ('Notes', {
            'fields': ('notes',)
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def save_model(self, request, obj, form, change):
        """Automatically set received_by to current staff member"""
        if not change and hasattr(request.user, 'person') and hasattr(request.user.person, 'staff'):
            obj.received_by = request.user.person.staff
        super().save_model(request, obj, form, change)


@admin.register(PaymentPlan)
class PaymentPlanAdmin(admin.ModelAdmin):
    list_display = [
        'account', 'total_amount', 'installment_amount', 'frequency',
        'number_of_installments', 'installments_paid', 'status'
    ]
    list_filter = ['status', 'frequency', 'start_date']
    search_fields = [
        'account__account_code',
        'account__student__person__given_name',
        'account__student__person__family_name'
    ]
    readonly_fields = [
        'amount_outstanding', 'is_completed', 'installments_remaining',
        'created_at', 'updated_at'
    ]
    autocomplete_fields = ['account', 'invoice', 'approved_by']
    date_hierarchy = 'start_date'

    fieldsets = (
        ('Payment Plan Details', {
            'fields': ('account', 'invoice', 'total_amount')
        }),
        ('Installment Details', {
            'fields': (
                'installment_amount', 'frequency', 'number_of_installments',
                'installments_paid', 'installments_remaining'
            )
        }),
        ('Dates', {
            'fields': ('start_date', 'end_date', 'first_payment_date')
        }),
        ('Status & Progress', {
            'fields': ('status', 'amount_paid', 'amount_outstanding', 'is_completed')
        }),
        ('Approval', {
            'fields': ('approved_by',)
        }),
        ('Notes', {
            'fields': ('notes',)
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def save_model(self, request, obj, form, change):
        """Automatically set approved_by to current staff member"""
        if not change and hasattr(request.user, 'person') and hasattr(request.user.person, 'staff'):
            obj.approved_by = request.user.person.staff
        super().save_model(request, obj, form, change)
