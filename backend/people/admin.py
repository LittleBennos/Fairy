from django.contrib import admin
from .models import Person


@admin.register(Person)
class PersonAdmin(admin.ModelAdmin):
    list_display = ['person_code', 'full_name', 'email', 'phone', 'date_of_birth', 'is_active']
    list_filter = ['is_active', 'country']
    search_fields = ['person_code', 'given_name', 'family_name', 'preferred_name', 'email', 'phone']
    readonly_fields = ['person_code', 'created_at', 'updated_at', 'full_name', 'display_name', 'full_address']

    fieldsets = (
        ('Basic Information', {
            'fields': ('person_code', 'given_name', 'family_name', 'preferred_name', 'date_of_birth')
        }),
        ('Display Names', {
            'fields': ('full_name', 'display_name'),
            'classes': ('collapse',)
        }),
        ('Contact Information', {
            'fields': ('email', 'phone', 'phone_secondary')
        }),
        ('Address', {
            'fields': (
                'address_line1', 'address_line2', 'city', 'state',
                'postal_code', 'country', 'full_address'
            )
        }),
        ('Emergency Contact', {
            'fields': ('emergency_contact_name', 'emergency_contact_phone'),
            'classes': ('collapse',)
        }),
        ('User Account', {
            'fields': ('user',),
            'description': 'Link to User account for portal access (optional)'
        }),
        ('Status & Notes', {
            'fields': ('is_active', 'notes')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
