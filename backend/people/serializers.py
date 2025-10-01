from rest_framework import serializers
from .models import Person


class PersonSerializer(serializers.ModelSerializer):
    """
    Full serializer for Person model.
    """
    full_name = serializers.ReadOnlyField()
    display_name = serializers.ReadOnlyField()
    full_address = serializers.ReadOnlyField()

    class Meta:
        model = Person
        fields = [
            'id',
            'person_code',
            'given_name',
            'family_name',
            'preferred_name',
            'full_name',
            'display_name',
            'date_of_birth',
            'email',
            'phone',
            'phone_secondary',
            'address_line1',
            'address_line2',
            'city',
            'state',
            'postal_code',
            'country',
            'full_address',
            'emergency_contact_name',
            'emergency_contact_phone',
            'notes',
            'is_active',
            'user',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'person_code', 'created_at', 'updated_at']


class PersonListSerializer(serializers.ModelSerializer):
    """
    Lightweight serializer for Person listings.
    """
    full_name = serializers.ReadOnlyField()

    class Meta:
        model = Person
        fields = [
            'id',
            'person_code',
            'full_name',
            'email',
            'phone',
            'is_active',
        ]


class PersonCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating a new Person.
    """
    class Meta:
        model = Person
        fields = [
            'given_name',
            'family_name',
            'preferred_name',
            'date_of_birth',
            'email',
            'phone',
            'phone_secondary',
            'address_line1',
            'address_line2',
            'city',
            'state',
            'postal_code',
            'country',
            'emergency_contact_name',
            'emergency_contact_phone',
            'notes',
            'is_active',
        ]

    def validate_email(self, value):
        """Ensure email is unique if provided"""
        if value and Person.objects.filter(email=value).exists():
            raise serializers.ValidationError("A person with this email already exists.")
        return value