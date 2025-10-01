from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters import rest_framework as filters
from .models import Student, Guardian, BillingContact, Staff, Account
from .serializers import (
    StudentSerializer, StudentListSerializer,
    GuardianSerializer, GuardianListSerializer,
    BillingContactSerializer,
    StaffSerializer,
    AccountSerializer, AccountListSerializer,
)


class StudentFilter(filters.FilterSet):
    """Filter for Student queries"""
    status = filters.ChoiceFilter(choices=Student.STATUS_CHOICES)
    school = filters.CharFilter(field_name='school_attending', lookup_expr='icontains')
    name = filters.CharFilter(field_name='person__given_name', lookup_expr='icontains')

    class Meta:
        model = Student
        fields = ['status', 'photo_consent']


class StudentViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing students.
    """
    queryset = Student.objects.select_related('person').all()
    serializer_class = StudentSerializer
    permission_classes = [IsAuthenticated]
    filterset_class = StudentFilter
    search_fields = ['person__given_name', 'person__family_name', 'person__person_code', 'school_attending']
    ordering_fields = ['person__family_name', 'person__given_name', 'status', 'start_date']
    ordering = ['person__family_name', 'person__given_name']

    def get_serializer_class(self):
        """Use lightweight serializer for list view"""
        if self.action == 'list':
            return StudentListSerializer
        return StudentSerializer

    @action(detail=True, methods=['get'])
    def enrollments(self, request, pk=None):
        """Get all enrollments for a student"""
        student = self.get_object()
        # Get enrollments through the account relationship
        if hasattr(student, 'accounts'):
            enrollments = []
            for account in student.accounts.all():
                enrollments.extend(account.enrollments.all())

            from scheduling.serializers import EnrollmentSerializer
            serializer = EnrollmentSerializer(enrollments, many=True)
            return Response(serializer.data)
        return Response([])

    @action(detail=True, methods=['get'])
    def evaluations(self, request, pk=None):
        """Get all evaluations for a student"""
        student = self.get_object()
        evaluations = student.evaluations.all().order_by('-evaluated_at')

        from scheduling.serializers import EvaluationSerializer
        serializer = EvaluationSerializer(evaluations, many=True)
        return Response(serializer.data)


class GuardianFilter(filters.FilterSet):
    """Filter for Guardian queries"""
    authorized_pickup = filters.BooleanFilter(field_name='authorized_for_pickup')
    preference = filters.ChoiceFilter(field_name='communication_preference', choices=Guardian.COMM_PREFERENCE_CHOICES)

    class Meta:
        model = Guardian
        fields = ['authorized_for_pickup', 'communication_preference']


class GuardianViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing guardians.
    """
    queryset = Guardian.objects.select_related('person').all()
    serializer_class = GuardianSerializer
    permission_classes = [IsAuthenticated]
    filterset_class = GuardianFilter
    search_fields = ['person__given_name', 'person__family_name', 'person__email', 'person__person_code']
    ordering_fields = ['person__family_name', 'person__given_name']
    ordering = ['person__family_name', 'person__given_name']

    def get_serializer_class(self):
        """Use lightweight serializer for list view"""
        if self.action == 'list':
            return GuardianListSerializer
        return GuardianSerializer

    @action(detail=True, methods=['get'])
    def students(self, request, pk=None):
        """Get all students associated with this guardian"""
        guardian = self.get_object()
        students = []

        # Get students through accounts
        for account in guardian.accounts.all():
            if account.student:
                students.append(account.student)

        serializer = StudentSerializer(students, many=True)
        return Response(serializer.data)


class BillingContactViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing billing contacts.
    """
    queryset = BillingContact.objects.select_related('person').all()
    serializer_class = BillingContactSerializer
    permission_classes = [IsAuthenticated]
    search_fields = ['person__given_name', 'person__family_name', 'person__email']
    ordering_fields = ['person__family_name', 'person__given_name']
    ordering = ['person__family_name', 'person__given_name']

    @action(detail=True, methods=['get'])
    def invoices(self, request, pk=None):
        """Get all invoices for this billing contact"""
        billing_contact = self.get_object()
        invoices = []

        # Get invoices through accounts
        for account in billing_contact.accounts.all():
            invoices.extend(account.invoices.all())

        from financial.serializers import InvoiceSerializer
        serializer = InvoiceSerializer(invoices, many=True)
        return Response(serializer.data)


class StaffFilter(filters.FilterSet):
    """Filter for Staff queries"""
    can_teach = filters.BooleanFilter()
    staff_type = filters.ChoiceFilter(field_name='staff_type', choices=[
        ('teacher', 'Teacher'),
        ('admin', 'Administrator'),
        ('support', 'Support Staff'),
    ])

    class Meta:
        model = Staff
        fields = ['can_teach', 'staff_type']


class StaffViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing staff members.
    """
    queryset = Staff.objects.select_related('person').all()
    serializer_class = StaffSerializer
    permission_classes = [IsAuthenticated]
    filterset_class = StaffFilter
    search_fields = ['person__given_name', 'person__family_name', 'employee_id']
    ordering_fields = ['person__family_name', 'person__given_name', 'staff_type']
    ordering = ['person__family_name', 'person__given_name']

    @action(detail=False, methods=['get'])
    def teachers(self, request):
        """Get all staff members who can teach"""
        teachers = self.queryset.filter(can_teach=True)
        serializer = self.get_serializer(teachers, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def classes(self, request, pk=None):
        """Get all classes taught by this staff member"""
        staff = self.get_object()
        classes = staff.classes_taught.all()

        from scheduling.serializers import ClassInstanceSerializer
        serializer = ClassInstanceSerializer(classes, many=True)
        return Response(serializer.data)


class AccountFilter(filters.FilterSet):
    """Filter for Account queries"""
    status = filters.ChoiceFilter(choices=[
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('suspended', 'Suspended'),
    ])
    has_student = filters.BooleanFilter(field_name='student', lookup_expr='isnull', exclude=True)
    has_guardian = filters.BooleanFilter(field_name='guardian', lookup_expr='isnull', exclude=True)

    class Meta:
        model = Account
        fields = ['status']


class AccountViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing accounts.
    Accounts group students, guardians, and billing contacts.
    """
    queryset = Account.objects.select_related(
        'student__person',
        'guardian__person',
        'billing_contact__person'
    ).all()
    serializer_class = AccountSerializer
    permission_classes = [IsAuthenticated]
    filterset_class = AccountFilter
    search_fields = ['account_code', 'student__person__given_name', 'guardian__person__family_name']
    ordering_fields = ['created_at', 'status']
    ordering = ['-created_at']

    def get_serializer_class(self):
        """Use lightweight serializer for list view"""
        if self.action == 'list':
            return AccountListSerializer
        return AccountSerializer

    @action(detail=True, methods=['get'])
    def enrollments(self, request, pk=None):
        """Get all enrollments for this account"""
        account = self.get_object()
        enrollments = account.enrollments.all()

        from scheduling.serializers import EnrollmentSerializer
        serializer = EnrollmentSerializer(enrollments, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def invoices(self, request, pk=None):
        """Get all invoices for this account"""
        account = self.get_object()
        invoices = account.invoices.all().order_by('-invoice_date')

        from financial.serializers import InvoiceSerializer
        serializer = InvoiceSerializer(invoices, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def balance(self, request, pk=None):
        """Get account balance summary"""
        account = self.get_object()

        # Calculate total invoiced
        total_invoiced = 0
        total_paid = 0

        for invoice in account.invoices.all():
            total_invoiced += invoice.total_amount
            for payment in invoice.payments.all():
                total_paid += payment.amount

        balance = total_invoiced - total_paid

        return Response({
            'total_invoiced': total_invoiced,
            'total_paid': total_paid,
            'balance': balance,
            'has_outstanding': balance > 0
        })