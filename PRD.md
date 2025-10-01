# Product Requirements Document (PRD)
## Fairy Dance Studio Management System

**Version:** 1.0
**Date:** September 30, 2025
**Author:** Development Team
**Status:** Draft

---

## 1. Executive Summary

### 1.1 Project Overview
Fairy Dance Studio Management System is a custom-built web application designed to streamline operations for a dance studio, including student enrollment, class scheduling, parent portal access, attendance tracking, and basic financial management.

### 1.2 Problem Statement
Current solutions (like Corteza) are either:
- Too complex and not designed for customer-facing portals
- Commercial solutions with high recurring costs
- Lack the specific features needed for dance studio operations

### 1.3 Goals
- Enable efficient student and guardian management
- Provide self-service parent portal for enrollment and information access
- Streamline class scheduling and attendance tracking
- Support basic invoicing and payment tracking
- Build foundation for future growth and features

### 1.4 Core Architecture Decision: Account-Based Structure

**Key Design Choice:**
The system uses an **Account-based structure** rather than treating students as independent entities. This provides maximum flexibility for different enrollment scenarios.

**Account Structure:**
- **Person** = Base entity for any individual (stores name, contact, address, DOB)
- **Account** = Groups together Student + Guardian + BillingContact
- **Student/Guardian/BillingContact** = Roles that link to Person records

**This handles all scenarios:**
1. **Child with Parents**: Child Person (Student), Parent 1 Person (Guardian), Parent 2 Person (BillingContact)
2. **Adult Student**: Same Person fills all three roles (Student, Guardian, BillingContact)
3. **Split Billing**: Child Person (Student), Parent 1 Person (Guardian), Grandparent Person (BillingContact)
4. **Sponsored Student**: Student Person (Student), Parent Person (Guardian), Organization Person (BillingContact)

**Benefits:**
- One Person can have multiple roles across different Accounts
- Adult students can self-register without needing a separate guardian
- Clear billing responsibility per Account
- Flexible for family situations (divorced parents, guardianships, etc.)
- Person data (contact info) stored once, referenced many times

---

## 2. Target Users

### 2.1 Primary Users

**Studio Staff (Admins)**
- Studio owners/administrators
- Front desk staff
- **Needs:** Manage students, schedule classes, track attendance, handle enrollments, view reports

**Teachers/Instructors**
- Dance instructors
- **Needs:** View class schedules, mark attendance, see student information, add class notes

**Parents/Guardians**
- Primary contacts for students
- **Needs:** Enroll children in classes, view schedules, update contact info, see invoices, book trial classes

**Students** (Future Phase)
- Dance students (age-appropriate access)
- **Needs:** View their own schedule, see attendance history

---

## 3. Core Features & Requirements

### 3.1 Phase 1: MVP (Minimum Viable Product)

#### 3.1.1 User Management & Authentication

**Staff Users**
- Email/password authentication
- Role-based access control (Admin, Staff, Teacher)
- Password reset functionality
- Session management

**Parent/Guardian Portal**
- Self-registration capability
- Email verification
- Password reset
- Profile management

**Requirements:**
- Secure authentication (Django allauth)
- JWT tokens for API access
- Session timeout after 30 minutes of inactivity
- Password requirements: min 8 characters, 1 uppercase, 1 number

#### 3.1.2 Person Management

**Person Records (Base Entity):**
- Core Information:
  - Person code (unique identifier, auto-generated)
  - Given name (required)
  - Family name (required)
  - Preferred name
  - Date of birth
  - Email (unique if provided)
  - Phone (primary and secondary)
  - Full address (line1, line2, city, state, postal_code, country)
  - Emergency contact name and phone
  - Notes

**CRUD Operations:**
- Create new person
- View person list (with search/filter)
- Edit person details
- Soft delete (mark as inactive)
- Search by: name, email, phone, person code
- Filter by: roles (student, guardian, staff, billing)

**Business Rules:**
- Person code must be unique
- Email must be unique if provided
- At least one contact method required (email or phone)

#### 3.1.3 Account Management

**Account Records:**
- Links together Student + Guardian + BillingContact
- Account Information:
  - Account code (unique identifier, auto-generated)
  - Student (Person reference - required)
  - Guardian (Person reference - required for minors, optional for adults)
  - BillingContact (Person reference - required)
  - Account status: Active, Inactive, Suspended, Closed
  - Start date
  - End date (if closed)
  - Notes

**Special Cases:**
- **Adult Student**: Same Person is Student, Guardian, and BillingContact
- **Child with Single Parent**: Parent Person is both Guardian and BillingContact, child is Student
- **Child with Split Billing**: Child is Student, Parent 1 is Guardian, Parent 2 is BillingContact
- **Sponsored Student**: Student is one Person, Guardian is another, BillingContact is a third (e.g., scholarship sponsor)

