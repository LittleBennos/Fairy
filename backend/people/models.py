from django.db import models
from django.core.validators import RegexValidator
from django.conf import settings
import uuid


def generate_person_code():
    """Generate unique person code like PER-XXXXX"""
    return f"PER-{uuid.uuid4().hex[:8].upper()}"


class Person(models.Model):
    """
    Base entity representing any individual (student, guardian, staff, billing contact).
    Stores core personal information that is shared across roles.
    """

    # Unique identifier
    person_code = models.CharField(
        max_length=20,
        unique=True,
        default=generate_person_code,
        help_text="Unique person code (auto-generated)"
    )

    # Name
    given_name = models.CharField(max_length=100, help_text="First name")
    family_name = models.CharField(max_length=100, help_text="Last name")
    preferred_name = models.CharField(
        max_length=100,
        blank=True,
        help_text="Nickname or preferred name"
    )

    # Date of birth
    date_of_birth = models.DateField(help_text="Date of birth")

    # Contact information
    email = models.EmailField(
        max_length=254,
        unique=True,
        null=True,
        blank=True,
        help_text="Email address (unique if provided)"
    )

    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed."
    )
    phone = models.CharField(
        validators=[phone_regex],
        max_length=17,
        blank=True,
        help_text="Primary phone number"
    )
    phone_secondary = models.CharField(
        validators=[phone_regex],
        max_length=17,
        blank=True,
        help_text="Secondary phone number"
    )

    # Address
    address_line1 = models.CharField(max_length=255, help_text="Street address")
    address_line2 = models.CharField(
        max_length=255,
        blank=True,
        help_text="Apartment, suite, unit, etc."
    )
    city = models.CharField(max_length=100, help_text="City")
    state = models.CharField(max_length=50, help_text="State/Province")
    postal_code = models.CharField(max_length=20, help_text="Postal/ZIP code")
    country = models.CharField(max_length=100, default="Australia", help_text="Country")

    # Emergency contact
    emergency_contact_name = models.CharField(
        max_length=200,
        blank=True,
        help_text="Emergency contact name"
    )
    emergency_contact_phone = models.CharField(
        validators=[phone_regex],
        max_length=17,
        blank=True,
        help_text="Emergency contact phone"
    )

    # Additional information
    notes = models.TextField(blank=True, help_text="General notes about this person")

    # Status
    is_active = models.BooleanField(default=True, help_text="Is this person active?")

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Optional link to User account for portal access
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='person_profile',
        help_text="User account for portal access (optional)"
    )

    class Meta:
        ordering = ['family_name', 'given_name']
        indexes = [
            models.Index(fields=['person_code']),
            models.Index(fields=['email']),
            models.Index(fields=['family_name', 'given_name']),
            models.Index(fields=['is_active']),
        ]
        verbose_name = 'Person'
        verbose_name_plural = 'People'

    def __str__(self):
        if self.preferred_name:
            return f"{self.given_name} '{self.preferred_name}' {self.family_name} ({self.person_code})"
        return f"{self.given_name} {self.family_name} ({self.person_code})"

    @property
    def full_name(self):
        """Returns full name"""
        return f"{self.given_name} {self.family_name}"

    @property
    def display_name(self):
        """Returns preferred name if available, otherwise full name"""
        if self.preferred_name:
            return f"{self.preferred_name} {self.family_name}"
        return self.full_name

    @property
    def full_address(self):
        """Returns formatted full address"""
        parts = [
            self.address_line1,
            self.address_line2,
            f"{self.city}, {self.state} {self.postal_code}",
            self.country
        ]
        return ', '.join(filter(None, parts))