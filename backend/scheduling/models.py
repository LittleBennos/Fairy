from django.db import models
from django.core.validators import MinValueValidator


class Genre(models.Model):
    """
    Dance genre/style (e.g., Ballet, Jazz, Tap).
    Used to categorize ClassTypes and track student skill levels via Evaluations.
    """

    name = models.CharField(max_length=100, unique=True, help_text="Genre name (e.g., Ballet)")
    code = models.CharField(max_length=20, unique=True, help_text="Unique genre code (e.g., BAL)")
    description = models.TextField(blank=True, help_text="Genre description")

    # Status
    is_active = models.BooleanField(
        default=True,
        help_text="Is this genre currently offered?"
    )

    # Metadata
    notes = models.TextField(blank=True, help_text="Internal notes about the genre")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']
        indexes = [
            models.Index(fields=['code']),
            models.Index(fields=['is_active']),
        ]

    def __str__(self):
        return f"{self.name} ({self.code})"


class ClassType(models.Model):
    """
    Class type catalog entry (e.g., Level 1 Ballet, Intermediate Jazz).
    This is a template/catalog entry, not a scheduled class.
    Renamed from Course to better reflect its purpose.
    """

    LEVEL_CHOICES = [
        ('beginner', 'Beginner'),
        ('elementary', 'Elementary'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced'),
        ('pre_professional', 'Pre-Professional'),
    ]

    name = models.CharField(max_length=200, help_text="Class type name (e.g., Level 1 Ballet)")
    code = models.CharField(max_length=50, unique=True, help_text="Unique class type code (e.g., BAL-L1)")

    # Link to Genre
    genre = models.ForeignKey(
        Genre,
        on_delete=models.PROTECT,
        related_name='class_types',
        help_text="The dance genre this class belongs to"
    )

    level = models.CharField(max_length=50, choices=LEVEL_CHOICES)
    description = models.TextField(blank=True, help_text="Class type description")

    # Age requirements
    min_age = models.IntegerField(
        validators=[MinValueValidator(0)],
        help_text="Minimum age in years"
    )
    max_age = models.IntegerField(
        validators=[MinValueValidator(0)],
        blank=True,
        null=True,
        help_text="Maximum age in years (optional)"
    )

    # Duration and pricing
    duration_minutes = models.IntegerField(
        validators=[MinValueValidator(1)],
        default=60,
        help_text="Class duration in minutes"
    )
    price_per_term = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        help_text="Price per term (in dollars)"
    )

    # Status
    is_active = models.BooleanField(
        default=True,
        help_text="Is this class type currently offered?"
    )

    # Metadata
    notes = models.TextField(blank=True, help_text="Internal notes about the class type")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['genre', 'level', 'name']
        indexes = [
            models.Index(fields=['code']),
            models.Index(fields=['genre', 'level']),
            models.Index(fields=['is_active']),
        ]

    def __str__(self):
        return f"{self.name} ({self.code})"


