from django.db import models
from django.core.validators import RegexValidator
import uuid


def generate_account_code():
    """Generate unique account code like ACC-XXXXX"""
    return f"ACC-{uuid.uuid4().hex[:8].upper()}"


class Student(models.Model):
    """
    Student role - links to Person for personal data.
    Stores student-specific information (medical, school, etc.)
    """

    STATUS_CHOICES = [
        ('prospect', 'Prospect'),
        ('trial', 'Trial'),
        ('active', 'Active'),
        ('waitlist', 'Waitlist'),
        ('left', 'Left'),
    ]

    person = models.OneToOneField(
        'people.Person',
        on_delete=models.CASCADE,
        related_name='student',
        help_text="Person this student role belongs to"
    )

    # Student-specific fields
    medical_notes = models.TextField(blank=True, help_text="Medical conditions, medications, etc.")
    allergies = models.TextField(blank=True, help_text="Known allergies")
    photo_consent = models.BooleanField(default=False, help_text="Consent for photos/videos")
    school_attending = models.CharField(max_length=200, blank=True, help_text="School name")
    year_level = models.CharField(max_length=50, blank=True, help_text="Year/Grade level")

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='prospect',
        help_text="Student status"
    )
    start_date = models.DateField(null=True, blank=True, help_text="Date started with studio")

    notes = models.TextField(blank=True, help_text="Additional notes about student")

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['person__family_name', 'person__given_name']
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['person']),
        ]

    def __str__(self):
        return f"Student: {self.person.full_name}"


class Guardian(models.Model):
    """
    Guardian role - links to Person for personal data.
    Stores guardian-specific information (pickup authorization, communication preferences)
    """

    COMM_PREFERENCE_CHOICES = [
        ('email', 'Email'),
        ('sms', 'SMS'),
        ('phone', 'Phone'),
        ('portal', 'Portal'),
    ]

    person = models.OneToOneField(
        'people.Person',
        on_delete=models.CASCADE,
        related_name='guardian',
        help_text="Person this guardian role belongs to"
    )

    # Guardian-specific fields
    authorized_for_pickup = models.BooleanField(
        default=True,
        help_text="Authorized to pick up student from classes"
    )
    communication_preference = models.CharField(
        max_length=20,
        choices=COMM_PREFERENCE_CHOICES,
        default='email',
        help_text="Preferred communication method"
    )
    relationship_notes = models.TextField(
        blank=True,
        help_text="Notes about relationship to student(s)"
    )

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['person__family_name', 'person__given_name']
        indexes = [
            models.Index(fields=['person']),
        ]

    def __str__(self):
        return f"Guardian: {self.person.full_name}"


class BillingContact(models.Model):
    """
    BillingContact role - links to Person for personal data.
    Stores billing-specific information (payment method, billing address)
    """

    PAYMENT_METHOD_CHOICES = [
        ('card', 'Credit/Debit Card'),
        ('bank_transfer', 'Bank Transfer'),
        ('cash', 'Cash'),
        ('other', 'Other'),
    ]

    BILLING_PREFERENCE_CHOICES = [
        ('email', 'Email'),
        ('pdf', 'PDF Download'),
        ('paper', 'Paper/Mail'),
        ('portal', 'Portal'),
    ]

    person = models.OneToOneField(
        'people.Person',
        on_delete=models.CASCADE,
        related_name='billing_contact',
        help_text="Person this billing contact role belongs to"
    )

    # Billing address override (if different from person's address)
    billing_address_line1 = models.CharField(max_length=255, blank=True)
    billing_address_line2 = models.CharField(max_length=255, blank=True)
    billing_city = models.CharField(max_length=100, blank=True)
    billing_state = models.CharField(max_length=50, blank=True)
    billing_postal_code = models.CharField(max_length=20, blank=True)
    billing_country = models.CharField(max_length=100, blank=True)

    # Payment preferences
    payment_method = models.CharField(
        max_length=20,
        choices=PAYMENT_METHOD_CHOICES,
        default='card',
        help_text="Preferred payment method"
    )
    billing_preference = models.CharField(
        max_length=20,
        choices=BILLING_PREFERENCE_CHOICES,
        default='email',
        help_text="How to receive invoices"
    )
    payment_notes = models.TextField(blank=True, help_text="Payment-related notes")

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['person__family_name', 'person__given_name']
        indexes = [
            models.Index(fields=['person']),
        ]

    def __str__(self):
        return f"BillingContact: {self.person.full_name}"

    @property
    def full_billing_address(self):
        """Returns formatted billing address (or person's address if no override)"""
        if self.billing_address_line1:
            parts = [
                self.billing_address_line1,
                self.billing_address_line2,
                f"{self.billing_city}, {self.billing_state} {self.billing_postal_code}",
                self.billing_country
            ]
            return ', '.join(filter(None, parts))
        return self.person.full_address