**CRUD Operations:**
- Create new account (requires selecting/creating 3 People: Student, Guardian, Billing)
- View account list (with search/filter)
- Edit account details (can swap out People as needed)
- Close account (soft delete)
- Search by: student name, guardian name, account code
- Filter by: status, account age, billing contact

**Business Rules:**
- Each Account must have exactly one Student Person
- Each Account must have exactly one Guardian Person (can be same as Student if adult)
- Each Account must have exactly one BillingContact Person
- All three can reference the same Person (adult student scenario)
- Cannot delete Person if they're referenced by active Accounts

#### 3.1.4 Student Role Management

**Student-Specific Fields:**
- Links to Person for personal info
- Medical notes (long text)
- Allergies (long text)
- Photo consent (boolean)
- School attending
- Year level
- Student status: Prospect, Trial, Active, Waitlist, Left
- Start date

**Business Rules:**
- One Person can only have one Student role
- Student records store class-specific information (medical, school, etc.)

#### 3.1.5 Guardian Role Management

**Guardian-Specific Fields:**
- Links to Person for personal info
- Authorized for pickup (boolean)
- Communication preferences (email, SMS, phone)
- Relationship notes

**Business Rules:**
- One Person can be Guardian on multiple Accounts
- Guardian role indicates emergency contact/legal guardian responsibility

#### 3.1.6 BillingContact Role Management

**BillingContact-Specific Fields:**
- Links to Person for personal info
- Billing address override (if different from Person address)
- Preferred payment method: Card, Bank Transfer, Cash, Other
- Billing preferences: Email, PDF, Paper, Portal
- Payment notes

**Business Rules:**
- One Person can be BillingContact on multiple Accounts
- BillingContact receives all invoices and payment communications

#### 3.1.7 Genre Management

**Genre Records:**
- Dance style categories (Ballet, Jazz, Tap, Hip Hop, Contemporary, Acrobatics, etc.)
- Genre Information:
  - Genre code (unique, required) - e.g., "BAL", "JAZ", "TAP"
  - Genre name (required) - e.g., "Ballet", "Jazz"
  - Description (long text)
  - Active status (boolean)
  - Display color (for UI/calendar)

**CRUD Operations:**
- Create new genres
- View genre list
- Edit genre details
- Archive genres (soft delete)
- Filter by: active status

**Business Rules:**
- Genre code must be unique
- Cannot delete genre if ClassTypes exist for it

#### 3.1.8 ClassType Management

**ClassType Catalog:**
- Specific class offerings with levels (e.g., "Level 1 Ballet", "Intermediate Jazz")
- ClassType Information:
  - ClassType code (unique, required) - e.g., "BAL-L1", "JAZ-INT"
  - ClassType name (required) - e.g., "Level 1 Ballet"
  - Genre (required) - foreign key to Genre (e.g., Ballet)
  - Level (required) - e.g., 1, 2, 3, or Beginner, Intermediate, Advanced
  - Age minimum
  - Age maximum
  - Default fee (per term)
  - Duration (minutes)
  - Active status (boolean)
  - Description (long text)

**CRUD Operations:**
- Create class types
- View class type catalog
- Edit class type details
- Archive class types (soft delete)
- Filter by: genre, level, active status

**Business Rules:**
- ClassType code must be unique
- Must reference valid Genre
- Cannot delete ClassType if active ClassInstances exist

#### 3.1.9 Terms (Academic Calendar)

**Term Configuration:**
- Term name (required) - e.g., "Term 1 2025"
- Start date (required)
- End date (required)
- Billing cycle: Per Term, Monthly
- Active status (boolean)

**Business Rules:**
- Terms cannot overlap
- Cannot delete term if classes are scheduled
- End date must be after start date

#### 3.1.10 Class Scheduling

**Class Instance (Scheduled Classes):**
- ClassType selection (required)
- Term (required)
- Teacher assignment
- Location details:
  - Venue
  - Room
- Schedule:
  - Day of week (required): Mon-Sun
  - Start time (required) - HH:MM format
  - End time (required)
  - Recurring weekly within term dates
- Capacity (number)
- Status: Planned, Open, Full, Cancelled
- Fee override (can override ClassType default fee)

**Business Rules:**
- No overlapping classes in same room at same time
- Teacher cannot be double-booked
- Capacity must be positive number
- End time must be after start time
- Cannot schedule class outside term dates

#### 3.1.10 Student Evaluation Management

