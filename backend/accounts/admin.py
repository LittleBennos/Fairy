from django.contrib import admin
from .models import Student, Guardian, BillingContact, Staff, Account


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ['person', 'status', 'start_date', 'school_attending', 'photo_consent']
    list_filter = ['status', 'photo_consent']
    search_fields = ['person__given_name', 'person__family_name', 'person__person_code', 'school_attending']
    readonly_fields = ['created_at', 'updated_at']
    autocomplete_fields = ['person']

    fieldsets = (
        ('Person', {
            'fields': ('person',)
        }),
        ('Student Information', {
            'fields': ('status', 'start_date', 'school_attending', 'year_level')
        }),
        ('Medical Information', {
            'fields': ('medical_notes', 'allergies'),
            'classes': ('collapse',)
        }),
        ('Permissions', {
            'fields': ('photo_consent',)
        }),
        ('Notes', {
            'fields': ('notes',)
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Guardian)
class GuardianAdmin(admin.ModelAdmin):
    list_display = ['person', 'authorized_for_pickup', 'communication_preference']
    list_filter = ['authorized_for_pickup', 'communication_preference']
    search_fields = ['person__given_name', 'person__family_name', 'person__person_code']
    readonly_fields = ['created_at', 'updated_at']
    autocomplete_fields = ['person']

    fieldsets = (
        ('Person', {
            'fields': ('person',)
        }),
        ('Guardian Information', {
            'fields': ('authorized_for_pickup', 'communication_preference')
        }),
        ('Notes', {
            'fields': ('relationship_notes',)
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(BillingContact)
class BillingContactAdmin(admin.ModelAdmin):
    list_display = ['person', 'payment_method', 'billing_preference']
    list_filter = ['payment_method', 'billing_preference']
    search_fields = ['person__given_name', 'person__family_name', 'person__person_code']
    readonly_fields = ['created_at', 'updated_at', 'full_billing_address']
    autocomplete_fields = ['person']

    fieldsets = (
        ('Person', {
            'fields': ('person',)
        }),
        ('Billing Address Override', {
            'fields': (
                'billing_address_line1', 'billing_address_line2',
                'billing_city', 'billing_state', 'billing_postal_code',
                'billing_country', 'full_billing_address'
            ),
            'description': 'Override person address for billing purposes (optional)'
        }),
        ('Payment Preferences', {
            'fields': ('payment_method', 'billing_preference')
        }),
        ('Notes', {
            'fields': ('payment_notes',)
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Staff)
class StaffAdmin(admin.ModelAdmin):
    list_display = ['person', 'role', 'employment_status', 'hire_date', 'termination_date']
    list_filter = ['role', 'employment_status']
    search_fields = ['person__given_name', 'person__family_name', 'person__person_code', 'specialties']
    readonly_fields = ['created_at', 'updated_at']
    autocomplete_fields = ['person']

    fieldsets = (
        ('Person', {
            'fields': ('person',)
        }),
        ('Employment Details', {
            'fields': ('role', 'employment_status', 'hire_date', 'termination_date')
        }),
        ('Professional Information', {
            'fields': ('bio', 'specialties', 'certifications'),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    list_display = ['account_code', 'student', 'guardian', 'billing_contact', 'status', 'start_date']
    list_filter = ['status']
    search_fields = [
        'account_code',
        'student__person__given_name',
        'student__person__family_name',
        'guardian__person__given_name',
        'guardian__person__family_name'
    ]
    readonly_fields = ['account_code', 'created_at', 'updated_at']
    autocomplete_fields = ['student', 'guardian', 'billing_contact']

    fieldsets = (
        ('Account Code', {
            'fields': ('account_code',)
        }),
        ('Roles', {
            'fields': ('student', 'guardian', 'billing_contact'),
            'description': 'Link student, guardian, and billing contact to this account'
        }),
        ('Account Status', {
            'fields': ('status', 'start_date', 'end_date')
        }),
        ('Notes', {
            'fields': ('notes',)
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