class Staff(models.Model):
    """
    Staff role - links to Person for personal data.
    Stores staff-specific information (hire date, role, employment status)
    """

    ROLE_CHOICES = [
        ('admin', 'Administrator'),
        ('teacher', 'Teacher'),
        ('front_desk', 'Front Desk'),
    ]

    EMPLOYMENT_STATUS_CHOICES = [
        ('active', 'Active'),
        ('on_leave', 'On Leave'),
        ('terminated', 'Terminated'),
    ]

    person = models.OneToOneField(
        'people.Person',
        on_delete=models.CASCADE,
        related_name='staff',
        help_text="Person this staff role belongs to"
    )

    # Employment details
    hire_date = models.DateField(help_text="Date of hire")
    termination_date = models.DateField(
        null=True,
        blank=True,
        help_text="Date of termination (if applicable)"
    )

    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default='teacher',
        help_text="Staff role"
    )

    # Additional information
    bio = models.TextField(blank=True, help_text="Staff biography")
    specialties = models.TextField(blank=True, help_text="Dance specialties (e.g., Ballet, Jazz)")
    certifications = models.TextField(blank=True, help_text="Certifications and qualifications")

    employment_status = models.CharField(
        max_length=20,
        choices=EMPLOYMENT_STATUS_CHOICES,
        default='active',
        help_text="Current employment status"
    )

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['person__family_name', 'person__given_name']
        indexes = [
            models.Index(fields=['employment_status']),
            models.Index(fields=['role']),
            models.Index(fields=['person']),
        ]
        verbose_name = 'Staff'
        verbose_name_plural = 'Staff'

    def __str__(self):
        return f"Staff: {self.person.full_name} ({self.get_role_display()})"


class Account(models.Model):
    """
    Account groups Student + Guardian + BillingContact.
    Represents a complete enrollment package.
    """

    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('suspended', 'Suspended'),
        ('closed', 'Closed'),
    ]

    account_code = models.CharField(
        max_length=20,
        unique=True,
        default=generate_account_code,
        help_text="Unique account code (auto-generated)"
    )

    # Three required roles
    student = models.ForeignKey(
        Student,
        on_delete=models.PROTECT,
        related_name='accounts',
        help_text="Student enrolled in this account"
    )
    guardian = models.ForeignKey(
        Guardian,
        on_delete=models.PROTECT,
        related_name='accounts',
        help_text="Guardian responsible for this student"
    )
    billing_contact = models.ForeignKey(
        BillingContact,
        on_delete=models.PROTECT,
        related_name='accounts',
        help_text="Billing contact for payments"
    )

    # Account status
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='active',
        help_text="Account status"
    )

    start_date = models.DateField(help_text="Account start date")
    end_date = models.DateField(
        null=True,
        blank=True,
        help_text="Account end date (if closed)"
    )

    notes = models.TextField(blank=True, help_text="Account notes")

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['account_code']),
            models.Index(fields=['status']),
            models.Index(fields=['student']),
            models.Index(fields=['guardian']),
            models.Index(fields=['billing_contact']),
        ]

    def __str__(self):
        return f"Account {self.account_code}: {self.student.person.full_name}"

    def clean(self):
        """Validate account business rules"""
        from django.core.exceptions import ValidationError

        # Can optionally add validation that guardian and billing must be adults
        # (check student.person.date_of_birth vs guardian.person.date_of_birth)
        pass