**Evaluation Records:**
- Student skill assessments per Genre to determine appropriate ClassType level
- Evaluation Information:
  - Student (required)
  - Genre (required) - e.g., Ballet, Jazz, Tap
  - Level achieved (required) - e.g., Level 1, Level 2, Beginner, Intermediate
  - Evaluation date
  - Evaluated by (Staff member - required)
  - Score/grade (optional)
  - Notes (long text) - instructor observations
  - Status: Pending, Completed, Expired
  - Valid until date (typically 6-12 months from evaluation date)

**CRUD Operations:**
- Schedule new evaluation (creates Pending status)
- Conduct evaluation and record results (changes to Completed)
- View evaluation history per student
- View evaluations requiring action (Pending)
- Filter by: student, genre, status, evaluator

**Evaluation Workflow:**
1. Student applies for class requiring evaluation
2. Staff schedules evaluation (status: Pending)
3. Instructor conducts evaluation and records level achieved (status: Completed)
4. Student can now enroll in ClassTypes at or below their evaluated level
5. Evaluation expires after validity period (status: Expired)
6. Re-evaluation required for expired evaluations or higher levels

**Business Rules:**
- Student must have **valid (Completed, not Expired) evaluation** for a Genre before enrolling in ClassType of that Genre
- Enrollment remains "Applied" until evaluation is Completed and meets ClassType level requirement
- One active evaluation per Student per Genre
- Evaluations expire after configurable period (default: 12 months)
- Students can enroll in ClassTypes at or below their evaluated level
- Students cannot enroll in ClassTypes above their evaluated level without new evaluation
- Re-evaluations override previous evaluations for same Genre

#### 3.1.11 Enrollment Management

**Enrollment Records:**
- Account (required) - links to Student, Guardian, BillingContact
- Class instance (required)
- Enrollment status: Applied, Trial, Active, Waitlist, Withdrawn
- Start date
- End date
- Discount code
- Fee override (override ClassType/ClassInstance fee for specific account)
- Notes

**Enrollment Workflow:**
1. Guardian/Student applies for class (status: Applied)
2. **System checks if Student has valid Evaluation for ClassType's Genre and Level**
3. If no valid evaluation exists, enrollment blocked until evaluation completed
4. Staff reviews application and approves or puts on waitlist
5. Student attends trial (status: Trial)
6. Converts to active enrollment (status: Active)
7. Can be withdrawn (status: Withdrawn)

**Business Rules:**
- **Student must have valid Evaluation for ClassType's Genre at appropriate level**
- Account cannot enroll in same class twice (unless withdrawn then re-enrolling)
- Cannot exceed class capacity (unless status is Waitlist)
- Must check age requirements against student's age (from Account → Student → Person → DOB)
- Automatic waitlist if class is full
- Cannot enroll if account status is "Closed"
- All billing flows through Account → BillingContact

#### 3.1.12 Attendance Tracking

**Attendance Records:**
- Class instance + date
- Student
- Attendance status: Present, Absent, Late, Excused
- Notes
- Marked by (staff member)
- Marked at (timestamp)

**Features:**
- Class roll call view (all enrolled students for a class session)
- Quick mark all present
- Bulk operations
- Attendance history per student
- Attendance reports per class

**Business Rules:**
- Can only mark attendance for enrolled students
- Cannot mark attendance for future dates
- Cannot mark attendance for cancelled classes

#### 3.1.10 Staff Dashboard

**Dashboard Views:**
- Today's classes overview
- Upcoming enrollments requiring action
- Recent student registrations
- Quick stats:
  - Total active students
  - Total enrollments this term
  - Classes today
  - Pending applications

**Navigation:**
- Quick access to common tasks
- Search functionality
- Recent activity feed

#### 3.1.11 Parent Portal (Basic)

**Parent Access:**
- Login with email/password
- Dashboard showing:
  - All children linked to account
  - Each child's enrolled classes
  - Upcoming classes this week
  - Attendance history

**Features:**
- View class schedules
- Update contact information
- View children's details
- Request to enroll in new classes (creates enrollment with "Applied" status)

**Business Rules:**
- Parents can only see their own linked students
- Cannot modify student records (except contact info)
- Cannot cancel enrollments (must contact staff)

---

### 3.2 Phase 2: Enhanced Features (Post-MVP)

#### 3.2.1 Financial Management
- Invoice generation
- Payment tracking
- Outstanding balance reports
- Automated invoice emails
- Payment receipts

#### 3.2.2 Communication
- Email notifications (enrollment confirmations, class reminders)
- SMS notifications
- Announcements system
- Newsletter management

#### 3.2.3 Reporting
- Financial reports (revenue, outstanding)
- Attendance reports
- Student progress reports
- Class utilization reports
- Export to PDF/Excel

