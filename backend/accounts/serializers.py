from rest_framework import serializers
from people.models import Person
from people.serializers import PersonSerializer
from .models import Student, Guardian, BillingContact, Staff, Account


class StudentSerializer(serializers.ModelSerializer):
    """
    Serializer for Student model with nested Person data.
    """
    person = PersonSerializer(read_only=True)
    person_id = serializers.PrimaryKeyRelatedField(
        queryset=Person.objects.all(),
        source='person',
        write_only=True,
        help_text="ID of the person to link as student"
    )

    # Computed fields from Person
    full_name = serializers.CharField(source='person.full_name', read_only=True)
    display_name = serializers.CharField(source='person.display_name', read_only=True)
    date_of_birth = serializers.DateField(source='person.date_of_birth', read_only=True)
    email = serializers.EmailField(source='person.email', read_only=True)
    phone = serializers.CharField(source='person.phone', read_only=True)

    class Meta:
        model = Student
        fields = [
            'id',
            'person',
            'person_id',
            'full_name',
            'display_name',
            'date_of_birth',
            'email',
            'phone',
            'medical_notes',
            'allergies',
            'photo_consent',
            'school_attending',
            'year_level',
            'status',
            'start_date',
            'notes',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class StudentListSerializer(serializers.ModelSerializer):
    """
    Lightweight serializer for listing students.
    """
    full_name = serializers.CharField(source='person.full_name', read_only=True)
    person_code = serializers.CharField(source='person.person_code', read_only=True)
    date_of_birth = serializers.DateField(source='person.date_of_birth', read_only=True)

    class Meta:
        model = Student
        fields = [
            'id',
            'person_code',
            'full_name',
            'date_of_birth',
            'status',
            'school_attending',
            'start_date',
        ]


class GuardianSerializer(serializers.ModelSerializer):
    """
    Serializer for Guardian model with nested Person data.
    """
    person = PersonSerializer(read_only=True)
    person_id = serializers.PrimaryKeyRelatedField(
        queryset=Person.objects.all(),
        source='person',
        write_only=True,
        help_text="ID of the person to link as guardian"
    )

    # Computed fields from Person
    full_name = serializers.CharField(source='person.full_name', read_only=True)
    display_name = serializers.CharField(source='person.display_name', read_only=True)
    email = serializers.EmailField(source='person.email', read_only=True)
    phone = serializers.CharField(source='person.phone', read_only=True)
    address = serializers.CharField(source='person.full_address', read_only=True)

    class Meta:
        model = Guardian
        fields = [
            'id',
            'person',
            'person_id',
            'full_name',
            'display_name',
            'email',
            'phone',
            'address',
            'authorized_for_pickup',
            'communication_preference',
            'relationship_notes',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class GuardianListSerializer(serializers.ModelSerializer):
    """
    Lightweight serializer for listing guardians.
    """
    full_name = serializers.CharField(source='person.full_name', read_only=True)
    person_code = serializers.CharField(source='person.person_code', read_only=True)
    email = serializers.EmailField(source='person.email', read_only=True)
    phone = serializers.CharField(source='person.phone', read_only=True)

    class Meta:
        model = Guardian
        fields = [
            'id',
            'person_code',
            'full_name',
            'email',
            'phone',
            'authorized_for_pickup',
            'communication_preference',
        ]


class BillingContactSerializer(serializers.ModelSerializer):
    """
    Serializer for BillingContact model.
    """
    person = PersonSerializer(read_only=True)
    person_id = serializers.PrimaryKeyRelatedField(
        queryset=Person.objects.all(),
        source='person',
        write_only=True,
        help_text="ID of the person to link as billing contact"
    )

    # Computed fields
    full_name = serializers.CharField(source='person.full_name', read_only=True)
    email = serializers.EmailField(source='person.email', read_only=True)
    billing_address = serializers.CharField(source='billing_full_address', read_only=True)

    class Meta:
        model = BillingContact
        fields = [
            'id',
            'person',
            'person_id',
            'full_name',
            'email',
            'billing_address_line1',
            'billing_address_line2',
            'billing_city',
            'billing_state',
            'billing_postal_code',
            'billing_country',
            'billing_address',
            'preferred_payment_method',
            'payment_terms',
            'invoice_delivery_method',
            'tax_exempt',
            'tax_id',
            'notes',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class StaffSerializer(serializers.ModelSerializer):
    """
    Serializer for Staff model.
    """
    person = PersonSerializer(read_only=True)
    person_id = serializers.PrimaryKeyRelatedField(
        queryset=Person.objects.all(),
        source='person',
        write_only=True,
        help_text="ID of the person to link as staff"
    )

    # Computed fields
    full_name = serializers.CharField(source='person.full_name', read_only=True)
    email = serializers.EmailField(source='person.email', read_only=True)
    phone = serializers.CharField(source='person.phone', read_only=True)

    class Meta:
        model = Staff
        fields = [
            'id',
            'person',
            'person_id',
            'full_name',
            'email',
            'phone',
            'staff_type',
            'employee_id',
            'start_date',
            'end_date',
            'can_teach',
            'bio',
            'notes',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class AccountSerializer(serializers.ModelSerializer):
    """
    Serializer for Account model with nested roles.
    """
    student = StudentSerializer(read_only=True)
    guardian = GuardianSerializer(read_only=True)
    billing_contact = BillingContactSerializer(read_only=True)

    # For creating/updating relationships
    student_id = serializers.PrimaryKeyRelatedField(
        queryset=Student.objects.all(),
        source='student',
        write_only=True,
        required=False,
        allow_null=True
    )
    guardian_id = serializers.PrimaryKeyRelatedField(
        queryset=Guardian.objects.all(),
        source='guardian',
        write_only=True,
        required=False,
        allow_null=True
    )
    billing_contact_id = serializers.PrimaryKeyRelatedField(
        queryset=BillingContact.objects.all(),
        source='billing_contact',
        write_only=True,
        required=False,
        allow_null=True
    )

    class Meta:
        model = Account
        fields = [
            'id',
            'account_code',
            'student',
            'student_id',
            'guardian',
            'guardian_id',
            'billing_contact',
            'billing_contact_id',
            'status',
            'notes',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'account_code', 'created_at', 'updated_at']


class AccountListSerializer(serializers.ModelSerializer):
    """
    Lightweight serializer for listing accounts.
    """
    student_name = serializers.CharField(source='student.person.full_name', read_only=True)
    guardian_name = serializers.CharField(source='guardian.person.full_name', read_only=True)

    class Meta:
        model = Account
        fields = [
            'id',
            'account_code',
            'student_name',
            'guardian_name',
            'status',
            'created_at',
        ]