class Evaluation(models.Model):
    """
    Student skill evaluation for a specific genre.
    Determines which class types a student is eligible to enroll in.
    Students must have a valid evaluation for a genre before enrolling in classes of that genre.
    """

    LEVEL_CHOICES = [
        ('beginner', 'Beginner'),
        ('elementary', 'Elementary'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced'),
        ('pre_professional', 'Pre-Professional'),
    ]

    student = models.ForeignKey(
        'accounts.Student',
        on_delete=models.CASCADE,
        related_name='evaluations',
        help_text="The student being evaluated"
    )
    genre = models.ForeignKey(
        Genre,
        on_delete=models.PROTECT,
        related_name='evaluations',
        help_text="The dance genre being evaluated"
    )

    # Evaluation details
    level_achieved = models.CharField(
        max_length=50,
        choices=LEVEL_CHOICES,
        help_text="Skill level achieved by student for this genre"
    )
    evaluation_date = models.DateField(help_text="Date of evaluation")

    # Evaluator (staff member who conducted the evaluation)
    evaluated_by = models.ForeignKey(
        'accounts.Staff',
        on_delete=models.PROTECT,
        related_name='evaluations_conducted',
        help_text="Staff member who conducted this evaluation"
    )

    # Additional information
    notes = models.TextField(
        blank=True,
        help_text="Notes about the evaluation (strengths, areas for improvement, etc.)"
    )

    # Expiry (optional - some studios want evaluations to be re-done periodically)
    expires_on = models.DateField(
        blank=True,
        null=True,
        help_text="Expiry date for this evaluation (optional)"
    )

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-evaluation_date', 'student', 'genre']
        indexes = [
            models.Index(fields=['student', 'genre']),
            models.Index(fields=['genre', 'level_achieved']),
            models.Index(fields=['evaluation_date']),
        ]

    def __str__(self):
        return f"{self.student.person.full_name} - {self.genre.name} ({self.level_achieved}) - {self.evaluation_date}"

    @property
    def is_expired(self):
        """Returns True if evaluation has expired"""
        if not self.expires_on:
            return False
        from django.utils import timezone
        return self.expires_on < timezone.now().date()

    def clean(self):
        """Validate evaluation business rules"""
        from django.core.exceptions import ValidationError
        from django.utils import timezone

        # Cannot evaluate for future dates
        if self.evaluation_date and self.evaluation_date > timezone.now().date():
            raise ValidationError('Cannot create evaluation for future dates')

        # If expiry is set, it must be after evaluation date
        if self.expires_on and self.evaluation_date and self.expires_on <= self.evaluation_date:
            raise ValidationError('Expiry date must be after evaluation date')


class Term(models.Model):
    """
    Academic term/semester (e.g., Spring 2025, Summer 2025).
    Defines the billing cycle and class scheduling period.
    """

    name = models.CharField(max_length=100, help_text="Term name (e.g., Spring 2025)")
    code = models.CharField(max_length=50, unique=True, help_text="Unique term code (e.g., 2025-SPRING)")

    start_date = models.DateField(help_text="First day of term")
    end_date = models.DateField(help_text="Last day of term")

    enrollment_open_date = models.DateField(
        blank=True,
        null=True,
        help_text="When enrollment opens for this term"
    )
    enrollment_close_date = models.DateField(
        blank=True,
        null=True,
        help_text="When enrollment closes for this term"
    )

    is_active = models.BooleanField(
        default=True,
        help_text="Is this term currently active?"
    )

    notes = models.TextField(blank=True, help_text="Internal notes about the term")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-start_date']
        indexes = [
            models.Index(fields=['code']),
            models.Index(fields=['start_date', 'end_date']),
            models.Index(fields=['is_active']),
        ]

    def __str__(self):
        return f"{self.name} ({self.start_date} - {self.end_date})"

    def clean(self):
        """Validate that end_date is after start_date"""
        from django.core.exceptions import ValidationError
        if self.end_date and self.start_date and self.end_date <= self.start_date:
            raise ValidationError('End date must be after start date')


class ClassInstance(models.Model):
    """
    A scheduled class instance (e.g., Level 1 Ballet, Mondays 4pm, Spring 2025).
    This is an actual scheduled class that students can enroll in.
    """

    DAY_OF_WEEK_CHOICES = [
        (0, 'Monday'),
        (1, 'Tuesday'),
        (2, 'Wednesday'),
        (3, 'Thursday'),
        (4, 'Friday'),
        (5, 'Saturday'),
        (6, 'Sunday'),
    ]

    STATUS_CHOICES = [
        ('scheduled', 'Scheduled'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]

    class_type = models.ForeignKey(
        ClassType,
        on_delete=models.PROTECT,
        related_name='class_instances',
        help_text="The class type this class is based on"
    )
    term = models.ForeignKey(
        Term,
        on_delete=models.PROTECT,
        related_name='class_instances',
        help_text="The term this class runs in"
    )

    # Teacher (optional - can be assigned later)
    teacher = models.ForeignKey(
        'accounts.Staff',
        on_delete=models.PROTECT,
        related_name='classes_taught',
        blank=True,
        null=True,
        help_text="Teacher assigned to this class"
    )

    # Scheduling
    day_of_week = models.IntegerField(
        choices=DAY_OF_WEEK_CHOICES,
        help_text="Day of week (0=Monday, 6=Sunday)"
    )
    start_time = models.TimeField(help_text="Class start time")
    end_time = models.TimeField(help_text="Class end time")

    # Location
    room = models.CharField(max_length=100, blank=True, help_text="Studio/room name")

    # Capacity
    max_students = models.IntegerField(
        validators=[MinValueValidator(1)],
        default=15,
        help_text="Maximum number of students"
    )

    # Status
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='scheduled',
        help_text="Current status of the class"
    )

    # Metadata
    notes = models.TextField(blank=True, help_text="Internal notes about this class instance")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['term', 'day_of_week', 'start_time']
        indexes = [
            models.Index(fields=['class_type', 'term']),
            models.Index(fields=['term', 'day_of_week']),
            models.Index(fields=['teacher']),
            models.Index(fields=['status']),
        ]

    def __str__(self):
        day_name = dict(self.DAY_OF_WEEK_CHOICES)[self.day_of_week]
        return f"{self.class_type.name} - {day_name} {self.start_time.strftime('%I:%M%p')} ({self.term.name})"

    @property
    def current_enrollment_count(self):
        """Returns the number of currently enrolled students"""
        return self.enrollments.filter(status='active').count()

    @property
    def is_full(self):
        """Returns True if the class is at capacity"""
        return self.current_enrollment_count >= self.max_students

    @property
    def available_spots(self):
        """Returns the number of available spots"""
        return max(0, self.max_students - self.current_enrollment_count)

    def clean(self):
        """Validate that end_time is after start_time"""
        from django.core.exceptions import ValidationError
        if self.end_time and self.start_time and self.end_time <= self.start_time:
            raise ValidationError('End time must be after start time')


class Enrollment(models.Model):
    """
    Account enrollment in a class instance.
    Tracks enrollment status through workflow: Applied → Trial → Active → Withdrawn/Completed.
    Links to Account (not Student directly) to support the Account-based architecture.
    """

    STATUS_CHOICES = [
        ('applied', 'Applied'),
        ('trial', 'Trial'),
        ('active', 'Active'),
        ('withdrawn', 'Withdrawn'),
        ('completed', 'Completed'),
    ]

    account = models.ForeignKey(
        'accounts.Account',
        on_delete=models.CASCADE,
        related_name='enrollments',
        help_text="The account enrolling in the class"
    )
    class_instance = models.ForeignKey(
        ClassInstance,
        on_delete=models.CASCADE,
        related_name='enrollments',
        help_text="The class instance"
    )

    # Status workflow
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='applied',
        help_text="Current enrollment status"
    )

    # Important dates
    enrollment_date = models.DateField(
        auto_now_add=True,
        help_text="Date of initial enrollment/application"
    )
    trial_date = models.DateField(
        blank=True,
        null=True,
        help_text="Date trial status was granted"
    )
    active_date = models.DateField(
        blank=True,
        null=True,
        help_text="Date enrollment became active"
    )
    withdrawn_date = models.DateField(
        blank=True,
        null=True,
        help_text="Date student withdrew"
    )
    completed_date = models.DateField(
        blank=True,
        null=True,
        help_text="Date enrollment was completed (end of term)"
    )

    # Financial
    amount_paid = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00,
        validators=[MinValueValidator(0)],
        help_text="Total amount paid for this enrollment"
    )

    # Metadata
    notes = models.TextField(blank=True, help_text="Notes about this enrollment")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['account', 'class_instance']
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['account', 'status']),
            models.Index(fields=['class_instance', 'status']),
            models.Index(fields=['status']),
        ]

    def __str__(self):
        return f"{self.account.student.person.full_name} - {self.class_instance.class_type.name} ({self.status})"

    @property
    def is_active_enrollment(self):
        """Returns True if enrollment is in an active state (trial or active)"""
        return self.status in ['trial', 'active']

    @property
    def total_cost(self):
        """Returns the total cost for this enrollment (from class type)"""
        return self.class_instance.class_type.price_per_term

    @property
    def amount_outstanding(self):
        """Returns the outstanding balance"""
        return max(0, self.total_cost - self.amount_paid)

    def clean(self):
        """Validate enrollment doesn't exceed class capacity and student has required evaluation"""
        from django.core.exceptions import ValidationError

        # Skip validation if this is an update to an existing enrollment
        if self.pk:
            return

        # Check if class is full (only count active enrollments)
        if self.class_instance.is_full:
            raise ValidationError(
                f'Class is full. Maximum capacity is {self.class_instance.max_students} students.'
            )

        # Check if student has valid evaluation for this genre
        student = self.account.student
        genre = self.class_instance.class_type.genre

        # Check for valid (non-expired) evaluation
        valid_evaluations = student.evaluations.filter(
            genre=genre
        ).exclude(
            expires_on__lt=models.functions.Now()
        )

        if not valid_evaluations.exists():
            raise ValidationError(
                f'Student must have a valid evaluation for {genre.name} before enrolling in this class.'
            )