#### 3.2.4 Advanced Scheduling
- Make-up class management
- Class substitutions (replacement teachers)
- Holiday/closure management
- Automatic waitlist processing

#### 3.2.5 Parent Portal Enhanced
- Online payment processing (Stripe integration)
- View and download invoices
- Book trial classes
- Cancel enrollments
- Upload documents (medical certificates, etc.)

#### 3.2.6 Student Portal
- Age-appropriate interface for students
- View own schedule
- See attendance
- Progress tracking

---

## 4. Technical Requirements

### 4.1 Technology Stack

**Backend:**
- Python 3.11+
- Django 4.2 LTS
- Django REST Framework 3.14+
- PostgreSQL 15+
- Redis 7+ (caching, future Celery)

**Frontend:**
- React 18+
- Vite (build tool)
- Tailwind CSS (styling)
- React Router (routing)
- React Query (API state management)
- Axios (HTTP client)

**DevOps:**
- Docker & Docker Compose
- Nginx (reverse proxy)
- Git version control

**Future Additions:**
- Celery + Celery Beat (async tasks, scheduled jobs)
- Stripe API (payments)
- SendGrid/AWS SES (email)

### 4.2 Architecture

**System Architecture:**
```
┌─────────────────┐
│   React SPA     │
│  (Port 5173)    │
└────────┬────────┘
         │ HTTPS/REST API
         ↓
┌─────────────────┐
│  Nginx Proxy    │
│  (Port 80/443)  │
└────────┬────────┘
         │
         ↓
┌─────────────────┐
│  Django API     │
│  (Port 8000)    │
└────────┬────────┘
         │
         ↓
┌─────────────────┐      ┌─────────────┐
│   PostgreSQL    │      │    Redis    │
│   (Port 5432)   │      │ (Port 6379) │
└─────────────────┘      └─────────────┘
```

**Database Design Principles:**
- Normalized structure
- Proper foreign key relationships
- Soft deletes where appropriate (is_active flag)
- Audit fields (created_at, updated_at, created_by, updated_by)
- Unique constraints on codes/emails
- Indexes on frequently queried fields

### 4.3 API Design

**REST API Conventions:**
- RESTful endpoints
- JSON request/response
- JWT authentication for protected endpoints
- Pagination for list endpoints (default 20 items)
- Filtering, searching, sorting support
- Consistent error responses

**API Examples:**
```
GET    /api/students/              - List students
POST   /api/students/              - Create student
GET    /api/students/{id}/         - Get student detail
PUT    /api/students/{id}/         - Update student
DELETE /api/students/{id}/         - Delete student

GET    /api/students/?status=Active&search=John
GET    /api/students/{id}/guardians/
GET    /api/students/{id}/enrollments/
```

### 4.4 Security Requirements

**Authentication & Authorization:**
- JWT tokens for API auth
- Role-based access control (RBAC)
- Secure password hashing (Django default: PBKDF2)
- HTTPS only in production
- CORS properly configured

**Data Protection:**
- Input validation on all fields
- SQL injection protection (Django ORM)
- XSS protection
- CSRF protection
- Rate limiting on API endpoints

**Privacy:**
- GDPR considerations (data export, deletion)
- Separate parent/guardian access
- Staff can only see students they manage
- Audit trail for sensitive operations

### 4.5 Performance Requirements

**Response Times:**
- API responses: < 200ms (p95)
- Page loads: < 2s (initial load)
- Search results: < 500ms

**Scalability:**
- Support up to 500 active students
- Support up to 1000 guardians
- Handle 50 concurrent users
- Database queries optimized (select_related, prefetch_related)

**Availability:**
- 99% uptime target
- Automatic database backups (daily)
- Error monitoring and alerts

---

## 5. User Interface Requirements

### 5.1 Design Principles

**Staff Interface:**
- Clean, professional design
- Desktop-first (primary use on computers)
- Quick access to common tasks
- Table views with sorting/filtering
- Inline editing where appropriate
- Confirmation dialogs for destructive actions

**Parent Portal:**
- Mobile-responsive (primary use on phones)
- Simple, intuitive navigation
- Card-based layouts
- Large touch targets
- Clear call-to-action buttons

### 5.2 Key Screens/Views

**Staff Interface:**
1. Dashboard (overview)
2. Student List & Detail views
3. Guardian List & Detail views
4. Class Schedule (calendar view)
5. Enrollment Management
6. Attendance Roll Call
7. Course Catalog Management
8. Term Management

**Parent Portal:**
1. Parent Dashboard
2. Child Profile views
3. Class Schedule view
4. Enrollment Request form
5. Contact Information update
6. Attendance History

