from django.contrib import admin
from .models import Genre, ClassType, Evaluation, Term, ClassInstance, Enrollment, AttendanceRecord


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'is_active']
    list_filter = ['is_active']
    search_fields = ['name', 'code', 'description']
    readonly_fields = ['created_at', 'updated_at']

    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'code', 'description')
        }),
        ('Status', {
            'fields': ('is_active', 'notes')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(ClassType)
class ClassTypeAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'genre', 'level', 'min_age', 'max_age', 'price_per_term', 'is_active']
    list_filter = ['genre', 'level', 'is_active']
    search_fields = ['name', 'code', 'description']
    readonly_fields = ['created_at', 'updated_at']
    autocomplete_fields = ['genre']

    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'code', 'genre', 'level', 'description')
        }),
        ('Age Requirements', {
            'fields': ('min_age', 'max_age')
        }),
        ('Duration & Pricing', {
            'fields': ('duration_minutes', 'price_per_term')
        }),
        ('Status', {
            'fields': ('is_active', 'notes')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Evaluation)
class EvaluationAdmin(admin.ModelAdmin):
    list_display = ['student', 'genre', 'level_achieved', 'evaluation_date', 'evaluated_by', 'expires_on', 'is_expired']
    list_filter = ['genre', 'level_achieved', 'evaluation_date']
    search_fields = ['student__person__given_name', 'student__person__family_name', 'genre__name', 'notes']
    readonly_fields = ['is_expired', 'created_at', 'updated_at']
    autocomplete_fields = ['student', 'genre', 'evaluated_by']
    date_hierarchy = 'evaluation_date'

    fieldsets = (
        ('Evaluation Details', {
            'fields': ('student', 'genre', 'level_achieved', 'evaluation_date')
        }),
        ('Evaluator', {
            'fields': ('evaluated_by',)
        }),
        ('Expiry', {
            'fields': ('expires_on', 'is_expired')
        }),
        ('Notes', {
            'fields': ('notes',)
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Term)
class TermAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'start_date', 'end_date', 'is_active']
    list_filter = ['is_active']
    search_fields = ['name', 'code']
    readonly_fields = ['created_at', 'updated_at']

    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'code')
        }),
        ('Dates', {
            'fields': ('start_date', 'end_date', 'enrollment_open_date', 'enrollment_close_date')
        }),
        ('Status', {
            'fields': ('is_active', 'notes')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(ClassInstance)
class ClassInstanceAdmin(admin.ModelAdmin):
    list_display = ['class_type', 'term', 'teacher', 'day_of_week', 'start_time', 'room', 'max_students', 'status']
    list_filter = ['term', 'day_of_week', 'status', 'class_type__genre']
    search_fields = ['class_type__name', 'term__name', 'room']
    readonly_fields = ['created_at', 'updated_at', 'current_enrollment_count', 'is_full', 'available_spots']
    autocomplete_fields = ['class_type', 'term', 'teacher']

    fieldsets = (
        ('Class Details', {
            'fields': ('class_type', 'term', 'teacher')
        }),
        ('Schedule', {
            'fields': ('day_of_week', 'start_time', 'end_time', 'room')
        }),
        ('Capacity', {
            'fields': ('max_students', 'current_enrollment_count', 'is_full', 'available_spots')
        }),
        ('Status', {
            'fields': ('status', 'notes')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ['account', 'class_instance', 'status', 'enrollment_date', 'amount_paid', 'amount_outstanding']
    list_filter = ['status', 'enrollment_date']
    search_fields = [
        'account__student__person__given_name',
        'account__student__person__family_name',
        'account__account_code',
        'class_instance__class_type__name'
    ]
    readonly_fields = ['enrollment_date', 'created_at', 'updated_at', 'is_active_enrollment', 'total_cost', 'amount_outstanding']
    autocomplete_fields = ['account', 'class_instance']

    fieldsets = (
        ('Enrollment Details', {
            'fields': ('account', 'class_instance', 'status', 'enrollment_date')
        }),
        ('Status Dates', {
            'fields': ('trial_date', 'active_date', 'withdrawn_date', 'completed_date')
        }),
        ('Financial', {
            'fields': ('amount_paid', 'total_cost', 'amount_outstanding')
        }),
        ('Metadata', {
            'fields': ('is_active_enrollment', 'notes', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(AttendanceRecord)
class AttendanceRecordAdmin(admin.ModelAdmin):
    list_display = ['student', 'class_instance', 'date', 'status', 'marked_by', 'marked_at']
    list_filter = ['status', 'date', 'class_instance__class_type__genre']
    search_fields = [
        'student__person__given_name',
        'student__person__family_name',
        'class_instance__class_type__name',
        'notes'
    ]
    readonly_fields = ['marked_at', 'created_at', 'updated_at']
    autocomplete_fields = ['student', 'class_instance', 'enrollment', 'marked_by']
    date_hierarchy = 'date'

    fieldsets = (
        ('Attendance Details', {
            'fields': ('class_instance', 'student', 'enrollment', 'date', 'status')
        }),
        ('Staff Tracking', {
            'fields': ('marked_by', 'marked_at')
        }),
        ('Additional Information', {
            'fields': ('notes',)
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def save_model(self, request, obj, form, change):
        """Automatically set marked_by to current staff member"""
        # Try to get staff object from current user
        if hasattr(request.user, 'person') and hasattr(request.user.person, 'staff'):
            obj.marked_by = request.user.person.staff
        super().save_model(request, obj, form, change)