class AttendanceRecord(models.Model):
    """
    Attendance record for a student in a specific class session.
    Tracks whether student was present, absent, late, or excused for a given date.
    """

    STATUS_CHOICES = [
        ('present', 'Present'),
        ('absent', 'Absent'),
        ('late', 'Late'),
        ('excused', 'Excused'),
    ]

    class_instance = models.ForeignKey(
        ClassInstance,
        on_delete=models.CASCADE,
        related_name='attendance_records',
        help_text="The class instance this attendance is for"
    )
    student = models.ForeignKey(
        'accounts.Student',
        on_delete=models.CASCADE,
        related_name='attendance_records',
        help_text="The student this attendance record is for"
    )
    enrollment = models.ForeignKey(
        Enrollment,
        on_delete=models.CASCADE,
        related_name='attendance_records',
        help_text="The enrollment this attendance is linked to"
    )

    # Attendance details
    date = models.DateField(help_text="Date of the class session")
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='present',
        help_text="Attendance status"
    )

    # Staff tracking
    marked_by = models.ForeignKey(
        'accounts.Staff',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='marked_attendance_records',
        help_text="Staff member who marked this attendance"
    )
    marked_at = models.DateTimeField(
        auto_now=True,
        help_text="When attendance was marked/last updated"
    )

    # Additional information
    notes = models.TextField(
        blank=True,
        help_text="Additional notes about attendance (e.g., reason for absence)"
    )

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['class_instance', 'student', 'date']
        ordering = ['-date', 'class_instance', 'student']
        indexes = [
            models.Index(fields=['class_instance', 'date']),
            models.Index(fields=['student', 'date']),
            models.Index(fields=['enrollment', 'date']),
            models.Index(fields=['status']),
            models.Index(fields=['date']),
        ]

    def __str__(self):
        return f"{self.student.person.full_name} - {self.class_instance.class_type.name} ({self.date}) - {self.status}"

    def clean(self):
        """Validate attendance record business rules"""
        from django.core.exceptions import ValidationError
        from django.utils import timezone

        # Cannot mark attendance for future dates
        if self.date and self.date > timezone.now().date():
            raise ValidationError('Cannot mark attendance for future dates')

        # Cannot mark attendance for cancelled classes
        if self.class_instance.status == 'cancelled':
            raise ValidationError('Cannot mark attendance for cancelled classes')

        # Verify student is enrolled in the class
        if self.enrollment:
            if self.enrollment.account.student != self.student:
                raise ValidationError('Enrollment student must match attendance student')
            if self.enrollment.class_instance != self.class_instance:
                raise ValidationError('Enrollment class must match attendance class')
        else:
            # Auto-link enrollment if not provided
            try:
                self.enrollment = Enrollment.objects.get(
                    account__student=self.student,
                    class_instance=self.class_instance,
                    status__in=['trial', 'active']
                )
            except Enrollment.DoesNotExist:
                raise ValidationError(
                    f'Student {self.student.person.full_name} is not enrolled in this class'
                )
            except Enrollment.MultipleObjectsReturned:
                raise ValidationError(
                    f'Multiple active enrollments found for {self.student.person.full_name} in this class'
                )