### 5.3 Responsive Breakpoints

- Desktop: 1024px+
- Tablet: 768px - 1023px
- Mobile: < 768px

---

## 6. Data Models (Core Entities)

### 6.0 Database Tables Overview

#### 1. User
**Table:** `auth_user` (Django built-in)
- `id` - Integer (PK)
- `username` - String(150)
- `email` - String(254)
- `password` - String(128) - hashed
- `first_name` - String(150)
- `last_name` - String(150)
- `is_active` - Boolean
- `is_staff` - Boolean
- `is_superuser` - Boolean
- `date_joined` - DateTime
- `last_login` - DateTime

**Extended with:**
- `role` - String(20) - choices: admin, staff, teacher, parent

**Relations:** (1-to-1 with Person - optional)

---

#### 2. Person
**Table:** `person`
- `id` - Integer (PK)
- `person_code` - String(20) - unique, auto-generated
- `given_name` - String(100)
- `family_name` - String(100)
- `preferred_name` - String(100) - nullable
- `date_of_birth` - Date
- `email` - String(254) - unique, nullable
- `phone` - String(17) - nullable
- `phone_secondary` - String(17) - nullable
- `address_line1` - String(255)
- `address_line2` - String(255) - nullable
- `city` - String(100)
- `state` - String(50)
- `postal_code` - String(20)
- `country` - String(100) - default "Australia"
- `emergency_contact_name` - String(200) - nullable
- `emergency_contact_phone` - String(17) - nullable
- `notes` - Text - nullable
- `is_active` - Boolean - default True
- `created_at` - DateTime
- `updated_at` - DateTime

**Relations:** (1-to-1 with User optional, 1-to-many with Student/Guardian/BillingContact/Staff)

---

#### 3. Student
**Table:** `student`
- `id` - Integer (PK)
- `person_id` - Integer (FK → Person)
- `medical_notes` - Text - nullable
- `allergies` - Text - nullable
- `photo_consent` - Boolean - default False
- `school_attending` - String(200) - nullable
- `year_level` - String(50) - nullable
- `status` - String(20) - choices: prospect, trial, active, waitlist, left
- `start_date` - Date - nullable
- `notes` - Text - nullable
- `created_at` - DateTime
- `updated_at` - DateTime

**Relations:** (FK to Person, 1-to-many with Evaluation/AttendanceRecord, used in Account)

---

#### 4. Guardian
**Table:** `guardian`
- `id` - Integer (PK)
- `person_id` - Integer (FK → Person)
- `authorized_for_pickup` - Boolean - default True
- `communication_preference` - String(20) - choices: email, sms, phone, portal
- `relationship_notes` - Text - nullable
- `created_at` - DateTime
- `updated_at` - DateTime

**Relations:** (FK to Person, used in Account)

---

#### 5. BillingContact
**Table:** `billing_contact`
- `id` - Integer (PK)
- `person_id` - Integer (FK → Person)
- `billing_address_line1` - String(255) - nullable
- `billing_address_line2` - String(255) - nullable
- `billing_city` - String(100) - nullable
- `billing_state` - String(50) - nullable
- `billing_postal_code` - String(20) - nullable
- `billing_country` - String(100) - nullable
- `payment_method` - String(20) - choices: card, bank_transfer, cash, other
- `billing_preference` - String(20) - choices: email, pdf, paper, portal
- `payment_notes` - Text - nullable
- `created_at` - DateTime
- `updated_at` - DateTime

**Relations:** (FK to Person, used in Account)

---

#### 6. Staff
**Table:** `staff`
- `id` - Integer (PK)
- `person_id` - Integer (FK → Person)
- `hire_date` - Date
- `termination_date` - Date - nullable
- `role` - String(20) - choices: admin, teacher, front_desk
- `bio` - Text - nullable
- `specialties` - Text - nullable
- `certifications` - Text - nullable
- `employment_status` - String(20) - choices: active, on_leave, terminated
- `created_at` - DateTime
- `updated_at` - DateTime

**Relations:** (FK to Person, 1-to-many with ClassInstance/Evaluation/AttendanceRecord)

---

#### 7. Account
**Table:** `account`
- `id` - Integer (PK)
- `account_code` - String(20) - unique, auto-generated
- `student_id` - Integer (FK → Student)
- `guardian_id` - Integer (FK → Guardian)
- `billing_contact_id` - Integer (FK → BillingContact)
- `status` - String(20) - choices: active, inactive, suspended, closed
- `start_date` - Date
- `end_date` - Date - nullable
- `notes` - Text - nullable
- `created_at` - DateTime
- `updated_at` - DateTime

