from rest_framework import serializers
from .models import Genre, ClassType, Evaluation, Term, ClassInstance, Enrollment, AttendanceRecord


class GenreSerializer(serializers.ModelSerializer):
    """Full serializer for Genre model"""

    class Meta:
        model = Genre
        fields = [
            'id', 'name', 'code', 'description', 'is_active',
            'notes', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class GenreListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for listing genres"""

    class Meta:
        model = Genre
        fields = ['id', 'name', 'code', 'is_active']


class ClassTypeSerializer(serializers.ModelSerializer):
    """Full serializer for ClassType model"""
    genre_name = serializers.CharField(source='genre.name', read_only=True)

    class Meta:
        model = ClassType
        fields = [
            'id', 'name', 'code', 'genre', 'genre_name', 'level', 'description',
            'min_age', 'max_age', 'duration_minutes', 'price_per_term',
            'is_active', 'notes', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class ClassTypeListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for listing class types"""
    genre_name = serializers.CharField(source='genre.name', read_only=True)

    class Meta:
        model = ClassType
        fields = ['id', 'name', 'code', 'genre_name', 'level', 'price_per_term', 'is_active']


class EvaluationSerializer(serializers.ModelSerializer):
    """Full serializer for Evaluation model"""
    student_name = serializers.CharField(source='student.person.full_name', read_only=True)
    genre_name = serializers.CharField(source='genre.name', read_only=True)
    evaluated_by_name = serializers.CharField(source='evaluated_by.person.full_name', read_only=True)
    is_expired = serializers.ReadOnlyField()

    class Meta:
        model = Evaluation
        fields = [
            'id', 'student', 'student_name', 'genre', 'genre_name',
            'level_achieved', 'evaluation_date', 'evaluated_by',
            'evaluated_by_name', 'notes', 'expires_on', 'is_expired',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def validate(self, data):
        """Validate evaluation business rules"""
        from django.utils import timezone

        # Cannot evaluate for future dates
        if data.get('evaluation_date') and data['evaluation_date'] > timezone.now().date():
            raise serializers.ValidationError({
                'evaluation_date': 'Cannot create evaluation for future dates'
            })

        # If expiry is set, it must be after evaluation date
        if data.get('expires_on') and data.get('evaluation_date'):
            if data['expires_on'] <= data['evaluation_date']:
                raise serializers.ValidationError({
                    'expires_on': 'Expiry date must be after evaluation date'
                })

        return data


class EvaluationListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for listing evaluations"""
    student_name = serializers.CharField(source='student.person.full_name', read_only=True)
    genre_name = serializers.CharField(source='genre.name', read_only=True)
    is_expired = serializers.ReadOnlyField()

    class Meta:
        model = Evaluation
        fields = [
            'id', 'student_name', 'genre_name', 'level_achieved',
            'evaluation_date', 'is_expired'
        ]


class TermSerializer(serializers.ModelSerializer):
    """Full serializer for Term model"""

    class Meta:
        model = Term
        fields = [
            'id', 'name', 'code', 'start_date', 'end_date',
            'enrollment_open_date', 'enrollment_close_date',
            'is_active', 'notes', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def validate(self, data):
        """Ensure end_date is after start_date"""
        if 'end_date' in data and 'start_date' in data:
            if data['end_date'] <= data['start_date']:
                raise serializers.ValidationError({'end_date': 'End date must be after start date'})
        return data


class TermListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for listing terms"""

    class Meta:
        model = Term
        fields = ['id', 'name', 'code', 'start_date', 'end_date', 'is_active']


class ClassInstanceSerializer(serializers.ModelSerializer):
    """Full serializer for ClassInstance model"""
    class_type_name = serializers.CharField(source='class_type.name', read_only=True)
    class_type_code = serializers.CharField(source='class_type.code', read_only=True)
    genre_name = serializers.CharField(source='class_type.genre.name', read_only=True)
    term_name = serializers.CharField(source='term.name', read_only=True)
    teacher_name = serializers.CharField(source='teacher.person.full_name', read_only=True)
    day_of_week_display = serializers.CharField(source='get_day_of_week_display', read_only=True)
    current_enrollment_count = serializers.ReadOnlyField()
    is_full = serializers.ReadOnlyField()
    available_spots = serializers.ReadOnlyField()

    class Meta:
        model = ClassInstance
        fields = [
            'id', 'class_type', 'class_type_name', 'class_type_code', 'genre_name',
            'term', 'term_name', 'teacher', 'teacher_name',
            'day_of_week', 'day_of_week_display', 'start_time', 'end_time',
            'room', 'max_students', 'current_enrollment_count', 'is_full',
            'available_spots', 'status', 'notes', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def validate(self, data):
        """Ensure end_time is after start_time"""
        if 'end_time' in data and 'start_time' in data:
            if data['end_time'] <= data['start_time']:
                raise serializers.ValidationError({'end_time': 'End time must be after start time'})
        return data


class ClassInstanceListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for listing class instances"""
    class_type_name = serializers.CharField(source='class_type.name', read_only=True)
    term_name = serializers.CharField(source='term.name', read_only=True)
    teacher_name = serializers.CharField(source='teacher.person.full_name', read_only=True)
    day_of_week_display = serializers.CharField(source='get_day_of_week_display', read_only=True)
    available_spots = serializers.ReadOnlyField()

    class Meta:
        model = ClassInstance
        fields = [
            'id', 'class_type_name', 'term_name', 'teacher_name',
            'day_of_week_display', 'start_time', 'room',
            'max_students', 'available_spots', 'status'
        ]


class EnrollmentSerializer(serializers.ModelSerializer):
    """Full serializer for Enrollment model"""
    student_name = serializers.CharField(source='account.student.person.full_name', read_only=True)
    account_code = serializers.CharField(source='account.account_code', read_only=True)
    class_name = serializers.CharField(source='class_instance.class_type.name', read_only=True)
    term_name = serializers.CharField(source='class_instance.term.name', read_only=True)
    is_active_enrollment = serializers.ReadOnlyField()
    total_cost = serializers.ReadOnlyField()
    amount_outstanding = serializers.ReadOnlyField()

    class Meta:
        model = Enrollment
        fields = [
            'id', 'account', 'account_code', 'student_name', 'class_instance',
            'class_name', 'term_name', 'status', 'enrollment_date', 'trial_date',
            'active_date', 'withdrawn_date', 'completed_date', 'amount_paid',
            'is_active_enrollment', 'total_cost', 'amount_outstanding',
            'notes', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'enrollment_date', 'created_at', 'updated_at']

    def validate(self, data):
        """Ensure class isn't full and student has required evaluation"""
        # Only validate capacity for new enrollments
        if not self.instance and data.get('class_instance'):
            class_instance = data['class_instance']

            # Check capacity
            if class_instance.is_full:
                raise serializers.ValidationError({
                    'class_instance': f'Class is full. Maximum capacity is {class_instance.max_students} students.'
                })

            # Check evaluation requirement
            if data.get('account'):
                student = data['account'].student
                genre = class_instance.class_type.genre

                # Check for valid (non-expired) evaluation
                from django.db.models import Q
                from django.utils import timezone

                valid_evaluations = student.evaluations.filter(
                    genre=genre
                ).filter(
                    Q(expires_on__isnull=True) | Q(expires_on__gte=timezone.now().date())
                )

                if not valid_evaluations.exists():
                    raise serializers.ValidationError({
                        'account': f'Student must have a valid evaluation for {genre.name} before enrolling in this class.'
                    })

        return data


class EnrollmentListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for listing enrollments"""
    student_name = serializers.CharField(source='account.student.person.full_name', read_only=True)
    account_code = serializers.CharField(source='account.account_code', read_only=True)
    class_name = serializers.CharField(source='class_instance.class_type.name', read_only=True)
    term_name = serializers.CharField(source='class_instance.term.name', read_only=True)
    amount_outstanding = serializers.ReadOnlyField()

    class Meta:
        model = Enrollment
        fields = [
            'id', 'account_code', 'student_name', 'class_name', 'term_name',
            'status', 'enrollment_date', 'amount_outstanding'
        ]


class AttendanceRecordSerializer(serializers.ModelSerializer):
    """Full serializer for AttendanceRecord model"""
    student_name = serializers.CharField(source='student.person.full_name', read_only=True)
    class_name = serializers.CharField(source='class_instance.class_type.name', read_only=True)
    marked_by_name = serializers.CharField(source='marked_by.person.full_name', read_only=True)

    class Meta:
        model = AttendanceRecord
        fields = [
            'id', 'class_instance', 'class_name', 'student', 'student_name',
            'enrollment', 'date', 'status', 'marked_by', 'marked_by_name',
            'marked_at', 'notes', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'marked_at', 'created_at', 'updated_at']

    def validate(self, data):
        """Validate attendance record business rules"""
        from django.utils import timezone

        # Cannot mark attendance for future dates
        if data.get('date') and data['date'] > timezone.now().date():
            raise serializers.ValidationError({
                'date': 'Cannot mark attendance for future dates'
            })

        # Cannot mark attendance for cancelled classes
        if data.get('class_instance') and data['class_instance'].status == 'cancelled':
            raise serializers.ValidationError({
                'class_instance': 'Cannot mark attendance for cancelled classes'
            })

        # Verify student is enrolled in the class (if enrollment not provided, try to find it)
        if not data.get('enrollment') and data.get('student') and data.get('class_instance'):
            try:
                enrollment = Enrollment.objects.get(
                    account__student=data['student'],
                    class_instance=data['class_instance'],
                    status__in=['trial', 'active']
                )
                data['enrollment'] = enrollment
            except Enrollment.DoesNotExist:
                raise serializers.ValidationError({
                    'student': f'Student is not enrolled in this class'
                })
            except Enrollment.MultipleObjectsReturned:
                raise serializers.ValidationError({
                    'student': 'Multiple active enrollments found for this student in this class'
                })

        # Verify enrollment matches student and class_instance
        if data.get('enrollment'):
            if data.get('student') and data['enrollment'].account.student != data['student']:
                raise serializers.ValidationError({
                    'enrollment': 'Enrollment student must match attendance student'
                })
            if data.get('class_instance') and data['enrollment'].class_instance != data['class_instance']:
                raise serializers.ValidationError({
                    'enrollment': 'Enrollment class must match attendance class'
                })

        return data


class AttendanceRecordListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for listing attendance records"""
    student_name = serializers.CharField(source='student.person.full_name', read_only=True)
    class_name = serializers.CharField(source='class_instance.class_type.name', read_only=True)

    class Meta:
        model = AttendanceRecord
        fields = [
            'id', 'student_name', 'class_name', 'date', 'status', 'marked_at'
        ]