**Relations:** (FKs to Student/Guardian/BillingContact, 1-to-many with Enrollment)

---

#### 8. Genre
**Table:** `genre`
- `id` - Integer (PK)
- `genre_code` - String(20) - unique
- `name` - String(100) - e.g., "Ballet", "Jazz", "Tap"
- `description` - Text - nullable
- `color` - String(7) - nullable - hex color for UI
- `is_active` - Boolean - default True
- `created_at` - DateTime
- `updated_at` - DateTime

**Relations:** (1-to-many with ClassType/Evaluation)

---

#### 9. ClassType
**Table:** `class_type`
- `id` - Integer (PK)
- `genre_id` - Integer (FK → Genre)
- `type_code` - String(50) - unique - e.g., "BAL-L1"
- `name` - String(200) - e.g., "Level 1 Ballet"
- `level` - String(50) - e.g., "1", "2", "beginner", "intermediate"
- `min_age` - Integer
- `max_age` - Integer - nullable
- `price_per_term` - Decimal(10,2)
- `duration_minutes` - Integer - default 60
- `description` - Text - nullable
- `is_active` - Boolean - default True
- `notes` - Text - nullable
- `created_at` - DateTime
- `updated_at` - DateTime

**Relations:** (FK to Genre, 1-to-many with ClassInstance)

---

#### 10. Term
**Table:** `term`
- `id` - Integer (PK)
- `term_code` - String(50) - unique
- `name` - String(100) - e.g., "Spring 2025"
- `start_date` - Date
- `end_date` - Date
- `enrollment_open_date` - Date - nullable
- `enrollment_close_date` - Date - nullable
- `is_active` - Boolean - default True
- `notes` - Text - nullable
- `created_at` - DateTime
- `updated_at` - DateTime

**Relations:** (1-to-many with ClassInstance)

---

#### 11. ClassInstance
**Table:** `class_instance`
- `id` - Integer (PK)
- `class_type_id` - Integer (FK → ClassType)
- `term_id` - Integer (FK → Term)
- `teacher_id` - Integer (FK → Staff) - nullable
- `day_of_week` - Integer - 0=Monday, 6=Sunday
- `start_time` - Time
- `end_time` - Time
- `room` - String(100) - nullable
- `max_students` - Integer - default 15
- `status` - String(20) - choices: scheduled, in_progress, completed, cancelled
- `fee_override` - Decimal(10,2) - nullable
- `notes` - Text - nullable
- `created_at` - DateTime
- `updated_at` - DateTime

**Relations:** (FKs to ClassType/Term/Staff, 1-to-many with Enrollment/AttendanceRecord)

---

#### 12. Evaluation
**Table:** `evaluation`
- `id` - Integer (PK)
- `student_id` - Integer (FK → Student)
- `genre_id` - Integer (FK → Genre)
- `evaluator_id` - Integer (FK → Staff)
- `evaluation_date` - Date
- `level_achieved` - String(50) - e.g., "1", "2", "beginner"
- `score` - Decimal(5,2) - nullable
- `status` - String(20) - choices: pending, completed, expired
- `valid_until` - Date
- `notes` - Text - nullable
- `created_at` - DateTime
- `updated_at` - DateTime

**Relations:** (FKs to Student/Genre/Staff)

---

#### 13. Enrollment
**Table:** `enrollment`
- `id` - Integer (PK)
- `account_id` - Integer (FK → Account)
- `class_instance_id` - Integer (FK → ClassInstance)
- `status` - String(20) - choices: applied, trial, active, waitlist, withdrawn, completed
- `enrollment_date` - Date - auto
- `trial_date` - Date - nullable
- `active_date` - Date - nullable
- `withdrawn_date` - Date - nullable
- `completed_date` - Date - nullable
- `amount_paid` - Decimal(10,2) - default 0.00
- `discount_code` - String(50) - nullable
- `fee_override` - Decimal(10,2) - nullable
- `notes` - Text - nullable
- `created_at` - DateTime
- `updated_at` - DateTime

**Relations:** (FKs to Account/ClassInstance, 1-to-many with AttendanceRecord)

---

#### 14. AttendanceRecord
**Table:** `attendance_record`
- `id` - Integer (PK)
- `student_id` - Integer (FK → Student)
- `class_instance_id` - Integer (FK → ClassInstance)
- `enrollment_id` - Integer (FK → Enrollment)
- `date` - Date
- `status` - String(20) - choices: present, absent, late, excused
- `marked_by_id` - Integer (FK → Staff) - nullable
- `marked_at` - DateTime - auto
- `notes` - Text - nullable
- `created_at` - DateTime
- `updated_at` - DateTime

**Relations:** (FKs to Student/ClassInstance/Enrollment/Staff)

---

## 6. Data Models (Core Entities)

### 6.1 User
- Built-in Django User model
- Extended with role field: admin, staff, teacher, parent
- Used for authentication and portal access

### 6.2 Person
- Base entity representing any individual (student, guardian, staff, or billing contact)
- Stores core personal information:
  - Given name, family name, preferred name
  - Date of birth
  - Email, phone (primary and secondary)
  - Full address (line1, line2, city, state, postal_code, country)
  - Emergency contact information
- One-to-one: Person → User (optional, only if portal access needed)
- Person can have multiple roles via linked entities

### 6.3 Account
- Central entity that groups Student + Guardian + BillingContact
- Represents a complete enrollment package
- Many-to-one: Account → Student (the enrolled person)
- Many-to-one: Account → Guardian (emergency contact/legal guardian)
- Many-to-one: Account → BillingContact (who pays)
- All three can reference the same Person (adult student) or different People (child with parents)
- Status: Active, Inactive, Suspended
- Notes field for account-level information

### 6.4 Student
- Extends Person concept via Person foreign key
- Many-to-one: Student → Person
- Student-specific fields:
  - Medical notes, allergies, photo consent
  - School attending, year level
  - Student status: Prospect, Trial, Active, Waitlist, Left
  - Start date
- One-to-many: Student → Enrollments
- One-to-many: Student → AttendanceRecords

### 6.5 Guardian
- Extends Person concept via Person foreign key
- Many-to-one: Guardian → Person
- Guardian-specific fields:
  - Relationship to student(s)
  - Authorized for pickup (boolean)
  - Communication preferences
- Linked to Accounts where this person is the guardian

### 6.6 BillingContact
- Extends Person concept via Person foreign key
- Many-to-one: BillingContact → Person
- Billing-specific fields:
  - Billing address (if different from person address)
  - Preferred payment method: Card, Bank Transfer, Cash, Other
  - Billing preferences: Email, PDF, Paper, Portal
  - Payment notes
- Linked to Accounts where this person handles billing

### 6.7 Staff
- Extends Person concept via Person foreign key
- Many-to-one: Staff → Person
- Staff-specific fields:
  - Hire date, termination date
  - Role: Admin, Teacher, Front Desk
  - Bio, specialties, certifications
  - Employment status: Active, On Leave, Terminated

### 6.8 Genre
- Dance style category (Ballet, Jazz, Tap, Hip Hop, Contemporary, etc.)
- Fields:
  - Genre code (unique identifier)
  - Name, description
  - Display color (for UI/calendar)
  - Active status
- One-to-many: Genre → ClassTypes

### 6.9 ClassType
- Specific class offering with level (e.g., "Level 1 Ballet", "Intermediate Jazz")
- Many-to-one: ClassType → Genre
- Fields:
  - ClassType code (unique identifier)
  - Name (e.g., "Level 1 Ballet")
  - Level (1, 2, 3, or Beginner/Intermediate/Advanced)
  - Age requirements (min/max)
  - Price per term
  - Duration in minutes
  - Description, active status
- One-to-many: ClassType → ClassInstances

### 6.10 Term
- Academic period/semester
- Fields:
  - Term code, name
  - Start/end dates
  - Enrollment open/close dates
  - Active status
- One-to-many: Term → ClassInstances

### 6.11 ClassInstance
- Scheduled class (e.g., "Level 1 Ballet, Mondays 4pm, Spring 2025")
- Many-to-one: ClassInstance → ClassType
- Many-to-one: ClassInstance → Term
- Many-to-one: ClassInstance → Teacher (Staff)
- Fields:
  - Day of week, start time, end time
  - Room/location
  - Max students capacity
  - Status (Scheduled, In Progress, Completed, Cancelled)
  - Fee override (optional)
- One-to-many: ClassInstance → Enrollments
- One-to-many: ClassInstance → AttendanceRecords

### 6.12 Enrollment
- Many-to-one: Enrollment → Account (not Student directly)
- Many-to-one: Enrollment → ClassInstance
- Enrollment binds an Account to a class, not just a student
- Billing flows through Account → BillingContact

### 6.13 Evaluation
- Student skill assessment per Genre (determines appropriate ClassType level)
- Many-to-one: Evaluation → Student
- Many-to-one: Evaluation → Genre
- Many-to-one: Evaluation → EvaluatedBy (Staff)
- Fields:
  - Evaluation date
  - Genre (Ballet, Jazz, Tap, etc.)
  - Level achieved (1, 2, 3, or Beginner/Intermediate/Advanced)
  - Score/notes
  - Status: Pending, Completed, Expired
  - Valid until date (evaluations expire after X months)
- Business Rules:
  - Student must have valid evaluation for a Genre before enrolling in ClassType of that Genre
  - Enrollment status remains "Applied" until evaluation is "Completed" and meets ClassType level requirement
  - Evaluations expire after 6-12 months (configurable)
  - One active evaluation per Student per Genre

### 6.14 AttendanceRecord
- Many-to-one: AttendanceRecord → ClassInstance
- Many-to-one: AttendanceRecord → Student
- Many-to-one: AttendanceRecord → MarkedBy (Staff)

---

## 7. Success Metrics

### 7.1 MVP Success Criteria

**Technical:**
- All Phase 1 features implemented and tested
- < 5 critical bugs reported in first month
- 99% uptime during business hours
- API response times < 200ms (p95)

**Business:**
- Staff can manage students without external tools
- Parents can successfully register and view information
- 80% of enrollments processed through system
- Staff saves 5+ hours/week on administration

**User Satisfaction:**
- Staff training completed in < 2 hours
- Parents successfully complete first login (80% success rate)
- Positive feedback from 3+ staff members
- Zero data loss incidents

---

## 8. Constraints & Assumptions

### 8.1 Constraints

**Technical:**
- Must be self-hosted (no cloud services required)
- Must work on existing hardware (reasonable specs)
- Budget: $0 (open-source only)
- Timeline: MVP in 4-6 weeks

**Business:**
- Single location initially (multi-location future)
- English language only (i18n future)
- Australian timezone (AEST/AEDT)

### 8.1 Assumptions

- Users have modern web browsers (Chrome, Firefox, Safari, Edge - latest 2 versions)
- Staff have computer access
- Parents have smartphones or computers
- Internet connectivity is reliable
- Basic technical literacy of users

---

## 9. Risks & Mitigations

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| Data loss | High | Low | Daily backups, version control |
| Security breach | High | Medium | Security best practices, regular updates |
| Poor user adoption | High | Medium | User testing, training, feedback loops |
| Performance issues | Medium | Low | Load testing, optimization, monitoring |
| Scope creep | Medium | High | Strict MVP definition, phased approach |
| Technical debt | Medium | Medium | Code reviews, refactoring time, documentation |

---

## 10. Out of Scope (Not in MVP)

**Explicitly NOT included in Phase 1:**
- Payment processing (Stripe integration)
- Automated email notifications
- SMS notifications
- Invoice generation
- Online class booking calendar
- Student progress tracking
- Mobile native apps
- Multi-location support
- Multiple languages
- Advanced reporting/analytics
- Integration with accounting software
- Video/photo galleries
- Student achievements/badges
- Public website integration
- Marketing automation
- Inventory management (merchandise, costumes)

---

## 11. Timeline & Milestones

### Phase 1: MVP (6 weeks)

**Week 1-2: Setup & Core Models**
- Project setup (Django + React)
- Database schema design
- User authentication
- Student & Guardian models
- Basic CRUD operations

**Week 3-4: Scheduling & Enrollment**
- Course/Term models
- Class scheduling
- Enrollment workflow
- Attendance tracking

**Week 5: Parent Portal**
- Parent authentication
- Dashboard
- View enrollments
- Request enrollment

**Week 6: Testing & Polish**
- Bug fixes
- UI polish
- Staff training
- Documentation
- Deployment

### Phase 2: Enhanced Features (TBD)
- Financial management (4 weeks)
- Communication system (2 weeks)
- Reporting (2 weeks)
- Advanced features (ongoing)

---

## 12. Appendices

### 12.1 Glossary

- **Guardian:** Parent or authorized adult responsible for a student
- **Student:** Child enrolled or prospective in dance classes
- **Course:** A type of dance class (e.g., "Ballet Beginners")
- **Term:** Academic period (typically 10-12 weeks)
- **Class Instance:** Specific scheduled class within a term
- **Enrollment:** Student's registration in a specific class instance
- **Attendance:** Record of student presence at a class session
- **Trial:** Student attending class to evaluate before committing
- **Waitlist:** Queue of students waiting for spot in full class

### 12.2 References

- Django Documentation: https://docs.djangoproject.com/
- Django REST Framework: https://www.django-rest-framework.org/
- React Documentation: https://react.dev/
- Costasiella (reference): https://github.com/costasiella/costasiella
- Django Dance School (reference): https://github.com/django-danceschool/django-danceschool

### 12.3 Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2025-09-30 | Dev Team | Initial PRD |

---

**Document Status:** ✅ Ready for Review

**Next Steps:**
1. Review and approval of PRD
2. Create database schema ERD
3. Set up development environment
4. Begin implementation